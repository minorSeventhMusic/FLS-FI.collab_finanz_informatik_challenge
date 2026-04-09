from __future__ import annotations

import streamlit as st

from bridge.config import DEFAULT_SCENARIO
from bridge.llm import build_llm_client
from bridge.models import Role
from bridge.persistence import ProjectStateStore
from bridge.reports import generate_report

st.set_page_config(page_title="FI-Collab — Reports", page_icon="\U0001f534", layout="wide")

# ── Initialize ───────────────────────────────────────────────────────────

if "store" not in st.session_state:
    st.session_state.store = ProjectStateStore()
if "llm" not in st.session_state:
    st.session_state.llm = build_llm_client()

store = st.session_state.store
llm = st.session_state.llm

st.title("\U0001f4dd Reports")
st.caption("Generate persona-adapted alignment and status reports")
st.markdown("---")

# ── Controls ─────────────────────────────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    from bridge.personas import PERSONAS
    _role_options = {p.display_name: r for r, p in PERSONAS.items()}
    role_label = st.selectbox(
        "Report recipient",
        list(_role_options.keys()),
        help="The report language and focus adapts to the selected role.",
    )
    role = _role_options[role_label]

with col2:
    report_type = st.selectbox(
        "Report type",
        [
            "Alignment Report",
            "Stakeholder Status Update",
            "Technical Debt Assessment",
        ],
    )

st.markdown("---")

# ── Generation ───────────────────────────────────────────────────────────

if st.button("Generate Report", type="primary", use_container_width=True):
    with st.spinner("Generating report..."):
        report = generate_report(
            role=role,
            report_type=report_type,
            scenario_id=DEFAULT_SCENARIO,
            llm=llm,
            store=store,
        )

    st.session_state.last_report = report
    st.session_state.last_report_type = report_type
    st.session_state.last_report_role = role_label

if "last_report" in st.session_state:
    st.markdown(f"### {st.session_state.last_report_type}")
    st.caption(f"Prepared for: **{st.session_state.last_report_role}**")
    st.markdown("---")
    st.markdown(st.session_state.last_report)

    st.markdown("---")
    st.download_button(
        label="Download Report (.md)",
        data=st.session_state.last_report,
        file_name=f"bridge_report_{st.session_state.last_report_type.lower().replace(' ', '_')}.md",
        mime="text/markdown",
    )
