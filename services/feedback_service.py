"""
services/feedback_service.py
----------------------------
Business logic layer for Event Feedback & Reviews.
Enforces all domain rules:
  1. Rating must be 1 to 5
  2. Student must exist
  3. Event must exist
  4. Event must be Completed
  5. Only registered students can submit feedback
  6. Prevent duplicate feedback from same student for same event
"""

from typing import Optional

from models.feedback import Feedback
from repositories.feedback_repository import FeedbackRepository
from repositories.event_repository import EventRepository
from repositories.student_repository import StudentRepository
from repositories.registration_repository import RegistrationRepository
from utils.constants import EventStatus, RATING_LABELS
from utils.exceptions import (
    StudentNotFoundError,
    EventNotFoundError,
    InvalidFeedbackError,
    FeedbackNotAllowedError,
    EventNotCompletedError,
    DuplicateFeedbackError,
    ValidationError,
)
from utils.validators import validate_student_id, validate_event_id, validate_rating


class FeedbackService:
    """Provides high-level feedback operations and business rule validations."""

    def __init__(
        self,
        feedback_repo: Optional[FeedbackRepository] = None,
        event_repo: Optional[EventRepository] = None,
        student_repo: Optional[StudentRepository] = None,
        registration_repo: Optional[RegistrationRepository] = None,
    ) -> None:
        self.feedback_repo = feedback_repo or FeedbackRepository()
        self.event_repo = event_repo or EventRepository()
        self.student_repo = student_repo or StudentRepository()
        self.registration_repo = registration_repo or RegistrationRepository()

    # ------------------------------------------------------------------
    # Submit Feedback
    # ------------------------------------------------------------------

    def submit_feedback(
        self,
        student_id: str,
        event_id: str,
        rating: int,
        comment: str = "",
    ) -> Feedback:
        """
        Validate and record student feedback for a completed event.
        Raises domain-specific exceptions on rule violations.
        """
        clean_sid = student_id.strip().upper()
        clean_eid = event_id.strip().upper()

        # Rule 1: Rating range 1–5
        ok_rating, msg_rating = validate_rating(rating)
        if not ok_rating:
            raise InvalidFeedbackError(msg_rating)

        # Rule 2: Student exists
        ok_sid, msg_sid = validate_student_id(clean_sid)
        if not ok_sid:
            raise ValidationError(msg_sid)
        student = self.student_repo.get_by_id(clean_sid)
        if not student:
            raise StudentNotFoundError(f"Student '{clean_sid}' not found.")

        # Rule 3: Event exists
        ok_eid, msg_eid = validate_event_id(clean_eid)
        if not ok_eid:
            raise ValidationError(msg_eid)
        event = self.event_repo.get_by_id(clean_eid)
        if not event:
            raise EventNotFoundError(f"Event '{clean_eid}' not found.")

        # Rule 4: Event must be completed
        if event.status != EventStatus.COMPLETED.value:
            raise EventNotCompletedError(
                f"Feedback cannot be submitted: Event '{event.event_name}' is not yet completed. "
                f"Current status: {event.status}."
            )

        # Rule 5: Student must have registered for the event
        has_reg = self.registration_repo.has_ever_registered(clean_sid, clean_eid)
        if not has_reg:
            raise FeedbackNotAllowedError(
                f"Feedback not allowed: Student '{student.name}' was not registered for '{event.event_name}'."
            )

        # Rule 6: No duplicate feedback
        if self.feedback_repo.has_submitted(clean_sid, clean_eid):
            raise DuplicateFeedbackError(
                f"Duplicate feedback: You have already submitted feedback for '{event.event_name}'."
            )

        # Create and persist feedback
        feedback = Feedback.create(
            student_id=clean_sid,
            event_id=clean_eid,
            rating=rating,
            comment=comment.strip(),
        )
        self.feedback_repo.save(feedback)
        return feedback

    # ------------------------------------------------------------------
    # Queries & Feedback Retrieval
    # ------------------------------------------------------------------

    def get_event_feedback(self, event_id: str) -> list[dict]:
        """Return enriched feedback entries for a specific event."""
        clean_eid = event_id.strip().upper()
        feedbacks = self.feedback_repo.get_by_event(clean_eid)
        students = {s.student_id: s for s in self.student_repo.get_all()}

        enriched = []
        for fbk in feedbacks:
            stu = students.get(fbk.student_id)
            enriched.append({
                "feedback_id": fbk.feedback_id,
                "student_id": fbk.student_id,
                "student_name": stu.name if stu else fbk.student_id,
                "department": stu.department if stu else "-",
                "course": stu.course if stu else "-",
                "rating": fbk.rating,
                "rating_label": fbk.rating_label,
                "comment": fbk.comment,
                "submission_date": fbk.submission_date,
            })
        return enriched

    def get_student_feedback_history(self, student_id: str) -> list[dict]:
        """Return all feedback submitted by a specific student."""
        clean_sid = student_id.strip().upper()
        feedbacks = self.feedback_repo.get_by_student(clean_sid)
        events = {e.event_id: e for e in self.event_repo.get_all()}

        enriched = []
        for fbk in feedbacks:
            evt = events.get(fbk.event_id)
            enriched.append({
                "feedback_id": fbk.feedback_id,
                "event_id": fbk.event_id,
                "event_name": evt.event_name if evt else fbk.event_id,
                "category": evt.category if evt else "-",
                "rating": fbk.rating,
                "rating_label": fbk.rating_label,
                "comment": fbk.comment,
                "submission_date": fbk.submission_date,
            })
        return enriched

    def get_events_pending_feedback_for_student(self, student_id: str) -> list[dict]:
        """
        Return list of completed events that the student attended but hasn't reviewed yet.
        """
        clean_sid = student_id.strip().upper()
        registrations = self.registration_repo.get_by_student(clean_sid)
        events = {e.event_id: e for e in self.event_repo.get_all()}

        pending = []
        for reg in registrations:
            evt = events.get(reg.event_id)
            if evt and evt.status == EventStatus.COMPLETED.value:
                if not self.feedback_repo.has_submitted(clean_sid, reg.event_id):
                    pending.append({
                        "event_id": evt.event_id,
                        "event_name": evt.event_name,
                        "category": evt.category,
                        "event_date": evt.event_date,
                        "venue": evt.venue,
                    })
        return pending

    def list_all_feedback(self) -> list[dict]:
        """Return enriched list of all feedback in system."""
        fbks = self.feedback_repo.get_all()
        events = {e.event_id: e for e in self.event_repo.get_all()}
        students = {s.student_id: s for s in self.student_repo.get_all()}

        enriched = []
        for fbk in fbks:
            evt = events.get(fbk.event_id)
            stu = students.get(fbk.student_id)
            enriched.append({
                "feedback_id": fbk.feedback_id,
                "student_id": fbk.student_id,
                "student_name": stu.name if stu else fbk.student_id,
                "department": stu.department if stu else "-",
                "event_id": fbk.event_id,
                "event_name": evt.event_name if evt else fbk.event_id,
                "category": evt.category if evt else "-",
                "rating": fbk.rating,
                "rating_label": fbk.rating_label,
                "comment": fbk.comment,
                "submission_date": fbk.submission_date,
            })
        return enriched
