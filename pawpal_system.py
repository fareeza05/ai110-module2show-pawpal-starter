from dataclasses import dataclass, field


@dataclass
class Pet:
    type: str  # "dog", "cat", or "other"
    name: str
    age: int
    prior_health_issues: list[str] = field(default_factory=list)
    focus_areas: list[str] = field(default_factory=list)

    def add_info(self, health_issues: list[str] = None, focus_areas: list[str] = None):
        if health_issues:
            self.prior_health_issues.extend(health_issues)
        if focus_areas:
            self.focus_areas.extend(focus_areas)


@dataclass
class Task:
    title: str
    description: str
    pet: Pet
    frequency: str  # "daily" or "weekly"
    is_completed: bool = False

    def check_off(self):
        self.is_completed = True


@dataclass
class Scheduler:
    tasks: list[Task] = field(default_factory=list)
    plan: str = ""

    def add_task(self, task: Task):
        self.tasks.append(task)

    def generate_plan(self, owner: "Owner", pet: Pet) -> str:
        # TODO: read owner.availability and pet.focus_areas / prior_health_issues to build a plan
        return self.plan

    def edit_plan(self, updated_plan: str):
        self.plan = updated_plan

    def view_tasks(self, frequency: str) -> list[Task]:
        return [t for t in self.tasks if t.frequency == frequency]

    def view_insights(self):
        pass


@dataclass
class Owner:
    username: str
    password: str
    first_name: str
    last_name: str
    availability: str
    pets: list[Pet] = field(default_factory=list)
    scheduler: Scheduler = field(default_factory=Scheduler)

    def add_info(self, availability: str = None):
        if availability:
            self.availability = availability
