"""
services/event_service.py
-------------------------
Business logic layer for Event operations.
Orchestrates validation, repository persistence, and state transitions.
"""

from typing import Optional
from datetime import date

from models.event import Event
from repositories.event_repository import EventRepository
from repositories.registration_repository import RegistrationRepository
from utils.constants import EventStatus, EventCategory
from utils.exceptions import (
    EventNotFoundError,
    DuplicateEventError,
    ValidationError,
)
from utils.validators import validate_event_form, validate_event_id
from utils.helpers import parse_date


class EventService:
    """Provides high-level event management operations."""

    def __init__(
        self,
        event_repo: Optional[EventRepository] = None,
        registration_repo: Optional[RegistrationRepository] = None,
    ) -> None:
        self.event_repo = event_repo or EventRepository()
        self.registration_repo = registration_repo or RegistrationRepository()

    # ------------------------------------------------------------------
    # Create / Update
    # ------------------------------------------------------------------

    def create_event(self, event_data: dict) -> Event:
        """
        Validate and create a new event.
        Raises ValidationError if fields are invalid.
        """
        errors = validate_event_form(event_data)
        if errors:
            raise ValidationError("Event validation failed.", details="\n".join(errors))

        # Check explicit ID if provided, otherwise auto-generate
        custom_id = event_data.get("event_id")
        if custom_id:
            ok, msg = validate_event_id(custom_id)
            if not ok:
                raise ValidationError(msg)
            if self.event_repo.exists(custom_id):
                raise DuplicateEventError(f"Event ID '{custom_id}' already exists.")

        event = Event.create(
            event_name=event_data["event_name"],
            description=event_data.get("description", ""),
            category=event_data["category"],
            event_date=event_data["event_date"],
            start_time=event_data["start_time"],
            end_time=event_data["end_time"],
            venue=event_data["venue"],
            organizer=event_data["organizer"],
            max_capacity=int(event_data["max_capacity"]),
            registration_deadline=event_data["registration_deadline"],
            status=event_data.get("status", EventStatus.REGISTRATION_OPEN.value),
        )

        if custom_id:
            event.event_id = custom_id.strip().upper()

        self.event_repo.save(event)
        return event

    def update_event(self, event_id: str, event_data: dict) -> Event:
        """
        Update an existing event.
        Raises EventNotFoundError or ValidationError.
        """
        existing = self.event_repo.get_by_id(event_id)
        if not existing:
            raise EventNotFoundError(f"Event with ID '{event_id}' not found.")

        errors = validate_event_form(event_data)
        if errors:
            raise ValidationError("Event update validation failed.", details="\n".join(errors))

        # Update fields
        existing.event_name = event_data["event_name"].strip()
        existing.description = event_data.get("description", "").strip()
        existing.category = event_data["category"]
        existing.event_date = event_data["event_date"]
        existing.start_time = event_data["start_time"]
        existing.end_time = event_data["end_time"]
        existing.venue = event_data["venue"].strip()
        existing.organizer = event_data["organizer"].strip()
        existing.max_capacity = int(event_data["max_capacity"])
        existing.registration_deadline = event_data["registration_deadline"]
        if "status" in event_data:
            existing.status = event_data["status"]

        # Recalculate status (e.g. if capacity was altered)
        self._sync_event_status(existing)

        self.event_repo.save(existing)
        return existing

    # ------------------------------------------------------------------
    # Status Transitions
    # ------------------------------------------------------------------

    def cancel_event(self, event_id: str) -> Event:
        """Cancel an event."""
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise EventNotFoundError(f"Event with ID '{event_id}' not found.")
        event.status = EventStatus.CANCELLED.value
        self.event_repo.save(event)
        return event

    def mark_completed(self, event_id: str) -> Event:
        """Mark an event as completed."""
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise EventNotFoundError(f"Event with ID '{event_id}' not found.")
        event.status = EventStatus.COMPLETED.value
        self.event_repo.save(event)
        return event

    def change_status(self, event_id: str, new_status: str) -> Event:
        """Manually change event status."""
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise EventNotFoundError(f"Event with ID '{event_id}' not found.")
        event.status = new_status
        self.event_repo.save(event)
        return event

    # ------------------------------------------------------------------
    # Query & Search
    # ------------------------------------------------------------------

    def get_event(self, event_id: str) -> Event:
        """Retrieve event by ID or raise EventNotFoundError."""
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise EventNotFoundError(f"Event with ID '{event_id}' not found.")
        return event

    def list_all_events(self) -> list[Event]:
        """Return all events, refreshing auto-statuses first."""
        events = self.event_repo.get_all()
        for evt in events:
            self._sync_event_status(evt)
        return events

    def list_upcoming_events(self) -> list[Event]:
        """Return upcoming active events."""
        events = self.event_repo.get_upcoming()
        return [evt for evt in events if evt.status == EventStatus.REGISTRATION_OPEN.value]

    def list_completed_events(self) -> list[Event]:
        """Return all completed events."""
        return self.event_repo.get_completed()

    def filter_events(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        search_query: Optional[str] = None,
        venue: Optional[str] = None,
    ) -> list[Event]:
        """Apply combined multi-attribute filters on events."""
        events = self.list_all_events()

        if category and category != "All":
            events = [e for e in events if e.category.lower() == category.lower()]
        if status and status != "All":
            events = [e for e in events if e.status.lower() == status.lower()]
        if venue and venue != "All":
            events = [e for e in events if e.venue.lower() == venue.lower()]
        if search_query and search_query.strip():
            q = search_query.strip().lower()
            events = [
                e for e in events
                if q in e.event_name.lower()
                or q in e.description.lower()
                or q in e.venue.lower()
                or q in e.organizer.lower()
                or q in e.category.lower()
            ]

        return events

    # ------------------------------------------------------------------
    # Seat & Capacity calculations
    # ------------------------------------------------------------------

    def get_registered_count(self, event_id: str) -> int:
        """Return active registration count for the event."""
        return self.registration_repo.count_active_for_event(event_id)

    def get_available_seats(self, event_id: str) -> int:
        """Return remaining seats for an event."""
        event = self.get_event(event_id)
        registered = self.get_registered_count(event_id)
        return max(0, event.max_capacity - registered)

    def get_capacity_utilization(self, event_id: str) -> float:
        """Return capacity utilization as a percentage (0.0 to 100.0)."""
        event = self.get_event(event_id)
        if event.max_capacity <= 0:
            return 0.0
        registered = self.get_registered_count(event_id)
        return min(100.0, (registered / event.max_capacity) * 100.0)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sync_event_status(self, event: Event) -> None:
        """
        Auto-update status based on date/capacity without overriding manual Cancelled/Draft/Completed.
        """
        if event.status in (EventStatus.CANCELLED.value, EventStatus.DRAFT.value, EventStatus.COMPLETED.value):
            return

        # Check deadline
        deadline = parse_date(event.registration_deadline)
        event_dt = parse_date(event.event_date)
        today = date.today()

        if event_dt and event_dt < today:
            event.status = EventStatus.COMPLETED.value
            self.event_repo.save(event)
            return

        registered = self.registration_repo.count_active_for_event(event.event_id)
        if registered >= event.max_capacity:
            if event.status != EventStatus.FULL.value:
                event.status = EventStatus.FULL.value
                self.event_repo.save(event)
            return

        if deadline and deadline < today:
            if event.status != EventStatus.REGISTRATION_CLOSED.value:
                event.status = EventStatus.REGISTRATION_CLOSED.value
                self.event_repo.save(event)
            return

        # Otherwise should be open
        if event.status in (EventStatus.FULL.value, EventStatus.REGISTRATION_CLOSED.value):
            event.status = EventStatus.REGISTRATION_OPEN.value
            self.event_repo.save(event)
