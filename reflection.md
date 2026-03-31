# PawPal+ Project Reflection

## 1. System Design

The 3 core actions a user should be able to perform:
1. Add their personal information along with their pet's information & constraints for both them and their pet (e.g - availability, age of pet, medical information) + choose what facet of their pet care they'd like to improve, if any.
2. User should be able to prompt the application to generate a pet care plan based on their information.
3. User should be able to clearly view their plan and adjust the given plan by adding their own tasks or editing any existing ones to better fit their needs.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
My initial UML design includes the following classes:
1. Pet:
    - Contains attributes such as the pet type, pet name, age, prior health issues, and the focus area for the care of this pet.
    - The primary method associated with this class is add_info - using which all of the information regarding a particular pet can be populated using the user's input.
2. Task:
    - Contains attributes such as a task title, description
    - It must be linked to a specific pet
    - Task cadence is also an attribute - task can either be a daily or weekly task
    - Contains a status of either completed/not completed
    - The method associated with this is check_off which allows user to signify whether they have completed this task.
3. Scheduler:
    - Contains the tasks and also methods to generate the plan
    - add_task method: allows user to add an additional task to the plan
    - generate_plan method: reads information entered by the owner and generates the care plan
    - edit_plan method: allows user to make changes to the plan
    - view_tasks method: allows user to see the tasks
    - view_insights method: allows user to see the reasoning behind the plan and understanding how it contributes to their goal.
4. User:
    - Contains the user's information including account log-in information, as well as personal information such as name
    - There exists a link between them and their pets
    - add_info method: allows them to add information regarding htemselves to populate their profile.
    - also contains a scheduler attribute : so that schedule generated for them is unique to them.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

- Yes, my design did change during implementation due to some bottlenecks in the logic.
- One change made was to add 2 enums - PetType and Frequency to constrain the pet types and task recurrence to a fixed amount of options
- Added from __future__ import annotations to resolve the Owner forward reference in Scheduler
- Added due_date: date to Task so view_tasks() can support real date-based filtering
- Changed generate_plan() to accept list[Pet] instead of a single Pet to cover all of an owner's pets
- Added add_pet() to Owner as the proper entry point for adding pets
- Added return types to view_insights() and generate_plan()

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers three main constraints:
- **Time of day** — every task has a `time_of_day` and `duration_minutes`, which together define a time window. This was the most important constraint because it is what makes a schedule actionable rather than just a to-do list.
- **Frequency** — daily vs. weekly determines how recurring tasks auto-advance their due dates after completion. This was prioritized because pet care is inherently routine-driven.
- **Owner availability** — stored as a free-text field and surfaced in the generated plan header. It is currently informational rather than enforced algorithmically, because formalizing availability into time slots would require a more complex constraint-satisfaction approach beyond the scope of this project.

Time was treated as the primary constraint because conflict detection, sorting, and the daily/weekly view all depend on it. Frequency was second because recurrence is core to pet care. Priority as a ranked field was deliberately left out — the owner decides priority by choosing what time to schedule a task.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

**Tradeoff: overlap detection uses scheduled start time + duration, not real-time tracking**

The `detect_conflicts` method flags two tasks as conflicting if one starts before the previous one ends — based purely on `time_of_day` and `duration_minutes` as entered by the user. It does not track how long a task actually takes in practice, account for travel time between tasks, or update dynamically if a task runs over.

A more accurate system would record actual start/end timestamps per task and recompute conflicts in real time as tasks are completed. However, that would require persistent state across sessions, a clock integration, and significantly more complexity.

For a pet care planning app, the current approach is a reasonable tradeoff: the goal is to help an owner spot obviously overlapping tasks at planning time (e.g., a 30-minute walk and a vet medication both scheduled at 7:00 AM), not to act as a real-time task monitor. The simplicity keeps the data model clean and the conflict logic easy to understand and test.

**AI suggestion reviewed:** A Pythonic rewrite using `itertools.combinations` was considered — it would eliminate the nested loop in favor of `for a, b in combinations(tagged, 2)`. This was rejected because it removes the `break` early-exit: since tasks are sorted by start time, once task B starts after task A ends, all further pairs with A are guaranteed non-overlapping. `itertools.combinations` has no mechanism to short-circuit, so it checks every pair regardless. The current nested loop is kept because the `break` makes it faster on longer task lists, even if it is slightly more code to read.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

AI tools were used across every phase of this project:

- **Design brainstorming** — the initial UML diagram was drafted by describing the four classes and their responsibilities in plain English. The AI produced the Mermaid diagram and identified missing relationships (e.g., `Scheduler` receiving `Owner` rather than holding tasks directly).
- **Skeleton generation** — describing each class's role in one sentence was enough to generate the dataclass structure with correct field types and method signatures.
- **Logic review** — asking "are there any missing relationships or logic bottlenecks?" before implementation caught issues like the missing `due_date` field on `Task` and the single-pet limitation of the original `generate_plan()`.
- **Algorithmic implementation** — methods like `detect_conflicts` and `filter_tasks_for_owner` were built iteratively: describe the behavior, get a draft, then review and adjust.
- **Refactoring and testing** — test cases were generated by describing the exact scenarios to verify (e.g., "adjacent tasks should not be flagged as conflicts"), then reviewed to ensure each one tested the boundary condition specifically.

The most effective prompt pattern was: **describe the constraint first, then ask for the implementation**. For example, "return warning strings rather than raising exceptions" or "use an early-exit break since tasks are sorted" produced better results than asking for a general conflict detector and adjusting afterward.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

The clearest example was the `itertools.combinations` suggestion for `detect_conflicts`. The AI suggested replacing the nested loop with `for a, b in combinations(tagged, 2)` to make the code more Pythonic. The suggestion was correct in terms of producing the same output, but it silently removed the `break` optimization.

The evaluation was done by tracing through both versions mentally: the sorted nested loop can stop checking pairs for task A the moment it finds a task B that starts after A ends, because all subsequent tasks will start even later. `combinations` generates all pairs regardless of order, so it cannot short-circuit. For a small list of 10 tasks this makes no practical difference, but the early-exit behavior is the entire reason the algorithm is correct to describe as "lightweight." Keeping the nested loop preserved both the performance property and the documentation of why the `break` is there.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

12 tests were written across four areas:

1. **Core behavior** — task completion status change and task count increase. These are the most fundamental invariants: if `check_off()` doesn't flip `is_completed`, nothing downstream works correctly.
2. **Sorting** — tasks added out of order are returned in chronological order, both within a single pet and across multiple pets interleaved. This matters because the UI depends on sort order being correct without the caller needing to think about it.
3. **Recurrence** — daily and weekly next-occurrence creation, and inheritance of `time_of_day` and `duration_minutes`. These tests catch the most likely regression: if `check_off()` is ever changed to return `None` or stop copying fields, the tests will immediately fail.
4. **Conflict detection** — five boundary cases: no conflict (happy path), same-pet overlap, cross-pet overlap, three-way overlap producing three warnings, and adjacent tasks that should not conflict. The adjacent-task boundary case was the most important to test explicitly, because `>=` vs `>` in the comparison is easy to get wrong.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

★★★★☆ (4/5). The implemented behaviors are well-tested and all 12 pass. The remaining uncertainty is in untested areas:

- Tasks scheduled across midnight (e.g., 11:45 PM, 30 minutes — does the conflict check handle wrapping?)
- An owner with zero pets (does `detect_conflicts` return an empty list cleanly?)
- Completing a task that has already been completed a second time
- The Streamlit UI layer has no automated tests — form submissions and session state mutations are only verified manually

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The conflict detection algorithm is the part I'm most satisfied with. It went from a vague requirement ("detect if two tasks overlap") to a clean, well-reasoned implementation with a specific algorithmic property (early-exit via `break` on sorted input), a deliberate design decision (return strings, never raise), and a documented justification for rejecting a simpler-looking alternative. The five boundary-condition tests give high confidence that it behaves correctly at the edges. That combination — a clear design decision, a documented tradeoff, and thorough tests — is the kind of engineering I want to be able to replicate on larger systems.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The `availability` field on `Owner` is the weakest part of the system. It is a free-text string that gets printed in the plan header but is never actually used to constrain which tasks are schedulable. In a next iteration, I would replace it with a structured list of time windows (e.g., `[("07:00", "09:00"), ("18:00", "20:00")]`) and add a method to `Scheduler` that warns when a task falls outside those windows — similar to how `detect_conflicts` works, but checking against owner availability rather than other tasks.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important lesson was that **AI is a fast drafter, not a decision-maker**. On every significant design question — where tasks should live (on `Pet`, not `Scheduler`), whether `check_off()` should mutate or return a new instance, whether to use `break` or `combinations` — the AI produced a reasonable option quickly, but the right answer only became clear after thinking through the consequences of each choice. The AI accelerated the typing; the design judgment had to come from me. Being the "lead architect" means knowing which AI suggestions to accept, which to modify, and which to reject — and being able to explain why in each case, as documented in section 3b.

---

## AI Strategy: VS Code Copilot

**Which Copilot features were most effective for building your scheduler?**

The inline completion and the chat panel (`#codebase`) were the two most useful features. Inline completions were most valuable during repetitive structural work — writing the dataclass fields, docstrings, and test helper functions — where the pattern was clear and the AI could complete it correctly with minimal guidance. The chat panel with `#codebase` was most useful for cross-file questions: asking "does my filter method correctly handle the case where pet_name is None?" required understanding both the method in `pawpal_system.py` and the call site in `app.py`, which the codebase context handled well.

**Give one example of an AI suggestion you rejected or modified.**

The `itertools.combinations` suggestion for `detect_conflicts` (documented in section 3b) is the clearest example. It was more concise and idiomatic Python, but it removed the early-exit optimization that made the algorithm correct to describe as lightweight. The more Pythonic version was rejected in favor of the nested loop with `break`, which is slightly more code but preserves the performance property and makes the reasoning explicit to a future reader.

**How did using separate chat sessions for different phases help you stay organized?**

Keeping design, implementation, and testing in separate sessions prevented earlier context from interfering with later decisions. During the design phase, the conversation was focused on class responsibilities and relationships — if implementation details had been mixed in, it would have been harder to think clearly about the structure. Similarly, the testing session benefited from a clean slate: rather than defending earlier implementation choices, the focus was purely on "what could go wrong and how do I prove it doesn't?"

**What did you learn about being the "lead architect" when collaborating with AI tools?**

Being the lead architect means maintaining ownership of the design while using AI to accelerate execution. Concretely, that means: writing requirements before asking for code (not the other way around), reviewing every suggestion against the existing system before accepting it, and documenting decisions — especially rejections — so the reasoning is preserved for the next session. The biggest risk when working with AI is that it is very good at producing code that looks correct and passes immediate inspection but violates a design constraint that was established earlier. The lead architect's job is to hold that design context and catch those violations before they compound.
