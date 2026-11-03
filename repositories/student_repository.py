"""
repositories/student_repository.py
------------------------------------
Concrete CSV repository for Student records.
"""

from pathlib import Path
from typing import Optional

from models.student import Student
from repositories.base_repository import BaseRepository
import config


class StudentRepository(BaseRepository[Student]):
    """Manages persistence for Student domain objects."""

    _id_column: str = "student_id"

    def __init__(self, filepath: Path = config.STUDENTS_CSV) -> None:
        super().__init__(filepath)

    # ------------------------------------------------------------------
    # BaseRepository interface
    # ------------------------------------------------------------------

    def _get_columns(self) -> list[str]:
        return [
            "student_id", "name", "email", "phone",
            "department", "course", "semester", "academic_year",
            "password", "created_date",
        ]

    def _to_dict(self, obj: Student) -> dict:
        return obj.to_dict()

    def _from_dict(self, row: dict) -> Student:
        return Student.from_dict(row)

    def _get_id(self, obj: Student) -> str:
        return obj.student_id

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_email(self, email: str) -> Optional[Student]:
        """Return the student matching the given email, or None."""
        results = self.filter_by(email=email.strip().lower())
        return results[0] if results else None

    def get_by_department(self, department: str) -> list[Student]:
        return self.filter_by(department=department)

    def get_by_course(self, course: str) -> list[Student]:
        return self.filter_by(course=course)

    def email_exists(self, email: str, exclude_id: str = "") -> bool:
        """
        Return True if the given email is already taken.
        Pass `exclude_id` to allow the current student to keep their email on update.
        """
        student = self.get_by_email(email)
        if student is None:
            return False
        if exclude_id and student.student_id.upper() == exclude_id.upper():
            return False
        return True

    def search_students(self, query: str) -> list[Student]:
        """Search name, email, or student_id for the given query."""
        df = self.get_dataframe()
        if df.empty or not query:
            return self.get_all()
        mask = (
            df["name"].str.contains(query, case=False, na=False)
            | df["email"].str.contains(query, case=False, na=False)
            | df["student_id"].str.contains(query, case=False, na=False)
        )
        return [Student.from_dict(row) for row in df[mask].to_dict(orient="records")]

    def get_next_sequence(self) -> int:
        """Return the next available numeric sequence for ID generation."""
        df = self.get_dataframe()
        if df.empty:
            return 1
        try:
            nums = df["student_id"].str.extract(r"(\d+)$")[0].dropna().astype(int)
            return int(nums.max()) + 1
        except Exception:
            return self.count() + 1
