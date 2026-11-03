"""
views/admin/reports_view.py
--------------------------
Administrator Formal Report Generation and Export Center.
Generates institutional-grade text and CSV reports, saved directly in
`reports/generated_reports/` with instant in-browser inspection and download.
"""

from pathlib import Path
import streamlit as st

from reports.report_generator import ReportGenerator
from components.ui_helpers import render_header
import config


def render_admin_reports() -> None:
    """Render the report generation control station."""
    generator = ReportGenerator()

    render_header(
        title="Official Reports & Data Exports",
        subtitle="Generate, archive, and download audit-ready institutional reports",
        badge_text="Reports",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px; height: 100%;">
                <h4 style="color: #1E3A8A; margin-top: 0;">📊 Event Performance</h4>
                <p style="color: #64748B; font-size: 0.85rem;">
                    Full audit of seat capacity, utilization percentage, feedback rating, and multi-factor performance tier.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Generate Event Report", type="primary", use_container_width=True):
            fpath, content = generator.generate_event_report()
            st.session_state["last_report_name"] = fpath.name
            st.session_state["last_report_content"] = content
            st.session_state["last_report_path"] = str(fpath)
            st.success(f"Generated: {fpath.name}")

    with col2:
        st.markdown(
            """
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px; height: 100%;">
                <h4 style="color: #0D9488; margin-top: 0;">🎓 Student Roster</h4>
                <p style="color: #64748B; font-size: 0.85rem;">
                    Comprehensive directory of all students, enrolled departments, degree courses, and lifetime participation counts.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Generate Student Report", type="primary", use_container_width=True):
            fpath, content = generator.generate_student_report()
            st.session_state["last_report_name"] = fpath.name
            st.session_state["last_report_content"] = content
            st.session_state["last_report_path"] = str(fpath)
            st.success(f"Generated: {fpath.name}")

    with col3:
        st.markdown(
            """
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px; height: 100%;">
                <h4 style="color: #7C3AED; margin-top: 0;">🏛️ Executive Summary</h4>
                <p style="color: #64748B; font-size: 0.85rem;">
                    High-level campus briefing combining event KPIs, NumPy empirical statistics, and top performers for university deans.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Generate Executive Brief", type="primary", use_container_width=True):
            fpath, content = generator.generate_executive_analytics_report()
            st.session_state["last_report_name"] = fpath.name
            st.session_state["last_report_content"] = content
            st.session_state["last_report_path"] = str(fpath)
            st.success(f"Generated: {fpath.name}")

    st.markdown("---")

    # Display generated report if available
    last_content = st.session_state.get("last_report_content")
    last_name = st.session_state.get("last_report_name")

    if last_content and last_name:
        st.markdown(f"#### 📄 Active Report Inspection: `{last_name}`")
        st.download_button(
            label=f"💾 Download {last_name}",
            data=last_content.encode("utf-8"),
            file_name=last_name,
            mime="text/plain",
            type="primary",
        )
        st.code(last_content, language="text")

    # Archive browser
    st.markdown("#### 📁 Archive of Previously Generated Reports")
    rep_files = sorted(config.REPORTS_DIR.glob("*.*"), key=lambda f: f.stat().st_mtime, reverse=True)

    if rep_files:
        items = []
        for f in rep_files[:15]:
            items.append({
                "Filename": f.name,
                "Format": f.suffix.replace(".", "").upper(),
                "Size (Bytes)": f.stat().st_size,
                "Last Modified": str(f.stat().st_mtime),
            })
        st.dataframe(items, use_container_width=True, hide_index=True)
    else:
        st.info("No saved reports in archive yet. Click any button above to generate your first report.")
