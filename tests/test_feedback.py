"""
tests/test_feedback.py
----------------------
Unit tests for Feedback & Rating business constraints:
  - Valid feedback recorded with star rating 1-5
  - Reject ratings outside 1-5 range
  - Reject duplicate feedback from same student
  - Reject feedback for ongoing / upcoming events (must be Completed)
  - Reject feedback from students who never registered for the event
"""

import unittest
import tempfile
from pathlib import Path
from datetime import date, timedelta

from models.event import Event
from models.student import Student
from models.registration import Registration
from repositories.event_repository import EventRepository
from repositories.student_repository import StudentRepository
from repositories.registration_repository import RegistrationRepository
from repositories.feedback_repository import FeedbackRepository
from services.feedback_service import FeedbackService
from utils.constants import EventStatus, EventCategory, RegistrationStatus
from utils.exceptions import (
    InvalidFeedbackError,
    DuplicateFeedbackError,
    EventNotCompletedError,
    FeedbackNotAllowedError,
)


class TestFeedbackSystem(unittest.TestCase):
    """Test suite for event review submission and validation rules."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.evt_path = Path(self.temp_dir.name) / "events.csv"
        self.stu_path = Path(self.temp_dir.name) / "students.csv"
        self.reg_path = Path(self.temp_dir.name) / "regs.csv"
        self.fbk_path = Path(self.temp_dir.name) / "fbk.csv"

        self.evt_repo = EventRepository(self.evt_path)
        self.stu_repo = StudentRepository(self.stu_path)
        self.reg_repo = RegistrationRepository(self.reg_path)
        self.fbk_repo = FeedbackRepository(self.fbk_path)

        self.service = FeedbackService(
            self.fbk_repo, self.evt_repo, self.stu_repo, self.reg_repo
        )

        # Registered student
        self.student = Student.create(
            student_id="STU001",
            name="Aarav Sharma",
            email="aarav@nit.edu",
            phone="9876543210",
            department="MCA",
            course="MCA",
            semester=4,
            academic_year="2024-25",
            plain_password="Password123",
        )
        self.stu_repo.save(self.student)

        # Completed Event
        today = date.today()
        self.event_completed = Event(
            event_id="EVT-DONE01",
            event_name="Completed AI Workshop",
            description="Event took place last week",
            category=EventCategory.WORKSHOP.value,
            event_date=(today - timedelta(days=7)).strftime("%Y-%m-%d"),
            start_time="10:00",
            end_time="16:00",
            venue="Auditorium",
            organizer="MCA Dept",
            max_capacity=50,
            registration_deadline=(today - timedelta(days=10)).strftime("%Y-%m-%d"),
            status=EventStatus.COMPLETED.value,
        )
        self.evt_repo.save(self.event_completed)

        # Enrolled registration
        self.registration = Registration.create(
            student_id="STU001",
            event_id="EVT-DONE01",
            status=RegistrationStatus.CONFIRMED.value,
        )
        self.reg_repo.save(self.registration)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_valid_feedback_submission(self) -> None:
        """A registered student reviewing a completed event with rating 1-5 should succeed."""
        fbk = self.service.submit_feedback(
            student_id="STU001",
            event_id="EVT-DONE01",
            rating=5,
            comment="Excellent workshop, very well conducted!",
        )
        self.assertIsNotNone(fbk.feedback_id)
        self.assertEqual(fbk.rating, 5)
        self.assertEqual(self.fbk_repo.count(), 1)

    def test_invalid_rating_rejected(self) -> None:
        """Ratings less than 1 or greater than 5 must raise InvalidFeedbackError."""
        with self.assertRaises(InvalidFeedbackError):
            self.service.submit_feedback("STU001", "EVT-DONE01", rating=0)

        with self.assertRaises(InvalidFeedbackError):
            self.service.submit_feedback("STU001", "EVT-DONE01", rating=6)

    def test_duplicate_feedback_rejected(self) -> None:
        """Submitting feedback more than once for the same event must raise DuplicateFeedbackError."""
        self.service.submit_feedback("STU001", "EVT-DONE01", rating=4, comment="First review")

        with self.assertRaises(DuplicateFeedbackError):
            self.service.submit_feedback("STU001", "EVT-DONE01", rating=5, comment="Second review")

    def test_feedback_before_completion_rejected(self) -> None:
        """Submitting feedback before event completion must raise EventNotCompletedError."""
        today = date.today()
        upcoming_evt = Event(
            event_id="EVT-FUTURE",
            event_name="Upcoming Boot Camp",
            description="Happens in future",
            category=EventCategory.TECHNICAL.value,
            event_date=(today + timedelta(days=5)).strftime("%Y-%m-%d"),
            start_time="10:00",
            end_time="16:00",
            venue="Lab 2",
            organizer="CS",
            max_capacity=30,
            registration_deadline=(today + timedelta(days=3)).strftime("%Y-%m-%d"),
            status=EventStatus.REGISTRATION_OPEN.value,
        )
        self.evt_repo.save(upcoming_evt)

        # Register student for upcoming event
        self.reg_repo.save(Registration.create("STU001", "EVT-FUTURE"))

        with self.assertRaises(EventNotCompletedError):
            self.service.submit_feedback("STU001", "EVT-FUTURE", rating=5)

    def test_unregistered_student_feedback_rejected(self) -> None:
        """A student who did not register for the event must not be allowed to review."""
        # Create non-registered student
        stu_unreg = Student.create(
            student_id="STU099",
            name="Stranger",
            email="stranger@nit.edu",
            phone="9876543299",
            department="BCA",
            course="BCA",
            semester=2,
            academic_year="2024-25",
            plain_password="Password123",
        )
        self.stu_repo.save(stu_unreg)

        with self.assertRaises(FeedbackNotAllowedError):
            self.service.submit_feedback("STU099", "EVT-DONE01", rating=4)


if __name__ == "__main__":
    unittest.main()
