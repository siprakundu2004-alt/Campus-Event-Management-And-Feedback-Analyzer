"""
views/student/feedback_view.py
------------------------------
Student Feedback & Review Submission module.
Allows registered students to submit post-event feedback on completed events,
enforcing business constraints (registration verification, completion check, 1-5 rating, no duplicates).
"""

import streamlit as st
import pandas as pd

from services.auth_service import UserSession
from services.feedback_service import FeedbackService
from utils.constants import RATING_LABELS
from utils.exceptions import (
    InvalidFeedbackError,
    FeedbackNotAllowedError,
    EventNotCompletedError,
    DuplicateFeedbackError,
    ValidationError,
)
from components.ui_helpers import render_header, render_star_rating


def render_student_feedback(user: UserSession) -> None:
    """Render the student feedback submission and review history interface."""
    fbk_service = FeedbackService()

    render_header(
        title="Share Event Feedback & Ratings",
        subtitle="Help organizers enhance future university events with your insights and evaluations",
        badge_text="Student Portal",
    )

    tab_submit, tab_history = st.tabs(["✍️ Submit Review", "📜 My Past Reviews"])

    # -------------------------------------------------------------
    # TAB 1: Submit Review
    # -------------------------------------------------------------
    with tab_submit:
        pending_events = fbk_service.get_events_pending_feedback_for_student(user.user_id)

        if not pending_events:
            st.success("🎉 You're all caught up! There are no completed events awaiting your review.")
            st.info(
                "Feedback can only be submitted for completed events that you were registered for. "
                "Check back once your upcoming events wrap up!"
            )
        else:
            st.markdown(f"#### 📝 Completed Events Awaiting Your Review ({len(pending_events)})")

            event_options = {
                f"{e['event_name']} ({e['category']} - {e['event_date']})": e["event_id"]
                for e in pending_events
            }
            selected_label = st.selectbox("Select Event to Evaluate*", list(event_options.keys()))
            selected_eid = event_options[selected_label]

            with st.form("feedback_submission_form"):
                st.markdown("##### 1. How would you rate the overall quality?")
                rating_val = st.radio(
                    "Rating Scale",
                    options=[5, 4, 3, 2, 1],
                    format_func=lambda r: f"{'★' * r} — {r} / 5 ({RATING_LABELS[r]})",
                    horizontal=True,
                )

                st.markdown("##### 2. Detailed Feedback & Comments")
                comments = st.text_area(
                    "Constructive Observations (optional)",
                    placeholder="Share your thoughts on speakers, venue management, practical labs, scheduling, or suggestions for future editions...",
                    height=120,
                )

                submit_btn = st.form_submit_button("Submit Official Feedback", type="primary", use_container_width=True)

                if submit_btn:
                    try:
                        fbk = fbk_service.submit_feedback(
                            student_id=user.user_id,
                            event_id=selected_eid,
                            rating=int(rating_val),
                            comment=comments,
                        )
                        st.balloons()
                        st.success(f"Thank you! Your feedback for '{selected_label}' has been recorded.")
                        st.rerun()
                    except (
                        InvalidFeedbackError,
                        FeedbackNotAllowedError,
                        EventNotCompletedError,
                        DuplicateFeedbackError,
                        ValidationError,
                    ) as err:
                        st.error(f"Submission Error: {err.message}")

    # -------------------------------------------------------------
    # TAB 2: Past Reviews History
    # -------------------------------------------------------------
    with tab_history:
        st.markdown("#### 📜 Your Published Feedback History")
        history = fbk_service.get_student_feedback_history(user.user_id)

        if not history:
            st.info("You haven't submitted any event reviews yet.")
        else:
            for item in history:
                st.markdown(
                    f"""
                    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="color: #1E3A8A; margin: 0 0 4px 0;">{item['event_name']}</h4>
                                <div style="font-size: 0.8rem; color: #64748B;">Category: {item['category']} | Submitted on: {item['submission_date']}</div>
                            </div>
                            <div style="text-align: right;">
                                {render_star_rating(item['rating'])}
                                <div style="font-size: 0.8rem; font-weight: 600; color: #1E293B;">{item['rating_label']}</div>
                            </div>
                        </div>
                        <div style="margin-top: 10px; font-size: 0.9rem; color: #334155; font-style: italic; background: #F8FAFC; padding: 10px; border-radius: 6px;">
                            "{item['comment'] if item['comment'] else 'No detailed comment provided.'}"
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
