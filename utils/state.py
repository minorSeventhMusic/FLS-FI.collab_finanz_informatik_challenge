from __future__ import annotations

from typing import Optional, cast

import streamlit as st

from services.mock_data import ChatMessage, MessageRole, Role, Ticket
from services.mock_data import get_mock_active_tickets, get_mock_history_tickets


ChatHistories = dict[Role, dict[str, list[ChatMessage]]]

AVAILABLE_ROLES: tuple[Role, Role] = ("Business Analyst", "Developer")
DEFAULT_ROLE: Role = "Business Analyst"


def initialize_session_state() -> None:
    if "current_role" not in st.session_state:
        st.session_state.current_role = DEFAULT_ROLE

    if "selected_ticket_id" not in st.session_state:
        st.session_state.selected_ticket_id = None

    if "active_tickets" not in st.session_state:
        st.session_state.active_tickets = get_mock_active_tickets()

    if "history_tickets" not in st.session_state:
        st.session_state.history_tickets = get_mock_history_tickets()

    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = _build_empty_chat_histories(
            get_all_tickets()
        )

    _ensure_chat_history_buckets()


def get_current_role() -> Role:
    return cast(Role, st.session_state.current_role)


def set_current_role(role: Role) -> None:
    st.session_state.current_role = role


def get_selected_ticket_id() -> str | None:
    return cast(Optional[str], st.session_state.selected_ticket_id)


def set_selected_ticket(ticket_id: str) -> None:
    st.session_state.selected_ticket_id = ticket_id


def get_active_tickets() -> list[Ticket]:
    return cast(list[Ticket], st.session_state.active_tickets)


def get_history_tickets() -> list[Ticket]:
    return cast(list[Ticket], st.session_state.history_tickets)


def get_all_tickets() -> list[Ticket]:
    return get_active_tickets() + get_history_tickets()


def get_selected_ticket() -> Ticket | None:
    selected_ticket_id = get_selected_ticket_id()
    if not selected_ticket_id:
        return None

    for ticket in get_all_tickets():
        if ticket["id"] == selected_ticket_id:
            return ticket

    return None


def get_chat_history(role: Role, ticket_id: str) -> list[ChatMessage]:
    chat_histories = cast(ChatHistories, st.session_state.chat_histories)
    return chat_histories.setdefault(role, {}).setdefault(ticket_id, [])


def append_chat_message(
    role: Role, ticket_id: str, message_role: MessageRole, content: str
) -> None:
    history = get_chat_history(role, ticket_id)
    history.append({"role": message_role, "content": content})


def _build_empty_chat_histories(tickets: list[Ticket]) -> ChatHistories:
    return {
        role: {ticket["id"]: [] for ticket in tickets}
        for role in AVAILABLE_ROLES
    }


def _ensure_chat_history_buckets() -> None:
    chat_histories = cast(ChatHistories, st.session_state.chat_histories)

    for role in AVAILABLE_ROLES:
        role_histories = chat_histories.setdefault(role, {})
        for ticket in get_all_tickets():
            role_histories.setdefault(ticket["id"], [])
