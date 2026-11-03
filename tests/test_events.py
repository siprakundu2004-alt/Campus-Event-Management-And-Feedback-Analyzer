"""
tests/test_events.py
--------------------
Unit tests for Event management business rules:
  - Create valid event
  - Prevent duplicate event ID
  - Reject invalid date formats
  - Reject invalid capacity limits
"""

import unittest
import tempfile
from pathlib import Path
from datetime import date, timedelta

from models.event import Event
from repositories.event_repository import EventRepository
from repositories.registration_repository import RegistrationRepository
from services.event_service import EventService
from utils.constants import EventCategory, EventStatus
from utils.exceptions import ValidationError, DuplicateEventError, EventNotFoundError


class TestEventManagement(unittest.TestCase):
    """Test suite for event creation, updates, and validations."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.evt_path = Path(self.temp_dir.name) / "test_events.csv"
        self.reg_path = Path(self.temp_dir.name) / "test_regs.csv"

        self.evt_repo = EventRepository(self.evt_path)
        self.reg_repo = RegistrationRepository(self.reg_path)
        self.service = EventService(self.evt_repo, self.reg_repo)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_valid_event(self) -> None:
        """A properly formatted event should be created and persisted."""
        today = date.today()
        data = {
            "event_name": "Test Python Hackathon",
            "description": "Test description of hackathon",
            "category": EventCategory.HACKATHON.value,
            "event_date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "start_time": "10:00",
            "end_time": "18:00",
            "venue": "Lab 1",
            "organizer": "MCA Dept",
            "max_capacity": 50,
            "registration_deadline": (today + timedelta(days=8)).strftime("%Y-%m-%d"),
            "status": EventStatus.REGISTRATION_OPEN.value,
        }
        event = self.service.create_event(data)
        self.assertIsNotNone(event.event_id)
        self.assertEqual(event.event_name, "Test Python Hackathon")
        self.assertEqual(self.evt_repo.count(), 1)

    def test_duplicate_event_id(self) -> None:
        """Attempting to create an event with an existing ID must raise DuplicateEventError."""
        today = date.today()
        data = {
            "event_id": "EVT-TEST01",
            "event_name": "Original Event",
            "description": "Desc",
            "category": EventCategory.WORKSHOP.value,
            "event_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "start_time": "09:00",
            "end_time": "12:00",
            "venue": "Hall A",
            "organizer": "CS Dept",
            "max_capacity": 30,
            "registration_deadline": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
        }
        self.service.create_event(data)

        # Attempt duplicate
        data_dup = data.copy()
        data_dup["event_name"] = "Different Name Same ID"
        with self.assertRaises(DuplicateEventError):
            self.service.create_event(data_dup)

    def test_invalid_date_format(self) -> None:
        """Date strings not conforming to YYYY-MM-DD should raise ValidationError."""
        data = {
            "event_name": "Bad Date Event",
            "description": "Desc",
            "category": EventCategory.TECHNICAL.value,
            "event_date": "25/12/2026",          # Invalid format
            "start_time": "10:00",
            "end_time": "12:00",
            "venue": "Hall B",
            "organizer": "IT Dept",
            "max_capacity": 40,
            "registration_deadline": "2026-12-20",
        }
        with self.assertRaises(ValidationError):
            self.service.create_event(data)

    def test_invalid_capacity(self) -> None:
        """Capacity less than 1 or exceeding 5000 must raise ValidationError."""
        today = date.today()
        data_zero = {
            "event_name": "Zero Cap Event",
            "description": "Desc",
            "category": EventCategory.SPORTS.value,
            "event_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "start_time": "09:00",
            "end_time": "11:00",
            "venue": "Ground",
            "organizer": "Sports",
            "max_capacity": 0,                   # Invalid capacity
            "registration_deadline": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
        }
        with self.assertRaises(ValidationError):
            self.service.create_event(data_zero)

        data_huge = data_zero.copy()
        data_huge["max_capacity"] = 99999        # Exceeds max
        with self.assertRaises(ValidationError):
            self.service.create_event(data_huge)


if __name__ == "__main__":
    unittest.main()
