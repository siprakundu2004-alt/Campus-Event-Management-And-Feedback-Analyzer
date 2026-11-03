"""
services/auth_service.py
------------------------
Session-based authentication service for Campus Event Management & Feedback Analyzer.
Supports:
  - Admin login via secure credentials
  - Student login via Student ID + hashed password
  - Role management (Admin, Student)
  - Password hashing & verification
"""

from dataclasses import dataclass
from typing import Optional

from models.student import Student
from repositories.student_repository import StudentRepository
from utils.constants import UserRole
from utils.exceptions import AuthenticationError, StudentNotFoundError
from utils.helpers import verify_password, hash_password
import config


@dataclass
class UserSession:
    """Represents an authenticated user in the current session."""
    user_id: str
    username: str
    display_name: str
    email: str
    role: str                       # "admin" or "student"
    department: Optional[str] = None
    course: Optional[str] = None

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN.value

    @property
    def is_student(self) -> bool:
        return self.role == UserRole.STUDENT.value


class AuthService:
    """Manages credentials and authentication checks for all roles."""

    def __init__(self, student_repo: Optional[StudentRepository] = None) -> None:
        self.student_repo = student_repo or StudentRepository()

    def authenticate_admin(self, username: str, password: str) -> UserSession:
        """
        Authenticate an admin user.
        Raises AuthenticationError if credentials do not match.
        """
        clean_user = username.strip()
        if clean_user != config.ADMIN_USERNAME or password != config.ADMIN_PASSWORD:
            raise AuthenticationError("Invalid admin username or password.")

        return UserSession(
            user_id="ADMIN",
            username=config.ADMIN_USERNAME,
            display_name=config.ADMIN_DISPLAY_NAME,
            email="admin@campusconnect.edu",
            role=UserRole.ADMIN.value,
        )

    def authenticate_student(self, student_id: str, password: str) -> UserSession:
        """
        Authenticate a student using Student ID and password.
        Raises AuthenticationError on invalid ID or incorrect password.
        """
        clean_sid = student_id.strip().upper()
        student = self.student_repo.get_by_id(clean_sid)

        if not student:
            raise AuthenticationError(f"No student registered with ID '{clean_sid}'.")

        if not verify_password(password, student.password):
            raise AuthenticationError("Incorrect password. Please verify and try again.")

        return UserSession(
            user_id=student.student_id,
            username=student.student_id,
            display_name=student.name,
            email=student.email,
            role=UserRole.STUDENT.value,
            department=student.department,
            course=student.course,
        )

    def change_student_password(self, student_id: str, old_pwd: str, new_pwd: str) -> bool:
        """
        Verify old password and update to new password.
        """
        clean_sid = student_id.strip().upper()
        student = self.student_repo.get_by_id(clean_sid)
        if not student:
            raise StudentNotFoundError(f"Student '{clean_sid}' not found.")

        if not verify_password(old_pwd, student.password):
            raise AuthenticationError("Current password is incorrect.")

        if len(new_pwd) < 6:
            raise AuthenticationError("New password must be at least 6 characters.")

        student.password = hash_password(new_pwd)
        self.student_repo.save(student)
        return True
