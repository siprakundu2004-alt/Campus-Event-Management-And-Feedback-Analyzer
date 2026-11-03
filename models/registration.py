"""
models/registration.py
----------------------
Registration domain model for Campus Event Management & Feedback Analyzer.
"""

from dataclasses import dataclass, field, asdict

from utils.constants import RegistrationStatus
from utils.helpers import generate_registration_id, now_str


@dataclass
class Registration:
    """Records a student's registration for an event."""

    registration_id: str
    student_id: str
    event_id: str
    registration_date: str              # YYYY-MM-DD HH:MM
    status: str = RegistrationStatus.CONFIRMED.value

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        student_id: str,
        event_id: str,
        status: str = RegistrationStatus.CONFIRMED.value,
    ) -> "Registration":
        """Create a new Registration with auto-generated ID and timestamp."""
        return cls(
            registration_id=generate_registration_id(),
            student_id=student_id.strip().upper(),
            event_id=event_id.strip().upper(),
            registration_date=now_str(),
            status=status,
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Registration":
        return cls(
            registration_id=str(data["registration_id"]),
            student_id=str(data["student_id"]),
            event_id=str(data["event_id"]),
            registration_date=str(data["registration_date"]),
            status=str(data.get("status", RegistrationStatus.CONFIRMED.value)),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def is_active(self) -> bool:
        return self.status == RegistrationStatus.CONFIRMED.value

    @property
    def is_cancelled(self) -> bool:
        return self.status == RegistrationStatus.CANCELLED.value

    def __repr__(self) -> str:
        return (
            f"Registration(id={self.registration_id!r}, "
            f"student={self.student_id!r}, event={self.event_id!r}, "
            f"status={self.status!r})"
        )
