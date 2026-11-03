"""
utils/validators.py
-------------------
Centralised input validation for Campus Event Management & Feedback Analyzer.
All validation functions return a (bool, str) tuple:
  - (True, "")           → valid
  - (False, "reason")    → invalid, human-readable reason
"""

import re
from datetime import date, datetime
from typing import Optional

import config


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------
ValidationResult = tuple[bool, str]


# ---------------------------------------------------------------------------
# ID validators
# ---------------------------------------------------------------------------

def validate_student_id(student_id: str) -> ValidationResult:
    """Student ID must match STU followed by 3–6 digits."""
    if not student_id or not student_id.strip():
        return False, "Student ID is required."
    pattern = rf"^{config.STUDENT_ID_PREFIX}\d{{3,6}}$"
    if not re.match(pattern, student_id.strip().upper()):
        return False, (
            f"Student ID must start with '{config.STUDENT_ID_PREFIX}' "
            "followed by 3–6 digits (e.g., STU001)."
        )
    return True, ""


def validate_event_id(event_id: str) -> ValidationResult:
    """Event ID must match EVT- followed by 6 alphanumeric chars."""
    if not event_id or not event_id.strip():
        return False, "Event ID is required."
    pattern = rf"^{config.EVENT_ID_PREFIX}-[A-Z0-9]{{6}}$"
    if not re.match(pattern, event_id.strip().upper()):
        return False, (
            f"Event ID must start with '{config.EVENT_ID_PREFIX}-' "
            "followed by 6 alphanumeric characters (e.g., EVT-A1B2C3)."
        )
    return True, ""


# ---------------------------------------------------------------------------
# Personal information validators
# ---------------------------------------------------------------------------

def validate_email(email: str) -> ValidationResult:
    """Validate a standard email address format."""
    if not email or not email.strip():
        return False, "Email address is required."
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email.strip()):
        return False, "Please enter a valid email address (e.g., name@domain.com)."
    return True, ""


def validate_phone(phone: str) -> ValidationResult:
    """Validate a 10-digit Indian mobile number (optional leading +91 or 0)."""
    if not phone or not phone.strip():
        return False, "Phone number is required."
    cleaned = re.sub(r"[\s\-()]", "", phone.strip())
    if cleaned.startswith("+91"):
        cleaned = cleaned[3:]
    elif cleaned.startswith("0"):
        cleaned = cleaned[1:]
    if not re.match(r"^[6-9]\d{9}$", cleaned):
        return False, "Phone number must be a valid 10-digit Indian mobile number."
    return True, ""


def validate_name(name: str, field: str = "Name") -> ValidationResult:
    """Validate that a name field is non-empty and reasonable."""
    if not name or not name.strip():
        return False, f"{field} is required."
    if len(name.strip()) < 2:
        return False, f"{field} must be at least 2 characters."
    if len(name.strip()) > 100:
        return False, f"{field} must not exceed 100 characters."
    return True, ""


# ---------------------------------------------------------------------------
# Date / time validators
# ---------------------------------------------------------------------------

def validate_date_format(date_str: str, field: str = "Date") -> ValidationResult:
    """Date must be parseable as YYYY-MM-DD."""
    if not date_str or not date_str.strip():
        return False, f"{field} is required."
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, f"{field} must be in YYYY-MM-DD format."


def validate_future_date(date_str: str, field: str = "Date") -> ValidationResult:
    """Date must be today or in the future."""
    ok, msg = validate_date_format(date_str, field)
    if not ok:
        return ok, msg
    event_date = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    if event_date < date.today():
        return False, f"{field} cannot be in the past."
    return True, ""


def validate_time_format(time_str: str, field: str = "Time") -> ValidationResult:
    """Time must be parseable as HH:MM."""
    if not time_str or not time_str.strip():
        return False, f"{field} is required."
    try:
        datetime.strptime(time_str.strip(), "%H:%M")
        return True, ""
    except ValueError:
        return False, f"{field} must be in HH:MM 24-hour format (e.g., 14:30)."


def validate_time_order(start: str, end: str) -> ValidationResult:
    """End time must be after start time."""
    ok1, m1 = validate_time_format(start, "Start time")
    ok2, m2 = validate_time_format(end, "End time")
    if not ok1:
        return ok1, m1
    if not ok2:
        return ok2, m2
    t1 = datetime.strptime(start.strip(), "%H:%M")
    t2 = datetime.strptime(end.strip(), "%H:%M")
    if t2 <= t1:
        return False, "End time must be after start time."
    return True, ""


def validate_date_order(start: str, end: str,
                        start_field: str = "Start date",
                        end_field: str = "End date") -> ValidationResult:
    """End date must be on or after start date."""
    ok1, m1 = validate_date_format(start, start_field)
    ok2, m2 = validate_date_format(end, end_field)
    if not ok1:
        return ok1, m1
    if not ok2:
        return ok2, m2
    d1 = datetime.strptime(start.strip(), "%Y-%m-%d").date()
    d2 = datetime.strptime(end.strip(), "%Y-%m-%d").date()
    if d2 < d1:
        return False, f"{end_field} must be on or after {start_field}."
    return True, ""


# ---------------------------------------------------------------------------
# Numeric validators
# ---------------------------------------------------------------------------

def validate_capacity(capacity: int) -> ValidationResult:
    """Capacity must be within the configured range."""
    if capacity < config.MIN_CAPACITY:
        return False, f"Capacity must be at least {config.MIN_CAPACITY}."
    if capacity > config.MAX_CAPACITY:
        return False, f"Capacity cannot exceed {config.MAX_CAPACITY}."
    return True, ""


def validate_rating(rating: int) -> ValidationResult:
    """Rating must be an integer between MIN_RATING and MAX_RATING."""
    if not isinstance(rating, int) or rating < config.MIN_RATING or rating > config.MAX_RATING:
        return False, (
            f"Rating must be a whole number between "
            f"{config.MIN_RATING} and {config.MAX_RATING}."
        )
    return True, ""


# ---------------------------------------------------------------------------
# Text validators
# ---------------------------------------------------------------------------

def validate_required(value: str, field: str) -> ValidationResult:
    """A generic required-field check."""
    if not value or not str(value).strip():
        return False, f"{field} is required."
    return True, ""


def validate_password(password: str) -> ValidationResult:
    """Password must be at least 6 characters."""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""


# ---------------------------------------------------------------------------
# Composite event validator
# ---------------------------------------------------------------------------

def validate_event_form(data: dict) -> list[str]:
    """
    Validate all fields of an event creation/update form.
    Returns a list of error messages (empty list = valid).
    """
    errors: list[str] = []

    checks = [
        validate_required(data.get("event_name", ""), "Event name"),
        validate_required(data.get("category", ""), "Category"),
        validate_required(data.get("venue", ""), "Venue"),
        validate_required(data.get("organizer", ""), "Organizer"),
        validate_date_format(data.get("event_date", ""), "Event date"),
        validate_time_format(data.get("start_time", ""), "Start time"),
        validate_time_format(data.get("end_time", ""), "End time"),
        validate_date_format(data.get("registration_deadline", ""), "Registration deadline"),
    ]

    for ok, msg in checks:
        if not ok:
            errors.append(msg)

    # Capacity
    try:
        cap = int(data.get("max_capacity", 0))
        ok, msg = validate_capacity(cap)
        if not ok:
            errors.append(msg)
    except (ValueError, TypeError):
        errors.append("Maximum capacity must be a valid number.")

    # Time order
    if data.get("start_time") and data.get("end_time"):
        ok, msg = validate_time_order(data["start_time"], data["end_time"])
        if not ok:
            errors.append(msg)

    return errors


# ---------------------------------------------------------------------------
# Composite student validator
# ---------------------------------------------------------------------------

def validate_student_form(data: dict) -> list[str]:
    """
    Validate all fields of a student creation/update form.
    Returns a list of error messages.
    """
    errors: list[str] = []

    checks = [
        validate_name(data.get("name", ""), "Name"),
        validate_email(data.get("email", "")),
        validate_phone(data.get("phone", "")),
        validate_required(data.get("department", ""), "Department"),
        validate_required(data.get("course", ""), "Course"),
        validate_required(data.get("academic_year", ""), "Academic year"),
    ]

    for ok, msg in checks:
        if not ok:
            errors.append(msg)

    # Semester
    try:
        sem = int(data.get("semester", 0))
        if sem < 1 or sem > 8:
            errors.append("Semester must be between 1 and 8.")
    except (ValueError, TypeError):
        errors.append("Semester must be a valid number.")

    return errors
