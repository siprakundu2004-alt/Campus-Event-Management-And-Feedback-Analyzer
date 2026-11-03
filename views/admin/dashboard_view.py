"""
views/admin/dashboard_view.py
-----------------------------
Administrator Executive Dashboard view for Campus Event Management & Feedback Analyzer.
Renders dynamic KPI cards, top-performing event highlights, and recent activity feeds.
All numbers dynamically computed from persistent storage.
"""

import streamlit as st
import pandas as pd

from services.event_service import EventService
from services.student_service import StudentService
from services.registration_service import RegistrationService
from services.feedback_service import FeedbackService
from analytics.event_analytics import EventAnalytics
from analytics.participation_analytics import ParticipationAnalytics
from analytics.feedback_analytics import FeedbackAnalytics
from components.ui_helpers import render_header, render_kpi, get_status_badge_html, render_star_rating
import config


def render_admin_dashboard() -> None:
    """Render the main administrative command center dashboard."""
    event_service = EventService()
    student_service = StudentService()
    reg_service = RegistrationService()
    fbk_service = FeedbackService()
    evt_analytics = EventAnalytics()
    part_analytics = ParticipationAnalytics()
    fbk_analytics = FeedbackAnalytics()

    render_header(
        title="Campus Event Command Center",
        subtitle=f"Real-time operational overview for {config.UNIVERSITY_NAME}",
        badge_text="Executive Dashboard",
    )

    # -------------------------------------------------------------
    # 1. High-Level KPI Cards (Dynamically calculated)
    # -------------------------------------------------------------
    evt_kpis = evt_analytics.get_summary_metrics()
    part_kpis = part_analytics.get_summary_metrics()
    fbk_kpis = fbk_analytics.get_summary_metrics()
    total_students = len(student_service.list_all_students())

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_kpi(
            title="Total Events",
            value=str(evt_kpis["total_events"]),
            subtitle=f"{evt_kpis['open_events']} Open | {evt_kpis['completed_events']} Completed",
        )

    with col2:
        render_kpi(
            title="Registered Students",
            value=str(total_students),
            subtitle=f"{part_kpis['overall_participation_rate']}% Participation Rate",
        )

    with col3:
        render_kpi(
            title="Total Registrations",
            value=f"{part_kpis['confirmed_registrations']:,}",
            subtitle=f"{part_kpis['overall_capacity_utilization']}% Capacity Utilized",
        )

    with col4:
        avg_r = fbk_kpis["overall_avg_rating"]
        render_kpi(
            title="Average Satisfaction",
            value=f"{avg_r} / 5.0",
            subtitle=f"{fbk_kpis['positive_percentage']}% Positive Reviews",
        )

    st.markdown("---")

    # -------------------------------------------------------------
    # 2. Performance Spotlight Banner
    # -------------------------------------------------------------
    perf_df = fbk_analytics.get_event_performance_scores()
    if not perf_df.empty:
        top_event = perf_df.iloc[0]
        st.markdown(
            f"""
            <div style="background-color: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 10px; padding: 16px 20px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="background-color: #10B981; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 700;">
                            ★ TOP PERFORMING EVENT
                        </span>
                        <h3 style="color: #065F46; margin: 6px 0 2px 0;">{top_event['Event Name']}</h3>
                        <div style="color: #047857; font-size: 0.85rem;">
                            Category: <b>{top_event['Category']}</b> &nbsp;|&nbsp; 
                            Registrations: <b>{top_event['Registered']} / {top_event['Capacity']}</b> &nbsp;|&nbsp; 
                            Student Rating: <b>{top_event['Avg Rating']} ★</b> ({top_event['Reviews']} reviews)
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.8rem; color: #047857; font-weight: 600;">PERFORMANCE SCORE</div>
                        <div style="font-size: 2.2rem; font-weight: 800; color: #065F46; line-height: 1;">
                            {top_event['Performance Score']}
                        </div>
                        <div style="font-size: 0.75rem; color: #059669;">out of 100</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -------------------------------------------------------------
    # 3. Two-Column Activity Feeds
    # -------------------------------------------------------------
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown("#### 📅 Upcoming Campus Events")
        upcoming = event_service.list_upcoming_events()
        if upcoming:
            display_upcoming = []
            for e in upcoming[:5]:
                reg_count = event_service.get_registered_count(e.event_id)
                seats_left = max(0, e.max_capacity - reg_count)
                display_upcoming.append({
                    "Event Name": e.event_name,
                    "Category": e.category,
                    "Date": e.event_date,
                    "Seats Left": f"{seats_left} / {e.max_capacity}",
                    "Venue": e.venue,
                })
            st.dataframe(pd.DataFrame(display_upcoming), use_container_width=True, hide_index=True)
        else:
            st.info("No upcoming events currently scheduled.")

    with right_col:
        st.markdown("#### 📝 Recent Student Registrations")
        all_regs = reg_service.list_all_registrations()
        if all_regs:
            display_regs = []
            for r in all_regs[-5:]:
                display_regs.append({
                    "Student": r["student_name"],
                    "Department": r["department"],
                    "Event": r["event_name"],
                    "Status": r["status"],
                })
            st.dataframe(pd.DataFrame(display_regs), use_container_width=True, hide_index=True)
        else:
            st.info("No registrations recorded yet.")

    # -------------------------------------------------------------
    # 4. Recent Student Feedback
    # -------------------------------------------------------------
    st.markdown("#### 💬 Latest Student Reviews")
    all_fbk = fbk_service.list_all_feedback()
    if all_fbk:
        cols = st.columns(min(3, len(all_fbk[-3:])))
        for idx, f in enumerate(all_fbk[-3:]):
            with cols[idx]:
                st.markdown(
                    f"""
                    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; height: 100%;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-weight: 700; color: #1E293B; font-size: 0.9rem;">{f['student_name']}</span>
                            <span>{render_star_rating(f['rating'])}</span>
                        </div>
                        <div style="font-size: 0.78rem; color: #64748B; margin-bottom: 8px;">
                            <b>{f['event_name']}</b> ({f['department']})
                        </div>
                        <div style="font-size: 0.85rem; color: #334155; font-style: italic;">
                            "{f['comment'][:110] + ('...' if len(f['comment']) > 110 else '')}"
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No student feedback submitted yet.")
