from __future__ import annotations

from dataclasses import dataclass

from bridge_mvp.persistence import ProjectStateStore
from bridge_mvp.scenarios import get_scenario_bundle
from bridge_mvp.types import JiraTicket, ScenarioBundle


class CodeContextAdapter:
    def get_scenario(self, scenario_id: str) -> ScenarioBundle:
        return get_scenario_bundle(scenario_id)


@dataclass
class JiraAdapter:
    store: ProjectStateStore

    def ensure_seed_ticket(self, scenario: ScenarioBundle) -> JiraTicket:
        existing = self.store.get_ticket(scenario.jira_ticket_key)
        if existing:
            return existing
        title = "Handle Division by Zero for 0% Interest Rate Loans"
        ticket = JiraTicket(
            key=scenario.jira_ticket_key,
            title=title,
            status="To Do",
            priority="High",
            description=scenario.jira_ticket,
            history=["Seeded from demo scenario"],
        )
        self.store.upsert_ticket(ticket)
        return ticket

    def get_ticket(self, key: str) -> JiraTicket | None:
        return self.store.get_ticket(key)

    def create_ticket(self, title: str, description: str, priority: str = "Medium") -> JiraTicket:
        state = self.store.load()
        counter = len(state["tickets"]) + 200
        key = f"BRIDGE-{counter}"
        ticket = JiraTicket(
            key=key,
            title=title,
            status="To Do",
            priority=priority,
            description=description,
            history=["Created by Bridge MVP"],
        )
        self.store.upsert_ticket(ticket)
        return ticket

    def update_ticket(self, key: str, status: str, note: str) -> JiraTicket:
        ticket = self.store.get_ticket(key)
        if ticket is None:
            raise KeyError(f"Unknown ticket: {key}")
        ticket.status = status
        ticket.history.append(note)
        self.store.upsert_ticket(ticket)
        return ticket

