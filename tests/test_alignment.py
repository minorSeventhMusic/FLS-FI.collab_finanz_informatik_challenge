from __future__ import annotations

import unittest

from bridge.alignment import analyze_alignment
from bridge.llm import StubLLMClient


class TestAlignment(unittest.TestCase):
    def setUp(self):
        self.llm = StubLLMClient()

    def test_stub_returns_all_discrepancies(self):
        result = analyze_alignment("test context", self.llm)
        self.assertEqual(len(result.discrepancies), 8)

    def test_catch_the_lie_critical(self):
        result = analyze_alignment("test context", self.llm)
        critical = [d for d in result.discrepancies if d.severity == "critical"]
        self.assertGreaterEqual(len(critical), 1)
        lie_found = any("code_vs_comms" in d.category for d in critical)
        self.assertTrue(lie_found, "Should detect the stakeholder email lie")

    def test_score_capped_on_critical(self):
        result = analyze_alignment("test context", self.llm)
        # Score should be capped at 35 due to critical code_vs_comms discrepancy
        self.assertLessEqual(result.overall_score, 35)

    def test_summary_present(self):
        result = analyze_alignment("test context", self.llm)
        self.assertTrue(len(result.summary) > 0)

    def test_discrepancy_fields_complete(self):
        result = analyze_alignment("test context", self.llm)
        for d in result.discrepancies:
            self.assertTrue(d.id)
            self.assertIn(d.severity, ("critical", "high", "medium", "low"))
            self.assertTrue(d.description)
            self.assertIsInstance(d.evidence_sources, list)


if __name__ == "__main__":
    unittest.main()
