"""
utils/constants.py
------------------
Domain enumerations and constant collections for Campus Event Management & Feedback Analyzer.
Import from here; never define domain strings inline elsewhere.
"""

from enum import Enum


# ---------------------------------------------------------------------------
# Event enumerations
# ---------------------------------------------------------------------------

class EventCategory(str, Enum):
    TECHNICAL = "Technical"
    CULTURAL = "Cultural"
    SPORTS = "Sports"
    WORKSHOP = "Workshop"
    SEMINAR = "Seminar"
    COMPETITION = "Competition"
    HACKATHON = "Hackathon"
    CLUB_ACTIVITY = "Club Activity"
    OTHER = "Other"


class EventStatus(str, Enum):
    DRAFT = "Draft"
    REGISTRATION_OPEN = "Registration Open"
    FULL = "Full"
    REGISTRATION_CLOSED = "Registration Closed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


# ---------------------------------------------------------------------------
# Registration enumerations
# ---------------------------------------------------------------------------

class RegistrationStatus(str, Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    ATTENDED = "Attended"


# ---------------------------------------------------------------------------
# Feedback / Rating labels
# ---------------------------------------------------------------------------

RATING_LABELS: dict[int, str] = {
    1: "Very Poor",
    2: "Poor",
    3: "Average",
    4: "Good",
    5: "Excellent",
}

# ---------------------------------------------------------------------------
# Student / Academic enumerations
# ---------------------------------------------------------------------------

class Department(str, Enum):
    COMPUTER_SCIENCE = "Computer Science"
    INFORMATION_TECHNOLOGY = "Information Technology"
    MCA = "MCA"
    BCA = "BCA"
    ELECTRONICS = "Electronics"
    MANAGEMENT = "Management"
    OTHER = "Other"


class Course(str, Enum):
    MCA = "MCA"
    BCA = "BCA"
    BTECH_CS = "B.Tech CS"
    BTECH_IT = "B.Tech IT"
    BTECH_ECE = "B.Tech ECE"
    MBA = "MBA"
    OTHER = "Other"


SEMESTERS: list[int] = [1, 2, 3, 4, 5, 6, 7, 8]

ACADEMIC_YEARS: list[str] = [
    "2023-24",
    "2024-25",
    "2025-26",
    "2026-27",
]

# ---------------------------------------------------------------------------
# User roles
# ---------------------------------------------------------------------------

class UserRole(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"


# ---------------------------------------------------------------------------
# Helper lists (for Streamlit select boxes)
# ---------------------------------------------------------------------------

EVENT_CATEGORIES: list[str] = [e.value for e in EventCategory]
EVENT_STATUSES: list[str] = [e.value for e in EventStatus]
DEPARTMENTS: list[str] = [d.value for d in Department]
COURSES: list[str] = [c.value for c in Course]
REGISTRATION_STATUSES: list[str] = [r.value for r in RegistrationStatus]
