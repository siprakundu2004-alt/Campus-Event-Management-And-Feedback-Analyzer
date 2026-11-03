"""
models/feedback.py
------------------
Feedback domain model for Campus Event Management & Feedback Analyzer.
"""

from dataclasses import dataclass, field, asdict

from utils.helpers import generate_feedback_id, now_str
from utils.constants import RATING_LABELS


@dataclass
class Feedback:
    """Stores a student's post-event feedback."""

    feedback_id: str
    student_id: str
    event_id: str
    rating: int                         # 1–5
    comment: str
    submission_date: str                # YYYY-MM-DD HH:MM

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        student_id: str,
        event_id: str,
        rating: int,
        comment: str = "",
    ) -> "Feedback":
        """Create a new Feedback entry with auto-generated ID and timestamp."""
        return cls(
            feedback_id=generate_feedback_id(),
            student_id=student_id.strip().upper(),
            event_id=event_id.strip().upper(),
            rating=int(rating),
            comment=comment.strip(),
            submission_date=now_str(),
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Feedback":
        return cls(
            feedback_id=str(data["feedback_id"]),
            student_id=str(data["student_id"]),
            event_id=str(data["event_id"]),
            rating=int(data["rating"]),
            comment=str(data.get("comment", "")),
            submission_date=str(data["submission_date"]),
        )

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    @property
    def rating_label(self) -> str:
        """Human-readable label for the numeric rating."""
        return RATING_LABELS.get(self.rating, "Unknown")

    @property
    def is_positive(self) -> bool:
        """Return True for ratings of 4 or 5."""
        return self.rating >= 4

    def __repr__(self) -> str:
        return (
            f"Feedback(id={self.feedback_id!r}, "
            f"student={self.student_id!r}, event={self.event_id!r}, "
            f"rating={self.rating})"
        )
