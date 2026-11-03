"""
components/auth_ui.py
---------------------
Streamlit authentication interface for Campus Event Management & Feedback Analyzer.
Renders the login experience with role selection, demo quick-fill credentials,
session state management, and logout buttons.
"""

from typing import Optional
import streamlit as st

from services.auth_service import AuthService, UserSession
from utils.exceptions import AuthenticationError
import config


def get_current_user() -> Optional[UserSession]:
    """Retrieve current logged-in user from Streamlit session state."""
    return st.session_state.get("current_user", None)


def set_current_user(user: Optional[UserSession]) -> None:
    """Store or clear current logged-in user in session state."""
    st.session_state["current_user"] = user


def logout_user() -> None:
    """Clear session and rerun application."""
    st.session_state["current_user"] = None
    st.rerun()


def render_login_page(auth_service: AuthService) -> None:
    """
    Renders an elegant authentication portal with dedicated tabs for
    Administrator and Student accounts.
    """
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 40px; margin-bottom: 25px;">
                <div style="font-size: 3rem; margin-bottom: 10px;">🎓</div>
                <h2 style="color: #1E3A8A; margin-bottom: 5px; font-weight: 700;">{config.APP_NAME}</h2>
                <p style="color: #64748B; font-size: 0.95rem;">{config.APP_TAGLINE}</p>
                <span style="background: #EEF2FF; color: #4338CA; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                    {config.UNIVERSITY_NAME}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_admin, tab_student = st.tabs(["🔐 Administrator Login", "🎒 Student Login"])

        # -------------------------------------------------------------
        # Admin Tab
        # -------------------------------------------------------------
        with tab_admin:
            st.markdown("#### Admin Portal")
            st.caption("Access campus analytics, event scheduling, and student records.")

            with st.form("admin_login_form"):
                admin_user = st.text_input("Username", value="admin", placeholder="e.g. admin")
                admin_pwd = st.text_input("Password", type="password", value="Admin@123", placeholder="Enter admin password")
                submit_admin = st.form_submit_button("Sign In as Administrator", use_container_width=True, type="primary")

                if submit_admin:
                    try:
                        user = auth_service.authenticate_admin(admin_user, admin_pwd)
                        set_current_user(user)
                        st.success(f"Welcome back, {user.display_name}!")
                        st.rerun()
                    except AuthenticationError as e:
                        st.error(f"Authentication Failed: {e.message}")
            # Form ended without demo credentials block

        # -------------------------------------------------------------
        # Student Tab
        # -------------------------------------------------------------
        with tab_student:
            st.markdown("#### Student Portal")
            st.caption("Browse university events, track registrations, and submit ratings.")

            with st.form("student_login_form"):
                student_id = st.text_input("Student ID", value="STU001", placeholder="e.g. STU001").strip().upper()
                student_pwd = st.text_input("Password", type="password", value="stu001@123", placeholder="Enter student password")
                submit_student = st.form_submit_button("Sign In as Student", use_container_width=True, type="primary")

                if submit_student:
                    try:
                        user = auth_service.authenticate_student(student_id, student_pwd)
                        set_current_user(user)
                        st.success(f"Welcome, {user.display_name}!")
                        st.rerun()
                    except AuthenticationError as e:
                        st.error(f"Authentication Failed: {e.message}")

            st.info("💡 **Demo Student Credentials:** ID `STU001` (to `STU040`) / Password `stu001@123`")


def render_sidebar_user_profile(user: UserSession) -> None:
    """Render the active user's status box and logout control in the sidebar."""
    role_badge = "👑 Administrator" if user.is_admin else "🎓 Student"
    dept_badge = (
        f'<span style="background-color: #E2E8F0; color: #334155; padding: 3px 8px; border-radius: 12px; font-size: 0.72rem; font-weight: 500; margin-left: 4px;">{user.department}</span>'
        if user.department
        else ""
    )
    profile_html = (
        '<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px; margin-bottom: 15px;">'
        '<div style="font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase;">Logged In As</div>'
        f'<div style="font-size: 1rem; font-weight: 700; color: #0F172A; margin: 2px 0;">{user.display_name}</div>'
        f'<div style="font-size: 0.82rem; color: #475569;">{user.email}</div>'
        '<div style="margin-top: 6px;">'
        f'<span style="background-color: #DBEAFE; color: #1E40AF; padding: 3px 8px; border-radius: 12px; font-size: 0.72rem; font-weight: 600;">{role_badge}</span>'
        f'{dept_badge}'
        '</div>'
        '</div>'
    )
    st.sidebar.markdown(profile_html, unsafe_allow_html=True)
    if st.sidebar.button("Sign Out", use_container_width=True):
        logout_user()

