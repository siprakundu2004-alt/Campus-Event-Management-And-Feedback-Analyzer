"""
models/event.py
---------------
Event domain model for Campus Event Management & Feedback Analyzer.
Pure dataclass — no UI, no file I/O, no business logic.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import date

from utils.constants import EventCategory, EventStatus
from utils.helpers import generate_event_id, today_str


@dataclass
class Event:
    """Represents a campus event."""

    event_id: str
    event_name: str
    description: str
    category: str                       # EventCategory value
    event_date: str                     # YYYY-MM-DD
    start_time: str                     # HH:MM
    end_time: str                       # HH:MM
    venue: str
    organizer: str
    max_capacity: int
    registration_deadline: str          # YYYY-MM-DD
    status: str = EventStatus.DRAFT.value
    created_date: str = field(default_factory=today_str)

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        event_name: str,
        description: str,
        category: str,
        event_date: str,
        start_time: str,
        end_time: str,
        venue: str,
        organizer: str,
        max_capacity: int,
        registration_deadline: str,
        status: str = EventStatus.REGISTRATION_OPEN.value,
    ) -> "Event":
        """Create a new Event with an auto-generated ID."""
        return cls(
            event_id=generate_event_id(),
            event_name=event_name.strip(),
            description=description.strip(),
            category=category,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            venue=venue.strip(),
            organizer=organizer.strip(),
            max_capacity=int(max_capacity),
            registration_deadline=registration_deadline,
            status=status,
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Convert to a plain dictionary (for CSV storage)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        """Reconstruct an Event from a CSV row dictionary."""
        return cls(
            event_id=str(data["event_id"]),
            event_name=str(data["event_name"]),
            description=str(data.get("description", "")),
            category=str(data["category"]),
            event_date=str(data["event_date"]),
            start_time=str(data["start_time"]),
            end_time=str(data["end_time"]),
            venue=str(data["venue"]),
            organizer=str(data["organizer"]),
            max_capacity=int(data["max_capacity"]),
            registration_deadline=str(data["registration_deadline"]),
            status=str(data.get("status", EventStatus.DRAFT.value)),
            created_date=str(data.get("created_date", today_str())),
        )

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    @property
    def is_active(self) -> bool:
        """Return True if the event can still accept registrations."""
        return self.status == EventStatus.REGISTRATION_OPEN.value

    @property
    def is_cancelled(self) -> bool:
        return self.status == EventStatus.CANCELLED.value

    @property
    def is_completed(self) -> bool:
        return self.status == EventStatus.COMPLETED.value

    def __repr__(self) -> str:
        return (
            f"Event(id={self.event_id!r}, name={self.event_name!r}, "
            f"date={self.event_date!r}, status={self.status!r})"
        )
