from __future__ import annotations

import streamlit as st

from bridge_mvp.scenarios import SCENARIOS
from bridge_mvp.service import DEFAULT_SCENARIO_ID, build_default_service
from bridge_mvp.types import Role


st.set_page_config(page_title="The Bridge MVP", layout="wide")

service = build_default_service()

ROLE_LABELS = {
    "Business Analyst": Role.BUSINESS_ANALYST,
    "Developer": Role.DEVELOPER,
}


def render_sidebar() -> Role:
    st.sidebar.title("The Bridge")
    role_label = st.sidebar.radio("Mock SSO role", list(ROLE_LABELS.keys()))
    st.sidebar.caption(SCENARIOS[DEFAULT_SCENARIO_ID].title)
    st.sidebar.caption("Seeded from the remote persona and technical draft branches.")
    return ROLE_LABELS[role_label]


def render_panels(result) -> None:
    left, right = st.columns([2, 1])

    with right:
        st.subheader("Repo Context")
        for path in result.relevant_files:
            st.code(path)
        st.subheader("Alignment")
        st.progress(result.alignment_score / 100)
        st.metric("Scenario Score", f"{result.alignment_score}%")
        if result.intent.value in {"create_ticket", "ticket_status"} and result.jira_ticket:
            st.subheader("Jira")
            st.write(f"**{result.jira_ticket.key}**")
            st.write(result.jira_ticket.title)
            st.write(f"Status: {result.jira_ticket.status}")
            st.write(f"Priority: {result.jira_ticket.priority}")
        if result.handoff_required:
            st.warning(result.handoff_reason)


def main() -> None:
    role = render_sidebar()
    st.title("The Bridge MVP")
    st.write(
        "Role-aware orchestration demo with mocked business requirements, code context, and Jira workflow."
    )
    st.caption(f"Focused demo: {SCENARIOS[DEFAULT_SCENARIO_ID].title}")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["kind"]):
            st.write(message["content"])

    prompt = st.chat_input("Ask about alignment, ticket status, or create a follow-up ticket")
    if not prompt:
        return

    st.session_state.messages.append({"kind": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    result = service.run_turn(role=role, message=prompt)
    with st.chat_message("assistant"):
        st.write(result.response)

    st.session_state.messages.append({"kind": "assistant", "content": result.response})
    render_panels(result)


if __name__ == "__main__":
    main()
