from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from bridge.models import Role


@dataclass(frozen=True)
class PersonaConfig:
    display_name: str
    system_instructions: str
    visible_doc_types: List[str]
    hidden_doc_types: List[str]
    tone: str
    voice_id: str = ""


PERSONAS: Dict[Role, PersonaConfig] = {
    Role.BUSINESS_ANALYST: PersonaConfig(
        display_name="Business Analyst",
        system_instructions=(
            "You are speaking to a Business Analyst. Follow these rules strictly:\n"
            "- Translate all technical concepts into business impact and customer outcomes\n"
            "- NEVER show raw source code, function signatures, or stack traces\n"
            "- Instead of code references, describe what the system does in plain English\n"
            "- Reference business requirements, KPIs, compliance needs, and stakeholder commitments\n"
            "- When discussing discrepancies, frame them as business risks and customer impact\n"
            "- Suggest business-appropriate actions: create tickets, escalate, schedule reviews\n"
            "- Use professional, non-technical language throughout"
        ),
        visible_doc_types=[
            "business_requirements",
            "stakeholder_comms",
            "jira_tickets",
            "persona_conflicts",
            "technical_documentation_summary",
        ],
        hidden_doc_types=["raw_code", "test_files"],
        tone="professional, non-technical, business-outcome focused",
        voice_id="EXAVITQu4vr4xnSDxMaL",  # "Sarah" — warm, professional
    ),
    Role.DEVELOPER: PersonaConfig(
        display_name="Developer",
        system_instructions=(
            "You are speaking to a Developer. Follow these rules strictly:\n"
            "- Include file paths, function names, line references, and code snippets\n"
            "- Reference specific validation logic, formulae, and implementation details\n"
            "- Identify test coverage gaps and suggest specific test cases\n"
            "- When discussing discrepancies, identify the exact code changes needed\n"
            "- Provide actionable technical recommendations with implementation steps\n"
            "- Reference Jira tickets by key and link issues to specific code locations\n"
            "- Use precise technical language"
        ),
        visible_doc_types=[
            "raw_code",
            "test_files",
            "technical_documentation",
            "jira_tickets",
            "business_requirements",
            "stakeholder_comms",
            "persona_conflicts",
        ],
        hidden_doc_types=["pricing_strategy", "customer_pii"],
        tone="technical, precise, actionable",
        voice_id="JBFqnCBsd6RMkjVDRZzb",  # "George" — clear, precise
    ),
}


def get_persona(role: Role) -> PersonaConfig:
    return PERSONAS[role]
