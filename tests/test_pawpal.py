from datetime import date, time, timedelta
from pawpal_system import Owner, Pet, PetType, Task, Frequency, Scheduler


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_owner() -> Owner:
    return Owner(
        username="test",
        password="",
        first_name="Test",
        last_name="User",
        availability="mornings",
    )

def make_task(title: str, hour: int, minute: int = 0,
              duration: int = 30, frequency: Frequency = Frequency.DAILY) -> Task:
    return Task(
        title=title,
        description="",
        frequency=frequency,
        due_date=date.today(),
        time_of_day=time(hour, minute),
        duration_minutes=duration,
    )


# ── Existing tests ────────────────────────────────────────────────────────────

def test_task_completion_changes_status():
    task = Task(
        title="Morning Walk",
        description="30-minute walk",
        frequency=Frequency.DAILY,
        due_date=date.today(),
    )
    assert task.is_completed is False
    task.check_off()
    assert task.is_completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(type=PetType.DOG, name="Biscuit", age=3)
    assert len(pet.tasks) == 0

    pet.add_task(Task(
        title="Joint Supplement",
        description="One tablet with breakfast",
        frequency=Frequency.DAILY,
        due_date=date.today(),
    ))
    assert len(pet.tasks) == 1

    pet.add_task(Task(
        title="Evening Walk",
        description="20-minute walk after dinner",
        frequency=Frequency.DAILY,
        due_date=date.today(),
    ))
    assert len(pet.tasks) == 2


# ── Sorting correctness ───────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    """Tasks added out of order should be returned sorted by time_of_day."""
    pet = Pet(type=PetType.DOG, name="Biscuit", age=3)
    pet.add_task(make_task("Evening Walk",   hour=19))
    pet.add_task(make_task("Lunch Meds",     hour=12))
    pet.add_task(make_task("Morning Walk",   hour=7))
    pet.add_task(make_task("Afternoon Play", hour=15))

    sorted_tasks = pet.get_tasks()
    times = [t.time_of_day for t in sorted_tasks]
    assert times == sorted(times), "get_tasks() should return tasks in chronological order"


def test_scheduler_sort_by_time_across_pets():
    """sort_by_time should interleave tasks from multiple pets correctly."""
    owner = make_owner()
    dog = Pet(type=PetType.DOG, name="Biscuit", age=3)
    cat = Pet(type=PetType.CAT, name="Mochi",   age=5)

    dog.add_task(make_task("Walk",       hour=9))
    cat.add_task(make_task("Feed",       hour=7))
    dog.add_task(make_task("Supplement", hour=8))

    owner.add_pet(dog)
    owner.add_pet(cat)

    sorted_tasks = owner.scheduler.sort_by_time(owner.get_all_tasks())
    titles = [t.title for t in sorted_tasks]
    assert titles == ["Feed", "Supplement", "Walk"]


# ── Recurrence logic ──────────────────────────────────────────────────────────

def test_complete_task_creates_next_daily_occurrence():
    """Completing a daily task should append a new task due the following day."""
    pet = Pet(type=PetType.DOG, name="Biscuit", age=3)
    task = make_task("Morning Walk", hour=7, frequency=Frequency.DAILY)
    pet.add_task(task)

    original_due = task.due_date
    pet.complete_task(task)

    assert task.is_completed is True
    assert len(pet.tasks) == 2

    next_task = pet.tasks[-1]
    assert next_task.is_completed is False
    assert next_task.due_date == original_due + timedelta(days=1)
    assert next_task.title == task.title


def test_complete_task_creates_next_weekly_occurrence():
    """Completing a weekly task should append a new task due 7 days later."""
    pet = Pet(type=PetType.CAT, name="Mochi", age=5)
    task = make_task("Brush Coat", hour=18, frequency=Frequency.WEEKLY)
    pet.add_task(task)

    original_due = task.due_date
    pet.complete_task(task)

    next_task = pet.tasks[-1]
    assert next_task.due_date == original_due + timedelta(weeks=1)
    assert next_task.frequency == Frequency.WEEKLY


def test_next_task_inherits_time_and_duration():
    """The auto-created next task should preserve time_of_day and duration_minutes."""
    pet = Pet(type=PetType.DOG, name="Biscuit", age=3)
    task = make_task("Walk", hour=7, minute=30, duration=45)
    pet.add_task(task)
    pet.complete_task(task)

    next_task = pet.tasks[-1]
    assert next_task.time_of_day == time(7, 30)
    assert next_task.duration_minutes == 45


# ── Conflict detection ────────────────────────────────────────────────────────

def test_detect_no_conflicts_when_tasks_dont_overlap():
    """Tasks with non-overlapping windows should produce no warnings."""
    owner = make_owner()
    dog = Pet(type=PetType.DOG, name="Biscuit", age=3)
    dog.add_task(make_task("Walk",       hour=7,  duration=30))  # 7:00–7:30
    dog.add_task(make_task("Supplement", hour=8,  duration=10))  # 8:00–8:10
    owner.add_pet(dog)

    warnings = owner.scheduler.detect_conflicts(owner)
    assert warnings == []


def test_detect_conflict_same_pet_overlap():
    """Two tasks for the same pet with overlapping windows should produce a warning."""
    owner = make_owner()
    dog = Pet(type=PetType.DOG, name="Biscuit", age=3)
    dog.add_task(make_task("Walk",    hour=7, duration=30))  # 7:00–7:30
    dog.add_task(make_task("Vet Med", hour=7, minute=15, duration=5))  # 7:15–7:20 — overlaps
    owner.add_pet(dog)

    warnings = owner.scheduler.detect_conflicts(owner)
    assert len(warnings) == 1
    assert "same pet" in warnings[0]
    assert "Walk" in warnings[0]
    assert "Vet Med" in warnings[0]


def test_detect_conflict_different_pets_overlap():
    """Two tasks for different pets with overlapping windows should produce a warning."""
    owner = make_owner()
    dog = Pet(type=PetType.DOG, name="Biscuit", age=3)
    cat = Pet(type=PetType.CAT, name="Mochi",   age=5)

    dog.add_task(make_task("Walk", hour=7, duration=30))   # 7:00–7:30
    cat.add_task(make_task("Feed", hour=7, minute=10, duration=10))  # 7:10–7:20 — overlaps

    owner.add_pet(dog)
    owner.add_pet(cat)

    warnings = owner.scheduler.detect_conflicts(owner)
    assert len(warnings) == 1
    assert "different pets" in warnings[0]


def test_detect_multiple_conflicts():
    """Three overlapping tasks should produce three conflict warnings."""
    owner = make_owner()
    dog = Pet(type=PetType.DOG, name="Biscuit", age=3)
    cat = Pet(type=PetType.CAT, name="Mochi",   age=5)

    dog.add_task(make_task("Walk",    hour=7, duration=30))       # 7:00–7:30
    dog.add_task(make_task("Vet Med", hour=7, minute=15, duration=5))  # overlaps Walk
    cat.add_task(make_task("Feed",    hour=7, minute=10, duration=10))  # overlaps both

    owner.add_pet(dog)
    owner.add_pet(cat)

    warnings = owner.scheduler.detect_conflicts(owner)
    assert len(warnings) == 3


def test_adjacent_tasks_are_not_flagged_as_conflicts():
    """A task that starts exactly when the previous one ends should not conflict."""
    owner = make_owner()
    dog = Pet(type=PetType.DOG, name="Biscuit", age=3)
    dog.add_task(make_task("Walk",       hour=7, duration=30))  # 7:00–7:30
    dog.add_task(make_task("Supplement", hour=7, minute=30, duration=5))  # starts at 7:30 exactly
    owner.add_pet(dog)

    warnings = owner.scheduler.detect_conflicts(owner)
    assert warnings == []
