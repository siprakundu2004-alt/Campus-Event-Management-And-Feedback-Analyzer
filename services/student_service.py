"""
services/student_service.py
---------------------------
Business logic layer for Student operations.
Handles student registration, updates, profile queries, and participation metrics.
"""

from typing import Optional

from models.student import Student
from repositories.student_repository import StudentRepository
from repositories.registration_repository import RegistrationRepository
from repositories.feedback_repository import FeedbackRepository
from utils.exceptions import (
    StudentNotFoundError,
    DuplicateStudentError,
    ValidationError,
)
from utils.validators import validate_student_form, validate_student_id, validate_email, validate_password
from utils.helpers import hash_password, generate_student_id


class StudentService:
    """Provides high-level student profile and management operations."""

    def __init__(
        self,
        student_repo: Optional[StudentRepository] = None,
        registration_repo: Optional[RegistrationRepository] = None,
        feedback_repo: Optional[FeedbackRepository] = None,
    ) -> None:
        self.student_repo = student_repo or StudentRepository()
        self.registration_repo = registration_repo or RegistrationRepository()
        self.feedback_repo = feedback_repo or FeedbackRepository()

    # ------------------------------------------------------------------
    # Create / Register Student
    # ------------------------------------------------------------------

    def add_student(self, student_data: dict, plain_password: Optional[str] = None) -> Student:
        """
        Validate and create a new student record.
        Raises ValidationError, DuplicateStudentError.
        """
        errors = validate_student_form(student_data)

        # Check student_id format or auto-generate
        student_id = student_data.get("student_id", "").strip().upper()
        if not student_id:
            seq = self.student_repo.get_next_sequence()
            student_id = generate_student_id(seq)
        else:
            ok, msg = validate_student_id(student_id)
            if not ok:
                errors.append(msg)

        # Check duplicates
        if self.student_repo.exists(student_id):
            raise DuplicateStudentError(f"Student ID '{student_id}' is already registered.")

        email = student_data.get("email", "").strip().lower()
        if self.student_repo.email_exists(email):
            raise DuplicateStudentError(f"Email address '{email}' is already registered.")

        # Default password if none provided
        password = plain_password or f"{student_id.lower()}@123"
        ok_pwd, msg_pwd = validate_password(password)
        if not ok_pwd:
            errors.append(msg_pwd)

        if errors:
            raise ValidationError("Student validation failed.", details="\n".join(errors))

        student = Student.create(
            student_id=student_id,
            name=student_data["name"],
            email=email,
            phone=student_data["phone"],
            department=student_data["department"],
            course=student_data["course"],
            semester=int(student_data["semester"]),
            academic_year=student_data["academic_year"],
            plain_password=password,
        )

        self.student_repo.save(student)
        return student

    # ------------------------------------------------------------------
    # Update Student
    # ------------------------------------------------------------------

    def update_student(self, student_id: str, student_data: dict) -> Student:
        """
        Update an existing student profile.
        Raises StudentNotFoundError, ValidationError, or DuplicateStudentError.
        """
        existing = self.student_repo.get_by_id(student_id)
        if not existing:
            raise StudentNotFoundError(f"Student '{student_id}' not found.")

        errors = validate_student_form(student_data)
        email = student_data.get("email", "").strip().lower()

        # Check if email changed and taken by another student
        if email != existing.email.lower() and self.student_repo.email_exists(email, exclude_id=student_id):
            raise DuplicateStudentError(f"Email '{email}' is already used by another student.")

        if errors:
            raise ValidationError("Student update validation failed.", details="\n".join(errors))

        existing.name = student_data["name"].strip()
        existing.email = email
        existing.phone = student_data["phone"].strip()
        existing.department = student_data["department"]
        existing.course = student_data["course"]
        existing.semester = int(student_data["semester"])
        existing.academic_year = student_data["academic_year"]

        # Optional password update
        new_pwd = student_data.get("new_password")
        if new_pwd and new_pwd.strip():
            ok_pwd, msg_pwd = validate_password(new_pwd)
            if not ok_pwd:
                raise ValidationError(msg_pwd)
            existing.password = hash_password(new_pwd.strip())

        self.student_repo.save(existing)
        return existing

    # ------------------------------------------------------------------
    # Queries & Participation
    # ------------------------------------------------------------------

    def get_student(self, student_id: str) -> Student:
        """Get student by ID or raise StudentNotFoundError."""
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise StudentNotFoundError(f"Student with ID '{student_id}' not found.")
        return student

    def get_student_by_email(self, email: str) -> Optional[Student]:
        return self.student_repo.get_by_email(email)

    def list_all_students(self) -> list[Student]:
        return self.student_repo.get_all()

    def search_students(
        self,
        query: Optional[str] = None,
        department: Optional[str] = None,
        course: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> list[Student]:
        """Multi-attribute search and filter across students."""
        students = self.student_repo.get_all()

        if department and department != "All":
            students = [s for s in students if s.department.lower() == department.lower()]
        if course and course != "All":
            students = [s for s in students if s.course.lower() == course.lower()]
        if semester and semester != "All":
            try:
                sem_val = int(semester)
                students = [s for s in students if s.semester == sem_val]
            except ValueError:
                pass

        if query and query.strip():
            q = query.strip().lower()
            students = [
                s for s in students
                if q in s.name.lower()
                or q in s.email.lower()
                or q in s.student_id.lower()
                or q in s.department.lower()
            ]

        return students

    def get_student_stats(self, student_id: str) -> dict:
        """Return participation metrics for a student."""
        student = self.get_student(student_id)
        registrations = self.registration_repo.get_by_student(student_id)
        active_regs = [r for r in registrations if r.is_active]
        feedbacks = self.feedback_repo.get_by_student(student_id)

        return {
            "student_id": student.student_id,
            "name": student.name,
            "email": student.email,
            "department": student.department,
            "course": student.course,
            "total_registrations": len(registrations),
            "active_registrations": len(active_regs),
            "feedbacks_submitted": len(feedbacks),
        }
