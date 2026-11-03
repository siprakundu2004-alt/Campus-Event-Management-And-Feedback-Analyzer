"""
views/admin/students_view.py
----------------------------
Administrator Student Management module.
Search, register, update students, and inspect detailed participation histories.
"""

import streamlit as st
import pandas as pd

from services.student_service import StudentService
from services.registration_service import RegistrationService
from services.feedback_service import FeedbackService
from utils.constants import (
    DEPARTMENTS,
    COURSES,
    SEMESTERS,
    ACADEMIC_YEARS,
)
from utils.exceptions import (
    ValidationError,
    DuplicateStudentError,
    StudentNotFoundError,
)
from components.ui_helpers import render_header, render_kpi


def render_admin_students() -> None:
    """Render the student administration portal."""
    student_service = StudentService()
    reg_service = RegistrationService()
    fbk_service = FeedbackService()

    render_header(
        title="Student Registry & Participation",
        subtitle="Manage student profiles, enrollments, and academic department distributions",
        badge_text="Administration",
    )

    tab_dir, tab_add, tab_inspect = st.tabs([
        "👥 Student Directory",
        "➕ Enroll New Student",
        "🔍 Student Profile Inspector",
    ])

    # -------------------------------------------------------------
    # TAB 1: Student Directory
    # -------------------------------------------------------------
    with tab_dir:
        st.markdown("#### 🔍 Filter & Search Students")
        sf1, sf2, sf3, sf4 = st.columns(4)

        with sf1:
            d_filter = st.selectbox("Department", ["All"] + DEPARTMENTS)
        with sf2:
            c_filter = st.selectbox("Course", ["All"] + COURSES)
        with sf3:
            s_filter = st.selectbox("Semester", ["All"] + [str(s) for s in SEMESTERS])
        with sf4:
            s_query = st.text_input("Search Name/Email/ID")

        students = student_service.search_students(
            query=s_query,
            department=d_filter if d_filter != "All" else None,
            course=c_filter if c_filter != "All" else None,
            semester=int(s_filter) if s_filter != "All" else None,
        )

        st.caption(f"Showing {len(students)} students.")

        if students:
            data = []
            for s in students:
                stats = student_service.get_student_stats(s.student_id)
                data.append({
                    "Student ID": s.student_id,
                    "Name": s.name,
                    "Email": s.email,
                    "Phone": s.phone,
                    "Department": s.department,
                    "Course": s.course,
                    "Semester": s.semester,
                    "Year": s.academic_year,
                    "Registrations": stats["total_registrations"],
                    "Reviews": stats["feedbacks_submitted"],
                })
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        else:
            st.info("No students found.")

    # -------------------------------------------------------------
    # TAB 2: Enroll New Student
    # -------------------------------------------------------------
    with tab_add:
        st.markdown("#### ➕ Register New Student Profile")

        with st.form("enroll_student_form"):
            c1, c2 = st.columns(2)
            with c1:
                st_id = st.text_input("Student ID (optional, auto-generated if blank)", placeholder="e.g. STU041").strip().upper()
                st_name = st.text_input("Full Name*", placeholder="e.g. Amit Kumar")
                st_email = st.text_input("University Email*", placeholder="e.g. amit.k@nit.edu")
                st_phone = st.text_input("Mobile Phone (10-digit)*", placeholder="9876543210")

            with c2:
                st_dept = st.selectbox("Academic Department*", DEPARTMENTS)
                st_course = st.selectbox("Degree Course*", COURSES)
                st_sem = st.selectbox("Current Semester*", SEMESTERS)
                st_year = st.selectbox("Academic Year*", ACADEMIC_YEARS)

            st_pwd = st.text_input("Account Password*", type="password", value="Student@123", placeholder="Min 6 characters")

            submit_student = st.form_submit_button("Enroll Student", type="primary", use_container_width=True)

            if submit_student:
                s_data = {
                    "student_id": st_id,
                    "name": st_name,
                    "email": st_email,
                    "phone": st_phone,
                    "department": st_dept,
                    "course": st_course,
                    "semester": st_sem,
                    "academic_year": st_year,
                }
                try:
                    new_stu = student_service.add_student(s_data, plain_password=st_pwd)
                    st.success(f"Student successfully registered! ID: **{new_stu.student_id}**")
                    st.rerun()
                except ValidationError as e:
                    st.error(f"Validation Error:\n{e.message}\n{e.details}")
                except DuplicateStudentError as e:
                    st.error(f"Duplicate Error: {e.message}")

    # -------------------------------------------------------------
    # TAB 3: Student Profile Inspector
    # -------------------------------------------------------------
    with tab_inspect:
        st.markdown("#### 🔍 Individual Student Engagement Dossier")
        all_students = student_service.list_all_students()

        if all_students:
            s_map = {f"{s.name} ({s.student_id}) - {s.department}": s.student_id for s in all_students}
            picked_s = st.selectbox("Select Student to Inspect", list(s_map.keys()))

            if picked_s:
                curr_sid = s_map[picked_s]
                curr_s = student_service.get_student(curr_sid)
                stats = student_service.get_student_stats(curr_sid)

                # Info cards
                i1, i2, i3, i4 = st.columns(4)
                with i1:
                    render_kpi("Student ID", curr_s.student_id, curr_s.academic_year)
                with i2:
                    render_kpi("Department", curr_s.department, curr_s.course)
                with i3:
                    render_kpi("Total Registrations", str(stats["total_registrations"]), "Events Enrolled")
                with i4:
                    render_kpi("Reviews Submitted", str(stats["feedbacks_submitted"]), "Completed Events")

                # Registration history table
                st.markdown("##### 🎟️ Registration History")
                history = reg_service.get_student_registrations(curr_sid)
                if history:
                    st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
                else:
                    st.caption("No event registrations found for this student.")

                # Feedback history table
                st.markdown("##### 💬 Feedback & Reviews Submitted")
                feedbacks = fbk_service.get_student_feedback_history(curr_sid)
                if feedbacks:
                    st.dataframe(pd.DataFrame(feedbacks), use_container_width=True, hide_index=True)
                else:
                    st.caption("No feedback submitted by this student.")
        else:
            st.info("No students registered.")
