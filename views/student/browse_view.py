"""
views/student/browse_view.py
---------------------------
Student Event Browsing & Instant Registration module.
Displays interactive event cards with real-time seat availability, deadline countdowns,
and one-click smart registration enforcement.
"""

from datetime import date
import streamlit as st

from services.auth_service import UserSession
from services.event_service import EventService
from services.registration_service import RegistrationService
from utils.constants import EVENT_CATEGORIES, EventStatus
from utils.exceptions import (
    EventFullError,
    DuplicateRegistrationError,
    RegistrationClosedError,
    EventCancelledError,
    ValidationError,
)
from utils.helpers import parse_date, days_until
from components.ui_helpers import render_header, get_status_badge_html


def render_student_browse(user: UserSession) -> None:
    """Render the student event discovery and registration portal."""
    event_service = EventService()
    reg_service = RegistrationService()

    render_header(
        title="Discover Campus Events",
        subtitle="Explore hackathons, workshops, guest lectures, sports, and cultural festivals",
        badge_text="Student Portal",
    )

    # Search & filters
    c1, c2 = st.columns([1, 2])
    with c1:
        cat_filter = st.selectbox("Filter by Category", ["All"] + EVENT_CATEGORIES)
    with c2:
        search_query = st.text_input("Search Events", placeholder="Search by topic, speaker, venue...")

    # Filter events
    events = event_service.filter_events(
        category=cat_filter if cat_filter != "All" else None,
        search_query=search_query,
    )

    # Show only open or upcoming events first
    display_events = [
        e for e in events
        if e.status in (
            EventStatus.REGISTRATION_OPEN.value,
            EventStatus.FULL.value,
            EventStatus.REGISTRATION_CLOSED.value,
        )
    ]

    st.caption(f"Found {len(display_events)} campus events.")

    if not display_events:
        st.info("No events match your current criteria.")
        return

    # Check which events this student is already registered for
    existing_regs = {r["event_id"] for r in reg_service.get_student_registrations(user.user_id) if r["status"] == "Confirmed"}

    for e in display_events:
        reg_count = event_service.get_registered_count(e.event_id)
        avail = max(0, e.max_capacity - reg_count)
        is_already_reg = e.event_id in existing_regs
        deadline_dt = parse_date(e.registration_deadline)
        d_left = days_until(e.registration_deadline)

        # Card container
        with st.container():
            st.markdown(
                f"""
                <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span style="background-color: #EEF2FF; color: #4F46E5; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                                {e.category}
                            </span>
                            <h3 style="color: #1E3A8A; margin: 8px 0 4px 0;">{e.event_name}</h3>
                            <div style="font-size: 0.85rem; color: #64748B;">
                                📍 <b>{e.venue}</b> &nbsp;|&nbsp; 
                                📅 <b>{e.event_date}</b> &nbsp;|&nbsp; 
                                ⏰ <b>{e.start_time} - {e.end_time}</b> &nbsp;|&nbsp; 
                                🏛️ Organized by: <b>{e.organizer}</b>
                            </div>
                        </div>
                        <div>
                            {get_status_badge_html(e.status)}
                        </div>
                    </div>
                    <div style="margin: 12px 0; color: #334155; font-size: 0.92rem; line-height: 1.5;">
                        {e.description}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Capacity progress bar & booking action
            col_bar, col_act = st.columns([3, 1])

            with col_bar:
                util_pct = min(1.0, reg_count / e.max_capacity) if e.max_capacity > 0 else 0.0
                st.progress(util_pct, text=f"Seat Availability: {avail} of {e.max_capacity} seats remaining ({reg_count} booked)")
                if d_left is not None:
                    if d_left > 0:
                        st.caption(f"⏳ Registration closes in **{d_left} day(s)** ({e.registration_deadline})")
                    elif d_left == 0:
                        st.caption("⚠️ **Registration closes TODAY!**")
                    else:
                        st.caption("🔒 Registration deadline has passed.")

            with col_act:
                if is_already_reg:
                    st.success("✅ Already Registered")
                elif e.status == EventStatus.FULL.value or avail <= 0:
                    st.error("🚫 Event Full")
                elif e.status == EventStatus.REGISTRATION_CLOSED.value or (d_left is not None and d_left < 0):
                    st.warning("🔒 Closed")
                else:
                    if st.button("Register Now", key=f"btn_reg_{e.event_id}", type="primary", use_container_width=True):
                        try:
                            receipt = reg_service.register_student(user.user_id, e.event_id)
                            st.balloons()
                            st.success(f"🎉 **Registration Confirmed!** Ticket ID: `{receipt['registration_id']}`")
                            st.rerun()
                        except (
                            EventFullError,
                            DuplicateRegistrationError,
                            RegistrationClosedError,
                            EventCancelledError,
                            ValidationError,
                        ) as err:
                            st.error(f"Registration Failed: {err.message}")

            st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
