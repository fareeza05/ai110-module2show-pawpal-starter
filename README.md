# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The scheduling system goes beyond a basic task list with four algorithmic improvements:

**Sort by time**
Tasks are always returned in chronological order using a `lambda` key on the `HH:MM` string. `Scheduler.sort_by_time()` and `Pet.get_tasks()` both apply this automatically, so the daily view is always correctly ordered regardless of the order tasks were added.

**Filter by pet and status**
`Scheduler.filter_tasks_for_owner()` accepts optional `pet_name` and `completed` filters that can be used independently or combined. This lets the UI show views like "Biscuit's pending tasks" or "all completed tasks today" without duplicating logic.

**Recurring task auto-creation**
When a task is marked complete via `Pet.complete_task()`, the original task is marked `✓` and a new `Task` instance is automatically appended with the same title, time, and duration — but with `due_date` advanced by 1 day (daily) or 7 days (weekly). The owner never has to manually recreate recurring tasks.

**Conflict detection**
`Scheduler.detect_conflicts()` scans all tasks across all pets and returns human-readable warning strings for any time-window overlaps — for example, a 30-minute walk and a medication both scheduled at 7:00 AM. It distinguishes same-pet conflicts from cross-pet conflicts, uses an early-exit `break` for efficiency, and never raises an exception.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
