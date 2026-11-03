"""
utils/helpers.py
----------------
General-purpose utility functions used across Campus Event Management & Feedback Analyzer.
No business logic here — pure helper utilities.
"""

import uuid
import hashlib
import re
from datetime import datetime, date
from typing import Optional

import config


# ---------------------------------------------------------------------------
# ID generators
# ---------------------------------------------------------------------------

def generate_event_id() -> str:
    """Generate a unique Event ID like EVT-A1B2C3."""
    suffix = uuid.uuid4().hex[:6].upper()
    return f"{config.EVENT_ID_PREFIX}-{suffix}"


def generate_student_id(sequence: int) -> str:
    """Generate a sequential Student ID like STU001."""
    return f"{config.STUDENT_ID_PREFIX}{sequence:03d}"


def generate_registration_id() -> str:
    """Generate a unique Registration ID like REG-X1Y2Z3."""
    suffix = uuid.uuid4().hex[:6].upper()
    return f"{config.REGISTRATION_ID_PREFIX}-{suffix}"


def generate_feedback_id() -> str:
    """Generate a unique Feedback ID like FBK-P9Q8R7."""
    suffix = uuid.uuid4().hex[:6].upper()
    return f"{config.FEEDBACK_ID_PREFIX}-{suffix}"


# ---------------------------------------------------------------------------
# Password utilities
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    """Return a SHA-256 hex digest of the plaintext password."""
    return hashlib.sha256(plain.strip().encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if the plaintext matches the stored hash."""
    return hash_password(plain) == hashed


# ---------------------------------------------------------------------------
# Date / time helpers
# ---------------------------------------------------------------------------

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"


def today_str() -> str:
    """Return today's date as YYYY-MM-DD string."""
    return date.today().strftime(DATE_FORMAT)


def now_str() -> str:
    """Return current datetime as YYYY-MM-DD HH:MM string."""
    return datetime.now().strftime(DATETIME_FORMAT)


def parse_date(date_str: str) -> Optional[date]:
    """Parse a YYYY-MM-DD string into a date object; return None on failure."""
    try:
        return datetime.strptime(date_str.strip(), DATE_FORMAT).date()
    except (ValueError, AttributeError):
        return None


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse a YYYY-MM-DD HH:MM string into a datetime object."""
    try:
        return datetime.strptime(dt_str.strip(), DATETIME_FORMAT)
    except (ValueError, AttributeError):
        return None


def is_past_date(date_str: str) -> bool:
    """Return True if the given date string is in the past."""
    d = parse_date(date_str)
    return d is not None and d < date.today()


def is_future_date(date_str: str) -> bool:
    """Return True if the given date string is strictly in the future."""
    d = parse_date(date_str)
    return d is not None and d > date.today()


def format_date_display(date_str: str) -> str:
    """Convert YYYY-MM-DD to a human-readable form like '27 Sep 2026'."""
    d = parse_date(date_str)
    if d:
        return d.strftime("%d %b %Y")
    return date_str


def days_until(date_str: str) -> Optional[int]:
    """Return number of days from today until the given date (negative = past)."""
    d = parse_date(date_str)
    if d:
        return (d - date.today()).days
    return None


# ---------------------------------------------------------------------------
# String helpers
# ---------------------------------------------------------------------------

def truncate(text: str, max_len: int = 60) -> str:
    """Truncate long text with an ellipsis."""
    if not text:
        return ""
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def normalize_str(value: str) -> str:
    """Strip whitespace and lowercase a string."""
    return value.strip().lower() if value else ""


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_percentage(numerator: float, denominator: float) -> str:
    """Return a percentage string like '72.5%'; returns '0.0%' on zero denom."""
    if not denominator:
        return "0.0%"
    return f"{(numerator / denominator * 100):.1f}%"


def format_score(score: float) -> str:
    """Format an event performance score to 1 decimal place."""
    return f"{score:.1f} / 100"


# ---------------------------------------------------------------------------
# Report filename helper
# ---------------------------------------------------------------------------

def report_filename(prefix: str, extension: str = "txt") -> str:
    """Generate a timestamped report filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"
