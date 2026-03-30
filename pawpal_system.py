from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
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
    """A single care activity assigned to a pet with a frequency and due date."""

    title: str
    description: str
    frequency: Frequency
    due_date: date = field(default_factory=date.today)
    is_completed: bool = False

    def check_off(self):
        """Mark this task as completed."""
        self.is_completed = True

    def is_due_today(self) -> bool:
        """Return True if this task is due today."""
        return self.due_date == date.today()

    def __str__(self) -> str:
        """Return a formatted one-line summary of the task."""
        status = "✓" if self.is_completed else "○"
        return f"[{status}] {self.title} ({self.frequency.value}) — due {self.due_date}"


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

    def remove_task(self, task: Task):
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def get_tasks(self, frequency: Frequency = None) -> list[Task]:
        """Return all tasks, optionally filtered by frequency."""
        if frequency:
            return [t for t in self.tasks if t.frequency == frequency]
        return list(self.tasks)

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
        """Build and store a formatted care plan from the owner's pets and availability."""
        lines = [f"Care plan for {owner.first_name}'s pets | Availability: {owner.availability}\n"]
        for pet in owner.pets:
            lines.append(f"  {pet}")
            if pet.focus_areas:
                lines.append(f"    Focus: {', '.join(pet.focus_areas)}")
            if pet.prior_health_issues:
                lines.append(f"    Health notes: {', '.join(pet.prior_health_issues)}")
            for task in pet.tasks:
                lines.append(f"    {task}")
        self.plan = "\n".join(lines)
        return self.plan

    def edit_plan(self, updated_plan: str):
        """Replace the current plan with a manually updated version."""
        self.plan = updated_plan

    def view_tasks(self, owner: Owner, frequency: Frequency) -> list[Task]:
        """Return all tasks across the owner's pets filtered by frequency."""
        return owner.get_all_tasks(frequency)

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
