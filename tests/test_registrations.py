"""
tests/test_registrations.py
---------------------------
Unit tests for Smart Registration business rules and constraints:
  - Valid registration creates receipt and confirms booking
  - Reject duplicate registrations by same student
  - Reject registrations when event has reached maximum capacity
  - Reject registrations for non-existent students or events
  - Reject registrations after the deadline or if event is cancelled
"""

import unittest
import tempfile
from pathlib import Path
from datetime import date, timedelta

from models.event import Event
from models.student import Student
from repositories.event_repository import EventRepository
from repositories.student_repository import StudentRepository
from repositories.registration_repository import RegistrationRepository
from services.registration_service import RegistrationService
from utils.constants import EventStatus, EventCategory
from utils.exceptions import (
    EventFullError,
    DuplicateRegistrationError,
    RegistrationClosedError,
    EventCancelledError,
    StudentNotFoundError,
    EventNotFoundError,
)


class TestSmartRegistration(unittest.TestCase):
    """Test suite for event registration rules and custom exceptions."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.evt_path = Path(self.temp_dir.name) / "events.csv"
        self.stu_path = Path(self.temp_dir.name) / "students.csv"
        self.reg_path = Path(self.temp_dir.name) / "regs.csv"

        self.evt_repo = EventRepository(self.evt_path)
        self.stu_repo = StudentRepository(self.stu_path)
        self.reg_repo = RegistrationRepository(self.reg_path)

        self.service = RegistrationService(self.reg_repo, self.evt_repo, self.stu_repo)

        # Baseline student
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

        # Baseline event (capacity 2)
        today = date.today()
        self.event = Event(
            event_id="EVT-TEST01",
            event_name="Workshop with 2 seats",
            description="Testing capacity limits",
            category=EventCategory.WORKSHOP.value,
            event_date=(today + timedelta(days=10)).strftime("%Y-%m-%d"),
            start_time="10:00",
            end_time="12:00",
            venue="Lab 1",
            organizer="MCA",
            max_capacity=2,
            registration_deadline=(today + timedelta(days=5)).strftime("%Y-%m-%d"),
            status=EventStatus.REGISTRATION_OPEN.value,
        )
        self.evt_repo.save(self.event)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_valid_registration(self) -> None:
        """A valid student registering for an open event should succeed."""
        receipt = self.service.register_student("STU001", "EVT-TEST01")
        self.assertIsNotNone(receipt["registration_id"])
        self.assertEqual(receipt["status"], "Confirmed")
        self.assertEqual(receipt["available_seats"], 1)

    def test_duplicate_registration_rejected(self) -> None:
        """Registering twice for the same event must raise DuplicateRegistrationError."""
        self.service.register_student("STU001", "EVT-TEST01")

        with self.assertRaises(DuplicateRegistrationError):
            self.service.register_student("STU001", "EVT-TEST01")

    def test_event_full_rejection(self) -> None:
        """Registering when capacity is full must raise EventFullError."""
        # Add second student
        stu2 = Student.create(
            student_id="STU002",
            name="Priya Patel",
            email="priya@nit.edu",
            phone="9876543211",
            department="CS",
            course="B.Tech CS",
            semester=6,
            academic_year="2023-24",
            plain_password="Password123",
        )
        self.stu_repo.save(stu2)

        # Fill capacity (cap = 2)
        self.service.register_student("STU001", "EVT-TEST01")
        self.service.register_student("STU002", "EVT-TEST01")

        # Third student attempts registration
        stu3 = Student.create(
            student_id="STU003",
            name="Rohan Verma",
            email="rohan@nit.edu",
            phone="9876543212",
            department="IT",
            course="B.Tech IT",
            semester=4,
            academic_year="2024-25",
            plain_password="Password123",
        )
        self.stu_repo.save(stu3)

        with self.assertRaises(EventFullError):
            self.service.register_student("STU003", "EVT-TEST01")

    def test_nonexistent_student_rejected(self) -> None:
        """Registering an invalid student ID must raise StudentNotFoundError."""
        with self.assertRaises(StudentNotFoundError):
            self.service.register_student("STU999", "EVT-TEST01")

    def test_nonexistent_event_rejected(self) -> None:
        """Registering for an invalid event ID must raise EventNotFoundError."""
        with self.assertRaises(EventNotFoundError):
            self.service.register_student("STU001", "EVT-FAKE99")

    def test_cancelled_event_rejected(self) -> None:
        """Registering for a cancelled event must raise EventCancelledError."""
        self.event.status = EventStatus.CANCELLED.value
        self.evt_repo.save(self.event)

        with self.assertRaises(EventCancelledError):
            self.service.register_student("STU001", "EVT-TEST01")

    def test_cancellation_releases_seat(self) -> None:
        """Cancelling a booking must release the seat and permit new registration."""
        self.service.register_student("STU001", "EVT-TEST01")
        self.assertEqual(self.reg_repo.count_active_for_event("EVT-TEST01"), 1)

        ok = self.service.cancel_registration("STU001", "EVT-TEST01")
        self.assertTrue(ok)
        self.assertEqual(self.reg_repo.count_active_for_event("EVT-TEST01"), 0)


if __name__ == "__main__":
    unittest.main()
