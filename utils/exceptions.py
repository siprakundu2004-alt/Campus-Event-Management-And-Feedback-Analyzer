"""
utils/exceptions.py
-------------------
Custom exception hierarchy for Campus Event Management & Feedback Analyzer.
All domain errors raise a subclass of CEMFAError so the UI
can catch them in a single broad handler when needed.
"""


class CEMFAError(Exception):
    """Base exception for all Campus Event Management & Feedback Analyzer domain errors."""

    def __init__(self, message: str, details: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}\n{self.details}"
        return self.message


# ---------------------------------------------------------------------------
# Entity not-found errors
# ---------------------------------------------------------------------------

class EventNotFoundError(CEMFAError):
    """Raised when an event with the given ID does not exist."""


class StudentNotFoundError(CEMFAError):
    """Raised when a student with the given ID does not exist."""


class RegistrationNotFoundError(CEMFAError):
    """Raised when a registration record does not exist."""


class FeedbackNotFoundError(CEMFAError):
    """Raised when a feedback record does not exist."""


# ---------------------------------------------------------------------------
# Duplicate record errors
# ---------------------------------------------------------------------------

class DuplicateEventError(CEMFAError):
    """Raised when attempting to create an event with an existing ID."""


class DuplicateStudentError(CEMFAError):
    """Raised when attempting to create a student with an existing ID."""


class DuplicateRegistrationError(CEMFAError):
    """Raised when a student tries to register for an event they are already registered for."""


class DuplicateFeedbackError(CEMFAError):
    """Raised when a student submits feedback for an event more than once."""


# ---------------------------------------------------------------------------
# Registration business-rule errors
# ---------------------------------------------------------------------------

class EventFullError(CEMFAError):
    """Raised when event capacity has been reached."""


class RegistrationClosedError(CEMFAError):
    """Raised when registration deadline has passed or event status disallows registration."""


class EventCancelledError(CEMFAError):
    """Raised when attempting to register for a cancelled event."""


# ---------------------------------------------------------------------------
# Feedback business-rule errors
# ---------------------------------------------------------------------------

class InvalidFeedbackError(CEMFAError):
    """Raised when feedback violates business rules (rating out of range, not registered, etc.)."""


class FeedbackNotAllowedError(CEMFAError):
    """Raised when a student who is not registered tries to submit feedback."""


class EventNotCompletedError(CEMFAError):
    """Raised when feedback is submitted before the event is marked as completed."""


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------

class ValidationError(CEMFAError):
    """Raised when input data fails validation checks."""


# ---------------------------------------------------------------------------
# Authentication errors
# ---------------------------------------------------------------------------

class AuthenticationError(CEMFAError):
    """Raised when login credentials are incorrect."""


class AuthorizationError(CEMFAError):
    """Raised when a user tries to perform an action they are not authorized for."""


# ---------------------------------------------------------------------------
# Storage errors
# ---------------------------------------------------------------------------

class DataStorageError(CEMFAError):
    """Raised when a file read/write operation fails."""
