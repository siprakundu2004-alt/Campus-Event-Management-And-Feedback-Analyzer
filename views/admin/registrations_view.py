"""
views/admin/registrations_view.py
--------------------------------
Administrator Event Registrations & Attendance Roster module.
Enables event organizers to verify tickets, check attendance, and manage cancellations.
"""

import streamlit as st
import pandas as pd

from services.registration_service import RegistrationService
from services.event_service import EventService
from utils.constants import RegistrationStatus, DEPARTMENTS
from components.ui_helpers import render_header, render_kpi


def render_admin_registrations() -> None:
    """Render the registration management and attendance verification view."""
    reg_service = RegistrationService()
    event_service = EventService()

    render_header(
        title="Event Registration & Attendance Roster",
        subtitle="Verify attendee check-ins, oversee booking statuses, and manage cancellations",
        badge_text="Administration",
    )

    all_regs = reg_service.list_all_registrations()
    events = event_service.list_all_events()

    # KPI summary
    k1, k2, k3, k4 = st.columns(4)
    total_reg = len(all_regs)
    confirmed = sum(1 for r in all_regs if r["status"] == RegistrationStatus.CONFIRMED.value)
    attended = sum(1 for r in all_regs if r["status"] == RegistrationStatus.ATTENDED.value)
    cancelled = sum(1 for r in all_regs if r["status"] == RegistrationStatus.CANCELLED.value)

    with k1:
        render_kpi("Total Bookings", str(total_reg), "All time")
    with k2:
        render_kpi("Confirmed", str(confirmed), "Active seats")
    with k3:
        render_kpi("Attended", str(attended), "Verified check-ins")
    with k4:
        render_kpi("Cancelled", str(cancelled), "Released seats")

    st.markdown("---")

    # Filters
    st.markdown("#### 🔍 Filter Registrations")
    rf1, rf2, rf3 = st.columns(3)

    event_titles = ["All Events"] + [f"{e.event_name} ({e.event_id})" for e in events]
    with rf1:
        sel_event_str = st.selectbox("Event", event_titles)
    with rf2:
        sel_dept = st.selectbox("Department", ["All"] + DEPARTMENTS)
    with rf3:
        sel_stat = st.selectbox("Status", ["All", RegistrationStatus.CONFIRMED.value, RegistrationStatus.ATTENDED.value, RegistrationStatus.CANCELLED.value])

    # Filter logic
    filtered = all_regs
    if sel_event_str != "All Events":
        sel_eid = sel_event_str.split("(")[-1].replace(")", "").strip()
        filtered = [r for r in filtered if r["event_id"] == sel_eid]

    if sel_dept != "All":
        filtered = [r for r in filtered if r["department"] == sel_dept]

    if sel_stat != "All":
        filtered = [r for r in filtered if r["status"] == sel_stat]

    st.caption(f"Showing {len(filtered)} registration records.")

    if filtered:
        df_filtered = pd.DataFrame(filtered)
        st.dataframe(
            df_filtered[[
                "registration_id", "student_id", "student_name", "department",
                "event_name", "event_date", "registration_date", "status"
            ]],
            use_container_width=True,
            hide_index=True,
        )

        # Quick action controls
        st.markdown("##### ⚡ Attendance & Booking Actions")
        a1, a2 = st.columns([2, 1])

        active_registrations = [r for r in filtered if r["status"] == RegistrationStatus.CONFIRMED.value]
        if active_registrations:
            reg_dict = {
                f"{r['student_name']} - {r['event_name']} ({r['registration_id']})": r
                for r in active_registrations
            }
            chosen_reg_key = a1.selectbox("Select Confirmed Registration", list(reg_dict.keys()))

            if chosen_reg_key:
                target_reg = reg_dict[chosen_reg_key]
                b1, b2 = a2.columns(2)

                if b1.button("Mark Attended", type="primary", use_container_width=True):
                    reg_service.mark_attendance(target_reg["registration_id"])
                    st.success(f"Marked {target_reg['student_name']} as Attended!")
                    st.rerun()

                if b2.button("Cancel Booking", type="secondary", use_container_width=True):
                    reg_service.cancel_registration(target_reg["student_id"], target_reg["event_id"])
                    st.warning(f"Cancelled booking for {target_reg['student_name']}.")
                    st.rerun()
        else:
            st.info("No active confirmed bookings in current filter.")
    else:
        st.info("No registrations match the selected criteria.")
