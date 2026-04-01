"""Historical dashboard - trends, metrics, and all past angles."""

import streamlit as st
import json
import csv
import io
from html import escape

st.set_page_config(page_title="Volta - History", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap');
[data-testid="stSidebarNav"] { display: none; }
.volta-header { padding: 0 0 24px 0; margin-bottom: 8px; }
.volta-title { font-family: 'DM Serif Display', Georgia, serif; font-size: 34px; font-weight: 400; letter-spacing: -0.5px; margin: 0 0 6px 0; }
.volta-subtitle { font-family: 'DM Sans', sans-serif; font-size: 15px; color: #6B7280; margin: 0; line-height: 1.5; }
.stat-row { display: flex; gap: 12px; margin: 20px 0 24px 0; }
.stat-box { flex: 1; border: 1px solid #E5E7EB; border-radius: 10px; padding: 16px 12px; text-align: center; }
.stat-value { font-family: 'DM Sans', sans-serif; font-size: 28px; font-weight: 700; color: #111827; line-height: 1; }
.stat-value.accent { color: #0D6E4F; }
.stat-label { font-family: 'DM Sans', sans-serif; font-size: 12px; color: #9CA3AF; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
.section-title { font-family: 'DM Sans', sans-serif; font-size: 18px; font-weight: 600; color: #111827; margin: 0 0 4px 0; }
.section-desc { font-family: 'DM Sans', sans-serif; font-size: 13px; color: #9CA3AF; margin: 0 0 16px 0; }
.chart-label { font-family: 'DM Sans', sans-serif; font-size: 13px; color: #6B7280; margin-bottom: 5px; }
.bar-row { display: flex; align-items: center; gap: 4px; margin-bottom: 14px; }
.bar-fill { height: 28px; border-radius: 4px; transition: width 0.3s; }
.bar-value { font-family: 'DM Sans', sans-serif; font-size: 13px; color: #6B7280; margin-left: 10px; white-space: nowrap; }
.legend { display: flex; gap: 16px; margin-top: 10px; }
.legend-item { display: flex; align-items: center; gap: 5px; font-family: 'DM Sans', sans-serif; font-size: 12px; color: #9CA3AF; }
.legend-dot { width: 10px; height: 10px; border-radius: 3px; }
.section-divider { border: none; border-top: 1px solid #F3F4F6; margin: 28px 0; }
.volta-footer { text-align: center; font-family: 'DM Sans', sans-serif; font-size: 12px; color: #D1D5DB; padding: 20px 0 8px 0; }
</style>
""", unsafe_allow_html=True)

st.sidebar.page_link("app.py", label="Story Angles", icon="⚡")
st.sidebar.page_link("pages/1_History.py", label="Historical Dashboard", icon="📊")
st.sidebar.divider()

from src.database import (
    init_db, get_all_angles, get_angles_by_month, get_articles_by_month,
    get_outlet_breakdown, get_articles_by_ids, toggle_angle_used,
)

init_db()

OUTLET_LABELS = {
    "trade_press": "Trade press", "consumer_tech": "Consumer tech",
    "business_press": "Business press", "local_news": "Local news",
    "lifestyle": "Lifestyle", "policy": "Policy",
}
MONTH_LABELS = {"2026-01": "Jan", "2026-02": "Feb", "2026-03": "Mar", "2026-04": "Apr"}

# --- Header ---
st.markdown(
    '<div class="volta-header">'
    '<h1 class="volta-title">Historical dashboard</h1>'
    '<p class="volta-subtitle">Track performance over time. Measure what lands coverage and refine your strategy.</p>'
    '</div>',
    unsafe_allow_html=True,
)

all_angles = get_all_angles()
total = len(all_angles)
pitched = sum(1 for a in all_angles if a.get("used"))
hit_rate = f"{(pitched / total * 100):.0f}%" if total > 0 else "N/A"

urgency_dist = {"high": 0, "medium": 0, "low": 0}
for a in all_angles:
    u = a.get("urgency", "medium").lower()
    if u in urgency_dist:
        urgency_dist[u] += 1

outlets_used = len(set(a.get("outlet_type", "") for a in all_angles if a.get("used")))

st.markdown(
    f'<div class="stat-row">'
    f'<div class="stat-box"><div class="stat-value">{total}</div><div class="stat-label">Total angles</div></div>'
    f'<div class="stat-box"><div class="stat-value accent">{pitched}</div><div class="stat-label">Pitched</div></div>'
    f'<div class="stat-box"><div class="stat-value accent">{hit_rate}</div><div class="stat-label">Pitch rate</div></div>'
    f'<div class="stat-box"><div class="stat-value" style="color: #C62828;">{urgency_dist["high"]}</div><div class="stat-label">High urgency</div></div>'
    f'<div class="stat-box"><div class="stat-value">{outlets_used}</div><div class="stat-label">Outlets reached</div></div>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# --- Monthly trends ---
monthly_angles = get_angles_by_month()
monthly_articles = get_articles_by_month()

if monthly_angles:
    st.markdown('<div class="section-title">Monthly activity</div><div class="section-desc">Generation volume and pitch conversion by month.</div>', unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown('<div class="chart-label" style="font-weight: 600;">Angles generated vs pitched</div>', unsafe_allow_html=True)
        max_total = max(m["total"] for m in monthly_angles)
        bars = ""
        for m in monthly_angles:
            label = MONTH_LABELS.get(m["month"], m["month"])
            pw = int(m["pitched"] / max_total * 100)
            nw = int((m["total"] - m["pitched"]) / max_total * 100)
            bars += (
                f'<div class="chart-label">{label}</div>'
                f'<div class="bar-row">'
                f'<div class="bar-fill" style="width: {pw}%; background: #0D6E4F; border-radius: 4px 0 0 4px; min-width: {2 if m["pitched"] > 0 else 0}px;"></div>'
                f'<div class="bar-fill" style="width: {nw}%; background: #E5E7EB; border-radius: 0 4px 4px 0; min-width: {2 if (m["total"] - m["pitched"]) > 0 else 0}px;"></div>'
                f'<span class="bar-value">{m["pitched"]}/{m["total"]}</span>'
                f'</div>'
            )
        bars += '<div class="legend"><div class="legend-item"><div class="legend-dot" style="background: #0D6E4F;"></div>Pitched</div><div class="legend-item"><div class="legend-dot" style="background: #E5E7EB;"></div>Not pitched</div></div>'
        st.markdown(bars, unsafe_allow_html=True)

    with chart_col2:
        st.markdown('<div class="chart-label" style="font-weight: 600;">Articles ingested</div>', unsafe_allow_html=True)
        if monthly_articles:
            max_art = max(m["total"] for m in monthly_articles)
            art_bars = ""
            for m in monthly_articles:
                label = MONTH_LABELS.get(m["month"], m["month"])
                bw = int(m["total"] / max_art * 100)
                art_bars += (
                    f'<div class="chart-label">{label}</div>'
                    f'<div class="bar-row">'
                    f'<div class="bar-fill" style="width: {bw}%; background: #3B82F6; border-radius: 4px; min-width: 2px;"></div>'
                    f'<span class="bar-value">{m["total"]} articles</span>'
                    f'</div>'
                )
            st.markdown(art_bars, unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# --- Outlet breakdown ---
outlet_data = get_outlet_breakdown()

if outlet_data:
    st.markdown('<div class="section-title">Outlet breakdown</div><div class="section-desc">Which outlet types are performing best for pitches.</div>', unsafe_allow_html=True)
    out_col1, out_col2 = st.columns(2)

    with out_col1:
        max_out = max(o["total"] for o in outlet_data)
        out_bars = ""
        for row in outlet_data:
            label = OUTLET_LABELS.get(row["outlet_type"], row["outlet_type"])
            pw = int(row["pitched"] / max_out * 100)
            nw = int((row["total"] - row["pitched"]) / max_out * 100)
            out_bars += (
                f'<div class="chart-label">{escape(label)}</div>'
                f'<div class="bar-row">'
                f'<div class="bar-fill" style="width: {pw}%; background: #0D6E4F; border-radius: 4px 0 0 4px; min-width: {2 if row["pitched"] > 0 else 0}px;"></div>'
                f'<div class="bar-fill" style="width: {nw}%; background: #E5E7EB; border-radius: 0 4px 4px 0; min-width: {2 if (row["total"] - row["pitched"]) > 0 else 0}px;"></div>'
                f'<span class="bar-value">{row["pitched"]}/{row["total"]}</span>'
                f'</div>'
            )
        out_bars += '<div class="legend"><div class="legend-item"><div class="legend-dot" style="background: #0D6E4F;"></div>Pitched</div><div class="legend-item"><div class="legend-dot" style="background: #E5E7EB;"></div>Not pitched</div></div>'
        st.markdown(out_bars, unsafe_allow_html=True)

    with out_col2:
        st.markdown("")
        for row in outlet_data:
            label = OUTLET_LABELS.get(row["outlet_type"], row["outlet_type"])
            pct = f"{(row['pitched'] / row['total'] * 100):.0f}%" if row["total"] > 0 else "0%"
            st.markdown(f"**{label}**: {row['pitched']}/{row['total']} pitched ({pct})")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# --- All angles ---
st.markdown('<div class="section-title">All angles</div><div class="section-desc">Every angle generated. Filter by status, outlet, or urgency. Expand any row for details.</div>', unsafe_allow_html=True)

filter_col1, filter_col2, filter_col3 = st.columns(3)
with filter_col1:
    status_filter = st.selectbox("Status", ["All", "Pitched", "Not pitched"], key="hist_status")
with filter_col2:
    outlet_options = ["All"] + list(OUTLET_LABELS.values())
    outlet_filter = st.selectbox("Outlet", outlet_options, key="hist_outlet")
with filter_col3:
    urgency_filter = st.selectbox("Urgency", ["All", "High", "Medium", "Low"], key="hist_urgency")

filtered = all_angles
if status_filter == "Pitched":
    filtered = [a for a in filtered if a.get("used")]
elif status_filter == "Not pitched":
    filtered = [a for a in filtered if not a.get("used")]
if outlet_filter != "All":
    outlet_key = [k for k, v in OUTLET_LABELS.items() if v == outlet_filter]
    if outlet_key:
        filtered = [a for a in filtered if a.get("outlet_type") == outlet_key[0]]
if urgency_filter != "All":
    filtered = [a for a in filtered if a.get("urgency", "").lower() == urgency_filter.lower()]

st.caption(f"Showing {len(filtered)} of {total} angles")

csv_buffer = io.StringIO()
writer = csv.writer(csv_buffer)
writer.writerow(["Headline", "News Peg", "Rationale", "Outlet Type", "Why This Outlet", "Urgency", "Pitched", "Generated"])
for a in filtered:
    writer.writerow([
        a.get("headline", ""), a.get("news_peg", ""), a.get("rationale", ""),
        OUTLET_LABELS.get(a.get("outlet_type", ""), a.get("outlet_type", "")),
        a.get("outlet_rationale", ""), a.get("urgency", "medium").title(),
        "Yes" if a.get("used") else "No", a.get("generated_at", "")[:10],
    ])

st.download_button(label="Download as CSV", data=csv_buffer.getvalue(), file_name="volta_angles_history.csv", mime="text/csv")

for angle in filtered:
    urgency = angle.get("urgency", "medium").lower()
    outlet = OUTLET_LABELS.get(angle.get("outlet_type", ""), angle.get("outlet_type", ""))
    is_used = bool(angle.get("used", 0))
    date = angle.get("generated_at", "")[:10]
    status_icon = "✅" if is_used else "⬜"
    u_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    u_icon = u_icons.get(urgency, "🟡")

    with st.container():
        top_col, check_col = st.columns([6, 1])
        with top_col:
            st.markdown(
                f"{status_icon} {u_icon} **{escape(angle.get('headline', ''))}**  \n"
                f"*{escape(outlet)}* | {date} | {urgency.title()} urgency"
            )
        with check_col:
            new_val = st.checkbox("Pitched", value=is_used, key=f"hist_used_{angle['id']}", label_visibility="collapsed")
            if new_val != is_used:
                toggle_angle_used(angle["id"], new_val)
                st.rerun()
        with st.expander("Details"):
            st.markdown(f"**News peg:** {escape(angle.get('news_peg', 'N/A'))}")
            st.markdown(f"**Rationale:** {escape(angle.get('rationale', ''))}")
            st.markdown(f"**Why this outlet:** {escape(angle.get('outlet_rationale', 'N/A'))}")
            source_ids = angle.get("source_article_ids", "[]")
            if isinstance(source_ids, str):
                try:
                    source_ids = json.loads(source_ids)
                except json.JSONDecodeError:
                    source_ids = []
            if source_ids:
                st.markdown("**Source articles:**")
                sources = get_articles_by_ids(source_ids)
                for sa in sources:
                    st.markdown(f"- [{sa['title']}]({sa.get('url', '#')}) ({sa['source']}, {sa.get('published_date', 'N/A')})")
        st.markdown("")

st.markdown('<div class="volta-footer">Volta Story Angle Generator &middot; Historical Dashboard &middot; Powered by Claude</div>', unsafe_allow_html=True)
