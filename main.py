from datetime import date
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

# --- Add Tasks ---
dog.add_task(Task(
    title="Morning Walk",
    description="30-minute walk around the block",
    frequency=Frequency.DAILY,
    due_date=date.today(),
))

dog.add_task(Task(
    title="Joint Supplement",
    description="One chewable hip & joint tablet with breakfast",
    frequency=Frequency.DAILY,
    due_date=date.today(),
))

cat.add_task(Task(
    title="Hairball Remedy",
    description="Half a teaspoon of hairball gel",
    frequency=Frequency.DAILY,
    due_date=date.today(),
))

cat.add_task(Task(
    title="Brush Coat",
    description="5-minute brushing to reduce shedding and stress",
    frequency=Frequency.WEEKLY,
    due_date=date.today(),
))

# --- Print Today's Schedule ---
print("=" * 50)
print(f"  TODAY'S SCHEDULE — {date.today()}")
print(f"  Owner: {owner}")
print("=" * 50)

for frequency in Frequency:
    tasks = owner.scheduler.view_tasks(owner, frequency)
    print(f"\n  [{frequency.value.upper()}]")
    if not tasks:
        print("    No tasks.")
    else:
        for task in tasks:
            print(f"    {task}")

print()
print(owner.scheduler.view_insights(owner))
print("=" * 50)
