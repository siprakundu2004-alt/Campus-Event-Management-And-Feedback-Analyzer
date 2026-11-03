"""
views/student/my_events_view.py
------------------------------
Student Bookings & Registration Management module.
Allows students to view confirmed bookings, review schedules, and cancel reservations.
"""

import streamlit as st
import pandas as pd

from services.auth_service import UserSession
from services.registration_service import RegistrationService
from components.ui_helpers import render_header, render_kpi


def render_student_my_events(user: UserSession) -> None:
    """Render the student's personal event registrations ledger."""
    reg_service = RegistrationService()

    render_header(
        title="My Event Passes & Bookings",
        subtitle="Manage your current registrations, download confirmations, or withdraw attendance",
        badge_text="Student Portal",
    )

    all_regs = reg_service.get_student_registrations(user.user_id)

    confirmed_regs = [r for r in all_regs if r["status"] == "Confirmed"]
    past_regs = [r for r in all_regs if r["status"] in ("Attended", "Cancelled")]

    k1, k2, k3 = st.columns(3)
    with k1:
        render_kpi("Active Event Passes", str(len(confirmed_regs)), "Upcoming Events")
    with k2:
        render_kpi("Attended Events", str(sum(1 for r in all_regs if r["status"] == "Attended")), "Verified Check-ins")
    with k3:
        render_kpi("Cancelled Passes", str(sum(1 for r in all_regs if r["status"] == "Cancelled")), "Seats Released")

    st.markdown("---")

    st.markdown("#### 🎟️ Confirmed Event Passes")

    if not confirmed_regs:
        st.info("You do not currently have any active event registrations.")
    else:
        for r in confirmed_regs:
            with st.container():
                st.markdown(
                    f"""
                    <div style="background: white; border: 1px solid #BBF7D0; border-radius: 10px; padding: 18px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="background-color: #DEF7EC; color: #03543F; padding: 3px 8px; border-radius: 12px; font-size: 0.72rem; font-weight: 700;">
                                    CONFIRMED PASS
                                </span>
                                <h4 style="color: #1E3A8A; margin: 6px 0 2px 0;">{r['event_name']}</h4>
                                <div style="font-size: 0.82rem; color: #64748B;">
                                    Ticket ID: <b>{r['registration_id']}</b> &nbsp;|&nbsp; 
                                    Category: <b>{r['category']}</b> &nbsp;|&nbsp; 
                                    Date: <b>{r['event_date']}</b> &nbsp;|&nbsp; 
                                    Venue: <b>{r['venue']}</b>
                                </div>
                            </div>
                            <div style="text-align: right; font-size: 0.8rem; color: #64748B;">
                                Booked on: {r['registration_date']}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                btn_col1, btn_col2 = st.columns([4, 1])
                with btn_col2:
                    if st.button("Cancel Pass", key=f"cancel_{r['registration_id']}", type="secondary", use_container_width=True):
                        ok = reg_service.cancel_registration(user.user_id, r["event_id"])
                        if ok:
                            st.warning(f"Registration for '{r['event_name']}' has been cancelled.")
                            st.rerun()

    # Past events table
    if past_regs:
        st.markdown("---")
        st.markdown("#### 📜 Booking History & Past Records")
        st.dataframe(pd.DataFrame(past_regs), use_container_width=True, hide_index=True)
