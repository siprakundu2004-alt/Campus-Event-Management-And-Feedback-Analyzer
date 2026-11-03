"""
visualization/charts.py
-----------------------
Professional data visualization module for Campus Event Management & Feedback Analyzer.
Generates publication-quality charts for the Streamlit dashboard and generated reports:
  - Chart 1: Bar Chart — Event Participation (Horizontal bar chart with values)
  - Chart 2: Histogram Graph — Feedback Rating Distribution (Color-coded frequency histogram)
  - Chart 3: Grouped Bar Graph — Event Popularity vs Capacity (Dual comparative bar chart)
  - Chart 4: Benchmark Bar Graph — Average Event Rating (Ranked horizontal chart with grade threshold)
  - Chart 5: Dual Donut & Bar Graph — Department Participation Distribution (Donut pie & bar graph)
  - Chart 6: Dual Donut & Bar Graph — Student Sentiment Share (Positive, Neutral, Critical breakdown)
  - Chart 7: Categorical Bar Graph — Event Category Analysis (Participation by domain)
  - Chart 8: Performance Score Matrix Graph — Composite Event Score Matrix (Ranked score breakdown)
"""

from typing import Optional
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

# University theme palette
COLOR_PRIMARY = "#1E3A8A"       # Royal Blue
COLOR_SECONDARY = "#0D9488"     # Teal
COLOR_ACCENT = "#F59E0B"        # Amber
COLOR_DANGER = "#EF4444"        # Crimson / Red
COLOR_SUCCESS = "#10B981"       # Emerald / Green
COLOR_MUTED = "#64748B"         # Slate Grey
PALETTE = ["#1E3A8A", "#0D9488", "#F59E0B", "#8B5CF6", "#EC4899", "#06B6D4", "#10B981", "#64748B"]


def _apply_theme(ax: plt.Axes, title: str, xlabel: str, ylabel: str) -> None:
    """Apply consistent styling across all Matplotlib axes."""
    ax.set_title(title, fontsize=13, fontweight="bold", pad=15, color="#0F172A")
    ax.set_xlabel(xlabel, fontsize=11, fontweight="bold", labelpad=10, color="#334155")
    ax.set_ylabel(ylabel, fontsize=11, fontweight="bold", labelpad=10, color="#334155")
    ax.grid(True, linestyle="--", alpha=0.5, color="#CBD5E1")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#94A3B8")
    ax.spines["bottom"].set_color("#94A3B8")
    ax.tick_params(colors="#334155", labelsize=10)


# ---------------------------------------------------------------------------
# Chart 1 — Bar Chart: Event Participation
# ---------------------------------------------------------------------------

def plot_event_participation(df_table: pd.DataFrame, top_n: int = 10) -> plt.Figure:
    """
    Horizontal Bar Chart showing confirmed student registrations per event.
    """
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

    if df_table is None or df_table.empty or "Registered" not in df_table.columns:
        ax.text(0.5, 0.5, "No event participation data available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    subset = df_table.sort_values(by="Registered", ascending=True).tail(top_n)
    if subset.empty:
        ax.text(0.5, 0.5, "No event participation data available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    y_pos = np.arange(len(subset))
    reg_vals = pd.to_numeric(subset["Registered"], errors="coerce").fillna(0)
    bars = ax.barh(y_pos, reg_vals, color=COLOR_PRIMARY, height=0.65, edgecolor="none")

    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 0.3,
            bar.get_y() + bar.get_height() / 2,
            f"{int(width)}",
            ha="left",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="#1E293B",
        )

    name_col = "Event Name" if "Event Name" in subset.columns else ("event_name" if "event_name" in subset.columns else None)
    names = [str(n) if len(str(n)) <= 28 else str(n)[:25] + "..." for n in subset[name_col]] if name_col else [f"Event {i+1}" for i in y_pos]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)

    max_val = float(reg_vals.max()) if not reg_vals.empty else 10.0
    ax.set_xlim(0, max(max_val * 1.15, 5.0))
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    _apply_theme(ax, f"Top {len(subset)} Events by Student Participation (Bar Chart)", "Confirmed Registrations", "Campus Event")
    try:
        fig.tight_layout()
    except Exception:
        pass
    return fig


# ---------------------------------------------------------------------------
# Chart 2 — Histogram Graph: Feedback Rating Distribution
# ---------------------------------------------------------------------------

def plot_feedback_distribution(df_dist: pd.DataFrame) -> plt.Figure:
    """
    Frequency Histogram & Distribution Graph showing student satisfaction from 1 to 5 Stars.
    """
    fig, ax = plt.subplots(figsize=(9, 5), dpi=100)

    if df_dist is None or df_dist.empty or "Rating" not in df_dist.columns or "Count" not in df_dist.columns:
        ax.text(0.5, 0.5, "No feedback data available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    STAR_COLORS = {1: "#EF4444", 2: "#F97316", 3: "#FBBF24", 4: "#34D399", 5: "#10B981"}

    x = df_dist["Rating"]
    counts = pd.to_numeric(df_dist["Count"], errors="coerce").fillna(0)
    bar_colors = [STAR_COLORS.get(int(r), COLOR_PRIMARY) for r in x]
    bars = ax.bar(x, counts, color=bar_colors, width=0.55, edgecolor="#0F172A", linewidth=0.5)

    total = counts.sum()
    pct_series = df_dist["Percentage"] if "Percentage" in df_dist.columns else (counts / total * 100 if total > 0 else [0]*len(counts))
    for bar, pct in zip(bars, pct_series):
        h = bar.get_height()
        pct_val = round(float(pct), 1) if pd.notnull(pct) else 0.0
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + 0.3,
            f"{int(h)} ({pct_val}%)",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color="#1E293B",
        )

    labels = []
    for r in x:
        matching = df_dist.loc[df_dist["Rating"] == r, "Label"].values if "Label" in df_dist.columns else []
        label_text = matching[0] if len(matching) > 0 else f"Rating {r}"
        labels.append(f"★ {r}\n({label_text})")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    max_c = float(counts.max()) if total > 0 else 5.0
    ax.set_ylim(0, max(max_c * 1.25, 5.0))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    _apply_theme(ax, "Student Feedback Rating Frequency Distribution (Histogram Graph)", "Rating Scale (1 to 5 Stars)", "Number of Reviews")
    try:
        fig.tight_layout()
    except Exception:
        pass
    return fig


# ---------------------------------------------------------------------------
# Chart 3 — Grouped Bar Graph: Event Popularity vs Capacity
# ---------------------------------------------------------------------------

def plot_popularity_vs_capacity(df_table: pd.DataFrame, top_n: int = 8) -> plt.Figure:
    """
    Grouped Bar Graph comparing Registered attendees vs Maximum capacity.
    """
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=100)

    if df_table is None or df_table.empty:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    subset = df_table.head(top_n)
    if subset.empty:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    indices = np.arange(len(subset))
    bar_width = 0.38

    reg_col = "Registered" if "Registered" in subset.columns else ("registered" if "registered" in subset.columns else None)
    cap_col = "Capacity" if "Capacity" in subset.columns else ("capacity" if "capacity" in subset.columns else None)
    reg_vals = pd.to_numeric(subset[reg_col], errors="coerce").fillna(0) if reg_col else pd.Series([0]*len(subset))
    cap_vals = pd.to_numeric(subset[cap_col], errors="coerce").fillna(0) if cap_col else pd.Series([0]*len(subset))

    bars1 = ax.bar(
        indices - bar_width / 2,
        reg_vals,
        width=bar_width,
        label="Registered Attendees",
        color=COLOR_PRIMARY,
        alpha=0.9,
    )
    bars2 = ax.bar(
        indices + bar_width / 2,
        cap_vals,
        width=bar_width,
        label="Total Capacity Seats",
        color="#CBD5E1",
        edgecolor=COLOR_MUTED,
        linewidth=0.8,
    )

    name_col = "Event Name" if "Event Name" in subset.columns else ("event_name" if "event_name" in subset.columns else None)
    names = [str(n) if len(str(n)) <= 20 else str(n)[:17] + "..." for n in subset[name_col]] if name_col else [f"Event {i+1}" for i in indices]
    ax.set_xticks(indices)
    ax.set_xticklabels(names, rotation=25, ha="right")
    ax.legend(frameon=True, facecolor="white", edgecolor="#E2E8F0")

    max_v = max(float(reg_vals.max()) if not reg_vals.empty else 0.0, float(cap_vals.max()) if not cap_vals.empty else 0.0)
    ax.set_ylim(0, max(max_v * 1.25, 5.0))

    _apply_theme(ax, "Event Registration vs Total Seat Capacity (Grouped Bar Graph)", "Campus Event", "Number of Seats")
    try:
        fig.tight_layout()
    except Exception:
        pass
    return fig


# ---------------------------------------------------------------------------
# Chart 4 — Benchmark Bar Graph: Average Event Rating
# ---------------------------------------------------------------------------

def plot_average_ratings(df_summary: pd.DataFrame, min_reviews: int = 1) -> plt.Figure:
    """
    Horizontal Benchmark Bar Graph showing average satisfaction score per event.
    """
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=100)

    if df_summary is None or df_summary.empty:
        ax.text(0.5, 0.5, "No rating data available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    rating_col = "Avg_Rating" if "Avg_Rating" in df_summary.columns else ("avg_rating" if "avg_rating" in df_summary.columns else ("Avg Rating" if "Avg Rating" in df_summary.columns else None))
    review_col = "Review_Count" if "Review_Count" in df_summary.columns else ("Reviews" if "Reviews" in df_summary.columns else None)

    if not rating_col:
        ax.text(0.5, 0.5, "No rating data available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    filtered = df_summary.copy()
    if review_col:
        filtered = filtered[pd.to_numeric(filtered[review_col], errors="coerce").fillna(0) >= min_reviews]
    filtered = filtered.sort_values(by=rating_col, ascending=True)

    if filtered.empty:
        ax.text(0.5, 0.5, "No events meet review criteria", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    y_pos = np.arange(len(filtered))
    ratings = pd.to_numeric(filtered[rating_col], errors="coerce").fillna(0.0)
    colors = [
        COLOR_SUCCESS if r >= 4.5 else (COLOR_SECONDARY if r >= 3.5 else COLOR_ACCENT)
        for r in ratings
    ]

    bars = ax.barh(y_pos, ratings, color=colors, height=0.6)

    for bar in bars:
        w = bar.get_width()
        ax.text(
            w + 0.05,
            bar.get_y() + bar.get_height() / 2,
            f"{w:.2f} ★",
            ha="left",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="#1E293B",
        )

    name_col = "event_name" if "event_name" in filtered.columns else ("Event Name" if "Event Name" in filtered.columns else None)
    names = [str(n) if len(str(n)) <= 26 else str(n)[:23] + "..." for n in filtered[name_col]] if name_col else [f"Event {i+1}" for i in y_pos]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)
    ax.set_xlim(0, 5.5)
    ax.axvline(4.0, color="#10B981", linestyle=":", alpha=0.7, label="Benchmark (4.0 ★)")
    ax.legend(loc="lower right")

    _apply_theme(ax, "Average Student Rating Benchmark by Event (Bar Graph)", "Rating (1 to 5 Stars)", "Campus Event")
    try:
        fig.tight_layout()
    except Exception:
        pass
    return fig


# ---------------------------------------------------------------------------
# Chart 5 — Dual Donut & Bar Graph: Department-Wise Participation
# ---------------------------------------------------------------------------

def plot_department_participation(df_dept: pd.DataFrame) -> plt.Figure:
    """
    Dual Donut (Pie) Chart and Horizontal Bar Graph of department student engagement.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=100)

    if df_dept is None or df_dept.empty:
        ax1.text(0.5, 0.5, "No department participation data", ha="center", va="center", fontsize=12)
        ax1.axis("off")
        ax2.axis("off")
        return fig

    reg_col = "Registrations" if "Registrations" in df_dept.columns else ("registrations" if "registrations" in df_dept.columns else None)
    dept_col = "Department" if "Department" in df_dept.columns else ("department" if "department" in df_dept.columns else None)

    if not reg_col or not dept_col:
        ax1.text(0.5, 0.5, "No department participation data", ha="center", va="center", fontsize=12)
        ax1.axis("off")
        ax2.axis("off")
        return fig

    sorted_df = df_dept.sort_values(by=reg_col, ascending=True)
    if sorted_df.empty:
        ax1.text(0.5, 0.5, "No department participation data", ha="center", va="center", fontsize=12)
        ax1.axis("off")
        ax2.axis("off")
        return fig

    reg_vals = pd.to_numeric(sorted_df[reg_col], errors="coerce").fillna(0)
    total_reg = reg_vals.sum()
    departments = [str(d) for d in sorted_df[dept_col]]
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(sorted_df))]

    # Subplot 1: Donut (Pie) Graph
    if total_reg > 0:
        wedges, texts, autotexts = ax1.pie(
            reg_vals,
            labels=departments,
            colors=colors,
            autopct="%1.1f%%",
            pctdistance=0.75,
            startangle=140,
            wedgeprops=dict(width=0.42, edgecolor="white", linewidth=2),
            textprops=dict(fontsize=9, color="#1E293B"),
        )
        for at in autotexts:
            at.set_fontsize(8.5)
            at.set_weight("bold")
        ax1.set_title("Department Share (Donut Graph)", fontsize=13, fontweight="bold", pad=12, color="#0F172A")
    else:
        ax1.text(0.5, 0.5, "0 Registrations", ha="center", va="center", fontsize=11)
        ax1.axis("off")

    # Subplot 2: Horizontal Bar Graph
    y_pos = np.arange(len(sorted_df))
    bars = ax2.barh(y_pos, reg_vals, color=colors, height=0.6)

    pct_col = "Percentage" if "Percentage" in sorted_df.columns else None
    pct_series = sorted_df[pct_col] if pct_col else (reg_vals / total_reg * 100 if total_reg > 0 else [0]*len(reg_vals))

    for bar, pct in zip(bars, pct_series):
        w = bar.get_width()
        pct_val = round(float(pct), 1) if pd.notnull(pct) else 0.0
        ax2.text(
            w + 0.4,
            bar.get_y() + bar.get_height() / 2,
            f"{int(w)} ({pct_val}%)",
            ha="left",
            va="center",
            fontsize=9.5,
            fontweight="bold",
            color="#1E293B",
        )

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(departments)
    max_val = float(reg_vals.max()) if not reg_vals.empty else 10.0
    ax2.set_xlim(0, max(max_val * 1.25, 5.0))
    ax2.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    _apply_theme(ax2, "Registration Totals (Bar Graph)", "Confirmed Registrations", "Department")
    try:
        fig.tight_layout()
    except Exception:
        pass
    return fig


# ---------------------------------------------------------------------------
# Chart 6 — Dual Donut & Bar Graph: Feedback Sentiment Breakdown
# ---------------------------------------------------------------------------

def plot_sentiment_breakdown(summary: dict) -> plt.Figure:
    """
    Dual Donut (Pie) Chart and Bar Graph of Student Feedback Sentiment.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=100)

    labels = ["Positive (4-5 ★)", "Neutral (3 ★)", "Critical (1-2 ★)"]
    pos = summary.get("positive_percentage", 0.0)
    neu = summary.get("neutral_percentage", 0.0)
    neg = summary.get("negative_percentage", 0.0)
    values = [pos, neu, neg]
    colors = ["#10B981", "#FBBF24", "#EF4444"]

    total = sum(values)
    if total > 0:
        wedges, texts, autotexts = ax1.pie(
            values,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            pctdistance=0.75,
            startangle=140,
            wedgeprops=dict(width=0.42, edgecolor="white", linewidth=2),
            textprops=dict(fontsize=9, color="#1E293B"),
        )
        for at in autotexts:
            at.set_fontsize(8.5)
            at.set_weight("bold")
        ax1.set_title("Sentiment Share (Donut Graph)", fontsize=13, fontweight="bold", pad=12, color="#0F172A")
    else:
        ax1.text(0.5, 0.5, "No feedback data", ha="center", va="center", fontsize=11)
        ax1.axis("off")

    x = np.arange(len(labels))
    bars = ax2.bar(x, values, color=colors, width=0.5)
    for bar in bars:
        h = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            h + 1.0,
            f"{h:.1f}%",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color="#1E293B",
        )

    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.set_ylim(0, max(max(values) * 1.25 if values else 10.0, 10.0))
    _apply_theme(ax2, "Sentiment Proportion (Bar Graph)", "Sentiment Category", "Percentage of Reviews (%)")

    try:
        fig.tight_layout()
    except Exception:
        pass
    return fig


# ---------------------------------------------------------------------------
# Chart 7 — Categorical Bar Graph: Event Category Analysis
# ---------------------------------------------------------------------------

def plot_category_analysis(df_cat: pd.DataFrame) -> plt.Figure:
    """
    Categorical Bar Graph showing total registrations by event domain.
    """
    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)

    if df_cat is None or df_cat.empty:
        ax.text(0.5, 0.5, "No category data available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    reg_col = "Total Registrations" if "Total Registrations" in df_cat.columns else ("Registrations" if "Registrations" in df_cat.columns else None)
    cat_col = "Category" if "Category" in df_cat.columns else ("category" if "category" in df_cat.columns else None)

    if not reg_col or not cat_col:
        ax.text(0.5, 0.5, "No category data available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    sorted_cat = df_cat.sort_values(by=reg_col, ascending=False)
    if sorted_cat.empty:
        ax.text(0.5, 0.5, "No category data available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    x = np.arange(len(sorted_cat))
    reg_vals = pd.to_numeric(sorted_cat[reg_col], errors="coerce").fillna(0)
    bar_colors = [PALETTE[i % len(PALETTE)] for i in range(len(sorted_cat))]
    bars = ax.bar(x, reg_vals, color=bar_colors, width=0.55)

    avg_col = "Average per Event" if "Average per Event" in sorted_cat.columns else None
    avg_series = sorted_cat[avg_col] if avg_col else [None]*len(sorted_cat)

    for bar, avg_p in zip(bars, avg_series):
        h = bar.get_height()
        label_text = f"{int(h)}\n(avg {avg_p})" if pd.notnull(avg_p) else f"{int(h)}"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + 0.8,
            label_text,
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color="#1E293B",
        )

    ax.set_xticks(x)
    ax.set_xticklabels([str(c) for c in sorted_cat[cat_col]], rotation=20, ha="right")
    max_h = float(reg_vals.max()) if not reg_vals.empty else 10.0
    ax.set_ylim(0, max(max_h * 1.25, 5.0))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    _apply_theme(ax, "Student Engagement Across Event Categories (Bar Graph)", "Category", "Total Registrations")
    try:
        fig.tight_layout()
    except Exception:
        pass
    return fig


# ---------------------------------------------------------------------------
# Chart 8 — Performance Score Matrix Graph: Multi-Criteria Scores
# ---------------------------------------------------------------------------

def plot_performance_scores(df_perf: pd.DataFrame, top_n: int = 10) -> plt.Figure:
    """
    Ranked composite bar graph of Event Performance Scores (0-100) color-coded by tier.
    """
    fig, ax = plt.subplots(figsize=(11, 6), dpi=100)

    if df_perf is None or df_perf.empty:
        ax.text(0.5, 0.5, "No performance score data", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    score_col = "Performance Score" if "Performance Score" in df_perf.columns else None
    if not score_col:
        ax.text(0.5, 0.5, "No performance score data", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    subset = df_perf.head(top_n).sort_values(by=score_col, ascending=True)
    if subset.empty:
        ax.text(0.5, 0.5, "No performance score data", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    y_pos = np.arange(len(subset))
    scores = pd.to_numeric(subset[score_col], errors="coerce").fillna(0.0)

    tier_colors = {
        "Top Performer": COLOR_SUCCESS,
        "Average Performer": COLOR_ACCENT,
        "Needs Improvement": COLOR_DANGER,
    }
    tier_col = "Tier" if "Tier" in subset.columns else None
    colors = [tier_colors.get(str(t), COLOR_PRIMARY) for t in (subset[tier_col] if tier_col else [""]*len(subset))]

    bars = ax.barh(y_pos, scores, color=colors, height=0.6)

    for bar, idx in zip(bars, range(len(subset))):
        w = bar.get_width()
        tier_text = f" ({subset[tier_col].iloc[idx]})" if tier_col and pd.notnull(subset[tier_col].iloc[idx]) else ""
        ax.text(
            w + 0.8,
            bar.get_y() + bar.get_height() / 2,
            f"{w:.1f}{tier_text}",
            ha="left",
            va="center",
            fontsize=9,
            fontweight="bold",
            color="#1E293B",
        )

    name_col = "Event Name" if "Event Name" in subset.columns else ("event_name" if "event_name" in subset.columns else None)
    names = [str(n) if len(str(n)) <= 24 else str(n)[:21] + "..." for n in subset[name_col]] if name_col else [f"Event {i+1}" for i in y_pos]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)
    ax.set_xlim(0, 115)
    ax.axvline(70, color=COLOR_SUCCESS, linestyle="--", alpha=0.6, label="Top Threshold (70)")
    ax.axvline(40, color=COLOR_DANGER, linestyle="--", alpha=0.6, label="Improvement (40)")
    ax.legend(loc="lower right")

    _apply_theme(ax, "Event Performance Score Matrix (0 - 100 Multi-Tier Graph)", "Composite Performance Score", "Campus Event")
    try:
        fig.tight_layout()
    except Exception:
        pass
    return fig


def figure_to_bytes(fig: plt.Figure, format: str = "png") -> bytes:
    """Export a Matplotlib Figure into binary bytes for downloading in Streamlit."""
    buf = io.BytesIO()
    fig.savefig(buf, format=format, dpi=150, bbox_inches="tight")
    buf.seek(0)
    return buf.getvalue()
