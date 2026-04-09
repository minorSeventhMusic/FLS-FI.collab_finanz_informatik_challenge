from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="FI-Collab",
    page_icon="\U0001f534",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Finanz Informatik / Sparkasse CI
st.markdown("""
<style>
    /* ── FI Color Palette ──────────────────────────────────── */
    :root {
        --fi-red: #FF0000;
        --fi-red-dark: #CC0000;
        --fi-grey-dark: #1D1D1B;
        --fi-grey-mid: #6B6B6B;
        --fi-grey-light: #F2F2F2;
        --fi-border: #E0E0E0;
        --fi-success: #28a745;
        --fi-white: #FFFFFF;
    }

    /* ── Typography ────────────────────────────────────────── */
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                     Roboto, Helvetica, Arial, sans-serif;
    }

    .fi-header {
        font-size: 2.4rem;
        font-weight: 800;
        color: var(--fi-grey-dark);
        margin: 0;
        letter-spacing: -0.5px;
    }
    .fi-header span {
        color: var(--fi-red);
    }
    .fi-subtitle {
        font-size: 1.0rem;
        color: var(--fi-grey-mid);
        margin-bottom: 1.5rem;
    }

    h2, h3 {
        color: var(--fi-grey-dark) !important;
        font-weight: 700 !important;
    }

    /* ── Severity Badges ───────────────────────────────────── */
    .severity-critical {
        background-color: var(--fi-red);
        color: white;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .severity-high {
        background-color: var(--fi-red-dark);
        color: white;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .severity-medium {
        background-color: #ffc107;
        color: #212529;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .severity-low {
        background-color: var(--fi-success);
        color: white;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    /* ── Status Badges ─────────────────────────────────────── */
    .status-todo {
        background-color: var(--fi-grey-mid);
        color: white;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    .status-progress {
        background-color: var(--fi-red);
        color: white;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    .status-done {
        background-color: var(--fi-success);
        color: white;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
    }

    /* ── Score Colors ──────────────────────────────────────── */
    .score-low { color: var(--fi-red); font-weight: 800; }
    .score-mid { color: var(--fi-red-dark); font-weight: 800; }
    .score-high { color: var(--fi-success); font-weight: 800; }

    /* ── Handoff Warning ───────────────────────────────────── */
    .handoff-warning {
        background-color: #fff3cd;
        border-left: 4px solid var(--fi-red);
        border-radius: 4px;
        padding: 12px;
        margin: 8px 0;
    }

    /* ── Sidebar ───────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: var(--fi-grey-light);
    }
    [data-testid="stSidebar"] hr {
        border: none;
        border-top: 2px solid var(--fi-border);
        margin: 1.5rem 0;
    }

    /* ── Metric Cards ──────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: var(--fi-white);
        border: 1px solid var(--fi-border);
        border-left: 4px solid var(--fi-red);
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    /* ── Buttons ───────────────────────────────────────────── */
    button[kind="primary"] {
        background-color: var(--fi-red) !important;
        border-color: var(--fi-red) !important;
    }
    button[kind="primary"]:hover {
        background-color: var(--fi-red-dark) !important;
        border-color: var(--fi-red-dark) !important;
    }

    /* ── Progress Bars ─────────────────────────────────────── */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--fi-red-dark), var(--fi-red)) !important;
        border-radius: 4px;
    }

    /* ── Containers ────────────────────────────────────────── */
    [data-testid="stContainer"] {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

from bridge.personas import PERSONAS

# Header
st.markdown(
    '<p class="fi-header"><span>\u25C6</span> FI-Collab</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="fi-subtitle">Collaborative AI for business-technical alignment</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# Role selector — compact, name + title only
_role_options = {p.display_name: r for r, p in PERSONAS.items()}
selected_label = st.selectbox(
    "Sign in as",
    [None] + list(_role_options.keys()),
    index=0,
    format_func=lambda x: "Select your role..." if x is None else x,
    key="landing_role",
)

# Only show persona details after selection
if selected_label and selected_label in _role_options:
    selected_role = _role_options[selected_label]
    st.session_state["selected_landing_role"] = selected_label
    persona = PERSONAS[selected_role]

    st.markdown("---")

    # Persona card with picture
    col_pic, col_info = st.columns([1, 3], gap="medium")
    with col_pic:
        if persona.picture:
            st.image(persona.picture, width=180)
    with col_info:
        with st.container(border=True):
            st.markdown(f"### {persona.display_name}")
            st.caption(f"_{persona.tone}_")
            bio = persona.system_instructions.replace("\\n", "\n").split("Follow these rules")[0].strip()
            bio_lines = [l for l in bio.split("\n") if l.strip()]
            for line in bio_lines:
                st.markdown(line)

    st.markdown("---")

    # Projects
    st.markdown("### Your Projects")
    with st.container(border=True):
        proj_col1, proj_col2 = st.columns([3, 1])
        with proj_col1:
            st.markdown("**FlexiLoan Retail Engine**")
            st.caption("Customer-facing loan calculator with 0% APR promotional support")
            st.caption("Alignment: Critical gaps detected | Open tickets: JIRA-104")
        with proj_col2:
            if st.button("\U0001f4ac Open in Chat", use_container_width=True):
                st.switch_page("pages/1_Chat.py")
