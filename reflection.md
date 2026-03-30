# PawPal+ Project Reflection

## 1. System Design

The 3 core actions a user should be able to perform:
1. Add their personal information along with their pet’s information & constraints for both them and their pet (e.g - availability, age of pet, medical information) + choose what facet of their pet care they’d like to improve, if any.
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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
