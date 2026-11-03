"""
config.py
---------
Central configuration for Campus Event Management & Feedback Analyzer.
All environment-specific and tuneable values live here.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Base paths
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data"
REPORTS_DIR: Path = BASE_DIR / "reports" / "generated_reports"
ASSETS_DIR: Path = BASE_DIR / "assets" / "images"
LOGS_DIR: Path = BASE_DIR / "logs"

# Ensure required directories exist
for _dir in (DATA_DIR, REPORTS_DIR, ASSETS_DIR, LOGS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Data file paths
# ---------------------------------------------------------------------------
EVENTS_CSV: Path = DATA_DIR / "events.csv"
STUDENTS_CSV: Path = DATA_DIR / "students.csv"
REGISTRATIONS_CSV: Path = DATA_DIR / "registrations.csv"
FEEDBACK_CSV: Path = DATA_DIR / "feedback.csv"

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
ADMIN_USERNAME: str = "admin"
ADMIN_PASSWORD: str = "Admin@123"          # Change in production
ADMIN_DISPLAY_NAME: str = "System Administrator"

# Default student password = lowercase student ID (e.g., "stu001")
DEFAULT_STUDENT_PASSWORD_FIELD: str = "password"

# ---------------------------------------------------------------------------
# Application metadata
# ---------------------------------------------------------------------------
APP_NAME: str = "Campus Event Management & Feedback Analyzer"
APP_TAGLINE: str = "Manage Events. Connect Students. Analyze Participation."
APP_VERSION: str = "1.0.0"
UNIVERSITY_NAME: str = "BRAINWARE UNIVERSITY"

# ---------------------------------------------------------------------------
# Event Performance Score weights  (must sum to 1.0)
# ---------------------------------------------------------------------------
SCORE_WEIGHT_CAPACITY: float = 0.40    # capacity utilization
SCORE_WEIGHT_RATING: float = 0.40      # normalized average rating
SCORE_WEIGHT_ENGAGEMENT: float = 0.20  # feedback engagement ratio

# Score thresholds
SCORE_TOP_PERFORMER: float = 70.0
SCORE_NEEDS_IMPROVEMENT: float = 40.0

# ---------------------------------------------------------------------------
# Pagination / display limits
# ---------------------------------------------------------------------------
DASHBOARD_RECENT_COUNT: int = 5
TABLE_PAGE_SIZE: int = 20

# ---------------------------------------------------------------------------
# Chart settings
# ---------------------------------------------------------------------------
CHART_DPI: int = 120
CHART_FIGSIZE_DEFAULT: tuple = (10, 5)
CHART_STYLE: str = "seaborn-v0_8-whitegrid"

# ---------------------------------------------------------------------------
# Validation rules
# ---------------------------------------------------------------------------
MIN_CAPACITY: int = 1
MAX_CAPACITY: int = 5000
MIN_RATING: int = 1
MAX_RATING: int = 5
STUDENT_ID_PREFIX: str = "STU"
EVENT_ID_PREFIX: str = "EVT"
REGISTRATION_ID_PREFIX: str = "REG"
FEEDBACK_ID_PREFIX: str = "FBK"
