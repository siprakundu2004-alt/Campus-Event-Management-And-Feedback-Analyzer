"""
analytics/participation_analytics.py
------------------------------------
Pandas and NumPy analytics engine for student participation and capacity utilization.
Merges student demographics with registration events.
"""

from typing import Optional
import pandas as pd
import numpy as np

from repositories.event_repository import EventRepository
from repositories.student_repository import StudentRepository
from repositories.registration_repository import RegistrationRepository
from utils.constants import RegistrationStatus


class ParticipationAnalytics:
    """Computes event registration metrics, demographic patterns, and capacity efficiency."""

    def __init__(
        self,
        event_repo: Optional[EventRepository] = None,
        student_repo: Optional[StudentRepository] = None,
        registration_repo: Optional[RegistrationRepository] = None,
    ) -> None:
        self.event_repo = event_repo or EventRepository()
        self.student_repo = student_repo or StudentRepository()
        self.registration_repo = registration_repo or RegistrationRepository()

    def get_summary_metrics(self) -> dict:
        """High-level participation metrics."""
        reg_df = self.registration_repo.get_dataframe()
        evt_df = self.event_repo.get_dataframe()
        stu_df = self.student_repo.get_dataframe()

        if reg_df.empty:
            return {
                "total_registrations": 0,
                "confirmed_registrations": 0,
                "cancelled_registrations": 0,
                "unique_students_participated": 0,
                "overall_participation_rate": 0.0,
                "avg_registrations_per_event": 0.0,
                "overall_capacity_utilization": 0.0,
            }

        total_reg = len(reg_df)
        confirmed_mask = reg_df["status"] == RegistrationStatus.CONFIRMED.value
        confirmed_count = int(confirmed_mask.sum())
        cancelled_count = int((reg_df["status"] == RegistrationStatus.CANCELLED.value).sum())

        unique_students = reg_df.loc[confirmed_mask, "student_id"].nunique()
        total_students = len(stu_df) if not stu_df.empty else 1
        part_rate = round((unique_students / total_students) * 100, 1)

        # Average per active event
        num_events = len(evt_df) if not evt_df.empty else 1
        avg_per_event = round(confirmed_count / num_events, 1)

        # Overall capacity utilization
        total_capacity = pd.to_numeric(evt_df["max_capacity"], errors="coerce").sum() if not evt_df.empty else 0
        overall_util = round((confirmed_count / total_capacity * 100), 1) if total_capacity > 0 else 0.0

        return {
            "total_registrations": total_reg,
            "confirmed_registrations": confirmed_count,
            "cancelled_registrations": cancelled_count,
            "unique_students_participated": unique_students,
            "overall_participation_rate": part_rate,
            "avg_registrations_per_event": avg_per_event,
            "overall_capacity_utilization": overall_util,
        }

    def get_event_participation_table(self) -> pd.DataFrame:
        """
        Produce a comprehensive table comparing events:
        Event Name, Category, Capacity, Registered, Available, Utilization %
        """
        evt_df = self.event_repo.get_dataframe()
        reg_df = self.registration_repo.get_dataframe()

        if evt_df.empty:
            return pd.DataFrame()

        # Count confirmed registrations per event
        if not reg_df.empty:
            confirmed_reg = reg_df[reg_df["status"] == RegistrationStatus.CONFIRMED.value]
            counts = confirmed_reg["event_id"].value_counts().to_dict()
        else:
            counts = {}

        data = []
        for _, row in evt_df.iterrows():
            eid = row["event_id"]
            name = row["event_name"]
            cat = row["category"]
            cap = int(row["max_capacity"]) if str(row["max_capacity"]).isdigit() else 0
            reg_count = counts.get(eid, 0)
            avail = max(0, cap - reg_count)
            util = round((reg_count / cap * 100), 1) if cap > 0 else 0.0
            status = row["status"]

            data.append({
                "Event ID": eid,
                "Event Name": name,
                "Category": cat,
                "Capacity": cap,
                "Registered": reg_count,
                "Available Seats": avail,
                "Utilization %": util,
                "Status": status,
            })

        df_result = pd.DataFrame(data)
        return df_result.sort_values(by="Registered", ascending=False)

    def get_department_participation(self) -> pd.DataFrame:
        """
        Department-wise breakdown of student participation.
        Merges registrations with student records.
        """
        reg_df = self.registration_repo.get_dataframe()
        stu_df = self.student_repo.get_dataframe()

        if reg_df.empty or stu_df.empty:
            return pd.DataFrame(columns=["Department", "Registrations", "Percentage"])

        confirmed = reg_df[reg_df["status"] == RegistrationStatus.CONFIRMED.value]
        merged = confirmed.merge(stu_df, on="student_id", how="inner")

        if merged.empty:
            return pd.DataFrame(columns=["Department", "Registrations", "Percentage"])

        dept_counts = merged["department"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Registrations"]
        total = dept_counts["Registrations"].sum()
        dept_counts["Percentage"] = (dept_counts["Registrations"] / total * 100).round(1)
        return dept_counts

    def get_course_participation(self) -> pd.DataFrame:
        """Course-wise breakdown of student participation."""
        reg_df = self.registration_repo.get_dataframe()
        stu_df = self.student_repo.get_dataframe()

        if reg_df.empty or stu_df.empty:
            return pd.DataFrame(columns=["Course", "Registrations", "Percentage"])

        confirmed = reg_df[reg_df["status"] == RegistrationStatus.CONFIRMED.value]
        merged = confirmed.merge(stu_df, on="student_id", how="inner")

        if merged.empty:
            return pd.DataFrame(columns=["Course", "Registrations", "Percentage"])

        course_counts = merged["course"].value_counts().reset_index()
        course_counts.columns = ["Course", "Registrations"]
        total = course_counts["Registrations"].sum()
        course_counts["Percentage"] = (course_counts["Registrations"] / total * 100).round(1) if total > 0 else 0
        return course_counts

    def get_category_participation(self) -> pd.DataFrame:
        """Registrations across event categories."""
        evt_df = self.event_repo.get_dataframe()
        reg_df = self.registration_repo.get_dataframe()

        if evt_df.empty or reg_df.empty:
            return pd.DataFrame(columns=["Category", "Total Registrations", "Average per Event"])

        confirmed = reg_df[reg_df["status"] == RegistrationStatus.CONFIRMED.value]
        merged = confirmed.merge(evt_df, on="event_id", how="inner")

        if merged.empty:
            return pd.DataFrame(columns=["Category", "Total Registrations", "Average per Event"])

        grouped = merged.groupby("category").agg(
            Total_Registrations=("registration_id", "count"),
            Unique_Events=("event_id", "nunique"),
        ).reset_index()

        grouped["Average_per_Event"] = (
            grouped["Total_Registrations"] / grouped["Unique_Events"]
        ).round(1)

        grouped.columns = ["Category", "Total Registrations", "Unique Events", "Average per Event"]
        return grouped.sort_values(by="Total Registrations", ascending=False)

    def get_most_and_least_popular(self, top_n: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Return top N most popular and least popular events by registrations."""
        table = self.get_event_participation_table()
        if table.empty:
            return pd.DataFrame(), pd.DataFrame()

        most_popular = table.head(top_n)
        least_popular = table.tail(top_n).sort_values(by="Registered", ascending=True)
        return most_popular, least_popular
