import streamlit as st

# ---------- Class ----------
class Student:
    def __init__(self, name, roll, subjects):
        self.name = name
        self.roll = roll
        self.subjects = subjects  # Dictionary {subject: marks}

    def get_total(self):
        return sum(self.subjects.values())

    def get_average(self):
        return self.get_total() / len(self.subjects)

    def get_grade(self):
        avg = self.get_average()
        if avg >= 90:
            return "A+"
        elif avg >= 75:
            return "A"
        elif avg >= 60:
            return "B"
        elif avg >= 50:
            return "C"
        else:
            return "Fail"

# ---------- List to Store Students ----------
student_list = []

# ---------- Streamlit UI ----------
st.title("📘 Student Report Card Generator")

with st.form("student_form"):
    name = st.text_input("Student Name")
    roll = st.text_input("Roll Number")
    subjects_str = st.text_area("Subjects and Marks (e.g., Math:90, Science:85)")

    submitted = st.form_submit_button("Add Student")
    if submitted:
        try:
            # Convert input string to dictionary
            subjects = dict()
            for item in subjects_str.split(","):
                subject, mark = item.strip().split(":")
                subjects[subject.strip()] = int(mark.strip())

            student = Student(name, roll, subjects)
            student_list.append(student)
            st.success("Student added!")
        except:
            st.error("Invalid format! Use Subject:Marks format.")

# ---------- Display Students ----------
if student_list:
    st.header("📋 All Student Reports")
    for s in student_list:
        st.subheader(f"{s.name} (Roll No: {s.roll})")
        for sub, mark in s.subjects.items():
            st.write(f"{sub}: {mark}")
        st.write(f"Total Marks: {s.get_total()}")
        st.write(f"Average: {s.get_average():.2f}")
        st.write(f"Grade: **{s.get_grade()}**")
        st.markdown("---")
