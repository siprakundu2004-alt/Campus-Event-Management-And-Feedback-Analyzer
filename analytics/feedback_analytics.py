"""
analytics/feedback_analytics.py
-------------------------------
Feedback and Sentiment Analytics Engine for Campus Event Management & Feedback Analyzer.
Leverages NumPy for rigorous statistical summaries (mean, median, variance, std dev, IQR)
and Pandas for grouping and ranking.
Calculates the multi-factor Event Performance Score (0-100).
"""

from typing import Optional
import pandas as pd
import numpy as np

from repositories.feedback_repository import FeedbackRepository
from repositories.event_repository import EventRepository
from repositories.registration_repository import RegistrationRepository
from utils.constants import RATING_LABELS
import config


class FeedbackAnalytics:
    """Computes feedback distributions, statistical metrics, and event performance scores."""

    def __init__(
        self,
        feedback_repo: Optional[FeedbackRepository] = None,
        event_repo: Optional[EventRepository] = None,
        registration_repo: Optional[RegistrationRepository] = None,
    ) -> None:
        self.feedback_repo = feedback_repo or FeedbackRepository()
        self.event_repo = event_repo or EventRepository()
        self.registration_repo = registration_repo or RegistrationRepository()

    # ------------------------------------------------------------------
    # Summary & Overall Metrics
    # ------------------------------------------------------------------

    def get_summary_metrics(self) -> dict:
        """High-level feedback overview."""
        fbk_df = self.feedback_repo.get_dataframe()
        if fbk_df.empty:
            return {
                "total_feedback": 0,
                "overall_avg_rating": 0.0,
                "positive_percentage": 0.0,
                "neutral_percentage": 0.0,
                "negative_percentage": 0.0,
                "events_reviewed": 0,
            }

        ratings = pd.to_numeric(fbk_df["rating"], errors="coerce").dropna().to_numpy()
        if len(ratings) == 0:
            return {
                "total_feedback": 0,
                "overall_avg_rating": 0.0,
                "positive_percentage": 0.0,
                "neutral_percentage": 0.0,
                "negative_percentage": 0.0,
                "events_reviewed": 0,
            }

        total = len(ratings)
        pos = int(np.sum(ratings >= 4))
        neu = int(np.sum(ratings == 3))
        neg = int(np.sum(ratings <= 2))

        return {
            "total_feedback": total,
            "overall_avg_rating": float(np.round(np.mean(ratings), 2)),
            "positive_percentage": float(np.round(pos / total * 100, 1)),
            "neutral_percentage": float(np.round(neu / total * 100, 1)),
            "negative_percentage": float(np.round(neg / total * 100, 1)),
            "events_reviewed": int(fbk_df["event_id"].nunique()),
        }

    # ------------------------------------------------------------------
    # NumPy Statistical Metrics
    # ------------------------------------------------------------------

    def get_numpy_statistics(self) -> dict:
        """
        Uses NumPy array methods to calculate descriptive statistical indicators
        across all campus feedback scores.
        """
        fbk_df = self.feedback_repo.get_dataframe()
        if fbk_df.empty:
            return {}

        ratings = pd.to_numeric(fbk_df["rating"], errors="coerce").dropna().to_numpy()
        if len(ratings) == 0:
            return {}

        mean_val = float(np.mean(ratings))
        median_val = float(np.median(ratings))
        std_val = float(np.std(ratings, ddof=0))
        var_val = float(np.var(ratings, ddof=0))
        min_val = int(np.min(ratings))
        max_val = int(np.max(ratings))
        p25 = float(np.percentile(ratings, 25))
        p75 = float(np.percentile(ratings, 75))
        iqr = float(p75 - p25)

        return {
            "sample_size": len(ratings),
            "mean": round(mean_val, 3),
            "median": round(median_val, 2),
            "variance": round(var_val, 3),
            "standard_deviation": round(std_val, 3),
            "min_rating": min_val,
            "max_rating": max_val,
            "percentile_25": round(p25, 2),
            "percentile_75": round(p75, 2),
            "interquartile_range": round(iqr, 2),
        }

    # ------------------------------------------------------------------
    # Rating Distribution (1–5)
    # ------------------------------------------------------------------

    def get_rating_distribution(self) -> pd.DataFrame:
        """
        Produce a DataFrame mapping Rating (1-5) and labels to counts and percentages.
        Guarantees all ratings 1..5 exist even if count is 0.
        """
        fbk_df = self.feedback_repo.get_dataframe()
        counts_dict = {r: 0 for r in range(1, 6)}

        if not fbk_df.empty:
            actual_counts = pd.to_numeric(fbk_df["rating"], errors="coerce").value_counts().to_dict()
            for r, c in actual_counts.items():
                if int(r) in counts_dict:
                    counts_dict[int(r)] = int(c)

        total = sum(counts_dict.values())
        data = []
        for r in range(1, 6):
            c = counts_dict[r]
            pct = round((c / total * 100), 1) if total > 0 else 0.0
            data.append({
                "Rating": r,
                "Label": RATING_LABELS.get(r, f"Rating {r}"),
                "Count": c,
                "Percentage": pct,
            })

        return pd.DataFrame(data)

    # ------------------------------------------------------------------
    # Event-wise Feedback Summary
    # ------------------------------------------------------------------

    def get_event_feedback_summary(self) -> pd.DataFrame:
        """
        Computes average rating, total reviews, and sentiment counts for each event.
        """
        fbk_df = self.feedback_repo.get_dataframe()
        evt_df = self.event_repo.get_dataframe()

        if evt_df.empty:
            return pd.DataFrame()

        if fbk_df.empty:
            evt_df["Average Rating"] = 0.0
            evt_df["Total Reviews"] = 0
            return evt_df

        fbk_df["rating_num"] = pd.to_numeric(fbk_df["rating"], errors="coerce")
        grouped = fbk_df.groupby("event_id").agg(
            Avg_Rating=("rating_num", "mean"),
            Review_Count=("feedback_id", "count"),
            Positive_Reviews=("rating_num", lambda s: (s >= 4).sum()),
            Negative_Reviews=("rating_num", lambda s: (s <= 2).sum()),
        ).reset_index()

        merged = evt_df.merge(grouped, on="event_id", how="left")
        merged["Avg_Rating"] = merged["Avg_Rating"].fillna(0.0).round(2)
        merged["Review_Count"] = merged["Review_Count"].fillna(0).astype(int)
        merged["Positive_Reviews"] = merged["Positive_Reviews"].fillna(0).astype(int)
        merged["Negative_Reviews"] = merged["Negative_Reviews"].fillna(0).astype(int)

        return merged

    # ------------------------------------------------------------------
    # EVENT PERFORMANCE SCORE ENGINE
    # ------------------------------------------------------------------

    def get_event_performance_scores(self) -> pd.DataFrame:
        """
        Computes a normalized Event Performance Score (0 to 100) using multi-criteria weighted synthesis:
          - Capacity Utilization Component (40%): How well the event filled its seats
          - Feedback Rating Component (40%): Academic/student satisfaction (scaled 0-5 -> 0-100)
          - Feedback Engagement Component (20%): Proportion of attendees that took the time to review
        Returns a sorted DataFrame from highest to lowest performing events.
        """
        evt_df = self.event_repo.get_dataframe()
        reg_df = self.registration_repo.get_dataframe()
        fbk_df = self.feedback_repo.get_dataframe()

        if evt_df.empty:
            return pd.DataFrame()

        # Registration counts
        reg_counts = {}
        if not reg_df.empty:
            active_reg = reg_df[reg_df["status"] != "Cancelled"]
            reg_counts = active_reg["event_id"].value_counts().to_dict()

        # Feedback stats
        fbk_stats = {}
        if not fbk_df.empty:
            fbk_df["rating_num"] = pd.to_numeric(fbk_df["rating"], errors="coerce")
            grouped_fbk = fbk_df.groupby("event_id").agg(
                avg_rating=("rating_num", "mean"),
                fbk_count=("feedback_id", "count"),
            ).to_dict(orient="index")
            fbk_stats = grouped_fbk

        results = []
        for _, row in evt_df.iterrows():
            eid = row["event_id"]
            name = row["event_name"]
            cat = row["category"]
            cap = int(row["max_capacity"]) if str(row["max_capacity"]).isdigit() and int(row["max_capacity"]) > 0 else 1
            status = row["status"]

            registered = reg_counts.get(eid, 0)
            fbk_info = fbk_stats.get(eid, {"avg_rating": 0.0, "fbk_count": 0})
            avg_rating = round(fbk_info["avg_rating"], 2)
            fbk_count = fbk_info["fbk_count"]

            # Component 1: Capacity Score (0 - 40 points)
            cap_ratio = min(1.0, registered / cap)
            capacity_score = cap_ratio * (config.SCORE_WEIGHT_CAPACITY * 100)

            # Component 2: Rating Score (0 - 40 points)
            # If no reviews yet, baseline depends on whether event happened
            normalized_rating = (avg_rating / 5.0) if avg_rating > 0 else (0.5 if status != "Completed" else 0.0)
            rating_score = normalized_rating * (config.SCORE_WEIGHT_RATING * 100)

            # Component 3: Engagement Score (0 - 20 points)
            engagement_ratio = min(1.0, fbk_count / max(1, registered)) if registered > 0 else 0.0
            engagement_score = engagement_ratio * (config.SCORE_WEIGHT_ENGAGEMENT * 100)

            # Total score
            total_score = round(capacity_score + rating_score + engagement_score, 1)

            # Performance tier
            if total_score >= config.SCORE_TOP_PERFORMER:
                tier = "Top Performer"
            elif total_score >= config.SCORE_NEEDS_IMPROVEMENT:
                tier = "Average Performer"
            else:
                tier = "Needs Improvement"

            results.append({
                "Event ID": eid,
                "Event Name": name,
                "Category": cat,
                "Status": status,
                "Capacity": cap,
                "Registered": registered,
                "Reviews": fbk_count,
                "Avg Rating": avg_rating,
                "Capacity Score": round(capacity_score, 1),
                "Rating Score": round(rating_score, 1),
                "Engagement Score": round(engagement_score, 1),
                "Performance Score": total_score,
                "Tier": tier,
            })

        df_perf = pd.DataFrame(results)
        return df_perf.sort_values(by="Performance Score", ascending=False)
