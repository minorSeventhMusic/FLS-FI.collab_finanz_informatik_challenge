from __future__ import annotations

from typing import Literal, TypedDict


Role = Literal["Business Analyst", "Developer"]
MessageRole = Literal["assistant", "user"]


class Ticket(TypedDict):
    id: str
    subject: str
    external_url: str
    status: str
    updated_at: str


class ChatMessage(TypedDict):
    role: MessageRole
    content: str


def get_mock_active_tickets() -> list[Ticket]:
    return [
        {
            "id": "INC-1042",
            "subject": "Dashboard export times out for finance report",
            "external_url": "https://support.example.com/tickets/INC-1042",
            "status": "In Progress",
            "updated_at": "2026-04-09 09:20",
        },
        {
            "id": "PRD-1088",
            "subject": "Customer requests bulk user import for onboarding",
            "external_url": "https://support.example.com/tickets/PRD-1088",
            "status": "Needs Review",
            "updated_at": "2026-04-09 08:45",
        },
        {
            "id": "BUG-1123",
            "subject": "Slack notification is missing assignee changes",
            "external_url": "https://support.example.com/tickets/BUG-1123",
            "status": "Blocked",
            "updated_at": "2026-04-08 17:35",
        },
    ]


def get_mock_history_tickets() -> list[Ticket]:
    return [
        {
            "id": "OPS-0991",
            "subject": "Weekly job retry policy needed better alerting",
            "external_url": "https://support.example.com/tickets/OPS-0991",
            "status": "Resolved",
            "updated_at": "2026-04-07 14:10",
        },
        {
            "id": "UX-0947",
            "subject": "Search filters were confusing first-time users",
            "external_url": "https://support.example.com/tickets/UX-0947",
            "status": "Closed",
            "updated_at": "2026-04-04 11:25",
        },
        {
            "id": "SEC-0904",
            "subject": "Audit log access needed clearer role permissions",
            "external_url": "https://support.example.com/tickets/SEC-0904",
            "status": "Closed",
            "updated_at": "2026-03-29 16:05",
        },
    ]
