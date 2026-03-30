from datetime import date
from pawpal_system import Pet, PetType, Task, Frequency


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
