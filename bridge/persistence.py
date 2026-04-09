from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from bridge.config import STATE_FILE
from bridge.models import ConversationEntry, HandoffRecord, JiraTicketData, Role


class ProjectStateStore:
    def __init__(self, path: Optional[str] = None) -> None:
        self.path = Path(path or STATE_FILE)

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return self._empty_state()
        raw = self.path.read_text(encoding="utf-8").strip()
        if not raw:
            return self._empty_state()
        return json.loads(raw)

    def save(self, state: Dict[str, Any]) -> None:
        self.path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def _empty_state() -> Dict[str, Any]:
        return {
            "conversations": {},
            "tickets": {},
            "handoffs": [],
            "alignment_snapshots": [],
        }

    # ── Conversations ────────────────────────────────────────────────────

    def get_conversations(self, role: Role) -> List[ConversationEntry]:
        state = self.load()
        entries = state["conversations"].get(role.value, [])
        return [ConversationEntry(**e) for e in entries]

    def append_conversation(self, entry: ConversationEntry) -> None:
        state = self.load()
        if not entry.timestamp:
            entry.timestamp = datetime.now(timezone.utc).isoformat()
        role_key = entry.role
        if role_key not in state["conversations"]:
            state["conversations"][role_key] = []
        state["conversations"][role_key].append({
            "role": entry.role,
            "user_message": entry.user_message,
            "assistant_response": entry.assistant_response,
            "intent": entry.intent,
            "alignment_score": entry.alignment_score,
            "timestamp": entry.timestamp,
        })
        self.save(state)

    # ── Tickets ──────────────────────────────────────────────────────────

    def get_ticket(self, key: str) -> Optional[JiraTicketData]:
        state = self.load()
        payload = state["tickets"].get(key)
        if not payload:
            return None
        return JiraTicketData(**payload)

    def upsert_ticket(self, ticket: JiraTicketData) -> None:
        state = self.load()
        state["tickets"][ticket.key] = {
            "key": ticket.key,
            "title": ticket.title,
            "status": ticket.status,
            "priority": ticket.priority,
            "description": ticket.description,
            "assignee": ticket.assignee,
            "external_url": ticket.external_url,
            "history": ticket.history,
        }
        self.save(state)

    def list_tickets(self) -> List[JiraTicketData]:
        state = self.load()
        return [JiraTicketData(**v) for v in state["tickets"].values()]

    # ── Handoffs ─────────────────────────────────────────────────────────

    def append_handoff(self, record: HandoffRecord) -> None:
        state = self.load()
        if not record.timestamp:
            record.timestamp = datetime.now(timezone.utc).isoformat()
        state["handoffs"].append({
            "role": record.role,
            "reason": record.reason,
            "original_message": record.original_message,
            "timestamp": record.timestamp,
        })
        self.save(state)

    def list_handoffs(self) -> List[HandoffRecord]:
        state = self.load()
        return [HandoffRecord(**h) for h in state["handoffs"]]

    # ── Alignment Snapshots ──────────────────────────────────────────────

    def append_alignment_snapshot(
        self, score: int, discrepancy_count: int, scenario_id: str
    ) -> None:
        state = self.load()
        state["alignment_snapshots"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "score": score,
            "discrepancy_count": discrepancy_count,
            "scenario_id": scenario_id,
        })
        self.save(state)

    def get_alignment_history(self) -> List[Dict[str, Any]]:
        state = self.load()
        return state["alignment_snapshots"]
