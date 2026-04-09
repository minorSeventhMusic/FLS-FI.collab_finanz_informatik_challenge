from __future__ import annotations

import tempfile
import unittest

from bridge.jira import JiraAdapter
from bridge.persistence import ProjectStateStore
from bridge.scenarios import get_scenario


class TestJira(unittest.TestCase):
    def _make_jira(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        tmp.close()
        store = ProjectStateStore(tmp.name)
        return JiraAdapter(store), store

    def test_seed_tickets_idempotent(self):
        jira, _ = self._make_jira()
        scenario = get_scenario("calculator_0_apr")
        first = jira.ensure_seed_tickets(scenario)
        second = jira.ensure_seed_tickets(scenario)
        self.assertEqual(len(first), len(second))
        self.assertEqual(first[0].key, second[0].key)
        # Should not duplicate
        all_tickets = jira.list_tickets()
        jira_104_count = sum(1 for t in all_tickets if t.key == "JIRA-104")
        self.assertEqual(jira_104_count, 1)

    def test_create_ticket_auto_key(self):
        jira, _ = self._make_jira()
        ticket = jira.create_ticket("Test", "Description")
        self.assertTrue(ticket.key.startswith("BRIDGE-"))
        self.assertEqual(ticket.status, "To Do")

    def test_update_ticket_status(self):
        jira, _ = self._make_jira()
        scenario = get_scenario("calculator_0_apr")
        jira.ensure_seed_tickets(scenario)
        updated = jira.update_ticket("JIRA-104", status="In Progress", note="Started work")
        self.assertEqual(updated.status, "In Progress")
        self.assertIn("Started work", updated.history)

    def test_search_tickets(self):
        jira, _ = self._make_jira()
        scenario = get_scenario("calculator_0_apr")
        jira.ensure_seed_tickets(scenario)
        results = jira.search_tickets("0% Interest")
        self.assertGreater(len(results), 0)

    def test_unknown_ticket_raises(self):
        jira, _ = self._make_jira()
        with self.assertRaises(KeyError):
            jira.update_ticket("NONEXISTENT-999")


if __name__ == "__main__":
    unittest.main()
