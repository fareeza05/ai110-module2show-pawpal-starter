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
        st.success(f"Owner saved: {owner}")

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
            pet = Pet(
                type=PetType(pet_type),
                name=pet_name,
                age=int(pet_age),
            )
            pet.add_info(
                health_issues=[h.strip() for h in health_issues.split(",") if h.strip()],
                focus_areas=[f.strip() for f in focus_areas.split(",") if f.strip()],
            )
            owner.add_pet(pet)  # ← Owner.add_pet() handles the data
            st.success(f"Added {pet}")

    if owner.pets:
        st.write("**Your pets:**")
        for pet in owner.pets:
            st.markdown(f"- **{pet.name}** ({pet.type.value}, age {pet.age})")

st.divider()

# ── Step 3: Add a task ────────────────────────────────────────────────────────
st.subheader("3. Add a Task")

if not owner or not owner.pets:
    st.info("Add at least one pet above before creating tasks.")
else:
    with st.form("task_form"):
        pet_names   = [p.name for p in owner.pets]
        target_pet  = st.selectbox("Assign to pet", pet_names)
        task_title  = st.text_input("Task title")
        task_desc   = st.text_area("Description")
        task_freq   = st.selectbox("Frequency", [f.value for f in Frequency])

        if st.form_submit_button("Add task"):
            pet  = next(p for p in owner.pets if p.name == target_pet)
            task = Task(
                title=task_title,
                description=task_desc,
                frequency=Frequency(task_freq),
            )
            pet.add_task(task)  # ← Pet.add_task() handles the data
            st.success(f"Task '{task_title}' added to {pet.name}")

    for pet in owner.pets:
        if pet.tasks:
            st.markdown(f"**{pet.name}'s tasks:**")
            for task in pet.tasks:
                st.markdown(f"  - {task}")

st.divider()

# ── Step 4: Generate schedule ─────────────────────────────────────────────────
st.subheader("4. Generate Schedule")

if not owner or not owner.pets:
    st.info("Add an owner and at least one pet to generate a schedule.")
else:
    if st.button("Generate schedule"):
        plan = owner.scheduler.generate_plan(owner)
        st.text(plan)

    st.markdown("#### Insights")
    st.text(owner.scheduler.view_insights(owner))
