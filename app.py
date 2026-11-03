"""
app.py
------
Main Application Entry Point for Campus Event Management & Feedback Analyzer.
Coordinates session authentication, role-based navigation, and view dispatching.
Run with: `streamlit run app.py`
"""

import streamlit as st

import config
from utils.seed_data import seed_all
from services.auth_service import AuthService
from components.ui_helpers import inject_custom_css
from components.auth_ui import (
    get_current_user,
    render_login_page,
    render_sidebar_user_profile,
)
from views.admin.dashboard_view import render_admin_dashboard
from views.admin.events_view import render_admin_events
from views.admin.students_view import render_admin_students
from views.admin.registrations_view import render_admin_registrations
from views.admin.analytics_view import render_admin_analytics
from views.admin.reports_view import render_admin_reports
from views.student.dashboard_view import render_student_dashboard
from views.student.browse_view import render_student_browse
from views.student.my_events_view import render_student_my_events
from views.student.feedback_view import render_student_feedback


def main() -> None:
    """Initialize application environment and handle navigation."""
    st.set_page_config(
        page_title=config.APP_NAME,
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject corporate styling
    inject_custom_css()

    # Ensure baseline data exists
    seed_all(force=False)

    auth_service = AuthService()
    current_user = get_current_user()

    # Authentication Gate
    if current_user is None:
        render_login_page(auth_service)
        return

    # User is logged in: render profile & role-based sidebar
    render_sidebar_user_profile(current_user)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 📌 Navigation")

    if current_user.is_admin:
        menu_choice = st.sidebar.radio(
            "Admin Menu",
            [
                "🏠 Command Center",
                "📅 Event Management",
                "👥 Student Directory",
                "🎟️ Registrations & Attendance",
                "📊 Analytics & Visualizations",
                "📑 Reports & Exports",
            ],
            index=0,
            label_visibility="collapsed",
        )

        if "Command Center" in menu_choice:
            render_admin_dashboard()
        elif "Event Management" in menu_choice:
            render_admin_events()
        elif "Student Directory" in menu_choice:
            render_admin_students()
        elif "Registrations" in menu_choice:
            render_admin_registrations()
        elif "Analytics" in menu_choice:
            render_admin_analytics()
        elif "Reports" in menu_choice:
            render_admin_reports()

    else:
        # Student Portal Navigation
        menu_choice = st.sidebar.radio(
            "Student Menu",
            [
                "🏠 My Dashboard",
                "🔍 Browse Events",
                "🎟️ My Event Passes",
                "⭐ Submit Feedback",
            ],
            index=0,
            label_visibility="collapsed",
        )

        if "Dashboard" in menu_choice:
            render_student_dashboard(current_user)
        elif "Browse" in menu_choice:
            render_student_browse(current_user)
        elif "Passes" in menu_choice:
            render_student_my_events(current_user)
        elif "Feedback" in menu_choice:
            render_student_feedback(current_user)

    # Sidebar branding footer
    st.sidebar.markdown("---")
    footer_html = (
        '<div style="font-size: 0.72rem; color: #94A3B8; text-align: center; line-height: 1.4;">'
        f'<b>{config.APP_NAME}</b> v{config.APP_VERSION}<br>'
        f'{config.UNIVERSITY_NAME}<br>'
        '<i>MCA PBL Capstone Architecture</i>'
        '</div>'
    )
    st.sidebar.markdown(footer_html, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
