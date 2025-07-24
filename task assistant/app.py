import streamlit as st
from task_manager import TaskManager

st.set_page_config(page_title="📝 Local Task Manager")

if "manager" not in st.session_state:
    st.session_state.manager = TaskManager()

st.title("📋 Task Manager (No LLM)")

# Add a task
st.subheader("➕ Add Task")
title = st.text_input("Task Title")
category = st.selectbox("Category", ["General", "Work", "Personal", "Study"])
priority = st.slider("Priority (1 = highest)", 1, 5, 3)

if st.button("Add Task"):
    st.session_state.manager.add_task(title, category, priority)
    st.success("Task added!")

# Filter and view tasks
st.subheader("📂 Your Tasks")
selected_category = st.selectbox("Filter by category", ["All", "General", "Work", "Personal", "Study"])
tasks = st.session_state.manager.get_tasks_by_category(selected_category)

for i, task in enumerate(tasks):
    col1, col2 = st.columns([6, 1])
    col1.write(f"{i + 1}. {task['title']} ({task['category']}, Priority: {task['priority']}) - {task['status']}")
    if col2.button("✅", key=f"done{i}"):
        st.session_state.manager.complete_task(i)
        st.rerun()

# Clear all
if st.button("Clear All Tasks"):
    st.session_state.manager.clear_tasks()
    st.success("All tasks cleared.")
