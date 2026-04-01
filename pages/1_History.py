"""Historical dashboard - trends, metrics, and all past angles."""

import streamlit as st
import json
from html import escape

st.set_page_config(
    page_title="Volta - History",
    page_icon="📊",
    layout="wide",
)

st.sidebar.page_link("app.py", label="Story Angles", icon="⚡")
st.sidebar.page_link("pages/1_History.py", label="Historical Dashboard", icon="📊")
st.sidebar.divider()

from src.database import (
    init_db, get_all_angles, get_angles_by_month, get_articles_by_month,
    get_outlet_breakdown, get_articles_by_ids, toggle_angle_used,
)

init_db()

OUTLET_LABELS = {
    "trade_press": "Trade press",
    "consumer_tech": "Consumer tech",
    "business_press": "Business press",
    "local_news": "Local news",
    "lifestyle": "Lifestyle",
    "policy": "Policy",
}

MONTH_LABELS = {
    "2026-01": "Jan 2026",
    "2026-02": "Feb 2026",
    "2026-03": "Mar 2026",
    "2026-04": "Apr 2026",
}

st.markdown("# Historical dashboard")
st.markdown("*Track angle generation, pitch rates, and trends over time.*")
st.markdown("")

all_angles = get_all_angles()
total = len(all_angles)
pitched = sum(1 for a in all_angles if a.get("used"))
hit_rate = f"{(pitched / total * 100):.0f}%" if total > 0 else "N/A"

urgency_dist = {"high": 0, "medium": 0, "low": 0}
for a in all_angles:
    u = a.get("urgency", "medium").lower()
    if u in urgency_dist:
        urgency_dist[u] += 1

cols = st.columns(5)
with cols[0]:
    st.metric("Total angles", total)
with cols[1]:
    st.metric("Pitched", pitched)
with cols[2]:
    st.metric("Pitch rate", hit_rate)
with cols[3]:
    st.metric("High urgency", urgency_dist["high"])
with cols[4]:
    outlets_used = len(set(a.get("outlet_type", "") for a in all_angles if a.get("used")))
    st.metric("Outlets reached", outlets_used)

st.markdown("---")

monthly_angles = get_angles_by_month()
monthly_articles = get_articles_by_month()

if monthly_angles:
    st.markdown("### Monthly activity")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("**Angles generated vs pitched**")
        max_total = max(m["total"] for m in monthly_angles) if monthly_angles else 1
        bars_html = ""
        for m in monthly_angles:
            label = MONTH_LABELS.get(m["month"], m["month"])
            pitched_w = int(m["pitched"] / max_total * 100)
            not_pitched_w = int((m["total"] - m["pitched"]) / max_total * 100)
            bars_html += (
                f'<div style="margin-bottom: 12px;">'
                f'<div style="font-size: 13px; color: #888; margin-bottom: 4px;">{label}</div>'
                f'<div style="display: flex; align-items: center; gap: 4px;">'
                f'<div style="height: 24px; width: {pitched_w}%; background: #1D9E75; border-radius: 4px 0 0 4px; min-width: {2 if m["pitched"] > 0 else 0}px;"></div>'
                f'<div style="height: 24px; width: {not_pitched_w}%; background: #E0E0E0; border-radius: 0 4px 4px 0; min-width: {2 if (m["total"] - m["pitched"]) > 0 else 0}px;"></div>'
                f'<span style="font-size: 13px; color: #555; margin-left: 8px;">{m["pitched"]}/{m["total"]}</span>'
                f'</div></div>'
            )
        bars_html += '<div style="display: flex; gap: 16px; margin-top: 8px; font-size: 12px; color: #888;"><div><span style="display: inline-block; width: 12px; height: 12px; background: #1D9E75; border-radius: 2px; vertical-align: middle;"></span> Pitched</div><div><span style="display: inline-block; width: 12px; height: 12px; background: #E0E0E0; border-radius: 2px; vertical-align: middle;"></span> Not pitched</div></div>'
        st.markdown(bars_html, unsafe_allow_html=True)

    with chart_col2:
        st.markdown("**Articles ingested per month**")
        if monthly_articles:
            max_art = max(m["total"] for m in monthly_articles) if monthly_articles else 1
            art_html = ""
            for m in monthly_articles:
                label = MONTH_LABELS.get(m["month"], m["month"])
                bar_w = int(m["total"] / max_art * 100)
                art_html += (
                    f'<div style="margin-bottom: 12px;">'
                    f'<div style="font-size: 13px; color: #888; margin-bottom: 4px;">{label}</div>'
                    f'<div style="display: flex; align-items: center; gap: 4px;">'
                    f'<div style="height: 24px; width: {bar_w}%; background: #378ADD; border-radius: 4px; min-width: 2px;"></div>'
                    f'<span style="font-size: 13px; color: #555; margin-left: 8px;">{m["total"]} articles</span>'
                    f'</div></div>'
                )
            st.markdown(art_html, unsafe_allow_html=True)
        else:
            st.caption("No article data available.")
    st.markdown("")

outlet_data = get_outlet_breakdown()

if outlet_data:
    st.markdown("### Outlet type breakdown")
    breakdown_col1, breakdown_col2 = st.columns(2)

    with breakdown_col1:
        max_out = max(o["total"] for o in outlet_data) if outlet_data else 1
        out_html = ""
        for row in outlet_data:
            label = OUTLET_LABELS.get(row["outlet_type"], row["outlet_type"])
            pitched_w = int(row["pitched"] / max_out * 100)
            not_pitched_w = int((row["total"] - row["pitched"]) / max_out * 100)
            out_html += (
                f'<div style="margin-bottom: 12px;">'
                f'<div style="font-size: 13px; color: #888; margin-bottom: 4px;">{escape(label)}</div>'
                f'<div style="display: flex; align-items: center; gap: 4px;">'
                f'<div style="height: 24px; width: {pitched_w}%; background: #1D9E75; border-radius: 4px 0 0 4px; min-width: {2 if row["pitched"] > 0 else 0}px;"></div>'
                f'<div style="height: 24px; width: {not_pitched_w}%; background: #E0E0E0; border-radius: 0 4px 4px 0; min-width: {2 if (row["total"] - row["pitched"]) > 0 else 0}px;"></div>'
                f'<span style="font-size: 13px; color: #555; margin-left: 8px;">{row["pitched"]}/{row["total"]}</span>'
                f'</div></div>'
            )
        out_html += '<div style="display: flex; gap: 16px; margin-top: 8px; font-size: 12px; color: #888;"><div><span style="display: inline-block; width: 12px; height: 12px; background: #1D9E75; border-radius: 2px; vertical-align: middle;"></span> Pitched</div><div><span style="display: inline-block; width: 12px; height: 12px; background: #E0E0E0; border-radius: 2px; vertical-align: middle;"></span> Not pitched</div></div>'
        st.markdown(out_html, unsafe_allow_html=True)

    with breakdown_col2:
        st.markdown("")
        st.markdown("")
        for row in outlet_data:
            label = OUTLET_LABELS.get(row["outlet_type"], row["outlet_type"])
            rate = f"{row['pitched']}/{row['total']}"
            pct = f"{(row['pitched'] / row['total'] * 100):.0f}%" if row["total"] > 0 else "0%"
            st.markdown(f"**{label}**: {rate} pitched ({pct})")
    st.markdown("")

st.markdown("---")
st.markdown("### All angles")

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

import csv
import io

csv_buffer = io.StringIO()
writer = csv.writer(csv_buffer)
writer.writerow(["Headline", "News Peg", "Rationale", "Outlet Type", "Why This Outlet", "Urgency", "Pitched", "Generated"])
for a in filtered:
    writer.writerow([
        a.get("headline", ""),
        a.get("news_peg", ""),
        a.get("rationale", ""),
        OUTLET_LABELS.get(a.get("outlet_type", ""), a.get("outlet_type", "")),
        a.get("outlet_rationale", ""),
        a.get("urgency", "medium").title(),
        "Yes" if a.get("used") else "No",
        a.get("generated_at", "")[:10],
    ])

st.download_button(
    label="Download as CSV",
    data=csv_buffer.getvalue(),
    file_name="volta_angles_history.csv",
    mime="text/csv",
    icon="📥",
)

for angle in filtered:
    urgency = angle.get("urgency", "medium").lower()
    outlet = OUTLET_LABELS.get(angle.get("outlet_type", ""), angle.get("outlet_type", ""))
    is_used = bool(angle.get("used", 0))
    date = angle.get("generated_at", "")[:10]
    status_icon = "✅" if is_used else "⬜"
    urgency_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    u_icon = urgency_icons.get(urgency, "🟡")

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

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #AAA; font-size: 12px;'>"
    "Volta Story Angle Generator - Historical Dashboard - Powered by Claude"
    "</div>",
    unsafe_allow_html=True,
)
