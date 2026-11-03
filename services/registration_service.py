"""
services/registration_service.py
--------------------------------
Core Smart Registration System for Campus Event Management & Feedback Analyzer.
Enforces all 10 registration rules:
  1. Validate Student ID
  2. Validate Event ID
  3. Check event status
  4. Check registration deadline
  5. Check event capacity
  6. Check duplicate registration
  7. Generate unique Registration ID
  8. Store registration record
  9. Update event status (e.g. mark FULL if cap reached)
  10. Return confirmation receipt details
"""

from typing import Optional
from datetime import date

from models.registration import Registration
from models.event import Event
from models.student import Student
from repositories.event_repository import EventRepository
from repositories.student_repository import StudentRepository
from repositories.registration_repository import RegistrationRepository
from utils.constants import EventStatus, RegistrationStatus
from utils.exceptions import (
    StudentNotFoundError,
    EventNotFoundError,
    EventFullError,
    DuplicateRegistrationError,
    RegistrationClosedError,
    EventCancelledError,
    ValidationError,
)
from utils.validators import validate_student_id, validate_event_id
from utils.helpers import parse_date


class RegistrationService:
    """Orchestrates event registrations with complete validation and business constraints."""

    def __init__(
        self,
        registration_repo: Optional[RegistrationRepository] = None,
        event_repo: Optional[EventRepository] = None,
        student_repo: Optional[StudentRepository] = None,
    ) -> None:
        self.registration_repo = registration_repo or RegistrationRepository()
        self.event_repo = event_repo or EventRepository()
        self.student_repo = student_repo or StudentRepository()

    # ------------------------------------------------------------------
    # Smart Registration
    # ------------------------------------------------------------------

    def register_student(self, student_id: str, event_id: str) -> dict:
        """
        Executes the 10-step smart registration process.
        Returns a receipt dictionary on success.
        Raises domain-specific exceptions with user-friendly explanations.
        """
        clean_sid = student_id.strip().upper()
        clean_eid = event_id.strip().upper()

        # Step 1: Validate Student ID format & existence
        ok_sid, msg_sid = validate_student_id(clean_sid)
        if not ok_sid:
            raise ValidationError(f"Invalid Student ID format: {msg_sid}")
        student = self.student_repo.get_by_id(clean_sid)
        if not student:
            raise StudentNotFoundError(f"Student with ID '{clean_sid}' does not exist in the system.")

        # Step 2: Validate Event ID format & existence
        ok_eid, msg_eid = validate_event_id(clean_eid)
        if not ok_eid:
            raise ValidationError(f"Invalid Event ID format: {msg_eid}")
        event = self.event_repo.get_by_id(clean_eid)
        if not event:
            raise EventNotFoundError(f"Event with ID '{clean_eid}' does not exist in the system.")

        # Step 3: Check Event Status
        if event.status == EventStatus.CANCELLED.value:
            raise EventCancelledError(f"Registration failed: Event '{event.event_name}' has been cancelled.")
        if event.status == EventStatus.COMPLETED.value:
            raise RegistrationClosedError(f"Registration failed: Event '{event.event_name}' has already taken place.")
        if event.status == EventStatus.DRAFT.value:
            raise RegistrationClosedError(f"Registration failed: Event '{event.event_name}' is not yet open for registration.")
        if event.status == EventStatus.REGISTRATION_CLOSED.value:
            raise RegistrationClosedError(f"Registration failed: Registration for '{event.event_name}' is currently closed.")

        # Step 4: Check Registration Deadline
        deadline = parse_date(event.registration_deadline)
        today = date.today()
        if deadline and deadline < today:
            event.status = EventStatus.REGISTRATION_CLOSED.value
            self.event_repo.save(event)
            raise RegistrationClosedError(
                f"Registration failed: The deadline was {event.registration_deadline}. Registration is now closed."
            )

        # Step 5: Check Event Capacity
        current_active = self.registration_repo.count_active_for_event(clean_eid)
        if current_active >= event.max_capacity:
            event.status = EventStatus.FULL.value
            self.event_repo.save(event)
            raise EventFullError(
                f"Registration failed: Event '{event.event_name}' has reached its maximum capacity "
                f"({event.max_capacity}/{event.max_capacity}). Available seats: 0."
            )

        # Step 6: Check Duplicate Registration
        if self.registration_repo.is_registered(clean_sid, clean_eid):
            raise DuplicateRegistrationError(
                f"Duplicate registration: Student '{student.name}' ({clean_sid}) is already registered "
                f"for '{event.event_name}'."
            )

        # Step 7 & 8: Create and Store Registration Record
        registration = Registration.create(
            student_id=clean_sid,
            event_id=clean_eid,
            status=RegistrationStatus.CONFIRMED.value,
        )
        self.registration_repo.save(registration)

        # Step 9: Update Event Status if capacity is now full
        new_active = current_active + 1
        if new_active >= event.max_capacity:
            event.status = EventStatus.FULL.value
            self.event_repo.save(event)

        # Step 10: Confirmation Receipt
        available_seats = max(0, event.max_capacity - new_active)
        return {
            "registration_id": registration.registration_id,
            "student_id": student.student_id,
            "student_name": student.name,
            "student_email": student.email,
            "event_id": event.event_id,
            "event_name": event.event_name,
            "event_date": event.event_date,
            "venue": event.venue,
            "registration_date": registration.registration_date,
            "status": registration.status,
            "available_seats": available_seats,
            "message": f"Successfully registered for '{event.event_name}'!",
        }

    # ------------------------------------------------------------------
    # Cancellation & Attendance
    # ------------------------------------------------------------------

    def cancel_registration(self, student_id: str, event_id: str) -> bool:
        """
        Cancel a student's active registration and update event availability.
        """
        clean_sid = student_id.strip().upper()
        clean_eid = event_id.strip().upper()

        if not self.registration_repo.is_registered(clean_sid, clean_eid):
            return False

        cancelled = self.registration_repo.cancel_registration(clean_sid, clean_eid)
        if cancelled:
            # Reopen event if it was FULL
            event = self.event_repo.get_by_id(clean_eid)
            if event and event.status == EventStatus.FULL.value:
                deadline = parse_date(event.registration_deadline)
                if not (deadline and deadline < date.today()):
                    event.status = EventStatus.REGISTRATION_OPEN.value
                    self.event_repo.save(event)

        return cancelled

    def mark_attendance(self, registration_id: str) -> bool:
        """Mark registration as attended."""
        return self.registration_repo.mark_attended(registration_id)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_student_registrations(self, student_id: str) -> list[dict]:
        """Return enriched list of registrations for a given student."""
        clean_sid = student_id.strip().upper()
        registrations = self.registration_repo.get_by_student(clean_sid)
        enriched = []
        for reg in registrations:
            evt = self.event_repo.get_by_id(reg.event_id)
            enriched.append({
                "registration_id": reg.registration_id,
                "event_id": reg.event_id,
                "event_name": evt.event_name if evt else "Unknown Event",
                "category": evt.category if evt else "-",
                "event_date": evt.event_date if evt else "-",
                "venue": evt.venue if evt else "-",
                "registration_date": reg.registration_date,
                "status": reg.status,
                "event_status": evt.status if evt else "-",
            })
        return enriched

    def get_event_registrations(self, event_id: str) -> list[dict]:
        """Return enriched list of registrations for a given event."""
        clean_eid = event_id.strip().upper()
        registrations = self.registration_repo.get_by_event(clean_eid)
        enriched = []
        for reg in registrations:
            stu = self.student_repo.get_by_id(reg.student_id)
            enriched.append({
                "registration_id": reg.registration_id,
                "student_id": reg.student_id,
                "student_name": stu.name if stu else "Unknown Student",
                "department": stu.department if stu else "-",
                "course": stu.course if stu else "-",
                "registration_date": reg.registration_date,
                "status": reg.status,
            })
        return enriched

    def list_all_registrations(self) -> list[dict]:
        """Return enriched list of all registrations."""
        regs = self.registration_repo.get_all()
        events = {e.event_id: e for e in self.event_repo.get_all()}
        students = {s.student_id: s for s in self.student_repo.get_all()}

        enriched = []
        for reg in regs:
            evt = events.get(reg.event_id)
            stu = students.get(reg.student_id)
            enriched.append({
                "registration_id": reg.registration_id,
                "student_id": reg.student_id,
                "student_name": stu.name if stu else reg.student_id,
                "department": stu.department if stu else "-",
                "course": stu.course if stu else "-",
                "event_id": reg.event_id,
                "event_name": evt.event_name if evt else reg.event_id,
                "category": evt.category if evt else "-",
                "event_date": evt.event_date if evt else "-",
                "registration_date": reg.registration_date,
                "status": reg.status,
            })
        return enriched
