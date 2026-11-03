"""
views/student/dashboard_view.py
-------------------------------
Student Personal Dashboard view for Campus Event Management & Feedback Analyzer.
Displays personalized KPIs, upcoming registered events, and pending review alerts.
"""

import streamlit as st
import pandas as pd

from services.auth_service import UserSession
from services.registration_service import RegistrationService
from services.feedback_service import FeedbackService
from services.event_service import EventService
from components.ui_helpers import render_header, render_kpi, render_star_rating
from utils.constants import RegistrationStatus, EventStatus


def render_student_dashboard(user: UserSession) -> None:
    """Render the student's personal home portal."""
    reg_service = RegistrationService()
    fbk_service = FeedbackService()
    event_service = EventService()

    render_header(
        title=f"Welcome back, {user.display_name}!",
        subtitle=f"{user.course} | {user.department} | Student ID: {user.user_id}",
        badge_text="Student Portal",
    )

    # Student specific metrics
    regs = reg_service.get_student_registrations(user.user_id)
    active_regs = [r for r in regs if r["status"] == RegistrationStatus.CONFIRMED.value]
    attended_regs = [r for r in regs if r["status"] == RegistrationStatus.ATTENDED.value]
    feedbacks = fbk_service.get_student_feedback_history(user.user_id)
    pending_fbk = fbk_service.get_events_pending_feedback_for_student(user.user_id)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi("Upcoming Bookings", str(len(active_regs)), "Active Events")
    with col2:
        render_kpi("Attended Events", str(len(attended_regs)), "Verified Check-ins")
    with col3:
        render_kpi("Reviews Submitted", str(len(feedbacks)), "All-time Reviews")
    with col4:
        render_kpi("Pending Reviews", str(len(pending_fbk)), "Completed Events Awaiting Rating")

    st.markdown("---")

    # Alert for pending feedback
    if pending_fbk:
        st.warning(
            f"🔔 You have **{len(pending_fbk)} completed event(s)** awaiting your feedback! "
            f"Navigate to **'Submit Feedback'** in the sidebar to share your thoughts."
        )

    # Two column layout: upcoming enrolled events + student review highlights
    left_c, right_c = st.columns([3, 2])

    with left_c:
        st.markdown("#### 🎟️ My Upcoming Registered Events")
        if active_regs:
            table_data = []
            for r in active_regs:
                table_data.append({
                    "Event Name": r["event_name"],
                    "Category": r["category"],
                    "Date": r["event_date"],
                    "Venue": r["venue"],
                    "Booked On": r["registration_date"],
                })
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
        else:
            st.info("You haven't registered for any upcoming events yet. Go to **'Browse Events'** to enroll!")

    with right_c:
        st.markdown("#### ⭐ My Recent Reviews")
        if feedbacks:
            for f in feedbacks[-3:]:
                st.markdown(
                    f"""
                    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <b>{f['event_name']}</b>
                            <span>{render_star_rating(f['rating'])}</span>
                        </div>
                        <div style="font-size: 0.78rem; color: #64748B;">{f['rating_label']} • {f['submission_date']}</div>
                        <div style="font-size: 0.85rem; color: #334155; margin-top: 4px; font-style: italic;">
                            "{f['comment']}"
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("You have not submitted any reviews yet.")
