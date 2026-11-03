"""
views/admin/analytics_view.py
----------------------------
Administrator Deep Analytics & Data Visualization Hub.
Integrates statistical modeling, array aggregations,
and publication-grade visualization charts.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from analytics.event_analytics import EventAnalytics
from analytics.participation_analytics import ParticipationAnalytics
from analytics.feedback_analytics import FeedbackAnalytics
from services.feedback_service import FeedbackService
from visualization.charts import (
    plot_event_participation,
    plot_feedback_distribution,
    plot_popularity_vs_capacity,
    plot_average_ratings,
    plot_department_participation,
    plot_sentiment_breakdown,
    plot_category_analysis,
    plot_performance_scores,
    figure_to_bytes,
)
from components.ui_helpers import render_header, render_kpi


def render_admin_analytics() -> None:
    """Render the full analytical intelligence and charts suite."""
    evt_analytics = EventAnalytics()
    part_analytics = ParticipationAnalytics()
    fbk_analytics = FeedbackAnalytics()
    fbk_service = FeedbackService()

    render_header(
        title="Predictive & Empirical Analytics Hub",
        subtitle="Data-driven insights using aggregations, mathematical statistics, and visualization charts",
        badge_text="Data Intelligence",
    )

    tab_overview, tab_charts, tab_stats, tab_feedback, tab_scores = st.tabs([
        "📊 High-Level Metrics",
        "📈 Visualizations",
        "🧮 Statistical Analysis",
        "💬 Feedback Analyzer",
        "🏆 Event Performance Scoring",
    ])

    # -------------------------------------------------------------
    # TAB 1: High-Level Metrics
    # -------------------------------------------------------------
    with tab_overview:
        st.markdown("#### 🏛️ Campus-Wide Analytical Breakdown")

        part_table = part_analytics.get_event_participation_table()
        st.markdown("##### 📌 Event Participation & Capacity Efficiency")
        if not part_table.empty:
            st.dataframe(part_table, use_container_width=True, hide_index=True)
            csv_data = part_table.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Export Participation Ledger (CSV)",
                data=csv_data,
                file_name="event_participation_data.csv",
                mime="text/csv",
            )
        else:
            st.info("No participation data available.")

        st.markdown("---")
        col_dept, col_cat = st.columns(2)
        with col_dept:
            st.markdown("##### 🏢 Department-Wise Engagement")
            df_dept = part_analytics.get_department_participation()
            if not df_dept.empty:
                st.dataframe(df_dept, use_container_width=True, hide_index=True)

        with col_cat:
            st.markdown("##### 🏷️ Event Category Distribution")
            df_cat = evt_analytics.get_events_by_category()
            if not df_cat.empty:
                st.dataframe(df_cat, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 2: Visualizations (Bar Chart, Histogram Graph, Donut & Ranked)
    # -------------------------------------------------------------
    with tab_charts:
        st.markdown("#### 🎨 Publication-Quality Visualizations")
        st.caption("Interactive data visualization suite showcasing bar charts, histogram graphs, donut diagrams, and comparative matrix graphs.")

        view_mode = st.radio(
            "Visualization Display Mode",
            [
                "🖼️ All Visualizations Gallery (Bar, Histogram, Donut & Ranked Graphs)",
                "🔍 Single Chart Deep-Dive",
            ],
            horizontal=True,
        )

        st.markdown("---")

        df_table = part_analytics.get_event_participation_table()
        df_dist = fbk_analytics.get_rating_distribution()
        df_summary = fbk_analytics.get_event_feedback_summary()
        df_dept = part_analytics.get_department_participation()
        df_cat = part_analytics.get_category_participation()
        df_perf = fbk_analytics.get_event_performance_scores()
        summary_kpis = fbk_analytics.get_summary_metrics()

        if view_mode == "🖼️ All Visualizations Gallery (Bar, Histogram, Donut & Ranked Graphs)":
            st.markdown("### 📊 Interactive Visualizations Gallery")

            # Row 1: Bar Chart & Histogram Graph
            r1_c1, r1_c2 = st.columns(2)
            with r1_c1:
                st.markdown("##### 📊 1. Event Participation (Bar Chart)")
                fig1 = plot_event_participation(df_table, top_n=10)
                st.pyplot(fig1)
                st.download_button("💾 Download Bar Chart (PNG)", figure_to_bytes(fig1), "chart_bar_participation.png", "image/png", key="dl_gallery_1")
                plt.close(fig1)

            with r1_c2:
                st.markdown("##### 📶 2. Feedback Rating Frequency (Histogram Graph)")
                fig2 = plot_feedback_distribution(df_dist)
                st.pyplot(fig2)
                st.download_button("💾 Download Histogram (PNG)", figure_to_bytes(fig2), "chart_histogram_feedback.png", "image/png", key="dl_gallery_2")
                plt.close(fig2)

            st.markdown("---")

            # Row 2: Grouped Bar & Department Donut/Bar Graph
            r2_c1, r2_c2 = st.columns(2)
            with r2_c1:
                st.markdown("##### 📊 3. Registration vs Capacity (Grouped Bar Graph)")
                fig3 = plot_popularity_vs_capacity(df_table, top_n=8)
                st.pyplot(fig3)
                st.download_button("💾 Download Grouped Bar (PNG)", figure_to_bytes(fig3), "chart_grouped_capacity.png", "image/png", key="dl_gallery_3")
                plt.close(fig3)

            with r2_c2:
                st.markdown("##### 🍩 4. Department Engagement (Dual Donut & Bar Graph)")
                fig4 = plot_department_participation(df_dept)
                st.pyplot(fig4)
                st.download_button("💾 Download Department Graph (PNG)", figure_to_bytes(fig4), "chart_donut_department.png", "image/png", key="dl_gallery_4")
                plt.close(fig4)

            st.markdown("---")

            # Row 3: Average Ratings & Sentiment Donut
            r3_c1, r3_c2 = st.columns(2)
            with r3_c1:
                st.markdown("##### 📈 5. Average Ratings Benchmark (Bar Graph)")
                fig5 = plot_average_ratings(df_summary)
                st.pyplot(fig5)
                st.download_button("💾 Download Benchmark Graph (PNG)", figure_to_bytes(fig5), "chart_benchmark_ratings.png", "image/png", key="dl_gallery_5")
                plt.close(fig5)

            with r3_c2:
                st.markdown("##### 🍩 6. Student Sentiment Share (Dual Donut & Bar Graph)")
                fig6 = plot_sentiment_breakdown(summary_kpis)
                st.pyplot(fig6)
                st.download_button("💾 Download Sentiment Graph (PNG)", figure_to_bytes(fig6), "chart_donut_sentiment.png", "image/png", key="dl_gallery_6")
                plt.close(fig6)

            st.markdown("---")

            # Row 4: Category Analysis & Performance Scores
            r4_c1, r4_c2 = st.columns(2)
            with r4_c1:
                st.markdown("##### 🏷️ 7. Event Category Analysis (Categorical Bar Graph)")
                fig7 = plot_category_analysis(df_cat)
                st.pyplot(fig7)
                st.download_button("💾 Download Category Graph (PNG)", figure_to_bytes(fig7), "chart_bar_category.png", "image/png", key="dl_gallery_7")
                plt.close(fig7)

            with r4_c2:
                st.markdown("##### 🏆 8. Composite Performance Scores (Ranked Matrix Graph)")
                fig8 = plot_performance_scores(df_perf, top_n=10)
                st.pyplot(fig8)
                st.download_button("💾 Download Score Matrix (PNG)", figure_to_bytes(fig8), "chart_score_matrix.png", "image/png", key="dl_gallery_8")
                plt.close(fig8)

        else:
            # Single Chart Deep-Dive
            chart_select = st.selectbox(
                "Select Specific Analytical Chart",
                [
                    "📊 Bar Chart — Event Participation (Participants per Event)",
                    "📶 Histogram Graph — Student Feedback Rating Frequency (1 to 5 Stars)",
                    "📊 Grouped Bar Graph — Event Popularity vs Capacity Comparison",
                    "📈 Benchmark Bar Graph — Average Event Rating Comparison",
                    "🍩 Dual Donut & Bar Graph — Department Participation Distribution",
                    "🍩 Dual Donut & Bar Graph — Student Sentiment Breakdown",
                    "📊 Categorical Bar Graph — Category Analysis & Engagement",
                    "🏆 Score Matrix Graph — Multi-Tier Event Performance Scores",
                ],
            )

            fig = None
            chart_name = "chart.png"

            if "Event Participation" in chart_select:
                top_n = st.slider("Number of Top Events to Display", 5, 15, 10)
                fig = plot_event_participation(df_table, top_n=top_n)
                chart_name = "chart_bar_participation.png"

            elif "Histogram Graph" in chart_select:
                fig = plot_feedback_distribution(df_dist)
                chart_name = "chart_histogram_feedback.png"

            elif "Grouped Bar Graph" in chart_select:
                top_n = st.slider("Number of Events to Compare", 4, 12, 8)
                fig = plot_popularity_vs_capacity(df_table, top_n=top_n)
                chart_name = "chart_grouped_capacity.png"

            elif "Benchmark Bar Graph" in chart_select:
                fig = plot_average_ratings(df_summary)
                chart_name = "chart_benchmark_ratings.png"

            elif "Department Participation" in chart_select:
                fig = plot_department_participation(df_dept)
                chart_name = "chart_donut_department.png"

            elif "Sentiment Breakdown" in chart_select:
                fig = plot_sentiment_breakdown(summary_kpis)
                chart_name = "chart_donut_sentiment.png"

            elif "Category Analysis" in chart_select:
                fig = plot_category_analysis(df_cat)
                chart_name = "chart_bar_category.png"

            elif "Score Matrix Graph" in chart_select:
                top_n = st.slider("Number of Top Events to Score", 5, 15, 10)
                fig = plot_performance_scores(df_perf, top_n=top_n)
                chart_name = "chart_score_matrix.png"

            if fig is not None:
                chart_bytes = figure_to_bytes(fig)
                st.pyplot(fig)
                st.download_button(
                    "💾 Download Chart as PNG",
                    data=chart_bytes,
                    file_name=chart_name,
                    mime="image/png",
                )
                plt.close(fig)

    # -------------------------------------------------------------
    # TAB 3: Statistical Analysis
    # -------------------------------------------------------------
    with tab_stats:
        st.markdown("#### 🧮 Numerical & Statistical Foundations")
        st.caption(
            "Empirical verification of feedback distributions. "
            "Includes central tendency, dispersion, and quantile distributions."
        )

        num_stats = fbk_analytics.get_numpy_statistics()

        if num_stats:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                render_kpi("Sample Size (N)", str(num_stats["sample_size"]), "Total Student Reviews")
                render_kpi("Minimum Rating", f"{num_stats['min_rating']} ★", "Floor Observation")
            with c2:
                render_kpi("Arithmetic Mean (μ)", f"{num_stats['mean']:.3f}", "Mean Value")
                render_kpi("Maximum Rating", f"{num_stats['max_rating']} ★", "Ceiling Observation")
            with c3:
                render_kpi("Median Rating", f"{num_stats['median']:.2f}", "50th Percentile")
                render_kpi("Interquartile Range", f"{num_stats['interquartile_range']:.2f}", "IQR = Q3 - Q1")
            with c4:
                render_kpi("Standard Deviation (σ)", f"{num_stats['standard_deviation']:.3f}", "Standard Deviation")
                render_kpi("Variance (σ²)", f"{num_stats['variance']:.3f}", "Variance")

            st.markdown("##### 📐 Quantile Breakdown")
            q_df = pd.DataFrame([
                {"Quantile": "25th Percentile (Q1)", "Value": num_stats["percentile_25"], "Method": "25th Percentile"},
                {"Quantile": "50th Percentile (Median)", "Value": num_stats["median"], "Method": "Median Value"},
                {"Quantile": "75th Percentile (Q3)", "Value": num_stats["percentile_75"], "Method": "75th Percentile"},
                {"Quantile": "Interquartile Range (IQR)", "Value": num_stats["interquartile_range"], "Method": "IQR (Q3 - Q1)"},
            ])
            st.table(q_df)
        else:
            st.info("Insufficient feedback data for statistical computation.")

    # -------------------------------------------------------------
    # TAB 4: Feedback Analyzer
    # -------------------------------------------------------------
    with tab_feedback:
        st.markdown("#### 💬 Student Feedback & Sentiment Analyzer")
        st.caption("Deep sentiment breakdown, qualitative review analysis, and student satisfaction metrics.")

        summary = fbk_analytics.get_summary_metrics()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_kpi("Total Reviews", str(summary.get("total_feedback", 0)), f"{summary.get('events_reviewed', 0)} Events Reviewed")
        with col2:
            avg_r = summary.get("overall_avg_rating", 0.0)
            star_display = "★" * int(round(avg_r)) if avg_r > 0 else "—"
            render_kpi("Overall Rating", f"{avg_r:.2f} ★", star_display)
        with col3:
            render_kpi("Positive Sentiment", f"{summary.get('positive_percentage', 0.0)}%", "Ratings 4-5 ★")
        with col4:
            render_kpi("Critical / Low Ratings", f"{summary.get('negative_percentage', 0.0)}%", "Ratings 1-2 ★")

        st.markdown("---")

        all_feedbacks = fbk_service.list_all_feedback()
        df_fbk = pd.DataFrame(all_feedbacks)

        if not df_fbk.empty:
            st.markdown("##### 🔍 Filter & Explore Reviews")
            f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
            with f_col1:
                event_options = ["All Events"] + sorted(df_fbk["event_name"].dropna().unique().tolist())
                selected_event = st.selectbox("Filter by Event", event_options)
            with f_col2:
                rating_filter = st.selectbox(
                    "Filter by Rating",
                    ["All Ratings", "5 Stars (Excellent)", "4 Stars (Very Good)", "3 Stars (Good)", "2 Stars (Fair)", "1 Star (Poor)"]
                )
            with f_col3:
                sentiment_filter = st.selectbox(
                    "Filter by Sentiment",
                    ["All Sentiments", "Positive (4-5 ★)", "Neutral (3 ★)", "Critical (1-2 ★)"]
                )

            filtered_df = df_fbk.copy()
            if selected_event != "All Events":
                filtered_df = filtered_df[filtered_df["event_name"] == selected_event]

            if rating_filter != "All Ratings":
                target_star = int(rating_filter[0])
                filtered_df = filtered_df[filtered_df["rating"] == target_star]

            if sentiment_filter == "Positive (4-5 ★)":
                filtered_df = filtered_df[filtered_df["rating"] >= 4]
            elif sentiment_filter == "Neutral (3 ★)":
                filtered_df = filtered_df[filtered_df["rating"] == 3]
            elif sentiment_filter == "Critical (1-2 ★)":
                filtered_df = filtered_df[filtered_df["rating"] <= 2]

            # ---------------------------------------------------------
            # REAL-TIME INTERACTIVE / MOVABLE FEEDBACK ANALYSIS CHARTS
            # ---------------------------------------------------------
            st.markdown("---")
            st.markdown("##### ⚡ Real-Time Movable Feedback Analysis Charts")
            st.caption("Interactive charts powered by Plotly. Drag to pan/move across the chart, scroll to zoom, hover for real-time review statistics, and click legend items to filter.")

            if not filtered_df.empty:
                # 1. Real-Time Rating Distribution (Movable Bar Chart)
                star_counts = {r: int((filtered_df["rating"] == r).sum()) for r in range(1, 6)}
                star_total = len(filtered_df)
                df_star_plot = pd.DataFrame([
                    {
                        "Rating": f"★ {r}",
                        "Reviews": star_counts[r],
                        "Percentage": round((star_counts[r] / star_total * 100), 1) if star_total > 0 else 0.0,
                    }
                    for r in range(1, 6)
                ])

                star_palette = ["#EF4444", "#F97316", "#FBBF24", "#34D399", "#10B981"]

                fig_bar = go.Figure(data=[
                    go.Bar(
                        x=df_star_plot["Rating"],
                        y=df_star_plot["Reviews"],
                        marker=dict(color=star_palette, line=dict(color="#0F172A", width=0.5)),
                        text=[f"{c} ({p}%)" for c, p in zip(df_star_plot["Reviews"], df_star_plot["Percentage"])],
                        textposition="auto",
                        hovertemplate="<b>Rating: %{x}</b><br>Reviews: %{y}<br>Share: %{customdata}%<extra></extra>",
                        customdata=df_star_plot["Percentage"],
                    )
                ])
                fig_bar.update_layout(
                    title=dict(text="Real-Time Rating Frequency (Movable Bar Chart)", font=dict(size=13, color="#0F172A")),
                    xaxis=dict(title="Rating Scale", tickfont=dict(size=11)),
                    yaxis=dict(title="Number of Reviews", rangemode="tozero"),
                    dragmode="pan",
                    margin=dict(l=30, r=20, t=40, b=30),
                    height=340,
                )

                # 2. Real-Time Sentiment Breakdown (Movable Donut Graph)
                pos_count = int((filtered_df["rating"] >= 4).sum())
                neu_count = int((filtered_df["rating"] == 3).sum())
                neg_count = int((filtered_df["rating"] <= 2).sum())

                fig_pie = go.Figure(data=[
                    go.Pie(
                        labels=["Positive (4-5 ★)", "Neutral (3 ★)", "Critical (1-2 ★)"],
                        values=[pos_count, neu_count, neg_count],
                        hole=0.45,
                        marker=dict(colors=["#10B981", "#FBBF24", "#EF4444"]),
                        textinfo="label+percent",
                        hovertemplate="<b>%{label}</b><br>Reviews: %{value}<br>Share: %{percent}<extra></extra>",
                    )
                ])
                fig_pie.update_layout(
                    title=dict(text="Real-Time Sentiment Proportion (Movable Donut Graph)", font=dict(size=13, color="#0F172A")),
                    margin=dict(l=20, r=20, t=40, b=30),
                    height=340,
                    showlegend=True,
                )

                mc1, mc2 = st.columns(2)
                with mc1:
                    st.plotly_chart(
                        fig_bar,
                        use_container_width=True,
                        config={"scrollZoom": True, "displayModeBar": True},
                    )
                with mc2:
                    st.plotly_chart(
                        fig_pie,
                        use_container_width=True,
                        config={"scrollZoom": True, "displayModeBar": True},
                    )

                # 3. If "All Events" is selected, show movable event average rating benchmark
                if selected_event == "All Events" and "event_name" in filtered_df.columns:
                    event_stats = filtered_df.groupby("event_name").agg(
                        Avg_Rating=("rating", "mean"),
                        Reviews=("feedback_id", "count"),
                    ).reset_index().sort_values(by="Avg_Rating", ascending=True)

                    if len(event_stats) > 1:
                        fig_evt = go.Figure(data=[
                            go.Bar(
                                y=[n if len(n) <= 25 else n[:22] + "..." for n in event_stats["event_name"]],
                                x=event_stats["Avg_Rating"].round(2),
                                orientation="h",
                                marker=dict(
                                    color=event_stats["Avg_Rating"],
                                    colorscale="Tealgrn",
                                    cmin=1.0,
                                    cmax=5.0,
                                    colorbar=dict(title="Rating ★"),
                                ),
                                text=[f"{r:.2f} ★ ({c} reviews)" for r, c in zip(event_stats["Avg_Rating"], event_stats["Reviews"])],
                                textposition="auto",
                                hovertemplate="<b>%{y}</b><br>Average Rating: %{x} ★<br>Reviews: %{customdata}<extra></extra>",
                                customdata=event_stats["Reviews"],
                            )
                        ])
                        fig_evt.add_vline(x=4.0, line_width=2, line_dash="dash", line_color="#10B981", annotation_text="Benchmark (4.0 ★)")
                        fig_evt.update_layout(
                            title=dict(text="Real-Time Event Average Rating Benchmark (Movable Horizontal Bar)", font=dict(size=13, color="#0F172A")),
                            xaxis=dict(title="Average Rating (0 to 5 Stars)", range=[0, 5.5]),
                            yaxis=dict(title="Campus Event"),
                            dragmode="pan",
                            margin=dict(l=30, r=20, t=40, b=30),
                            height=320,
                        )
                        st.plotly_chart(
                            fig_evt,
                            use_container_width=True,
                            config={"scrollZoom": True, "displayModeBar": True},
                        )
            else:
                st.info("No reviews match the selected filter criteria to display real-time charts.")

            st.markdown("---")

            # Event Summary Breakdown
            st.markdown("##### 📊 Event-Wise Feedback Breakdown")
            df_event_summary = fbk_analytics.get_event_feedback_summary()
            if not df_event_summary.empty:
                display_cols = ["event_id", "event_name", "category", "Avg_Rating", "Review_Count", "Positive_Reviews", "Negative_Reviews"]
                existing_cols = [c for c in display_cols if c in df_event_summary.columns]
                renamed_summary = df_event_summary[existing_cols].rename(columns={
                    "event_id": "Event ID",
                    "event_name": "Event Name",
                    "category": "Category",
                    "Avg_Rating": "Avg Rating ★",
                    "Review_Count": "Total Reviews",
                    "Positive_Reviews": "Positive (4-5★)",
                    "Negative_Reviews": "Critical (1-2★)",
                })
                st.dataframe(renamed_summary, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown(f"##### 📝 Student Qualitative Reviews ({len(filtered_df)} Matching)")

            if not filtered_df.empty:
                def get_sentiment_badge(r):
                    if r >= 4:
                        return "🟢 Positive"
                    elif r == 3:
                        return "🟡 Neutral"
                    return "🔴 Critical"

                filtered_df["Sentiment"] = filtered_df["rating"].apply(get_sentiment_badge)
                
                # Check for date column dynamically
                date_col = "submission_date" if "submission_date" in filtered_df.columns else ("submitted_at" if "submitted_at" in filtered_df.columns else None)
                cols_to_use = ["feedback_id", "event_name", "student_name", "student_id", "rating", "Sentiment", "comment"]
                if date_col:
                    cols_to_use.append(date_col)

                display_feedback = filtered_df[[c for c in cols_to_use if c in filtered_df.columns]].rename(columns={
                    "feedback_id": "Feedback ID",
                    "event_name": "Event",
                    "student_name": "Student Name",
                    "student_id": "Student ID",
                    "rating": "Rating (1-5)",
                    "comment": "Student Comment / Review",
                    "submission_date": "Submitted At",
                    "submitted_at": "Submitted At",
                })
                st.dataframe(display_feedback, use_container_width=True, hide_index=True)

                csv_fbk = display_feedback.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Export Feedback Analysis (CSV)",
                    data=csv_fbk,
                    file_name="feedback_analysis_export.csv",
                    mime="text/csv",
                )
            else:
                st.info("No reviews match the selected filters.")
        else:
            st.info("No feedback records available in the system.")

    # -------------------------------------------------------------
    # TAB 5: Event Performance Scoring
    # -------------------------------------------------------------
    with tab_scores:
        st.markdown("#### 🏆 Multi-Criteria Event Performance Score (0 - 100)")

        perf_scores = fbk_analytics.get_event_performance_scores()
        if not perf_scores.empty:
            st.dataframe(perf_scores, use_container_width=True, hide_index=True)
            csv_scores = perf_scores.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Export Performance Matrix (CSV)",
                data=csv_scores,
                file_name="event_performance_matrix.csv",
                mime="text/csv",
            )
        else:
            st.info("No performance scores computed yet.")
