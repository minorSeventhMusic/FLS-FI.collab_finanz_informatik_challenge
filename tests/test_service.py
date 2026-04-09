from __future__ import annotations

import tempfile
import unittest

from bridge_mvp.adapters import CodeContextAdapter, JiraAdapter
from bridge_mvp.llm import StubLLMClient
from bridge_mvp.persistence import ProjectStateStore
from bridge_mvp.service import BridgeService
from bridge_mvp.types import Role


class BridgeServiceTests(unittest.TestCase):
    def make_service(self) -> BridgeService:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        store = ProjectStateStore(tmp.name)
        return BridgeService(
            store=store,
            jira=JiraAdapter(store),
            code_context=CodeContextAdapter(),
            llm=StubLLMClient(),
        )

    def test_business_role_uses_business_summary(self) -> None:
        service = self.make_service()
        result = service.run_turn(
            role=Role.BUSINESS_ANALYST,
            message="What does this repo currently support?",
            scenario_id="calculator_0_apr",
        )
        self.assertEqual(result.role, Role.BUSINESS_ANALYST)
        self.assertIn("one implemented user journey", result.response)
        self.assertIn("Loan-term calculation is mentioned in the menu but not implemented", result.response)

    def test_developer_role_gets_technical_detail(self) -> None:
        service = self.make_service()
        result = service.run_turn(
            role=Role.DEVELOPER,
            message="How is the monthly payment calculated?",
            scenario_id="calculator_0_apr",
        )
        self.assertEqual(result.role, Role.DEVELOPER)
        self.assertIn("calculate_monthly_payment", result.response)
        self.assertIn("monthly_rate = annual_interest_rate / 12 / 100", result.response)

    def test_business_raw_code_request_creates_handoff(self) -> None:
        service = self.make_service()
        result = service.run_turn(
            role=Role.BUSINESS_ANALYST,
            message="Show me the raw code and source for this discrepancy.",
            scenario_id="calculator_0_apr",
        )
        self.assertTrue(result.handoff_required)
        self.assertIn("business-safe handoff", result.response)

    def test_create_ticket_generates_follow_up_ticket(self) -> None:
        service = self.make_service()
        result = service.run_turn(
            role=Role.DEVELOPER,
            message="Create a ticket for this mismatch.",
            scenario_id="calculator_0_apr",
        )
        self.assertEqual(result.intent.value, "create_ticket")
        self.assertIsNotNone(result.jira_ticket)
        self.assertTrue(result.jira_ticket.key.startswith("BRIDGE-"))

    def test_developer_fix_prompt_gets_fix_specific_answer(self) -> None:
        service = self.make_service()
        result = service.run_turn(
            role=Role.DEVELOPER,
            message="Does the code support 0% interest?",
            scenario_id="calculator_0_apr",
        )
        self.assertIn("does not support 0% interest loans", result.response)
        self.assertIn("annual_interest_rate <= 0", result.response)

    def test_business_impact_prompt_gets_impact_specific_answer(self) -> None:
        service = self.make_service()
        result = service.run_turn(
            role=Role.DEVELOPER,
            message="What tests exist today?",
            scenario_id="calculator_0_apr",
        )
        self.assertIn("The current tests cover several repayment cases", result.response)
        self.assertIn("0% interest handling", result.response)


if __name__ == "__main__":
    unittest.main()
