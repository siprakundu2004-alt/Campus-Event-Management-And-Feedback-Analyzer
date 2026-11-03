"""
components/ui_helpers.py
------------------------
Presentation utilities, CSS injection, KPI cards, and status badge renderers
for the Streamlit frontend of Campus Event Management & Feedback Analyzer.
"""

import streamlit as st


def inject_custom_css() -> None:
    """Inject modern, clean, university-grade CSS styling into the Streamlit application."""
    custom_css = """
    <style>
    /* Global Fonts & Smoothing */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Clean up default margins */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
    }
    
    /* Modern Metric Cards */
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
    }
    .kpi-title {
        color: #64748B;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .kpi-value {
        color: #0F172A;
        font-size: 1.85rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .kpi-subtitle {
        color: #94A3B8;
        font-size: 0.78rem;
        margin-top: 4px;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-align: center;
    }
    .badge-open { background-color: #DEF7EC; color: #03543F; }
    .badge-full { background-color: #FEECDC; color: #9C4221; }
    .badge-closed { background-color: #F3F4F6; color: #374151; }
    .badge-completed { background-color: #E1EFFE; color: #1E429F; }
    .badge-cancelled { background-color: #FDE8E8; color: #9B1C1C; }
    .badge-draft { background-color: #EDEBFE; color: #5521B5; }
    
    .badge-top { background-color: #DEF7EC; color: #03543F; }
    .badge-avg { background-color: #FEF08A; color: #854D0E; }
    .badge-improve { background-color: #FEE2E2; color: #991B1B; }

    /* Event Card in Student Browse */
    .event-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .event-title {
        color: #1E3A8A;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .event-desc {
        color: #475569;
        font-size: 0.9rem;
        line-height: 1.4;
        margin-bottom: 12px;
    }
    .event-meta {
        color: #64748B;
        font-size: 0.82rem;
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        margin-bottom: 10px;
    }

    /* Role Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #1E3A8A 0%, #1E40AF 50%, #0D9488 100%);
        color: #FFFFFF;
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .header-banner h1 {
        color: #FFFFFF !important;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0 0 6px 0 !important;
        padding: 0 !important;
    }
    .header-banner p {
        color: #E2E8F0 !important;
        font-size: 0.95rem;
        margin: 0 !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_header(title: str, subtitle: str, badge_text: str = "") -> None:
    """Render a modern hero header banner at the top of a page/view."""
    badge_html = f"<span class='badge' style='background-color: rgba(255,255,255,0.2); color: #fff; margin-left: 10px;'>{badge_text}</span>" if badge_text else ""
    html = f'<div class="header-banner"><h1>{title}{badge_html}</h1><p>{subtitle}</p></div>'
    st.markdown(html, unsafe_allow_html=True)


def render_kpi(title: str, value: str, subtitle: str = "") -> None:
    """Render a single styled KPI card."""
    sub_html = f'<div class="kpi-subtitle">{subtitle}</div>' if subtitle else ""
    html = f'<div class="kpi-card"><div class="kpi-title">{title}</div><div class="kpi-value">{value}</div>{sub_html}</div>'
    st.markdown(html, unsafe_allow_html=True)



def get_status_badge_html(status: str) -> str:
    """Return an inline HTML badge styled for the given event or registration status."""
    st_lower = status.lower()
    if "open" in st_lower or "confirmed" in st_lower:
        cls = "badge-open"
    elif "full" in st_lower:
        cls = "badge-full"
    elif "closed" in st_lower:
        cls = "badge-closed"
    elif "completed" in st_lower or "attended" in st_lower:
        cls = "badge-completed"
    elif "cancelled" in st_lower:
        cls = "badge-cancelled"
    elif "draft" in st_lower:
        cls = "badge-draft"
    else:
        cls = "badge-closed"
    return f"<span class='badge {cls}'>{status}</span>"


def render_star_rating(rating: int, max_stars: int = 5) -> str:
    """Return gold stars string representation."""
    gold = "★" * rating
    empty = "☆" * (max_stars - rating)
    return f"<span style='color: #F59E0B; font-size: 1.1rem;'>{gold}</span><span style='color: #CBD5E1;'>{empty}</span>"
