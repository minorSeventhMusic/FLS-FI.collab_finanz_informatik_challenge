from __future__ import annotations

import unittest

from bridge.context import assemble
from bridge.models import ConversationEntry, Intent, Role
from bridge.scenarios import get_scenario


class TestContext(unittest.TestCase):
    def setUp(self):
        self.scenario = get_scenario("calculator_0_apr")

    def test_ba_context_excludes_raw_code(self):
        result = assemble(
            Role.BUSINESS_ANALYST, Intent.GENERAL, self.scenario, "overview", []
        )
        self.assertNotIn("def calculate_monthly_payment", result.context_string)
        self.assertIn("REPOSITORY OVERVIEW", result.context_string)

    def test_dev_context_includes_raw_code(self):
        result = assemble(
            Role.DEVELOPER, Intent.CODE_QUESTION, self.scenario, "code", []
        )
        self.assertIn("def calculate_monthly_payment", result.context_string)
        self.assertIn("REPOSITORY FILES", result.context_string)

    def test_stakeholder_comms_always_included(self):
        for role in [Role.BUSINESS_ANALYST, Role.DEVELOPER]:
            result = assemble(role, Intent.GENERAL, self.scenario, "test", [])
            self.assertIn("STAKEHOLDER COMMUNICATIONS", result.context_string)
            self.assertIn("0% Interest Loans now live", result.context_string)

    def test_jira_always_included(self):
        result = assemble(
            Role.DEVELOPER, Intent.GENERAL, self.scenario, "test", []
        )
        self.assertIn("JIRA-104", result.context_string)

    def test_conversation_history_included(self):
        history = [
            ConversationEntry(
                role="developer",
                user_message="Previous question",
                assistant_response="Previous answer",
                intent="general",
            )
        ]
        result = assemble(
            Role.DEVELOPER, Intent.GENERAL, self.scenario, "follow up", history
        )
        self.assertIn("Previous question", result.conversation_history_string)
        self.assertIn("Previous answer", result.conversation_history_string)

    def test_empty_history(self):
        result = assemble(
            Role.DEVELOPER, Intent.GENERAL, self.scenario, "test", []
        )
        self.assertIn("No prior conversation", result.conversation_history_string)

    def test_relevant_files_returned(self):
        result = assemble(
            Role.DEVELOPER, Intent.CODE_QUESTION, self.scenario, "calculator validation", []
        )
        self.assertIsInstance(result.relevant_files, list)
        self.assertGreater(len(result.relevant_files), 0)


if __name__ == "__main__":
    unittest.main()
