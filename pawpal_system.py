from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from enum import Enum


class PetType(Enum):
    DOG = "dog"
    CAT = "cat"
    OTHER = "other"


class Frequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Task:
    """A single care activity assigned to a pet with a frequency, time, and duration."""

    title: str
    description: str
    frequency: Frequency
    due_date: date = field(default_factory=date.today)
    time_of_day: time = field(default_factory=lambda: time(8, 0))
    duration_minutes: int = 30
    is_completed: bool = False

    def check_off(self) -> Task:
        """Mark this task as completed and return a new Task instance for the next occurrence."""
        self.is_completed = True
        return Task(
            title=self.title,
            description=self.description,
            frequency=self.frequency,
            due_date=self.next_due(),
            time_of_day=self.time_of_day,
            duration_minutes=self.duration_minutes,
            is_completed=False,
        )

    def is_due_today(self) -> bool:
        """Return True if this task is due today."""
        return self.due_date == date.today()

    def next_due(self) -> date:
        """Return the next due date based on frequency."""
        if self.frequency == Frequency.DAILY:
            return self.due_date + timedelta(days=1)
        return self.due_date + timedelta(weeks=1)

    def reset_for_next_cycle(self):
        """Uncheck the task and advance its due date to the next occurrence."""
        self.is_completed = False
        self.due_date = self.next_due()

    def __str__(self) -> str:
        """Return a formatted one-line summary of the task."""
        status = "✓" if self.is_completed else "○"
        return (
            f"[{status}] {self.title} ({self.frequency.value}) "
            f"@ {self.time_of_day.strftime('%I:%M %p')} "
            f"[{self.duration_minutes}min] — due {self.due_date}"
        )


@dataclass
class Pet:
    """A pet with health details and an associated list of care tasks."""

    type: PetType
    name: str
    age: int
    tasks: list[Task] = field(default_factory=list)
    prior_health_issues: list[str] = field(default_factory=list)
    focus_areas: list[str] = field(default_factory=list)

    def add_task(self, task: Task):
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def complete_task(self, task: Task):
        """Mark a task complete and automatically append its next occurrence to the list."""
        next_task = task.check_off()
        self.tasks.append(next_task)

    def remove_task(self, task: Task):
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def get_tasks(self, frequency: Frequency = None) -> list[Task]:
        """Return all tasks sorted by time_of_day, optionally filtered by frequency."""
        tasks = self.tasks if not frequency else [t for t in self.tasks if t.frequency == frequency]
        return sorted(tasks, key=lambda t: t.time_of_day)

    def add_info(self, health_issues: list[str] = None, focus_areas: list[str] = None):
        """Append health issues and focus areas to this pet's profile."""
        if health_issues:
            self.prior_health_issues.extend(health_issues)
        if focus_areas:
            self.focus_areas.extend(focus_areas)

    def __str__(self) -> str:
        """Return a short description of the pet."""
        return f"{self.name} ({self.type.value}, age {self.age})"


@dataclass
class Scheduler:
    """The brain that organizes and surfaces tasks across all of an owner's pets."""

    plan: str = ""

    def generate_plan(self, owner: Owner) -> str:
        """Build a care plan sorted by time, and advance any completed recurring tasks."""
        for pet in owner.pets:
            for task in pet.tasks:
                if task.is_completed:
                    task.reset_for_next_cycle()

        lines = [f"Care plan for {owner.first_name}'s pets | Availability: {owner.availability}\n"]
        for pet in owner.pets:
            lines.append(f"  {pet}")
            if pet.focus_areas:
                lines.append(f"    Focus: {', '.join(pet.focus_areas)}")
            if pet.prior_health_issues:
                lines.append(f"    Health notes: {', '.join(pet.prior_health_issues)}")
            for task in pet.get_tasks():  # already sorted by time_of_day
                lines.append(f"    {task}")

        self.plan = "\n".join(lines)
        return self.plan

    def edit_plan(self, updated_plan: str):
        """Replace the current plan with a manually updated version."""
        self.plan = updated_plan

    def view_tasks(
        self,
        owner: Owner,
        frequency: Frequency = None,
        pet: Pet = None,
        completed: bool = None,
    ) -> list[Task]:
        """Return tasks filtered by frequency, pet, and/or completion status, sorted by time."""
        tasks = owner.get_all_tasks(frequency)
        if pet is not None:
            tasks = [t for t in tasks if t in pet.tasks]
        if completed is not None:
            tasks = [t for t in tasks if t.is_completed == completed]
        return sorted(tasks, key=lambda t: t.time_of_day)

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by time_of_day using a lambda key on the HH:MM string."""
        return sorted(tasks, key=lambda t: t.time_of_day.strftime("%H:%M"))

    def filter_tasks_for_owner(
        self,
        owner: Owner,
        pet_name: str = None,
        completed: bool = None,
    ) -> list[Task]:
        """Return tasks across all pets, filtered by pet name and/or completion status."""
        results = []
        for pet in owner.pets:
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if completed is not None and task.is_completed != completed:
                    continue
                results.append(task)
        return self.sort_by_time(results)

    def detect_conflicts(self, owner: Owner) -> list[str]:
        """Return warning strings for any overlapping tasks across all pets; never raises."""
        warnings = []
        # Build a flat list of (task, pet) pairs sorted by start time
        tagged = sorted(
            [(task, pet) for pet in owner.pets for task in pet.tasks],
            key=lambda tp: tp[0].time_of_day,
        )
        for i, (a, pet_a) in enumerate(tagged):
            for b, pet_b in tagged[i + 1:]:
                a_start = a.time_of_day.hour * 60 + a.time_of_day.minute
                a_end   = a_start + a.duration_minutes
                b_start = b.time_of_day.hour * 60 + b.time_of_day.minute
                if b_start >= a_end:
                    break  # sorted — no further overlaps possible with a
                scope = "same pet" if pet_a is pet_b else "different pets"
                warnings.append(
                    f"⚠ CONFLICT ({scope}): '{a.title}' ({pet_a.name}) "
                    f"@ {a.time_of_day.strftime('%I:%M %p')} [{a.duration_minutes}min] "
                    f"overlaps '{b.title}' ({pet_b.name}) "
                    f"@ {b.time_of_day.strftime('%I:%M %p')}"
                )
        return warnings

    def view_insights(self, owner: Owner) -> str:
        """Return a summary of task completion progress across all pets."""
        total = sum(len(p.tasks) for p in owner.pets)
        completed = sum(sum(1 for t in p.tasks if t.is_completed) for p in owner.pets)
        lines = [
            f"Insights for {owner.first_name} {owner.last_name}:",
            f"  Pets: {len(owner.pets)}",
            f"  Total tasks: {total}  |  Completed: {completed}  |  Pending: {total - completed}",
        ]
        for pet in owner.pets:
            pet_done = sum(1 for t in pet.tasks if t.is_completed)
            lines.append(f"  {pet.name}: {pet_done}/{len(pet.tasks)} tasks complete")
            if pet.focus_areas:
                lines.append(f"    Focus areas: {', '.join(pet.focus_areas)}")
        return "\n".join(lines)


@dataclass
class Owner:
    """A user account that manages one or more pets and their care scheduler."""

    username: str
    password: str
    first_name: str
    last_name: str
    availability: str
    pets: list[Pet] = field(default_factory=list)
    scheduler: Scheduler = field(default_factory=Scheduler)

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet):
        """Remove a pet from this owner's pet list."""
        self.pets.remove(pet)

    def get_all_tasks(self, frequency: Frequency = None) -> list[Task]:
        """Return all tasks across every pet, optionally filtered by frequency."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks(frequency))
        return all_tasks

    def add_info(self, availability: str = None):
        """Update the owner's availability."""
        if availability:
            self.availability = availability

    def __str__(self) -> str:
        """Return the owner's full name and username."""
        return f"{self.first_name} {self.last_name} (@{self.username})"
