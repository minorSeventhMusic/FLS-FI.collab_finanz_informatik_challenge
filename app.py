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

# Show persona preview
persona = PERSONAS[selected_role]
with st.container(border=True):
    st.markdown(f"**{persona.display_name}**")
    st.caption(f"Tone: {persona.tone}")
    st.markdown(persona.system_instructions.replace("\\n", "\n").split("Follow these rules")[0].strip())

st.markdown("---")
st.markdown("Navigate to **Chat**, **Dashboard**, or **Reports** in the sidebar.")
