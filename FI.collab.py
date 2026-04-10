from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="FI.collab",
    page_icon="\U0001f91d",
    layout="wide",
    initial_sidebar_state="expanded",
)

# FI Corporate Identity CSS
st.markdown("""
<style>
    /* ── FI Color Palette ─────────────────────────────────── */
    :root {
        --fi-red: #e30613;
        --fi-red-bright: #FF0000;
        --fi-dark: #1a1a1a;
        --fi-grey: #6c757d;
        --fi-light-bg: #f5f5f5;
        --fi-border: #e0e0e0;
        --fi-white: #ffffff;
    }

    /* ── Top red accent line ──────────────────────────────── */
    .fi-topline {
        border-top: 3px solid var(--fi-red-bright);
        margin-bottom: 1.5rem;
    }

    /* ── Brand header ─────────────────────────────────────── */
    .fi-brand {
        font-size: 1.4rem;
        color: var(--fi-red);
        margin: 0;
    }
    .fi-brand-bold {
        font-weight: 700;
    }
    .fi-subtitle {
        font-size: 0.95rem;
        color: var(--fi-grey);
        margin-bottom: 1rem;
    }
    .fi-subtitle strong {
        color: var(--fi-dark);
    }

    /* ── Section headers (red) ────────────────────────────── */
    .fi-section-header {
        color: var(--fi-red) !important;
        font-size: 3.6rem !important;
        font-weight: 700 !important;
        margin: 2rem 0 1rem 0 !important;
        line-height: 1.2 !important;
    }

    /* ── Persona card ─────────────────────────────────────── */
    .fi-persona-name {
        color: var(--fi-red) !important;
        font-size: 3rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }
    .fi-persona-tone {
        color: var(--fi-grey) !important;
        font-style: italic !important;
        font-size: 0.85rem !important;
        margin: 0.25rem 0 0.75rem 0 !important;
    }

    /* ── Global overrides ─────────────────────────────────── */

    /* Severity badges — keep functional */
    .severity-critical { background-color: #dc3545; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
    .severity-high { background-color: #fd7e14; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
    .severity-medium { background-color: #ffc107; color: #212529; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
    .severity-low { background-color: #28a745; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }

    /* Status badges */
    .status-todo { background-color: var(--fi-grey); color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
    .status-progress { background-color: var(--fi-red); color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
    .status-done { background-color: #28a745; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }

    /* Score colors */
    .score-low { color: #dc3545; font-weight: 800; }
    .score-mid { color: #fd7e14; font-weight: 800; }
    .score-high { color: #28a745; font-weight: 800; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: var(--fi-white); }
    [data-testid="stSidebar"] hr { border: none; border-top: 1px solid var(--fi-border); margin: 1.5rem 0; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: var(--fi-white);
        border: 1px solid var(--fi-border);
        border-radius: 8px;
        padding: 1.25rem;
    }

    /* Progress bars — red */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--fi-red), var(--fi-red-bright)) !important;
        border-radius: 4px;
    }

    /* Primary buttons — red */
    button[kind="primary"] {
        background-color: var(--fi-red) !important;
        border-color: var(--fi-red) !important;
    }
    button[kind="primary"]:hover {
        background-color: #c00510 !important;
        border-color: #c00510 !important;
    }

    /* Handoff warning */
    .handoff-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
    }

    /* Headers in red */
    h2, h3 { color: var(--fi-dark) !important; }

    /* Sidebar: only active nav item in red */
    [data-testid="stSidebarNavLink"][aria-current="page"] span,
    [data-testid="stSidebarNavLink"][aria-current="page"] a {
        color: #e30613 !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Landing Page Content ─────────────────────────────────────────────────

from bridge.jira import JiraAdapter
from bridge.personas import PERSONAS
from bridge.persistence import ProjectStateStore
from bridge.scenarios import get_scenario
from bridge.config import DEFAULT_SCENARIO

# Red top line
st.markdown('<div class="fi-topline"></div>', unsafe_allow_html=True)

# Brand with Sparkasse logo
import base64
from pathlib import Path

_logo_path = Path(__file__).parent / "personas_pictures" / "Sparkasse.svg"
_logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode()

st.markdown(
    f'<div style="display: flex; align-items: center; gap: 0.75rem;">'
    f'<img src="data:image/svg+xml;base64,{_logo_b64}" style="height: 3.2rem;">'
    f'<div>'
    f'<div style="color: #e30613; font-size: 1.4rem; line-height: 1.3;">FI.<span style="font-weight: 700;">collab</span></div>'
    f'<div style="color: #6c757d; font-size: 0.95rem; line-height: 1.3;">Collaborative AI for business-technical alignment | <strong style="color: #1a1a1a;">finanz informatik</strong></div>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown("---")

# Sign in dropdown — just name (role)
_role_options = {p.display_name: r for r, p in PERSONAS.items()}
_all_options = ["Select your role..."] + list(_role_options.keys())
_default_idx = 0
if "selected_landing_role" in st.session_state:
    prev = st.session_state["selected_landing_role"]
    if prev in _all_options:
        _default_idx = _all_options.index(prev)

selected_label = st.selectbox(
    "Sign in as",
    _all_options,
    index=_default_idx,
    key="landing_role",
)

# Only show persona card and projects after a role is selected
if selected_label != "Select your role...":
    selected_role = _role_options[selected_label]
    persona = PERSONAS[selected_role]

    # Store selection for Chat page
    st.session_state["selected_landing_role"] = selected_label

    st.markdown("---")

    # Persona card: photo + info
    col_pic, col_info = st.columns([1, 3], gap="medium")
    with col_pic:
        if persona.picture:
            st.image(persona.picture, width=180)
    with col_info:
        with st.container(border=True):
            st.markdown(
                f'<div style="color: #e30613; font-size: 1.5rem; font-weight: 700; line-height: 1.2; margin-bottom: 0.25rem;">{persona.display_name}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="color: #6c757d; font-style: italic; font-size: 0.85rem; margin-bottom: 0.75rem;">{persona.tone}</div>',
                unsafe_allow_html=True,
            )
            bio = persona.system_instructions.replace("\\n", "\n").split("Follow these rules")[0].strip()
            bio_lines = [l for l in bio.split("\n") if l.strip()]
            for line in bio_lines:
                st.markdown(line)

    # Projects section
    st.markdown(
        '<div style="color: #e30613; font-size: 1.8rem; font-weight: 700; margin: 2rem 0 1rem 0; line-height: 1.2;">Your Projects</div>',
        unsafe_allow_html=True,
    )

    # Project 1: FlexiLoan (bundled scenario)
    with st.container(border=True):
        proj_col1, proj_col2 = st.columns([3, 1])
        with proj_col1:
            st.markdown("**FlexiLoan Retail Engine**")
            st.caption("Customer-facing loan calculator with 0% APR promotional support")
            st.caption("Alignment: Critical gaps detected | Open tickets: JIRA-104")
        with proj_col2:
            if st.button("Open in Chat", key="proj-flexiloan", use_container_width=True):
                st.session_state["selected_landing_role"] = selected_label
                st.session_state["active_project"] = "calculator_0_apr"
                st.switch_page("pages/1_Chat.py")

    # Project 2: GitHub repo (live)
    with st.container(border=True):
        proj_col1, proj_col2 = st.columns([3, 1])
        with proj_col1:
            st.markdown("**Loan Calculator** \u2014 [GitHub](https://github.com/skleinke/ChefTreffHackFIChallenge_v2)")
            st.caption("Live repository: skleinke/ChefTreffHackFIChallenge_v2")
            st.caption("Source: GitHub API | Files fetched on connect")
        with proj_col2:
            if st.button("Open in Chat", key="proj-github", use_container_width=True):
                st.session_state["selected_landing_role"] = selected_label
                st.session_state["active_project"] = "github_skleinke_ChefTreffHackFIChallenge_v2"
                st.session_state["github_repo"] = ("skleinke", "ChefTreffHackFIChallenge_v2")
                st.switch_page("pages/1_Chat.py")

    # Urgent section — high/highest priority tickets assigned to this persona
    _store = ProjectStateStore()
    _jira = JiraAdapter(_store)
    _jira.ensure_seed_tickets(get_scenario(DEFAULT_SCENARIO))
    _all_tickets = _jira.list_tickets()

    _urgent = [
        t for t in _all_tickets
        if t.priority in ("High", "Highest", "Critical")
        and t.status != "Done"
        and (
            t.assignee
            and persona.display_name.split("(")[0].strip().lower()
            in t.assignee.lower()
        )
    ]

    if _urgent:
        st.markdown(
            '<div style="color: #e30613; font-size: 1.8rem; font-weight: 700; margin: 2rem 0 1rem 0; line-height: 1.2;">Action required</div>',
            unsafe_allow_html=True,
        )
        for t in _urgent:
            with st.container(border=True):
                urg_col1, urg_col2 = st.columns([3, 1])
                with urg_col1:
                    st.markdown(f"**{t.key}**: {t.title}")
                    st.caption(f"Priority: {t.priority} | Status: {t.status}")
                with urg_col2:
                    if st.button("Open in Chat", key=f"urgent-{t.key}", use_container_width=True):
                        st.session_state["selected_landing_role"] = selected_label
                        st.session_state["active_ticket_key"] = t.key
                        st.session_state["messages"] = [{
                            "kind": "assistant",
                            "content": (
                                f"**{t.key}**: {t.title}\n\n"
                                f"- **Status:** {t.status}\n"
                                f"- **Priority:** {t.priority}\n"
                                f"- **Assignee:** {t.assignee or 'Unassigned'}"
                            ),
                        }]
                        st.session_state["pending_resume"] = False
                        st.switch_page("pages/1_Chat.py")
