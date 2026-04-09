from __future__ import annotations

import tempfile
import unittest

from bridge.models import ConversationEntry, HandoffRecord, JiraTicketData, Role
from bridge.persistence import ProjectStateStore


class TestPersistence(unittest.TestCase):
    def _make_store(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        tmp.close()
        return ProjectStateStore(tmp.name)

    def test_empty_state(self):
        store = self._make_store()
        state = store.load()
        self.assertEqual(state["conversations"], {})
        self.assertEqual(state["tickets"], {})

    def test_conversation_round_trip(self):
        store = self._make_store()
        entry = ConversationEntry(
            role="developer",
            user_message="test question",
            assistant_response="test answer",
            intent="general",
            alignment_score=50,
        )
        store.append_conversation(entry)
        convos = store.get_conversations(Role.DEVELOPER)
        self.assertEqual(len(convos), 1)
        self.assertEqual(convos[0].user_message, "test question")

    def test_separate_role_conversations(self):
        store = self._make_store()
        store.append_conversation(ConversationEntry(
            role="developer", user_message="dev q", assistant_response="dev a", intent="general",
        ))
        store.append_conversation(ConversationEntry(
            role="business_analyst", user_message="ba q", assistant_response="ba a", intent="general",
        ))
        dev_convos = store.get_conversations(Role.DEVELOPER)
        ba_convos = store.get_conversations(Role.BUSINESS_ANALYST)
        self.assertEqual(len(dev_convos), 1)
        self.assertEqual(len(ba_convos), 1)
        self.assertEqual(dev_convos[0].user_message, "dev q")
        self.assertEqual(ba_convos[0].user_message, "ba q")

    def test_ticket_upsert(self):
        store = self._make_store()
        ticket = JiraTicketData(
            key="TEST-1", title="Test", status="To Do",
            priority="High", description="desc",
        )
        store.upsert_ticket(ticket)
        loaded = store.get_ticket("TEST-1")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.title, "Test")

    def test_handoff_round_trip(self):
        store = self._make_store()
        store.append_handoff(HandoffRecord(
            role="business_analyst", reason="restricted",
            original_message="show code", timestamp="",
        ))
        handoffs = store.list_handoffs()
        self.assertEqual(len(handoffs), 1)

    def test_alignment_snapshot(self):
        store = self._make_store()
        store.append_alignment_snapshot(35, 8, "calculator_0_apr")
        history = store.get_alignment_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["score"], 35)


if __name__ == "__main__":
    unittest.main()
