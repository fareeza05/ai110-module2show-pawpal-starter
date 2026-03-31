from datetime import date, time
from pawpal_system import Owner, Pet, PetType, Task, Frequency

# --- Setup ---
owner = Owner(
    username="fareez",
    password="secret123",
    first_name="Fareez",
    last_name="Rahman",
    availability="Mornings and evenings",
)

# --- Create Pets ---
dog = Pet(type=PetType.DOG, name="Biscuit", age=3)
dog.add_info(
    health_issues=["mild hip dysplasia"],
    focus_areas=["joint health", "weight management"],
)

cat = Pet(type=PetType.CAT, name="Mochi", age=5)
cat.add_info(
    health_issues=["hairball sensitivity"],
    focus_areas=["diet", "stress reduction"],
)

owner.add_pet(dog)
owner.add_pet(cat)

# --- Add Tasks OUT OF ORDER (intentionally scrambled times) ---
dog.add_task(Task(
    title="Evening Walk",
    description="Wind-down walk after dinner",
    frequency=Frequency.DAILY,
    due_date=date.today(),
    time_of_day=time(19, 0),
    duration_minutes=20,
))

cat.add_task(Task(
    title="Brush Coat",
    description="5-minute brushing to reduce shedding and stress",
    frequency=Frequency.WEEKLY,
    due_date=date.today(),
    time_of_day=time(18, 0),
    duration_minutes=10,
))

dog.add_task(Task(
    title="Joint Supplement",
    description="One chewable hip & joint tablet with breakfast",
    frequency=Frequency.DAILY,
    due_date=date.today(),
    time_of_day=time(8, 0),
    duration_minutes=5,
))

cat.add_task(Task(
    title="Hairball Remedy",
    description="Half a teaspoon of hairball gel",
    frequency=Frequency.DAILY,
    due_date=date.today(),
    time_of_day=time(9, 30),
    duration_minutes=5,
    is_completed=True,  # already done — used to test completed filter
))

dog.add_task(Task(
    title="Morning Walk",
    description="30-minute walk around the block",
    frequency=Frequency.DAILY,
    due_date=date.today(),
    time_of_day=time(7, 0),
    duration_minutes=30,
))

cat.add_task(Task(
    title="Playtime",
    description="10 minutes of interactive toy play",
    frequency=Frequency.DAILY,
    due_date=date.today(),
    time_of_day=time(17, 0),
    duration_minutes=10,
))

# Conflict 1 (same pet — Biscuit): "Vet Meds" starts at 7:15 AM, inside Morning Walk (7:00–7:30)
dog.add_task(Task(
    title="Vet Meds",
    description="Administer prescribed medication",
    frequency=Frequency.DAILY,
    due_date=date.today(),
    time_of_day=time(7, 15),
    duration_minutes=5,
))

# Conflict 2 (different pets): Mochi's "Morning Feed" starts at 7:10 AM, also inside Morning Walk
cat.add_task(Task(
    title="Morning Feed",
    description="Wet food breakfast for Mochi",
    frequency=Frequency.DAILY,
    due_date=date.today(),
    time_of_day=time(7, 10),
    duration_minutes=10,
))

# ── 1. RAW ORDER (as added) ───────────────────────────────────────────────────
print("=" * 55)
print("  RAW ORDER (as added — intentionally scrambled)")
print("=" * 55)
for pet in owner.pets:
    print(f"\n  {pet.name}:")
    for task in pet.tasks:
        print(f"    {task.time_of_day.strftime('%I:%M %p')}  {task.title}")

# ── 2. SORTED BY TIME across all pets ────────────────────────────────────────
print("\n" + "=" * 55)
print("  SORTED BY TIME (all pets, sort_by_time)")
print("=" * 55)
all_tasks = owner.get_all_tasks()
for task in owner.scheduler.sort_by_time(all_tasks):
    print(f"  {task.time_of_day.strftime('%I:%M %p')}  {task.title}")

# ── 3. FILTER: Biscuit's tasks only ──────────────────────────────────────────
print("\n" + "=" * 55)
print("  FILTER: Biscuit's tasks (filter_tasks_for_owner)")
print("=" * 55)
for task in owner.scheduler.filter_tasks_for_owner(owner, pet_name="Biscuit"):
    print(f"  {task.time_of_day.strftime('%I:%M %p')}  {task.title}")

# ── 4. FILTER: completed tasks only ──────────────────────────────────────────
print("\n" + "=" * 55)
print("  FILTER: completed tasks only")
print("=" * 55)
completed = owner.scheduler.filter_tasks_for_owner(owner, completed=True)
if completed:
    for task in completed:
        print(f"  {task.time_of_day.strftime('%I:%M %p')}  {task.title}")
else:
    print("  None.")

# ── 5. FILTER: pending tasks only ────────────────────────────────────────────
print("\n" + "=" * 55)
print("  FILTER: pending tasks only")
print("=" * 55)
for task in owner.scheduler.filter_tasks_for_owner(owner, completed=False):
    print(f"  {task.time_of_day.strftime('%I:%M %p')}  {task.title}")

# ── 6. FILTER: Mochi's pending tasks ─────────────────────────────────────────
print("\n" + "=" * 55)
print("  FILTER: Mochi's pending tasks (combined filter)")
print("=" * 55)
for task in owner.scheduler.filter_tasks_for_owner(owner, pet_name="Mochi", completed=False):
    print(f"  {task.time_of_day.strftime('%I:%M %p')}  {task.title}")

# ── 7. CONFLICT DETECTION ────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("  CONFLICT DETECTION (same-pet and cross-pet)")
print("=" * 55)
warnings = owner.scheduler.detect_conflicts(owner)
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts detected.")

# ── 8. RECURRING TASK AUTO-CREATION ──────────────────────────────────────────
print("\n" + "=" * 55)
print("  RECURRING: complete a task, next instance auto-created")
print("=" * 55)

morning_walk = next(t for t in dog.tasks if t.title == "Morning Walk")
print(f"  Before:     {morning_walk}")
print(f"  Biscuit task count: {len(dog.tasks)}")

dog.complete_task(morning_walk)

print(f"\n  After complete_task():")
print(f"  Completed:  {morning_walk}")
next_walk = dog.tasks[-1]
print(f"  New instance: {next_walk}")
print(f"  Biscuit task count: {len(dog.tasks)}")

print("\n" + "=" * 55)
