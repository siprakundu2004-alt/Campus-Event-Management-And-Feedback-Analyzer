"""
repositories/__init__.py
"""
from repositories.event_repository import EventRepository
from repositories.student_repository import StudentRepository
from repositories.registration_repository import RegistrationRepository
from repositories.feedback_repository import FeedbackRepository

__all__ = [
    "EventRepository",
    "StudentRepository",
    "RegistrationRepository",
    "FeedbackRepository",
]
