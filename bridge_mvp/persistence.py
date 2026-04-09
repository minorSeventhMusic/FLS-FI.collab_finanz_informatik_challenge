from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

from bridge_mvp.types import JiraTicket, Role


class ProjectStateStore:
    def __init__(self, path: str = "project_state.json") -> None:
        self.path = Path(path)

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {"tickets": {}, "handoffs": [], "conversations": []}
        raw = self.path.read_text(encoding="utf-8").strip()
        if not raw:
            return {"tickets": {}, "handoffs": [], "conversations": []}
        return json.loads(raw)

    def save(self, state: Dict[str, Any]) -> None:
        self.path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def get_ticket(self, key: str) -> JiraTicket | None:
        state = self.load()
        payload = state["tickets"].get(key)
        if not payload:
            return None
        return JiraTicket(**payload)

    def upsert_ticket(self, ticket: JiraTicket) -> None:
        state = self.load()
        state["tickets"][ticket.key] = asdict(ticket)
        self.save(state)

    def append_handoff(self, role: Role, reason: str, message: str) -> None:
        state = self.load()
        state["handoffs"].append(
            {"role": role.value, "reason": reason, "message": message}
        )
        self.save(state)

    def append_conversation(self, role: Role, message: str, response: str) -> None:
        state = self.load()
        state["conversations"].append(
            {"role": role.value, "message": message, "response": response}
        )
        self.save(state)

    def list_handoffs(self) -> List[Dict[str, str]]:
        state = self.load()
        return state["handoffs"]
