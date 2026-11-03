"""
views/__init__.py
"""
from views.admin.dashboard_view import render_admin_dashboard
from views.admin.events_view import render_admin_events
from views.admin.students_view import render_admin_students
from views.admin.registrations_view import render_admin_registrations
from views.admin.analytics_view import render_admin_analytics
from views.admin.reports_view import render_admin_reports

from views.student.dashboard_view import render_student_dashboard
from views.student.browse_view import render_student_browse
from views.student.my_events_view import render_student_my_events
from views.student.feedback_view import render_student_feedback

__all__ = [
    "render_admin_dashboard",
    "render_admin_events",
    "render_admin_students",
    "render_admin_registrations",
    "render_admin_analytics",
    "render_admin_reports",
    "render_student_dashboard",
    "render_student_browse",
    "render_student_my_events",
    "render_student_feedback",
]
