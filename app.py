from __future__ import annotations

import streamlit as st

from components.sidebar_sections import render_role_section, render_ticket_section
from services.agent_client import (
    build_assistant_status,
    build_chat_input_placeholder,
    build_mock_agent_reply,
    build_starter_message,
)
from services.mock_data import Role, Ticket
from utils.state import (
    append_chat_message,
    get_active_tickets,
    get_chat_history,
    get_history_tickets,
    get_selected_ticket,
    initialize_session_state,
)


st.set_page_config(
    page_title="Ticket Copilot Demo",
    page_icon=":ticket:",
    layout="wide",
)


def render_workspace_header(ticket: Ticket, current_role: Role) -> None:
    st.caption("Collaboration assistant workspace")
    st.title(ticket["subject"])

    ticket_col, status_col, role_col, link_col = st.columns([1.1, 1, 1.2, 1.5])
    with ticket_col:
        st.caption("Ticket ID")
        st.write(ticket["id"])
    with status_col:
        st.caption("Status")
        st.write(ticket["status"])
    with role_col:
        st.caption("Current role")
        st.write(current_role)
    with link_col:
        st.caption("External ticket")
        st.markdown(f"[Open ticket]({ticket['external_url']})")

    st.caption(f"Last updated {ticket['updated_at']}")


def render_chat_thread(ticket: Ticket, current_role: Role) -> None:
    messages = get_chat_history(current_role, ticket["id"])

    if not messages:
        append_chat_message(
            current_role,
            ticket["id"],
            "assistant",
            build_starter_message(ticket, current_role),
        )
        messages = get_chat_history(current_role, ticket["id"])

    st.caption("Conversation")
    st.caption(
        f"This thread is scoped to `{ticket['id']}` and the **{current_role}** role."
    )

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    status_title, status_detail = build_assistant_status(ticket, current_role)
    with st.container(border=True):
        st.caption("Assistant status")
        st.markdown(f"**{status_title}**")
        st.caption(status_detail)

    prompt = st.chat_input(build_chat_input_placeholder(current_role))
    if not prompt:
        return

    append_chat_message(current_role, ticket["id"], "user", prompt)
    assistant_reply = build_mock_agent_reply(ticket, current_role, prompt)
    append_chat_message(current_role, ticket["id"], "assistant", assistant_reply)
    st.rerun()


def render_empty_state() -> None:
    st.title("Ticket Copilot Demo")
    st.caption("Collaboration assistant for ticket review, planning, and follow-up.")

    with st.container(border=True):
        st.subheader("Open a ticket to start collaborating")
        st.write("Choose **Open in chat** from the sidebar to load a ticket workspace.")
        st.caption(
            "Each role keeps its own conversation history for every ticket, which makes "
            "handoffs easy to demo."
        )
        st.markdown(
            "- Business Analyst view focuses on requirements, impact, and stakeholder alignment.\n"
            "- Developer view focuses on implementation details, APIs, tests, and rollout risk."
        )


def main() -> None:
    initialize_session_state()

    with st.sidebar:
        current_role = render_role_section()
        st.divider()
        render_ticket_section("Active tickets", get_active_tickets(), "active-ticket")
        st.divider()
        render_ticket_section("Ticket history", get_history_tickets(), "history-ticket")

    _, center_column, _ = st.columns([1, 5, 1])

    with center_column:
        selected_ticket = get_selected_ticket()

        if selected_ticket is None:
            render_empty_state()
            return

        render_workspace_header(selected_ticket, current_role)
        st.divider()
        render_chat_thread(selected_ticket, current_role)


if __name__ == "__main__":
    main()
