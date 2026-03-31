"""Volta Story Angle Generator — Streamlit Dashboard."""

import streamlit as st
import json
from datetime import datetime
from html import escape

st.set_page_config(
    page_title="Volta — Story Angle Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Helpers ---

def get_keys():
    """Get API keys from Streamlit secrets or environment."""
    import os
    anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))
    newsapi_key = st.secrets.get("NEWSAPI_KEY", os.getenv("NEWSAPI_KEY", ""))
    return anthropic_key, newsapi_key


URGENCY_COLORS = {
    "high": ("#D32F2F", "#FFEBEE", "🔴"),
    "medium": ("#F57C00", "#FFF3E0", "🟡"),
    "low": ("#388E3C", "#E8F5E9", "🟢"),
}

OUTLET_LABELS = {
    "trade_press": "Trade press",
    "consumer_tech": "Consumer tech",
    "business_press": "Business press",
    "local_news": "Local news",
    "lifestyle": "Lifestyle",
    "policy": "Policy",
}


# --- Custom CSS ---

st.markdown("""
<style>
    .angle-card {
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        background: white;
    }
    .angle-headline {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 8px;
        color: #1A1A1A;
    }
    .angle-peg {
        font-size: 14px;
        color: #1D9E75;
        font-weight: 500;
        margin-bottom: 12px;
    }
    .angle-rationale {
        font-size: 14px;
        color: #555;
        line-height: 1.6;
        margin-bottom: 12px;
    }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 8px;
    }
    .stat-card {
        text-align: center;
        padding: 16px;
    }
    .stat-number {
        font-size: 32px;
        font-weight: 700;
        color: #1D9E75;
    }
    .stat-label {
        font-size: 13px;
        color: #888;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)


# --- Sidebar ---

st.sidebar.markdown("## ⚡ Volta")
st.sidebar.markdown("**Story Angle Generator**")
st.sidebar.divider()

# Import here to avoid import errors during initial load
from src.database import (
    init_db, get_angles, get_articles_by_ids, get_db_stats, get_top_articles,
    get_blocked_terms, add_blocked_term, remove_blocked_term,
    get_custom_instructions, set_custom_instructions,
    toggle_angle_used,
)

init_db()

# Auto-seed if database is empty (first run)
_initial_stats = get_db_stats()
if _initial_stats["articles"] == 0:
    from seed_data import seed
    from seed_history import seed_history
    seed()
    seed_history()

stats = get_db_stats()

st.sidebar.markdown("### Pipeline stats")
st.sidebar.metric("Articles ingested", stats["articles"])
st.sidebar.metric("Classified", stats["classified"])
st.sidebar.metric("Angles generated", stats["angles"])

if stats["sources"]:
    st.sidebar.markdown("### Sources")
    for source in sorted(stats["sources"]):
        st.sidebar.markdown(f"- {source}")

st.sidebar.divider()

# Filters
st.sidebar.markdown("### Filters")

outlet_options = ["All"] + list(OUTLET_LABELS.values())
selected_outlet = st.sidebar.selectbox("Outlet type", outlet_options)

urgency_options = ["All", "High", "Medium", "Low"]
selected_urgency = st.sidebar.selectbox("Urgency", urgency_options)

st.sidebar.divider()

# Refresh pipeline button
st.sidebar.markdown("### Run pipeline")
if st.sidebar.button("🔄 Refresh — Fetch & Generate", use_container_width=True):
    anthropic_key, newsapi_key = get_keys()
    if not anthropic_key:
        st.sidebar.error("Missing Anthropic API key. Add it to .streamlit/secrets.toml")
    else:
        from src.pipeline import run_full_pipeline
        with st.spinner("Running full pipeline... This may take 1-2 minutes."):
            try:
                result = run_full_pipeline(newsapi_key, anthropic_key)
                st.sidebar.success(
                    f"Done! Ingested {result['ingestion']['inserted']} articles, "
                    f"generated {result['generation']['angles']} angles."
                )
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Pipeline error: {e}")

st.sidebar.divider()

# --- Custom Instructions (Feedback C) ---
st.sidebar.markdown("### Team instructions")
st.sidebar.caption("Guide the AI when generating angles. Saved automatically.")

current_instructions = get_custom_instructions()
new_instructions = st.sidebar.text_area(
    "Custom instructions",
    value=current_instructions,
    height=120,
    placeholder="e.g. Our CEO is available for grid reliability commentary this month.\n\nAvoid angles about Tesla unless they directly impact charging networks.\n\nWe have a product launch in Texas in April - prioritize Texas angles.",
    label_visibility="collapsed",
)
if new_instructions != current_instructions:
    set_custom_instructions(new_instructions)
    st.sidebar.success("Instructions saved")

st.sidebar.divider()

# --- Blocked Terms (Feedback B) ---
st.sidebar.markdown("### Blocked topics")
st.sidebar.caption("Articles matching these terms will be filtered out.")

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

st.markdown("# This week's story angles")
st.markdown("*AI-generated pitch ideas for Volta's PR team, grounded in recent news coverage.*")
st.markdown("")

# Build filters for query
outlet_filter = None
if selected_outlet != "All":
    outlet_filter = [k for k, v in OUTLET_LABELS.items() if v == selected_outlet]
    outlet_filter = outlet_filter[0] if outlet_filter else None

urgency_filter = selected_urgency.lower() if selected_urgency != "All" else None

angles = get_angles(outlet_type=outlet_filter, urgency=urgency_filter)

if not angles:
    st.markdown("---")
    st.markdown(
        "**No angles yet.** Click **Refresh — Fetch & Generate** in the sidebar to run the pipeline, "
        "or check your filters."
    )
    st.markdown("")
    st.info(
        "💡 **First run?** Make sure your API keys are configured in `.streamlit/secrets.toml` "
        "or as environment variables, then hit the refresh button."
    )
else:
    # Summary row
    cols = st.columns(5)
    urgency_counts = {"high": 0, "medium": 0, "low": 0}
    pitched_count = 0
    for a in angles:
        u = a.get("urgency", "medium").lower()
        if u in urgency_counts:
            urgency_counts[u] += 1
        if a.get("used"):
            pitched_count += 1

    with cols[0]:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(angles)}</div><div class="stat-label">Total angles</div></div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{pitched_count}</div><div class="stat-label">Pitched</div></div>', unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{urgency_counts["high"]}</div><div class="stat-label">🔴 High</div></div>', unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{urgency_counts["medium"]}</div><div class="stat-label">🟡 Medium</div></div>', unsafe_allow_html=True)
    with cols[4]:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{urgency_counts["low"]}</div><div class="stat-label">🟢 Low</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Angle cards
    for angle in angles:
        urgency = angle.get("urgency", "medium").lower()
        u_color, u_bg, u_icon = URGENCY_COLORS.get(urgency, URGENCY_COLORS["medium"])
        outlet = OUTLET_LABELS.get(angle.get("outlet_type", ""), angle.get("outlet_type", ""))
        is_used = bool(angle.get("used", 0))

        used_badge = ""
        if is_used:
            used_badge = '<span class="badge" style="background: #E8F5E9; color: #388E3C;">Pitched</span>'

        st.markdown(f"""
        <div class="angle-card" style="{'border-left: 3px solid #388E3C;' if is_used else ''}">
            <div style="margin-bottom: 10px;">
                <span class="badge" style="background: {u_bg}; color: {u_color};">{u_icon} {urgency.title()}</span>
                <span class="badge" style="background: #E8F0FE; color: #1967D2;">{escape(outlet)}</span>
                {used_badge}
            </div>
            <div class="angle-headline">{escape(angle.get('headline', ''))}</div>
            <div class="angle-peg">📌 {escape(angle.get('news_peg', 'N/A'))}</div>
            <div class="angle-rationale">{escape(angle.get('rationale', ''))}</div>
            <div style="font-size: 13px; color: #777;"><strong>Why this outlet:</strong> {escape(angle.get('outlet_rationale', 'N/A'))}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.checkbox("Mark as pitched", value=is_used, key=f"used_{angle['id']}"):
            if not is_used:
                toggle_angle_used(angle["id"], True)
                st.rerun()
        else:
            if is_used:
                toggle_angle_used(angle["id"], False)
                st.rerun()

        # Source articles expander
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
                        # Extract a blocking keyword from the title
                        skip_words = {"the","a","an","in","of","for","and","to","is","how","why","new","with","from","by","at","on","its","are","as","or"}
                        words = [w for w in sa["title"].split() if w.lower().strip(".,;:!?") not in skip_words and len(w) > 2]
                        suggest = words[0].strip(".,;:!?").lower() if words else sa["source"].lower()
                        if st.button("Block similar", key=f"block_{angle['id']}_{sa['id']}", use_container_width=True):
                            add_blocked_term(suggest, reason=f"From: {sa['title'][:60]}")
                            st.toast(f"Blocking articles about '{suggest}'")
                            st.rerun()
                    st.markdown("")


# --- Footer ---

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #AAA; font-size: 12px;'>"
    "Volta Story Angle Generator · Prototype · Powered by Claude"
    "</div>",
    unsafe_allow_html=True,
)
