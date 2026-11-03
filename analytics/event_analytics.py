"""
analytics/event_analytics.py
----------------------------
Pandas-powered analytical engine for campus events.
Computes event lifecycle breakdowns, category distributions, and venue utilization.
"""

from typing import Optional
import pandas as pd
import numpy as np

from repositories.event_repository import EventRepository
from repositories.registration_repository import RegistrationRepository
from utils.constants import EventStatus, EventCategory


class EventAnalytics:
    """Computes event-level descriptive and aggregated statistics."""

    def __init__(
        self,
        event_repo: Optional[EventRepository] = None,
        registration_repo: Optional[RegistrationRepository] = None,
    ) -> None:
        self.event_repo = event_repo or EventRepository()
        self.registration_repo = registration_repo or RegistrationRepository()

    def get_summary_metrics(self) -> dict:
        """Return high-level event KPIs."""
        df = self.event_repo.get_dataframe()
        if df.empty:
            return {
                "total_events": 0,
                "upcoming_events": 0,
                "completed_events": 0,
                "cancelled_events": 0,
                "open_events": 0,
                "full_events": 0,
                "total_capacity": 0,
                "avg_capacity": 0.0,
            }

        total = len(df)
        status_counts = df["status"].value_counts().to_dict()

        capacities = pd.to_numeric(df["max_capacity"], errors="coerce").fillna(0).to_numpy()

        return {
            "total_events": total,
            "upcoming_events": int(status_counts.get(EventStatus.REGISTRATION_OPEN.value, 0)),
            "completed_events": int(status_counts.get(EventStatus.COMPLETED.value, 0)),
            "cancelled_events": int(status_counts.get(EventStatus.CANCELLED.value, 0)),
            "open_events": int(status_counts.get(EventStatus.REGISTRATION_OPEN.value, 0)),
            "full_events": int(status_counts.get(EventStatus.FULL.value, 0)),
            "draft_events": int(status_counts.get(EventStatus.DRAFT.value, 0)),
            "total_capacity": int(np.sum(capacities)),
            "avg_capacity": float(np.mean(capacities)) if len(capacities) > 0 else 0.0,
            "max_single_capacity": int(np.max(capacities)) if len(capacities) > 0 else 0,
        }

    def get_events_by_category(self) -> pd.DataFrame:
        """Return distribution of events across categories with counts and percentages."""
        df = self.event_repo.get_dataframe()
        if df.empty:
            return pd.DataFrame(columns=["Category", "Count", "Percentage"])

        cat_counts = df["category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        total = len(df)
        cat_counts["Percentage"] = (cat_counts["Count"] / total * 100).round(1)
        return cat_counts

    def get_events_by_status(self) -> pd.DataFrame:
        """Return distribution of events by status."""
        df = self.event_repo.get_dataframe()
        if df.empty:
            return pd.DataFrame(columns=["Status", "Count", "Percentage"])

        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        total = len(df)
        status_counts["Percentage"] = (status_counts["Count"] / total * 100).round(1)
        return status_counts

    def get_events_by_venue(self) -> pd.DataFrame:
        """Return frequency of events hosted at each campus venue."""
        df = self.event_repo.get_dataframe()
        if df.empty:
            return pd.DataFrame(columns=["Venue", "Event Count"])

        venue_counts = df["venue"].value_counts().reset_index()
        venue_counts.columns = ["Venue", "Event Count"]
        return venue_counts

    def get_capacity_distribution(self) -> dict:
        """Return statistical percentiles of event capacities using NumPy."""
        df = self.event_repo.get_dataframe()
        if df.empty:
            return {}

        caps = pd.to_numeric(df["max_capacity"], errors="coerce").dropna().to_numpy()
        if len(caps) == 0:
            return {}

        return {
            "mean": float(np.mean(caps)),
            "median": float(np.median(caps)),
            "std_dev": float(np.std(caps)),
            "min": int(np.min(caps)),
            "max": int(np.max(caps)),
            "p25": float(np.percentile(caps, 25)),
            "p75": float(np.percentile(caps, 75)),
        }
