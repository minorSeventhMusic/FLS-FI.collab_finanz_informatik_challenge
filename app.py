from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="The Bridge",
    page_icon="\U0001f309",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished look
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #6c757d;
        margin-bottom: 1.5rem;
    }

    /* Severity badges */
    .severity-critical {
        background-color: #dc3545;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .severity-high {
        background-color: #fd7e14;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .severity-medium {
        background-color: #ffc107;
        color: #212529;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .severity-low {
        background-color: #28a745;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* Status badges */
    .status-todo {
        background-color: #6c757d;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    .status-progress {
        background-color: #007bff;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    .status-done {
        background-color: #28a745;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
    }

    /* Score color coding */
    .score-low { color: #dc3545; font-weight: 700; }
    .score-mid { color: #fd7e14; font-weight: 700; }
    .score-high { color: #28a745; font-weight: 700; }

    /* Handoff warning */
    .handoff-warning {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
    }

    /* Clean sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }

    /* Card-like metric containers */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

from bridge.personas import PERSONAS

st.markdown('<p class="main-header">\U0001f309 The Bridge</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">AI-powered orchestration for business-technical alignment</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("### Welcome — select your role to get started")
st.markdown(
    "The Bridge adapts its language, visibility, and recommendations to your role. "
    "Choose who you are, then head to **Chat** to start."
)

_role_options = {p.display_name: r for r, p in PERSONAS.items()}
selected_label = st.selectbox(
    "Who are you?",
    list(_role_options.keys()),
    index=0,
    key="landing_role",
)
selected_role = _role_options[selected_label]

# Store selection so Chat page picks it up
st.session_state["selected_landing_role"] = selected_label

# Show persona card with picture
persona = PERSONAS[selected_role]

col_pic, col_info = st.columns([1, 3], gap="medium")
with col_pic:
    if persona.picture:
        st.image(persona.picture, width=180)
with col_info:
    with st.container(border=True):
        st.markdown(f"### {persona.display_name}")
        st.caption(f"Tone: _{persona.tone}_")
        # Extract the persona background (before "Follow these rules")
        bio = persona.system_instructions.replace("\\n", "\n").split("Follow these rules")[0].strip()
        # Clean up the "You are speaking to..." prefix
        bio_lines = [l for l in bio.split("\n") if l.strip()]
        for line in bio_lines:
            st.markdown(line)

st.markdown("---")

# Project list
st.markdown("### Your Projects")
with st.container(border=True):
    proj_col1, proj_col2 = st.columns([3, 1])
    with proj_col1:
        st.markdown("**FlexiLoan Retail Engine**")
        st.caption("Customer-facing loan calculator with 0% APR promotional support")
        st.caption("Alignment: Critical gaps detected | Open tickets: JIRA-104")
    with proj_col2:
        if st.button("\U0001f4ac Open in Chat", use_container_width=True):
            st.session_state["selected_landing_role"] = selected_label
            st.switch_page("pages/1_Chat.py")
