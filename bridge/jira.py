from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from bridge.models import JiraTicketData, ScenarioBundle
from bridge.persistence import ProjectStateStore


@dataclass
class JiraAdapter:
    store: ProjectStateStore

    def ensure_seed_tickets(self, scenario: ScenarioBundle) -> List[JiraTicketData]:
        seeded = []
        for ticket in scenario.jira_tickets:
            existing = self.store.get_ticket(ticket.key)
            if existing:
                # Update seed fields that may have changed (e.g., assignee added)
                if not existing.assignee and ticket.assignee:
                    existing.assignee = ticket.assignee
                    self.store.upsert_ticket(existing)
                seeded.append(existing)
            else:
                self.store.upsert_ticket(ticket)
                seeded.append(ticket)
        return seeded

    def get_ticket(self, key: str) -> Optional[JiraTicketData]:
        return self.store.get_ticket(key)

    def list_tickets(self) -> List[JiraTicketData]:
        return self.store.list_tickets()

    def search_tickets(self, query: str) -> List[JiraTicketData]:
        lowered = query.lower()
        results = []
        for ticket in self.store.list_tickets():
            if lowered in ticket.title.lower() or lowered in ticket.description.lower():
                results.append(ticket)
        return results

    def create_ticket(
        self,
        title: str,
        description: str,
        priority: str = "Medium",
        assignee: Optional[str] = None,
        component: Optional[str] = None,
        reporter: Optional[str] = None,
    ) -> JiraTicketData:
        state = self.store.load()
        counter = len(state["tickets"]) + 100
        key = f"JIRA-{counter}"
        # Ensure unique key
        while key in state["tickets"]:
            counter += 1
            key = f"JIRA-{counter}"

        history = ["Created by FI-Collab"]
        if reporter:
            history.append(f"Reporter: {reporter}")
        if component:
            history.append(f"Component: {component}")

        ticket = JiraTicketData(
            key=key,
            title=title,
            status="To Do",
            priority=priority,
            description=description,
            assignee=assignee,
            external_url=f"https://jira.example.com/browse/{key}",
            history=history,
        )
        self.store.upsert_ticket(ticket)
        return ticket

    def update_ticket(
        self,
        key: str,
        status: Optional[str] = None,
        note: Optional[str] = None,
    ) -> JiraTicketData:
        ticket = self.store.get_ticket(key)
        if ticket is None:
            raise KeyError(f"Unknown ticket: {key}")
        if status:
            ticket.status = status
        if note:
            ticket.history.append(note)
        self.store.upsert_ticket(ticket)
        return ticket
