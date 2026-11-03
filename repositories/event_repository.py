"""
repositories/event_repository.py
---------------------------------
Concrete CSV repository for Event records.
"""

from pathlib import Path
from typing import Optional

import pandas as pd

from models.event import Event
from repositories.base_repository import BaseRepository
from utils.constants import EventStatus
import config


class EventRepository(BaseRepository[Event]):
    """Manages persistence for Event domain objects."""

    _id_column: str = "event_id"

    def __init__(self, filepath: Path = config.EVENTS_CSV) -> None:
        super().__init__(filepath)

    # ------------------------------------------------------------------
    # BaseRepository interface
    # ------------------------------------------------------------------

    def _get_columns(self) -> list[str]:
        return [
            "event_id", "event_name", "description", "category",
            "event_date", "start_time", "end_time", "venue", "organizer",
            "max_capacity", "registration_deadline", "status", "created_date",
        ]

    def _to_dict(self, obj: Event) -> dict:
        return obj.to_dict()

    def _from_dict(self, row: dict) -> Event:
        return Event.from_dict(row)

    def _get_id(self, obj: Event) -> str:
        return obj.event_id

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_status(self, status: str) -> list[Event]:
        """Return all events matching the given status string."""
        return self.filter_by(status=status)

    def get_upcoming(self) -> list[Event]:
        """Return events with Registration Open status, sorted by date."""
        df = self.get_dataframe()
        if df.empty:
            return []
        mask = df["status"] == EventStatus.REGISTRATION_OPEN.value
        filtered = df[mask].sort_values("event_date")
        return [Event.from_dict(row) for row in filtered.to_dict(orient="records")]

    def get_completed(self) -> list[Event]:
        """Return all completed events."""
        return self.get_by_status(EventStatus.COMPLETED.value)

    def search_events(self, query: str) -> list[Event]:
        """Search event name, venue, or organizer for the given query."""
        df = self.get_dataframe()
        if df.empty or not query:
            return self.get_all()
        mask = (
            df["event_name"].str.contains(query, case=False, na=False)
            | df["venue"].str.contains(query, case=False, na=False)
            | df["organizer"].str.contains(query, case=False, na=False)
            | df["category"].str.contains(query, case=False, na=False)
        )
        return [Event.from_dict(row) for row in df[mask].to_dict(orient="records")]

    def get_by_category(self, category: str) -> list[Event]:
        return self.filter_by(category=category)

    def update_status(self, event_id: str, new_status: str) -> bool:
        """Update only the status field of an event."""
        event = self.get_by_id(event_id)
        if not event:
            return False
        event.status = new_status
        self.save(event)
        return True
