from __future__ import annotations

from datetime import datetime
from typing import cast

import streamlit as st

from services.mock_data import Role, Ticket
from utils.state import (
    AVAILABLE_ROLES,
    get_current_role,
    get_selected_ticket_id,
    set_current_role,
    set_selected_ticket,
)

TICKET_LIST_HEIGHT = 320
UPDATED_AT_FORMAT = "%Y-%m-%d %H:%M"


def render_role_section() -> Role:
    current_role = get_current_role()
    role_options = list(AVAILABLE_ROLES)
    with st.container(border=True):
        st.caption("Collaboration role")
        selected_role = cast(
            Role,
            st.radio(
                "Select user role",
                options=role_options,
                index=role_options.index(current_role),
                label_visibility="collapsed",
            ),
        )

        if selected_role != current_role:
            set_current_role(selected_role)
            current_role = selected_role

        st.markdown(f"**User : {current_role}**")
        st.caption("Switch perspectives to review the same ticket as business or engineering.")

    return current_role


def render_ticket_section(title: str, tickets: list[Ticket], key_prefix: str) -> None:
    st.subheader(title)
    sorted_tickets = _sort_tickets_by_updated_at(tickets)

    if not sorted_tickets:
        st.caption(_build_empty_state_message(title))
        return

    st.caption(_build_ticket_count_caption(title, len(sorted_tickets)))
    selected_ticket_id = get_selected_ticket_id()

    with st.container(height=TICKET_LIST_HEIGHT):
        for ticket in sorted_tickets:
            _render_ticket_row(ticket, key_prefix, selected_ticket_id)


def _render_ticket_row(
    ticket: Ticket, key_prefix: str, selected_ticket_id: str | None
) -> None:
    is_selected = selected_ticket_id == ticket["id"]

    with st.container(border=True):
        details_column, action_column = st.columns([3.3, 1.1])

        with details_column:
            st.markdown(f"[{ticket['subject']}]({ticket['external_url']})")
            st.caption(_build_ticket_metadata(ticket))

            if is_selected:
                st.caption("Selected in chat")

        with action_column:
            if st.button(
                "Open in chat",
                key=f"{key_prefix}-{ticket['id']}",
                type="primary" if is_selected else "secondary",
                use_container_width=True,
            ):
                set_selected_ticket(ticket["id"])
                st.rerun()


def _sort_tickets_by_updated_at(tickets: list[Ticket]) -> list[Ticket]:
    return sorted(
        tickets,
        key=lambda ticket: _parse_updated_at(ticket["updated_at"]),
        reverse=True,
    )


def _parse_updated_at(updated_at: str) -> datetime:
    try:
        return datetime.strptime(updated_at, UPDATED_AT_FORMAT)
    except ValueError:
        return datetime.min


def _build_ticket_metadata(ticket: Ticket) -> str:
    return (
        f"ID: {ticket['id']} | Status: {ticket['status']} | "
        f"Updated: {ticket['updated_at']}"
    )


def _build_empty_state_message(title: str) -> str:
    if title == "Active tickets":
        return "No active tickets right now."

    return "No ticket history yet."


def _build_ticket_count_caption(title: str, ticket_count: int) -> str:
    return f"{ticket_count} {title.lower()} shown, most recent first."
