"""
repositories/feedback_repository.py
-------------------------------------
Concrete CSV repository for Feedback records.
"""

from pathlib import Path
from typing import Optional

from models.feedback import Feedback
from repositories.base_repository import BaseRepository
import config


class FeedbackRepository(BaseRepository[Feedback]):
    """Manages persistence for Feedback domain objects."""

    _id_column: str = "feedback_id"

    def __init__(self, filepath: Path = config.FEEDBACK_CSV) -> None:
        super().__init__(filepath)

    # ------------------------------------------------------------------
    # BaseRepository interface
    # ------------------------------------------------------------------

    def _get_columns(self) -> list[str]:
        return [
            "feedback_id", "student_id", "event_id",
            "rating", "comment", "submission_date",
        ]

    def _to_dict(self, obj: Feedback) -> dict:
        return obj.to_dict()

    def _from_dict(self, row: dict) -> Feedback:
        return Feedback.from_dict(row)

    def _get_id(self, obj: Feedback) -> str:
        return obj.feedback_id

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_event(self, event_id: str) -> list[Feedback]:
        return self.filter_by(event_id=event_id)

    def get_by_student(self, student_id: str) -> list[Feedback]:
        return self.filter_by(student_id=student_id)

    def has_submitted(self, student_id: str, event_id: str) -> bool:
        """Return True if the student has already submitted feedback for the event."""
        df = self.get_dataframe()
        if df.empty:
            return False
        mask = (
            (df["student_id"].str.upper() == student_id.upper())
            & (df["event_id"].str.upper() == event_id.upper())
        )
        return df[mask].shape[0] > 0

    def get_feedback_for_event(self, event_id: str) -> Optional[list[Feedback]]:
        """Return all feedback for an event, or empty list if none."""
        return self.get_by_event(event_id)

    def average_rating_for_event(self, event_id: str) -> Optional[float]:
        """Return the average rating for an event; None if no feedback exists."""
        feedbacks = self.get_by_event(event_id)
        if not feedbacks:
            return None
        return sum(f.rating for f in feedbacks) / len(feedbacks)
