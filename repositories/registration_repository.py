"""
repositories/registration_repository.py
----------------------------------------
Concrete CSV repository for Registration records.
"""

from pathlib import Path
from typing import Optional

from models.registration import Registration
from repositories.base_repository import BaseRepository
from utils.constants import RegistrationStatus
import config


class RegistrationRepository(BaseRepository[Registration]):
    """Manages persistence for Registration domain objects."""

    _id_column: str = "registration_id"

    def __init__(self, filepath: Path = config.REGISTRATIONS_CSV) -> None:
        super().__init__(filepath)

    # ------------------------------------------------------------------
    # BaseRepository interface
    # ------------------------------------------------------------------

    def _get_columns(self) -> list[str]:
        return [
            "registration_id", "student_id", "event_id",
            "registration_date", "status",
        ]

    def _to_dict(self, obj: Registration) -> dict:
        return obj.to_dict()

    def _from_dict(self, row: dict) -> Registration:
        return Registration.from_dict(row)

    def _get_id(self, obj: Registration) -> str:
        return obj.registration_id

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_student(self, student_id: str) -> list[Registration]:
        """Return all registrations for a given student."""
        return self.filter_by(student_id=student_id)

    def get_by_event(self, event_id: str) -> list[Registration]:
        """Return all registrations for a given event."""
        return self.filter_by(event_id=event_id)

    def get_active_by_event(self, event_id: str) -> list[Registration]:
        """Return only confirmed registrations for an event."""
        df = self.get_dataframe()
        if df.empty:
            return []
        mask = (
            (df["event_id"].str.upper() == event_id.upper())
            & (df["status"] == RegistrationStatus.CONFIRMED.value)
        )
        return [Registration.from_dict(r) for r in df[mask].to_dict(orient="records")]

    def get_active_by_student(self, student_id: str) -> list[Registration]:
        """Return only confirmed registrations for a student."""
        df = self.get_dataframe()
        if df.empty:
            return []
        mask = (
            (df["student_id"].str.upper() == student_id.upper())
            & (df["status"] == RegistrationStatus.CONFIRMED.value)
        )
        return [Registration.from_dict(r) for r in df[mask].to_dict(orient="records")]

    def is_registered(self, student_id: str, event_id: str) -> bool:
        """
        Return True if the student has an ACTIVE registration for the event.
        """
        df = self.get_dataframe()
        if df.empty:
            return False
        mask = (
            (df["student_id"].str.upper() == student_id.upper())
            & (df["event_id"].str.upper() == event_id.upper())
            & (df["status"] == RegistrationStatus.CONFIRMED.value)
        )
        return df[mask].shape[0] > 0

    def has_ever_registered(self, student_id: str, event_id: str) -> Optional[Registration]:
        """Return the registration record (any status) or None."""
        df = self.get_dataframe()
        if df.empty:
            return None
        mask = (
            (df["student_id"].str.upper() == student_id.upper())
            & (df["event_id"].str.upper() == event_id.upper())
        )
        rows = df[mask]
        if rows.empty:
            return None
        return Registration.from_dict(rows.iloc[0].to_dict())

    def count_active_for_event(self, event_id: str) -> int:
        """Return the count of confirmed registrations for an event."""
        return len(self.get_active_by_event(event_id))

    def cancel_registration(self, student_id: str, event_id: str) -> bool:
        """Mark the registration as cancelled. Returns True on success."""
        df = self.get_dataframe()
        if df.empty:
            return False
        mask = (
            (df["student_id"].str.upper() == student_id.upper())
            & (df["event_id"].str.upper() == event_id.upper())
            & (df["status"] == RegistrationStatus.CONFIRMED.value)
        )
        if not mask.any():
            return False
        df.loc[mask, "status"] = RegistrationStatus.CANCELLED.value
        self._write_df(df)
        return True

    def mark_attended(self, registration_id: str) -> bool:
        """Mark a registration as attended."""
        reg = self.get_by_id(registration_id)
        if not reg:
            return False
        reg.status = RegistrationStatus.ATTENDED.value
        self.save(reg)
        return True
