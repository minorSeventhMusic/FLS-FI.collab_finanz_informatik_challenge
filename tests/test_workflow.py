from __future__ import annotations

import tempfile
import unittest

from bridge.jira import JiraAdapter
from bridge.llm import StubLLMClient
from bridge.persistence import ProjectStateStore
from bridge.workflow import compile_workflow, init_services


def _setup():
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    tmp.close()
    store = ProjectStateStore(tmp.name)
    llm = StubLLMClient()
    jira = JiraAdapter(store)
    init_services(llm=llm, store=store, jira=jira)
    return compile_workflow(), store


class TestWorkflow(unittest.TestCase):
    def test_ba_gets_business_language(self):
        wf, _ = _setup()
        result = wf.invoke({
            "user_message": "What is the 0% interest issue?",
            "role": "business_analyst",
            "scenario_id": "calculator_0_apr",
        })
        response = result["final_response"]
        self.assertIn("not working", response.lower())
        self.assertIn("JIRA-104", response)
        # BA should not see raw code
        self.assertNotIn("def calculate_monthly_payment", response)

    def test_dev_gets_technical_detail(self):
        wf, _ = _setup()
        result = wf.invoke({
            "user_message": "What is the 0% interest issue?",
            "role": "developer",
            "scenario_id": "calculator_0_apr",
        })
        response = result["final_response"]
        self.assertIn("calculator.py", response)
        self.assertIn("JIRA-104", response)

    def test_ba_raw_code_triggers_handoff(self):
        wf, _ = _setup()
        result = wf.invoke({
            "user_message": "Show me the raw code for the calculator",
            "role": "business_analyst",
            "scenario_id": "calculator_0_apr",
        })
        self.assertTrue(result.get("restricted"))
        self.assertIn("Business Analyst", result.get("handoff_reason", ""))

    def test_dev_not_restricted(self):
        wf, _ = _setup()
        result = wf.invoke({
            "user_message": "Show me the raw code for the calculator",
            "role": "developer",
            "scenario_id": "calculator_0_apr",
        })
        self.assertFalse(result.get("restricted", False))

    def test_create_ticket_intent(self):
        wf, store = _setup()
        result = wf.invoke({
            "user_message": "Create a ticket for this alignment gap",
            "role": "developer",
            "scenario_id": "calculator_0_apr",
        })
        self.assertEqual(result["intent"], "create_ticket")
        self.assertEqual(result["jira_action"], "create")
        self.assertIn("JIRA-", result["final_response"])

    def test_alignment_score_present(self):
        wf, _ = _setup()
        result = wf.invoke({
            "user_message": "Check alignment",
            "role": "developer",
            "scenario_id": "calculator_0_apr",
        })
        self.assertIn("alignment_score", result)
        self.assertIsInstance(result["alignment_score"], int)
        self.assertLessEqual(result["alignment_score"], 100)

    def test_conversation_persisted(self):
        wf, store = _setup()
        wf.invoke({
            "user_message": "First question about 0% APR",
            "role": "business_analyst",
            "scenario_id": "calculator_0_apr",
        })
        from bridge.models import Role
        convos = store.get_conversations(Role.BUSINESS_ANALYST)
        self.assertEqual(len(convos), 1)
        self.assertIn("0% APR", convos[0].user_message)


if __name__ == "__main__":
    unittest.main()
