from datetime import time
import streamlit as st
from pawpal_system import Owner, Pet, PetType, Task, Frequency

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Session state vault ───────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None

owner: Owner | None = st.session_state.owner

# ── Step 1: Owner setup ───────────────────────────────────────────────────────
st.subheader("1. Owner Profile")

with st.form("owner_form"):
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First name")
        username   = st.text_input("Username")
    with col2:
        last_name    = st.text_input("Last name")
        availability = st.text_input("Availability (e.g. mornings and evenings)")

    if st.form_submit_button("Save owner"):
        st.session_state.owner = Owner(
            username=username,
            password="",
            first_name=first_name,
            last_name=last_name,
            availability=availability,
        )
        owner = st.session_state.owner
        st.success(f"Profile saved for {owner.first_name} {owner.last_name}")

st.divider()

# ── Step 2: Add a pet ─────────────────────────────────────────────────────────
st.subheader("2. Add a Pet")

if owner is None:
    st.info("Save an owner profile above before adding pets.")
else:
    with st.form("pet_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            pet_name = st.text_input("Pet name")
        with col2:
            pet_age  = st.number_input("Age", min_value=0, max_value=30, value=1)
        with col3:
            pet_type = st.selectbox("Species", [p.value for p in PetType])

        health_issues = st.text_input("Prior health issues (comma-separated)")
        focus_areas   = st.text_input("Focus areas (comma-separated)")

        if st.form_submit_button("Add pet"):
            pet = Pet(type=PetType(pet_type), name=pet_name, age=int(pet_age))
            pet.add_info(
                health_issues=[h.strip() for h in health_issues.split(",") if h.strip()],
                focus_areas=[f.strip() for f in focus_areas.split(",") if f.strip()],
            )
            owner.add_pet(pet)
            st.success(f"Added **{pet.name}** ({pet.type.value}, age {pet.age})")

    if owner.pets:
        st.write("**Your pets:**")
        pet_rows = [
            {
                "Name": p.name,
                "Species": p.type.value,
                "Age": p.age,
                "Focus areas": ", ".join(p.focus_areas) or "—",
                "Health notes": ", ".join(p.prior_health_issues) or "—",
            }
            for p in owner.pets
        ]
        st.table(pet_rows)

st.divider()

# ── Step 3: Add a task ────────────────────────────────────────────────────────
st.subheader("3. Add a Task")

if not owner or not owner.pets:
    st.info("Add at least one pet above before creating tasks.")
else:
    with st.form("task_form"):
        col1, col2 = st.columns(2)
        with col1:
            target_pet = st.selectbox("Assign to pet", [p.name for p in owner.pets])
            task_title = st.text_input("Task title")
            task_freq  = st.selectbox("Frequency", [f.value for f in Frequency])
        with col2:
            task_time     = st.time_input("Time of day", value=time(8, 0))
            task_duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)

        task_desc = st.text_area("Description")

        if st.form_submit_button("Add task"):
            pet  = next(p for p in owner.pets if p.name == target_pet)
            task = Task(
                title=task_title,
                description=task_desc,
                frequency=Frequency(task_freq),
                time_of_day=task_time,
                duration_minutes=int(task_duration),
            )
            pet.add_task(task)
            st.success(f"Task **'{task_title}'** added to {pet.name} at {task_time.strftime('%I:%M %p')}")

    # Display each pet's tasks sorted by time via Scheduler.sort_by_time()
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("**All tasks — sorted by time:**")
        sorted_tasks = owner.scheduler.sort_by_time(all_tasks)
        task_rows = [
            {
                "Time": t.time_of_day.strftime("%I:%M %p"),
                "Pet": next(p.name for p in owner.pets if t in p.tasks),
                "Task": t.title,
                "Frequency": t.frequency.value,
                "Duration": f"{t.duration_minutes} min",
                "Done": "✓" if t.is_completed else "○",
            }
            for t in sorted_tasks
        ]
        st.table(task_rows)

st.divider()

# ── Step 4: Schedule & Conflicts ──────────────────────────────────────────────
st.subheader("4. Generate Schedule")

if not owner or not owner.pets:
    st.info("Add an owner and at least one pet to generate a schedule.")
else:
    # ── Conflict detection (always visible) ───────────────────────────────────
    conflicts = owner.scheduler.detect_conflicts(owner)
    if conflicts:
        st.error(f"**{len(conflicts)} scheduling conflict(s) detected — resolve before generating:**")
        for w in conflicts:
            st.warning(w)
    else:
        st.success("No scheduling conflicts detected.")

    st.write("")

    # ── Filtered views ────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        filter_pet = st.selectbox(
            "Filter by pet",
            ["All pets"] + [p.name for p in owner.pets],
            key="filter_pet",
        )
    with col2:
        filter_status = st.selectbox(
            "Filter by status",
            ["All", "Pending", "Completed"],
            key="filter_status",
        )

    pet_name_filter  = None if filter_pet == "All pets" else filter_pet
    completed_filter = None if filter_status == "All" else (filter_status == "Completed")

    filtered = owner.scheduler.filter_tasks_for_owner(
        owner, pet_name=pet_name_filter, completed=completed_filter
    )

    if filtered:
        filter_rows = [
            {
                "Time": t.time_of_day.strftime("%I:%M %p"),
                "Pet": next(p.name for p in owner.pets if t in p.tasks),
                "Task": t.title,
                "Frequency": t.frequency.value,
                "Duration": f"{t.duration_minutes} min",
                "Status": "✓ Done" if t.is_completed else "○ Pending",
            }
            for t in filtered
        ]
        st.table(filter_rows)
    else:
        st.info("No tasks match the selected filters.")

    st.divider()

    # ── Generate plan ──────────────────��──────────────────────────────────────
    if st.button("Generate full plan"):
        plan = owner.scheduler.generate_plan(owner)
        st.text(plan)

    # ── Insights ──────────────────────────────────────────────────────────────
    with st.expander("View insights", expanded=False):
        total     = sum(len(p.tasks) for p in owner.pets)
        completed = sum(1 for p in owner.pets for t in p.tasks if t.is_completed)
        pending   = total - completed

        m1, m2, m3 = st.columns(3)
        m1.metric("Total tasks",  total)
        m2.metric("Completed",    completed)
        m3.metric("Pending",      pending)

        for pet in owner.pets:
            pet_done  = sum(1 for t in pet.tasks if t.is_completed)
            pet_total = len(pet.tasks)
            pct       = int(pet_done / pet_total * 100) if pet_total else 0
            st.write(f"**{pet.name}** — {pet_done}/{pet_total} tasks complete")
            st.progress(pct)
            if pet.focus_areas:
                st.caption(f"Focus: {', '.join(pet.focus_areas)}")
