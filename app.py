"""Volta Story Angle Generator - Streamlit Dashboard."""

import streamlit as st
import json
import csv
import io
from datetime import datetime
from html import escape

st.set_page_config(
    page_title="Volta - Story Angle Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- Helpers ---

def get_keys():
    import os
    anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))
    newsapi_key = st.secrets.get("NEWSAPI_KEY", os.getenv("NEWSAPI_KEY", ""))
    return anthropic_key, newsapi_key


def clean(text):
    return escape(str(text)).replace("\n", " ").replace("\r", "")


URGENCY_CONFIG = {
    "high": {"color": "#C62828", "bg": "#FFEBEE", "label": "High", "dot": "#C62828"},
    "medium": {"color": "#E65100", "bg": "#FFF3E0", "label": "Medium", "dot": "#E65100"},
    "low": {"color": "#2E7D32", "bg": "#E8F5E9", "label": "Low", "dot": "#2E7D32"},
}

OUTLET_LABELS = {
    "trade_press": "Trade press",
    "consumer_tech": "Consumer tech",
    "business_press": "Business press",
    "local_news": "Local news",
    "lifestyle": "Lifestyle",
    "policy": "Policy",
}


# --- Design System CSS ---

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap');

[data-testid="stSidebarNav"] { display: none; }

.volta-header {
    padding: 0 0 24px 0;
    margin-bottom: 8px;
}
.volta-title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 34px;
    font-weight: 400;
    letter-spacing: -0.5px;
    margin: 0 0 6px 0;
}
.volta-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    color: #6B7280;
    margin: 0;
    line-height: 1.5;
}

.stat-row {
    display: flex;
    gap: 12px;
    margin: 20px 0 24px 0;
}
.stat-box {
    flex: 1;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 16px 12px;
    text-align: center;
}
.stat-value {
    font-family: 'DM Sans', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #111827;
    line-height: 1;
}
.stat-value.accent { color: #0D6E4F; }
.stat-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    color: #9CA3AF;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.angle-card {
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 24px 28px;
    margin-bottom: 12px;
    transition: border-color 0.15s;
}
.angle-card:hover { border-color: #D1D5DB; }
.angle-card.pitched {
    border-left: 3px solid #0D6E4F;
}
.angle-badges {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}
.pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 11px;
    border-radius: 100px;
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    font-weight: 500;
}
.pill-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    display: inline-block;
}
.pill-outlet {
    background: #F0F4FF;
    color: #3B5998;
}
.pill-pitched {
    background: #ECFDF5;
    color: #065F46;
}

.angle-headline {
    font-family: 'DM Sans', sans-serif;
    font-size: 18px;
    font-weight: 600;
    color: #111827;
    line-height: 1.4;
    margin-bottom: 10px;
}
.angle-peg {
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    color: #0D6E4F;
    font-weight: 500;
    margin-bottom: 12px;
    line-height: 1.5;
    padding-left: 14px;
    border-left: 2px solid #A7F3D0;
}
.angle-rationale {
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    color: #4B5563;
    line-height: 1.65;
    margin-bottom: 12px;
}
.angle-outlet-note {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    color: #9CA3AF;
    line-height: 1.5;
}
.angle-outlet-note strong {
    color: #6B7280;
    font-weight: 500;
}

.section-divider {
    border: none;
    border-top: 1px solid #F3F4F6;
    margin: 28px 0;
}

.volta-footer {
    text-align: center;
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    color: #D1D5DB;
    padding: 20px 0 8px 0;
}
</style>
""", unsafe_allow_html=True)


# --- Sidebar ---

st.sidebar.page_link("app.py", label="Story Angles", icon="⚡")
st.sidebar.page_link("pages/1_History.py", label="Historical Dashboard", icon="📊")
st.sidebar.divider()

from src.database import (
    init_db, get_angles, get_articles_by_ids, get_db_stats, get_top_articles,
    get_blocked_terms, add_blocked_term, remove_blocked_term,
    get_custom_instructions, set_custom_instructions,
    toggle_angle_used,
)

init_db()

_initial_stats = get_db_stats()
if _initial_stats["articles"] == 0:
    from seed_data import seed
    from seed_history import seed_history
    seed()
    seed_history()

stats = get_db_stats()

st.sidebar.markdown("### Pipeline stats")
st.sidebar.caption("Data from the latest pipeline run.")
st.sidebar.metric("Articles ingested", stats["articles"])
st.sidebar.metric("Classified", stats["classified"])
st.sidebar.metric("Angles generated", stats["angles"])

if stats["sources"]:
    st.sidebar.markdown("### Sources")
    for source in sorted(stats["sources"]):
        st.sidebar.markdown(f"- {source}")

st.sidebar.divider()

st.sidebar.markdown("### Filters")
st.sidebar.caption("Narrow angles by outlet type or urgency.")

outlet_options = ["All"] + list(OUTLET_LABELS.values())
selected_outlet = st.sidebar.selectbox("Outlet type", outlet_options)

urgency_options = ["All", "High", "Medium", "Low"]
selected_urgency = st.sidebar.selectbox("Urgency", urgency_options)

st.sidebar.divider()

st.sidebar.markdown("### Run pipeline")
st.sidebar.caption("Fetch new articles, classify, and generate fresh angles.")
if st.sidebar.button("Refresh - Fetch & Generate", use_container_width=True, type="primary"):
    anthropic_key, newsapi_key = get_keys()
    if not anthropic_key:
        st.sidebar.error("Missing Anthropic API key.")
    else:
        from src.pipeline import run_full_pipeline
        with st.spinner("Running full pipeline..."):
            try:
                result = run_full_pipeline(newsapi_key, anthropic_key)
                st.sidebar.success(
                    f"Done! {result['ingestion']['inserted']} articles, "
                    f"{result['generation']['angles']} angles."
                )
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Pipeline error: {e}")

st.sidebar.divider()

st.sidebar.markdown("### Team instructions")
st.sidebar.caption("Guide angle generation. Saved automatically.")

current_instructions = get_custom_instructions()
new_instructions = st.sidebar.text_area(
    "Custom instructions",
    value=current_instructions,
    height=100,
    placeholder="e.g. Our CEO is available for grid reliability commentary.\nAvoid angles about Tesla unless they impact charging.\nWe have a Texas launch in April.",
    label_visibility="collapsed",
)
if new_instructions != current_instructions:
    set_custom_instructions(new_instructions)
    st.sidebar.success("Saved")

st.sidebar.divider()

st.sidebar.markdown("### Blocked topics")
st.sidebar.caption("Articles matching these terms are filtered out.")

blocked = get_blocked_terms()

col_input, col_btn = st.sidebar.columns([3, 1])
with col_input:
    new_term = st.text_input("Add term", placeholder="e.g. tesla, crypto", label_visibility="collapsed")
with col_btn:
    if st.button("Add", use_container_width=True) and new_term.strip():
        add_blocked_term(new_term.strip())
        st.rerun()

if blocked:
    for term in blocked:
        col_label, col_x = st.sidebar.columns([4, 1])
        with col_label:
            st.markdown(f"`{term['term']}`")
        with col_x:
            if st.button("x", key=f"rm_{term['id']}", use_container_width=True):
                remove_blocked_term(term["id"])
                st.rerun()
else:
    st.sidebar.caption("No blocked topics yet.")


# --- Main Content ---

st.markdown(
    '<div class="volta-header">'
    '<h1 class="volta-title">Today\'s story angles</h1>'
    '<p class="volta-subtitle">AI-generated pitch ideas grounded in recent news. Expand any angle to see source articles.</p>'
    '</div>',
    unsafe_allow_html=True,
)

outlet_filter = None
if selected_outlet != "All":
    outlet_filter = [k for k, v in OUTLET_LABELS.items() if v == selected_outlet]
    outlet_filter = outlet_filter[0] if outlet_filter else None

urgency_filter = selected_urgency.lower() if selected_urgency != "All" else None
angles = get_angles(outlet_type=outlet_filter, urgency=urgency_filter)

if not angles:
    st.info("No angles yet. Click **Refresh** in the sidebar to run the pipeline, or adjust your filters.")
else:
    urgency_counts = {"high": 0, "medium": 0, "low": 0}
    pitched_count = 0
    for a in angles:
        u = a.get("urgency", "medium").lower()
        if u in urgency_counts:
            urgency_counts[u] += 1
        if a.get("used"):
            pitched_count += 1

    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-box"><div class="stat-value">{len(angles)}</div><div class="stat-label">Total</div></div>'
        f'<div class="stat-box"><div class="stat-value accent">{pitched_count}</div><div class="stat-label">Pitched</div></div>'
        f'<div class="stat-box"><div class="stat-value" style="color: #C62828;">{urgency_counts["high"]}</div><div class="stat-label">High</div></div>'
        f'<div class="stat-box"><div class="stat-value" style="color: #E65100;">{urgency_counts["medium"]}</div><div class="stat-label">Medium</div></div>'
        f'<div class="stat-box"><div class="stat-value" style="color: #2E7D32;">{urgency_counts["low"]}</div><div class="stat-label">Low</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["Headline", "News Peg", "Rationale", "Outlet Type", "Why This Outlet", "Urgency", "Pitched", "Generated"])
    for a in angles:
        writer.writerow([
            a.get("headline", ""), a.get("news_peg", ""), a.get("rationale", ""),
            OUTLET_LABELS.get(a.get("outlet_type", ""), a.get("outlet_type", "")),
            a.get("outlet_rationale", ""), a.get("urgency", "medium").title(),
            "Yes" if a.get("used") else "No", a.get("generated_at", "")[:10],
        ])

    st.download_button(
        label="Download as CSV",
        data=csv_buffer.getvalue(),
        file_name="volta_angles.csv",
        mime="text/csv",
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    for angle in angles:
        urgency = angle.get("urgency", "medium").lower()
        uc = URGENCY_CONFIG.get(urgency, URGENCY_CONFIG["medium"])
        outlet = OUTLET_LABELS.get(angle.get("outlet_type", ""), angle.get("outlet_type", ""))
        is_used = bool(angle.get("used", 0))

        pitched_pill = f'<span class="pill pill-pitched">Pitched</span>' if is_used else ""
        card_class = "angle-card pitched" if is_used else "angle-card"

        card_html = (
            f'<div class="{card_class}">'
            f'<div class="angle-badges">'
            f'<span class="pill" style="background: {uc["bg"]}; color: {uc["color"]};"><span class="pill-dot" style="background: {uc["dot"]};"></span>{uc["label"]}</span>'
            f'<span class="pill pill-outlet">{clean(outlet)}</span>'
            f'{pitched_pill}'
            f'</div>'
            f'<div class="angle-headline">{clean(angle.get("headline", ""))}</div>'
            f'<div class="angle-peg">{clean(angle.get("news_peg", "N/A"))}</div>'
            f'<div class="angle-rationale">{clean(angle.get("rationale", ""))}</div>'
            f'<div class="angle-outlet-note"><strong>Why this outlet:</strong> {clean(angle.get("outlet_rationale", "N/A"))}</div>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

        if st.checkbox("Mark as pitched", value=is_used, key=f"used_{angle['id']}"):
            if not is_used:
                toggle_angle_used(angle["id"], True)
                st.rerun()
        else:
            if is_used:
                toggle_angle_used(angle["id"], False)
                st.rerun()

        source_ids = angle.get("source_article_ids", "[]")
        if isinstance(source_ids, str):
            try:
                source_ids = json.loads(source_ids)
            except json.JSONDecodeError:
                source_ids = []

        if source_ids:
            with st.expander(f"Source articles ({len(source_ids)})"):
                source_articles = get_articles_by_ids(source_ids)
                for sa in source_articles:
                    sa_col, block_col = st.columns([5, 1])
                    with sa_col:
                        st.markdown(
                            f"**{sa['title']}**  \n"
                            f"*{sa['source']}* | {sa.get('published_date', 'N/A')}  \n"
                            f"{sa.get('summary', '')[:200]}...  \n"
                            f"[Read original]({sa.get('url', '#')})"
                        )
                    with block_col:
                        skip_words = {"the","a","an","in","of","for","and","to","is","how","why","new","with","from","by","at","on","its","are","as","or"}
                        words = [w for w in sa["title"].split() if w.lower().strip(".,;:!?") not in skip_words and len(w) > 2]
                        suggest = words[0].strip(".,;:!?").lower() if words else sa["source"].lower()
                        if st.button("Block similar", key=f"block_{angle['id']}_{sa['id']}", use_container_width=True):
                            add_blocked_term(suggest, reason=f"From: {sa['title'][:60]}")
                            st.toast(f"Blocking articles about '{suggest}'")
                            st.rerun()
                    st.markdown("")

st.markdown('<div class="volta-footer">Volta Story Angle Generator &middot; Prototype &middot; Powered by Claude</div>', unsafe_allow_html=True)
