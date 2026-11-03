"""
reports/report_generator.py
---------------------------
Automated report generation engine for Campus Event Management & Feedback Analyzer.
Generates comprehensive textual summaries and CSV export datasets in `reports/generated_reports/`:
  1. Event Comprehensive Performance Report
  2. Student Participation & Demographic Report
  3. Campus Analytics Executive Summary Report
"""

from pathlib import Path
from datetime import datetime
import pandas as pd

from services.event_service import EventService
from services.student_service import StudentService
from services.registration_service import RegistrationService
from services.feedback_service import FeedbackService
from analytics.event_analytics import EventAnalytics
from analytics.participation_analytics import ParticipationAnalytics
from analytics.feedback_analytics import FeedbackAnalytics
from utils.helpers import report_filename, now_str, today_str
import config


class ReportGenerator:
    """Generates and archives university event management reports."""

    def __init__(self) -> None:
        self.event_service = EventService()
        self.student_service = StudentService()
        self.reg_service = RegistrationService()
        self.fbk_service = FeedbackService()
        self.evt_analytics = EventAnalytics()
        self.part_analytics = ParticipationAnalytics()
        self.fbk_analytics = FeedbackAnalytics()
        self.output_dir: Path = config.REPORTS_DIR

    # ------------------------------------------------------------------
    # 1. Event Performance Report
    # ------------------------------------------------------------------

    def generate_event_report(self) -> tuple[Path, str]:
        """
        Compiles an all-events performance ledger and saves as text file.
        Returns (filepath, file_content).
        """
        perf_df = self.fbk_analytics.get_event_performance_scores()
        filename = report_filename("Event_Performance_Report", "txt")
        filepath = self.output_dir / filename

        lines = [
            "=" * 78,
            f"{config.APP_NAME.upper()} - EVENT PERFORMANCE & STATUS REPORT",
            f"Institution: {config.UNIVERSITY_NAME}",
            f"Generated:   {now_str()}",
            "=" * 78,
            "",
            f"{'EVENT ID':<12} {'EVENT NAME':<30} {'CAP':<5} {'REG':<5} {'AVG ★':<7} {'SCORE':<7} {'TIER'}",
            "-" * 78,
        ]

        for _, r in perf_df.iterrows():
            name = r["Event Name"][:28]
            lines.append(
                f"{r['Event ID']:<12} {name:<30} {r['Capacity']:<5} {r['Registered']:<5} "
                f"{r['Avg Rating']:<7.2f} {r['Performance Score']:<7.1f} {r['Tier']}"
            )

        lines.extend([
            "-" * 78,
            f"Total Events Tracked: {len(perf_df)}",
            "",
            "SCORING METHODOLOGY:",
            "  * Capacity Utilization (40%): How successfully the event met capacity targets.",
            "  * Feedback Satisfaction (40%): Normalized student review ratings (0-5 stars).",
            "  * Review Engagement (20%): Proportion of registered participants submitting feedback.",
            "=" * 78,
        ])

        content = "\n".join(lines)
        filepath.write_text(content, encoding="utf-8")

        # Also save CSV version
        csv_path = self.output_dir / report_filename("Event_Performance_Data", "csv")
        perf_df.to_csv(csv_path, index=False)

        return filepath, content

    # ------------------------------------------------------------------
    # 2. Student Participation Report
    # ------------------------------------------------------------------

    def generate_student_report(self) -> tuple[Path, str]:
        """
        Compiles student participation ledger and archives it.
        Returns (filepath, file_content).
        """
        students = self.student_service.list_all_students()
        filename = report_filename("Student_Participation_Report", "txt")
        filepath = self.output_dir / filename

        lines = [
            "=" * 78,
            f"{config.APP_NAME.upper()} - STUDENT PARTICIPATION DIRECTORY",
            f"Institution: {config.UNIVERSITY_NAME}",
            f"Generated:   {now_str()}",
            "=" * 78,
            "",
            f"{'STUDENT ID':<12} {'STUDENT NAME':<24} {'DEPT':<18} {'COURSE':<10} {'REG':<5} {'FEEDBACK'}",
            "-" * 78,
        ]

        records = []
        for s in students:
            stats = self.student_service.get_student_stats(s.student_id)
            name = s.name[:22]
            dept = s.department[:16]
            lines.append(
                f"{s.student_id:<12} {name:<24} {dept:<18} {s.course:<10} "
                f"{stats['total_registrations']:<5} {stats['feedbacks_submitted']}"
            )
            records.append({
                "Student ID": s.student_id,
                "Name": s.name,
                "Email": s.email,
                "Department": s.department,
                "Course": s.course,
                "Semester": s.semester,
                "Total Registrations": stats["total_registrations"],
                "Feedback Submitted": stats["feedbacks_submitted"],
            })

        lines.extend([
            "-" * 78,
            f"Total Registered Students: {len(students)}",
            "=" * 78,
        ])

        content = "\n".join(lines)
        filepath.write_text(content, encoding="utf-8")

        # Also export CSV
        csv_path = self.output_dir / report_filename("Student_Directory_Data", "csv")
        pd.DataFrame(records).to_csv(csv_path, index=False)

        return filepath, content

    # ------------------------------------------------------------------
    # 3. Campus Analytics Executive Summary
    # ------------------------------------------------------------------

    def generate_executive_analytics_report(self) -> tuple[Path, str]:
        """
        Compiles campus-wide executive leadership analytics report.
        """
        evt_kpis = self.evt_analytics.get_summary_metrics()
        part_kpis = self.part_analytics.get_summary_metrics()
        fbk_kpis = self.fbk_analytics.get_summary_metrics()
        num_stats = self.fbk_analytics.get_numpy_statistics()
        perf_df = self.fbk_analytics.get_event_performance_scores()

        filename = report_filename("Campus_Analytics_Executive_Summary", "txt")
        filepath = self.output_dir / filename

        top_event = perf_df.iloc[0]["Event Name"] if not perf_df.empty else "N/A"
        top_score = perf_df.iloc[0]["Performance Score"] if not perf_df.empty else 0.0

        lines = [
            "#" * 80,
            f"         {config.APP_NAME.upper()} - EXECUTIVE ANALYTICS REPORT",
            f"         {config.UNIVERSITY_NAME}",
            f"         Generated on: {now_str()}",
            "#" * 80,
            "",
            "1. HIGH-LEVEL CAMPUS EVENT KPIS",
            "-" * 45,
            f"  * Total Events Organized:        {evt_kpis['total_events']}",
            f"  * Completed Events:              {evt_kpis['completed_events']}",
            f"  * Currently Open for Reg:        {evt_kpis['open_events']}",
            f"  * Events at Full Capacity:       {evt_kpis['full_events']}",
            f"  * Total Seat Capacity Created:   {evt_kpis['total_capacity']}",
            f"  * Average Capacity per Event:    {evt_kpis['avg_capacity']:.1f}",
            "",
            "2. PARTICIPATION & ENGAGEMENT METRICS",
            "-" * 45,
            f"  * Total Event Registrations:     {part_kpis['total_registrations']}",
            f"  * Confirmed Registrations:       {part_kpis['confirmed_registrations']}",
            f"  * Cancelled Registrations:       {part_kpis['cancelled_registrations']}",
            f"  * Unique Students Engaged:       {part_kpis['unique_students_participated']}",
            f"  * Student Participation Rate:    {part_kpis['overall_participation_rate']}%",
            f"  * Average Attendees / Event:     {part_kpis['avg_registrations_per_event']}",
            f"  * Overall Capacity Utilization:  {part_kpis['overall_capacity_utilization']}%",
            "",
            "3. STUDENT SATISFACTION & NUMPY METRICS",
            "-" * 45,
            f"  * Overall Average Rating:        {fbk_kpis['overall_avg_rating']} / 5.0",
            f"  * Positive Feedback (4-5 Stars): {fbk_kpis['positive_percentage']}%",
            f"  * Neutral Feedback (3 Stars):    {fbk_kpis['neutral_percentage']}%",
            f"  * Critical Feedback (1-2 Stars): {fbk_kpis['negative_percentage']}%",
            f"  * Rating Mean:                   {num_stats.get('mean', 0.0)}",
            f"  * Rating Median:                 {num_stats.get('median', 0.0)}",
            f"  * Standard Deviation:            {num_stats.get('standard_deviation', 0.0)}",
            f"  * Interquartile Range (IQR):     {num_stats.get('interquartile_range', 0.0)}",
            "",
            "4. TOP-RANKED CAMPUS EVENT",
            "-" * 45,
            f"  * Star Event:                    {top_event}",
            f"  * Performance Score:             {top_score} / 100",
            "",
            "#" * 80,
            "End of Executive Report",
            "#" * 80,
        ]

        content = "\n".join(lines)
        filepath.write_text(content, encoding="utf-8")
        return filepath, content
