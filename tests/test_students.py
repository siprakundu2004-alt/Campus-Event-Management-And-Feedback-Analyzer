"""
tests/test_students.py
----------------------
Unit tests for Student profile management and validations:
  - Create valid student
  - Prevent duplicate student ID
  - Prevent duplicate email address
  - Reject invalid email formats
"""

import unittest
import tempfile
from pathlib import Path

from models.student import Student
from repositories.student_repository import StudentRepository
from services.student_service import StudentService
from utils.constants import Department, Course
from utils.exceptions import ValidationError, DuplicateStudentError


class TestStudentManagement(unittest.TestCase):
    """Test suite for student entity and validation rules."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.stu_path = Path(self.temp_dir.name) / "test_students.csv"
        self.stu_repo = StudentRepository(self.stu_path)
        self.service = StudentService(student_repo=self.stu_repo)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_valid_student(self) -> None:
        """A valid student profile should be registered and hashed."""
        data = {
            "student_id": "STU101",
            "name": "Kunal Sen",
            "email": "kunal.sen@nit.edu",
            "phone": "9876543210",
            "department": Department.MCA.value,
            "course": Course.MCA.value,
            "semester": 4,
            "academic_year": "2024-25",
        }
        student = self.service.add_student(data, plain_password="SecretPass123")
        self.assertEqual(student.student_id, "STU101")
        self.assertEqual(student.email, "kunal.sen@nit.edu")
        self.assertNotEqual(student.password, "SecretPass123")  # Must be hashed

    def test_duplicate_student_id(self) -> None:
        """Attempting to register with an existing Student ID must raise DuplicateStudentError."""
        data = {
            "student_id": "STU102",
            "name": "First Student",
            "email": "first@nit.edu",
            "phone": "9876543210",
            "department": Department.BCA.value,
            "course": Course.BCA.value,
            "semester": 2,
            "academic_year": "2024-25",
        }
        self.service.add_student(data)

        # Attempt same ID
        data_dup = data.copy()
        data_dup["email"] = "other.email@nit.edu"
        with self.assertRaises(DuplicateStudentError):
            self.service.add_student(data_dup)

    def test_duplicate_email(self) -> None:
        """Attempting to register with an existing Email must raise DuplicateStudentError."""
        data = {
            "student_id": "STU103",
            "name": "Original Student",
            "email": "shared@nit.edu",
            "phone": "9876543210",
            "department": Department.COMPUTER_SCIENCE.value,
            "course": Course.BTECH_CS.value,
            "semester": 6,
            "academic_year": "2023-24",
        }
        self.service.add_student(data)

        data2 = {
            "student_id": "STU104",
            "name": "Second Student",
            "email": "shared@nit.edu",             # Duplicate email
            "phone": "9876543211",
            "department": Department.INFORMATION_TECHNOLOGY.value,
            "course": Course.BTECH_IT.value,
            "semester": 2,
            "academic_year": "2024-25",
        }
        with self.assertRaises(DuplicateStudentError):
            self.service.add_student(data2)

    def test_invalid_email_format(self) -> None:
        """Invalid email strings must raise ValidationError."""
        data = {
            "student_id": "STU105",
            "name": "Bad Email",
            "email": "not-a-valid-email",
            "phone": "9876543210",
            "department": Department.MANAGEMENT.value,
            "course": Course.MBA.value,
            "semester": 2,
            "academic_year": "2024-25",
        }
        with self.assertRaises(ValidationError):
            self.service.add_student(data)


if __name__ == "__main__":
    unittest.main()
