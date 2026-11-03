"""
views/admin/events_view.py
--------------------------
Administrator Event Management module.
Allows full CRUD operations, live seat capacity monitoring, status automation,
and multi-field search and filtering.
"""

from datetime import date, timedelta
import streamlit as st
import pandas as pd

from services.event_service import EventService
from utils.constants import (
    EVENT_CATEGORIES,
    EVENT_STATUSES,
    EventStatus,
    EventCategory,
)
from utils.exceptions import (
    ValidationError,
    DuplicateEventError,
    EventNotFoundError,
)
from components.ui_helpers import render_header, get_status_badge_html


def render_admin_events() -> None:
    """Render the administrator event management interface."""
    event_service = EventService()

    render_header(
        title="Event Operations & Scheduling",
        subtitle="Create, update, monitor capacity, and manage lifecycle of university events",
        badge_text="Administration",
    )

    tab_list, tab_create, tab_edit = st.tabs([
        "📋 Event Registry",
        "➕ Schedule New Event",
        "✏️ Edit / Update Event",
    ])

    # -------------------------------------------------------------
    # TAB 1: Event Registry
    # -------------------------------------------------------------
    with tab_list:
        st.markdown("#### 🔍 Filter & Search Events")
        f_col1, f_col2, f_col3 = st.columns(3)

        with f_col1:
            cat_filter = st.selectbox("Category", ["All"] + EVENT_CATEGORIES, index=0)
        with f_col2:
            status_filter = st.selectbox("Status", ["All"] + EVENT_STATUSES, index=0)
        with f_col3:
            search_query = st.text_input("Search", placeholder="Search by name, venue, organizer...")

        # Filtered event list
        events = event_service.filter_events(
            category=cat_filter if cat_filter != "All" else None,
            status=status_filter if status_filter != "All" else None,
            search_query=search_query,
        )

        st.caption(f"Showing {len(events)} events matching criteria.")

        if events:
            table_data = []
            for e in events:
                reg_count = event_service.get_registered_count(e.event_id)
                avail = max(0, e.max_capacity - reg_count)
                util = event_service.get_capacity_utilization(e.event_id)
                table_data.append({
                    "Event ID": e.event_id,
                    "Event Name": e.event_name,
                    "Category": e.category,
                    "Date": e.event_date,
                    "Time": f"{e.start_time} - {e.end_time}",
                    "Venue": e.venue,
                    "Capacity": e.max_capacity,
                    "Registered": reg_count,
                    "Seats Left": avail,
                    "Utilization": f"{util:.1f}%",
                    "Status": e.status,
                })

            df_events = pd.DataFrame(table_data)
            st.dataframe(df_events, use_container_width=True, hide_index=True)

            # Quick action bar for single event
            st.markdown("##### ⚡ Quick Event Actions")
            action_col1, action_col2 = st.columns([2, 1])

            event_options = {f"{e.event_name} ({e.event_id})": e.event_id for e in events}
            selected_key = action_col1.selectbox("Select Event for Action", list(event_options.keys()))

            if selected_key:
                sel_id = event_options[selected_key]
                sel_event = event_service.get_event(sel_id)

                act_b1, act_b2, act_b3 = st.columns(3)
                if act_b1.button("Mark as Completed", use_container_width=True):
                    event_service.mark_completed(sel_id)
                    st.success(f"'{sel_event.event_name}' marked as Completed!")
                    st.rerun()

                if act_b2.button("Cancel Event", type="secondary", use_container_width=True):
                    event_service.cancel_event(sel_id)
                    st.warning(f"'{sel_event.event_name}' marked as Cancelled.")
                    st.rerun()

                if act_b3.button("Reopen Registration", use_container_width=True):
                    event_service.change_status(sel_id, EventStatus.REGISTRATION_OPEN.value)
                    st.success(f"Registration reopened for '{sel_event.event_name}'.")
                    st.rerun()
        else:
            st.info("No events match the selected filters.")

    # -------------------------------------------------------------
    # TAB 2: Schedule New Event
    # -------------------------------------------------------------
    with tab_create:
        st.markdown("#### ➕ Add New Campus Event")
        st.caption("Fill out the official event scheduling specifications.")

        with st.form("create_event_form"):
            c1, c2 = st.columns(2)
            with c1:
                e_name = st.text_input("Event Name*", placeholder="e.g. Artificial Intelligence Workshop")
                e_cat = st.selectbox("Category*", EVENT_CATEGORIES)
                e_venue = st.text_input("Venue / Location*", placeholder="e.g. Auditorium Hall A")
                e_organizer = st.text_input("Organizer / Department*", placeholder="e.g. MCA Student Council")
                e_cap = st.number_input("Maximum Seat Capacity*", min_value=1, max_value=5000, value=50, step=5)

            with c2:
                e_date = st.date_input("Event Date*", value=date.today() + timedelta(days=7))
                t1, t2 = st.columns(2)
                with t1:
                    e_start = st.text_input("Start Time (HH:MM)*", value="10:00")
                with t2:
                    e_end = st.text_input("End Time (HH:MM)*", value="16:00")
                e_deadline = st.date_input("Registration Deadline*", value=date.today() + timedelta(days=5))
                e_status = st.selectbox("Initial Status*", [
                    EventStatus.REGISTRATION_OPEN.value,
                    EventStatus.DRAFT.value,
                ])

            e_desc = st.text_area("Event Description*", placeholder="Provide detailed agenda, pre-requisites, speaker details, etc.")

            submit_event = st.form_submit_button("Create & Publish Event", type="primary", use_container_width=True)

            if submit_event:
                data = {
                    "event_name": e_name,
                    "description": e_desc,
                    "category": e_cat,
                    "event_date": str(e_date),
                    "start_time": e_start,
                    "end_time": e_end,
                    "venue": e_venue,
                    "organizer": e_organizer,
                    "max_capacity": e_cap,
                    "registration_deadline": str(e_deadline),
                    "status": e_status,
                }
                try:
                    new_evt = event_service.create_event(data)
                    st.success(f"Event successfully scheduled! Generated ID: **{new_evt.event_id}**")
                    st.rerun()
                except ValidationError as e:
                    st.error(f"Validation Error:\n{e.message}\n{e.details}")
                except DuplicateEventError as e:
                    st.error(f"Duplicate Error: {e.message}")

    # -------------------------------------------------------------
    # TAB 3: Edit / Update Event
    # -------------------------------------------------------------
    with tab_edit:
        st.markdown("#### ✏️ Update Existing Event")
        all_evts = event_service.list_all_events()

        if not all_evts:
            st.info("No events to edit.")
        else:
            evt_map = {f"{e.event_name} [{e.event_id}]": e for e in all_evts}
            chosen_key = st.selectbox("Select Event to Modify", list(evt_map.keys()))
            target_evt = evt_map[chosen_key]

            with st.form("edit_event_form"):
                ed1, ed2 = st.columns(2)
                with ed1:
                    up_name = st.text_input("Event Name", value=target_evt.event_name)
                    cat_idx = EVENT_CATEGORIES.index(target_evt.category) if target_evt.category in EVENT_CATEGORIES else 0
                    up_cat = st.selectbox("Category", EVENT_CATEGORIES, index=cat_idx)
                    up_venue = st.text_input("Venue", value=target_evt.venue)
                    up_organizer = st.text_input("Organizer", value=target_evt.organizer)
                    up_cap = st.number_input("Max Capacity", min_value=1, max_value=5000, value=int(target_evt.max_capacity))

                with ed2:
                    try:
                        cur_date = date.fromisoformat(target_evt.event_date)
                    except Exception:
                        cur_date = date.today()
                    up_date = st.date_input("Event Date", value=cur_date)

                    ut1, ut2 = st.columns(2)
                    with ut1:
                        up_start = st.text_input("Start Time", value=target_evt.start_time)
                    with ut2:
                        up_end = st.text_input("End Time", value=target_evt.end_time)

                    try:
                        cur_dead = date.fromisoformat(target_evt.registration_deadline)
                    except Exception:
                        cur_dead = date.today()
                    up_deadline = st.date_input("Registration Deadline", value=cur_dead)

                    stat_idx = EVENT_STATUSES.index(target_evt.status) if target_evt.status in EVENT_STATUSES else 0
                    up_status = st.selectbox("Status", EVENT_STATUSES, index=stat_idx)

                up_desc = st.text_area("Description", value=target_evt.description)

                submit_update = st.form_submit_button("Save Changes", type="primary", use_container_width=True)

                if submit_update:
                    update_data = {
                        "event_name": up_name,
                        "description": up_desc,
                        "category": up_cat,
                        "event_date": str(up_date),
                        "start_time": up_start,
                        "end_time": up_end,
                        "venue": up_venue,
                        "organizer": up_organizer,
                        "max_capacity": up_cap,
                        "registration_deadline": str(up_deadline),
                        "status": up_status,
                    }
                    try:
                        event_service.update_event(target_evt.event_id, update_data)
                        st.success(f"Event '{target_evt.event_id}' updated successfully!")
                        st.rerun()
                    except ValidationError as e:
                        st.error(f"Validation Error:\n{e.message}\n{e.details}")
                    except EventNotFoundError as e:
                        st.error(e.message)
