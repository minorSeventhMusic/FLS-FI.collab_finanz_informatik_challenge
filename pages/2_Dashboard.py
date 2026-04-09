from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from bridge.alignment import analyze_alignment
from bridge.config import DEFAULT_SCENARIO
from bridge.context import assemble
from bridge.llm import build_llm_client
from bridge.models import Intent, Role
from bridge.persistence import ProjectStateStore
from bridge.scenarios import get_scenario

st.set_page_config(page_title="The Bridge — Dashboard", page_icon="\U0001f309", layout="wide")

# ── Initialize ───────────────────────────────────────────────────────────

if "store" not in st.session_state:
    st.session_state.store = ProjectStateStore()
if "llm" not in st.session_state:
    st.session_state.llm = build_llm_client()

store = st.session_state.store
llm = st.session_state.llm

st.title("\U0001f4ca Dashboard")
st.caption("Real-time alignment overview")
st.markdown("---")

# ── Run Alignment Analysis ───────────────────────────────────────────────

_data = get_scenario(DEFAULT_SCENARIO)

# Cache alignment to avoid re-running LLM on every page load
if "cached_alignment" not in st.session_state:
    ctx = assemble(Role.DEVELOPER, Intent.ALIGNMENT_REPORT, _data, "", [])
    st.session_state.cached_alignment = analyze_alignment(ctx.context_string, llm)
alignment = st.session_state.cached_alignment

if st.button("Refresh alignment analysis"):
    ctx = assemble(Role.DEVELOPER, Intent.ALIGNMENT_REPORT, _data, "", [])
    st.session_state.cached_alignment = analyze_alignment(ctx.context_string, llm)
    st.rerun()

# ── Top Metrics ──────────────────────────────────────────────────────────

col1, col2, col3 = st.columns(3)

with col1:
    score = alignment.overall_score
    st.metric("Alignment Score", f"{score}%")
    if score < 40:
        st.progress(score / 100)
        st.error("Critical misalignment detected")
    elif score < 70:
        st.progress(score / 100)
        st.warning("Moderate alignment gaps")
    else:
        st.progress(score / 100)
        st.success("Well aligned")

with col2:
    tickets = store.list_tickets()
    open_count = sum(1 for t in tickets if t.status != "Done")
    st.metric("Open Tickets", open_count)

with col3:
    st.metric("Discrepancies Found", len(alignment.discrepancies))

st.markdown("---")

# ── Alignment Summary ────────────────────────────────────────────────────

st.subheader("Alignment Summary")
st.info(alignment.summary)

# ── Discrepancy Table ────────────────────────────────────────────────────

st.subheader("Discrepancies")

if alignment.discrepancies:
    rows = []
    for d in alignment.discrepancies:
        rows.append({
            "ID": d.id,
            "Severity": d.severity.upper(),
            "Category": d.category.replace("_", " ").title(),
            "Description": d.description[:200],
            "Evidence": ", ".join(d.evidence_sources),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Detailed expandable view
    for d in alignment.discrepancies:
        severity_class = f"severity-{d.severity}"
        with st.expander(f"{d.id}: {d.description[:80]}..."):
            st.markdown(
                f'<span class="{severity_class}">{d.severity.upper()}</span> '
                f"| {d.category.replace('_', ' ').title()}",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Description:** {d.description}")
            st.markdown(f"**Business Impact:** {d.business_impact}")
            st.markdown(f"**Technical Detail:** {d.technical_detail}")
            st.markdown(f"**Evidence:** {', '.join(d.evidence_sources)}")
else:
    st.success("No discrepancies detected.")

st.markdown("---")

# ── Jira Tickets ─────────────────────────────────────────────────────────

st.subheader("Jira Tickets")

tickets = store.list_tickets()
if tickets:
    for ticket in tickets:
        status_lower = ticket.status.lower().replace(" ", "")
        if status_lower == "todo":
            badge = "status-todo"
        elif "progress" in status_lower:
            badge = "status-progress"
        else:
            badge = "status-done"

        with st.expander(f"{ticket.key}: {ticket.title}"):
            st.markdown(
                f'<span class="{badge}">{ticket.status}</span> | '
                f"Priority: **{ticket.priority}**",
                unsafe_allow_html=True,
            )
            st.markdown(ticket.description[:500])
            if ticket.history:
                st.markdown("**History:**")
                for h in ticket.history:
                    st.markdown(f"- {h}")
else:
    st.info("No tickets yet. Use Chat to create tickets.")

st.markdown("---")

# ── Handoff Log ──────────────────────────────────────────────────────────

st.subheader("Handoff Log")

handoffs = store.list_handoffs()
if handoffs:
    for h in handoffs:
        with st.expander(f"Handoff: {h.role} — {h.timestamp[:19] if h.timestamp else 'N/A'}"):
            st.markdown(f"**Role:** {h.role}")
            st.markdown(f"**Reason:** {h.reason}")
            st.markdown(f"**Original message:** {h.original_message}")
else:
    st.info("No handoffs recorded yet.")

# ── Alignment History ────────────────────────────────────────────────────

st.subheader("Alignment History")

history = store.get_alignment_history()
if history:
    hist_df = pd.DataFrame(history)
    hist_df["timestamp"] = pd.to_datetime(hist_df["timestamp"])
    st.line_chart(hist_df.set_index("timestamp")["score"])
else:
    st.info("Alignment history will appear after chat interactions.")
