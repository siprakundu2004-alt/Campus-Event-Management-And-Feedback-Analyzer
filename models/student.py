"""
models/student.py
-----------------
Student domain model for Campus Event Management & Feedback Analyzer.
"""

from dataclasses import dataclass, field, asdict

from utils.helpers import today_str, hash_password


@dataclass
class Student:
    """Represents a registered student."""

    student_id: str
    name: str
    email: str
    phone: str
    department: str
    course: str
    semester: int
    academic_year: str
    password: str                       # SHA-256 hashed
    created_date: str = field(default_factory=today_str)

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        student_id: str,
        name: str,
        email: str,
        phone: str,
        department: str,
        course: str,
        semester: int,
        academic_year: str,
        plain_password: str,
    ) -> "Student":
        """Create a new Student, hashing the password before storage."""
        return cls(
            student_id=student_id.strip().upper(),
            name=name.strip(),
            email=email.strip().lower(),
            phone=phone.strip(),
            department=department,
            course=course,
            semester=int(semester),
            academic_year=academic_year,
            password=hash_password(plain_password),
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        return cls(
            student_id=str(data["student_id"]),
            name=str(data["name"]),
            email=str(data["email"]),
            phone=str(data["phone"]),
            department=str(data["department"]),
            course=str(data["course"]),
            semester=int(data["semester"]),
            academic_year=str(data["academic_year"]),
            password=str(data["password"]),
            created_date=str(data.get("created_date", today_str())),
        )

    # ------------------------------------------------------------------
    # Presentation helper
    # ------------------------------------------------------------------

    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.student_id})"

    def __repr__(self) -> str:
        return (
            f"Student(id={self.student_id!r}, name={self.name!r}, "
            f"dept={self.department!r})"
        )
