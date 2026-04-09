from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Protocol


class LLMClient(Protocol):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        ...


@dataclass
class StubLLMClient:
    """Deterministic fallback for demos and tests without an API key."""

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        lowered_system = system_prompt.lower()

        if "intent classifier" in lowered_system:
            return self._classify_intent(user_prompt)
        if "alignment analyst" in lowered_system:
            return self._alignment_stub()
        if "access control filter" in lowered_system:
            return self._concierge_stub(system_prompt, user_prompt)
        if "concierge protocol" in lowered_system:
            return self._handoff_stub(user_prompt)

        return self._response_stub(system_prompt, user_prompt)

    def _classify_intent(self, user_prompt: str) -> str:
        lowered = user_prompt.lower()
        if "create" in lowered and "ticket" in lowered:
            return "create_ticket"
        if any(w in lowered for w in ("open ticket", "raise ticket", "make ticket")):
            return "create_ticket"
        if any(w in lowered for w in ("update ticket", "change status", "move ticket")):
            return "update_ticket"
        if any(w in lowered for w in ("ticket status", "status of", "jira status", "what tickets")):
            return "ticket_status"
        if any(w in lowered for w in ("mismatch", "discrepancy", "drift", "not matching", "contradiction", "conflict")):
            return "discrepancy_check"
        if any(w in lowered for w in ("report", "summary", "alignment overview", "overall")):
            return "alignment_report"
        if any(w in lowered for w in ("code", "function", "implementation", "calculate", "validation", "test")):
            return "code_question"
        if any(w in lowered for w in ("business", "requirement", "stakeholder", "customer", "compliance")):
            return "business_question"
        return "general"

    def _concierge_stub(self, system_prompt: str, user_prompt: str) -> str:
        lowered = user_prompt.lower()
        is_ba = "business_analyst" in system_prompt.lower()
        if is_ba and any(w in lowered for w in ("raw code", "full code", "source code", "stack trace", "show me the code")):
            return json.dumps({"restricted": True, "reason": "Business Analysts receive translated summaries instead of raw source code."})
        return json.dumps({"restricted": False, "reason": ""})

    def _handoff_stub(self, user_prompt: str) -> str:
        return (
            "I understand you're looking for detailed technical information. "
            "That level of detail is best reviewed by the development team directly. "
            "However, I can share that the current implementation has a validation gap "
            "around 0% promotional loan handling. Would you like me to create a ticket "
            "for the technical team to provide a detailed code review?"
        )

    def _alignment_stub(self) -> str:
        return json.dumps({
            "discrepancies": [
                {
                    "id": "D1",
                    "severity": "critical",
                    "category": "code_vs_comms",
                    "description": "Stakeholder email claims '0% Interest Loans now live' but calculator.py rejects annual_interest_rate <= 0 with ValueError, and JIRA-104 status is still 'To Do'.",
                    "evidence_sources": ["mockup_answer_to_jira.md", "calculator.py", "mockup_jira.md"],
                    "business_impact": "Promotional 0% APR campaigns would fail at runtime, causing customer drop-off and trust damage.",
                    "technical_detail": "calculator.py line: if annual_interest_rate <= 0: raise ValueError. The amortization formula also divides by zero when rate is 0."
                },
                {
                    "id": "D2",
                    "severity": "critical",
                    "category": "code_vs_docs",
                    "description": "Amortization formula produces division by zero at 0% interest but documentation does not acknowledge this limitation.",
                    "evidence_sources": ["calculator.py", "mockup_calc_doc.md"],
                    "business_impact": "No mathematical path exists for the advertised 0% promotional product.",
                    "technical_detail": "Formula denominator (1+r)^n - 1 becomes 0 when r=0, causing division by zero before the ValueError guard."
                },
                {
                    "id": "D3",
                    "severity": "high",
                    "category": "jira_vs_comms",
                    "description": "JIRA-104 status is 'To Do' but stakeholder email subject says 'now live'.",
                    "evidence_sources": ["mockup_jira.md", "mockup_answer_to_jira.md"],
                    "business_impact": "Project tracking is out of sync with external communications, risking misinformed decisions.",
                    "technical_detail": "JIRA-104 has not been started; no commits reference this ticket."
                },
                {
                    "id": "D4",
                    "severity": "high",
                    "category": "test_coverage_gap",
                    "description": "No unit tests exist for 0% interest rate handling despite it being a high-priority Jira requirement.",
                    "evidence_sources": ["test_calculator.py", "mockup_jira.md"],
                    "business_impact": "Even if the code is fixed, there is no automated verification of the promotional product behavior.",
                    "technical_detail": "test_calculator.py tests standard, small, and large loans but no test for rate=0. Only negative rate raises are tested."
                },
                {
                    "id": "D5",
                    "severity": "high",
                    "category": "requirements_vs_code",
                    "description": "Business requirements describe a complex system (TCC, API integrations, CRM sync, compliance) but code is a basic CLI calculator.",
                    "evidence_sources": ["business_requirements.md", "calculator.py"],
                    "business_impact": "Massive scope gap between promised product capabilities and actual implementation.",
                    "technical_detail": "calculator.py has one function: calculate_monthly_payment. No APIs, no CRM, no compliance features."
                },
                {
                    "id": "D6",
                    "severity": "medium",
                    "category": "docs_vs_comms",
                    "description": "Technical documentation states annual_interest_rate must be > 0, but stakeholder email claims 0 is supported.",
                    "evidence_sources": ["mockup_calc_doc.md", "mockup_answer_to_jira.md"],
                    "business_impact": "Documentation and communications tell different stories to different audiences.",
                    "technical_detail": "mockup_calc_doc.md Input Validation section: 'annual_interest_rate > 0'."
                },
                {
                    "id": "D7",
                    "severity": "medium",
                    "category": "requirements_vs_code",
                    "description": "Persona conflicts (PM vs Compliance vs Marketing vs Risk vs UX) are documented but unresolved in technical scope.",
                    "evidence_sources": ["persona_overview.md", "business_requirements.md"],
                    "business_impact": "No architectural decisions address fundamental stakeholder trade-offs.",
                    "technical_detail": "No code or configuration reflects any resolution of the documented persona conflicts."
                },
                {
                    "id": "D8",
                    "severity": "low",
                    "category": "docs_vs_docs",
                    "description": "JIRA-104 acceptance criteria reference updating a 'Technical Constraints' section in documentation.md, but no such section exists.",
                    "evidence_sources": ["mockup_jira.md", "mockup_calc_doc.md"],
                    "business_impact": "Completion criteria cannot be verified against current documentation structure.",
                    "technical_detail": "mockup_calc_doc.md has no 'Technical Constraints' section; the referenced file name is also wrong (documentation.md vs mockup_calc_doc.md)."
                }
            ],
            "score": 28,
            "summary": "Critical misalignment: stakeholder communications claim a feature is live that the code actively rejects, while the Jira ticket tracking it has not been started."
        })

    def _response_stub(self, system_prompt: str, user_prompt: str) -> str:
        lowered = user_prompt.lower() if user_prompt else ""
        is_ba = "business analyst" in system_prompt.lower()

        # Ticket-related queries
        if any(w in lowered for w in ("ticket", "jira", "open ticket")):
            if "create" in lowered:
                return (
                    "I've created a follow-up ticket for this issue.\n\n"
                    "**JIRA-201**: \"Follow-up: alignment gap detected\"\n"
                    "- Priority: High\n"
                    "- Status: To Do\n\n"
                    "This is in addition to the existing **JIRA-104** which tracks the 0% interest rate fix."
                )
            if any(w in lowered for w in ("show", "list", "all", "open", "status")):
                return (
                    "**Open tickets:**\n\n"
                    "| Ticket | Title | Status | Priority |\n"
                    "|--------|-------|--------|----------|\n"
                    "| JIRA-104 | Handle Division by Zero for 0% Interest Rate Loans | To Do | High |\n\n"
                    "JIRA-104 has been open since the initial review. "
                    "No work has started despite the stakeholder email claiming the fix is live."
                )
            return (
                "**JIRA-104** — Handle Division by Zero for 0% Interest Rate Loans\n"
                "- Status: **To Do** (not started)\n"
                "- Priority: **High**\n\n"
                "Note: The stakeholder email claims this is already live, but the ticket is still open "
                "and the code still rejects 0% rates."
            )

        # 0% / interest queries
        if "0%" in lowered or "zero" in lowered or "interest" in lowered or "work" in lowered or "doesn't" in lowered or "doesn" in lowered:
            if is_ba:
                return (
                    "The 0% promotional loan feature is **not working**. Here's the situation:\n\n"
                    "1. The stakeholder email claims it's live — **this is incorrect**\n"
                    "2. JIRA-104 (the fix) is still in **To Do** status\n"
                    "3. Any customer trying a 0% loan will get an error\n\n"
                    "**Business risk:** Marketing campaigns for 0% APR will fail at checkout, "
                    "causing customer drop-off.\n\n"
                    "Would you like me to escalate this or create a follow-up ticket?"
                )
            return (
                "**Root cause:** `calculator.py` — validation rejects `annual_interest_rate <= 0`.\n\n"
                "```python\n"
                "if annual_interest_rate <= 0:\n"
                "    raise ValueError(\"annual_interest_rate must be greater than 0\")\n"
                "```\n\n"
                "The amortization formula also divides by zero when rate=0.\n\n"
                "**Fix:** Add a zero-rate branch before the formula:\n"
                "```python\n"
                "if annual_interest_rate == 0:\n"
                "    monthly_payment = loan_amount / loan_duration_months\n"
                "```\n\n"
                "**Tracked by:** JIRA-104 (Status: To Do, Priority: High)"
            )

        # Discrepancy / mismatch queries
        if any(w in lowered for w in ("mismatch", "discrepancy", "wrong", "lie", "contradiction")):
            if is_ba:
                return (
                    "**Key contradiction found:**\n\n"
                    "The stakeholder email (sent to the client) states:\n"
                    "> \"Support for 0% Interest Loans now live\"\n\n"
                    "However:\n"
                    "- The system **still rejects** 0% interest rates\n"
                    "- JIRA-104 tracking this fix is **still in To Do**\n"
                    "- No tests verify 0% loan behavior\n\n"
                    "This is a communication-to-reality gap that needs immediate attention."
                )
            return (
                "**Critical discrepancy:** Stakeholder email vs. code vs. Jira\n\n"
                "- `mockup_answer_to_jira.md`: claims \"0% Interest Loans now live\"\n"
                "- `calculator.py`: `annual_interest_rate <= 0` raises `ValueError`\n"
                "- `mockup_jira.md`: JIRA-104 status is \"To Do\"\n"
                "- `test_calculator.py`: no test for 0% rate\n\n"
                "Three sources contradict each other. The email is false."
            )

        # Default fallback
        if is_ba:
            return (
                "The loan calculator currently supports basic monthly payment calculation. "
                "The main issue is a **misalignment around 0% promotional loans** — "
                "the stakeholder email says it's supported, but it isn't.\n\n"
                "**Open ticket:** JIRA-104 (Priority: High, Status: To Do)\n\n"
                "What would you like to know more about?"
            )
        return (
            "Current state of `calculator.py`:\n"
            "- Monthly payment calculation via amortization formula\n"
            "- Strict validation: amount > 0, duration > 0, rate > 0\n"
            "- No 0% rate support (JIRA-104, To Do)\n"
            "- No TCC, no API integrations, no CRM sync\n\n"
            "What specific area would you like to explore?"
        )


class GeminiClient:
    def __init__(self) -> None:
        from google import genai

        self._model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self._fallback = StubLLMClient()

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        from google.genai import types

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.3,
                ),
            )
            return response.text
        except Exception as e:
            import streamlit as st
            st.warning(f"Gemini API error: {e.__class__.__name__}. Using offline mode.")
            return self._fallback.generate(system_prompt, user_prompt)


class OpenAIChatClient:
    def __init__(self) -> None:
        from openai import OpenAI

        self._model = os.getenv("OPENAI_MODEL", "gpt-5.4")
        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self._fallback = StubLLMClient()

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self._client.responses.create(
                model=self._model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.output_text
        except Exception as e:
            import streamlit as st
            st.warning(f"OpenAI API error: {e.__class__.__name__}. Using offline mode.")
            return self._fallback.generate(system_prompt, user_prompt)


def build_llm_client() -> LLMClient:
    if os.getenv("GEMINI_API_KEY"):
        return GeminiClient()
    if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your-key-here":
        return OpenAIChatClient()
    return StubLLMClient()
