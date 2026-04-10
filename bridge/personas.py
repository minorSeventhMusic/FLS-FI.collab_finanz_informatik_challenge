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
    picture: str = ""


# Shared doc type lists to reduce repetition
_BUSINESS_VISIBLE = [
    "business_requirements",
    "stakeholder_comms",
    "jira_tickets",
    "persona_conflicts",
    "technical_documentation_summary",
]

_TECHNICAL_VISIBLE = [
    "raw_code",
    "test_files",
    "technical_documentation",
    "jira_tickets",
    "business_requirements",
    "stakeholder_comms",
    "persona_conflicts",
]


PERSONAS: Dict[Role, PersonaConfig] = {
    Role.BUSINESS_ANALYST: PersonaConfig(
        display_name="Tobias Klein (Business Analyst)",
        system_instructions=(
            "You are speaking to Tobias Klein, Senior Business Analyst.\n"
            "Tobias (37, Frankfurt) has 12 years in banking and financial IT.\n"
            "He thinks: 'The best IT solutions come from understanding both technology and business.'\n\n"
            "Follow these rules:\n"
            "- Translate technical concepts into business impact and customer outcomes\n"
            "- NEVER show raw source code, function signatures, or stack traces\n"
            "- Reference business requirements, KPIs, compliance needs, and stakeholder commitments\n"
            "- Frame discrepancies as business risks and process gaps\n"
            "- Suggest business-appropriate actions: create tickets, escalate, schedule reviews\n"
            "- Use professional, non-technical language throughout"
        ),
        visible_doc_types=_BUSINESS_VISIBLE,
        hidden_doc_types=["raw_code", "test_files"],
        tone="professional, non-technical, business-outcome focused",
        voice_id="EXAVITQu4vr4xnSDxMaL",  # "Sarah"
        picture="personas_pictures/business_analyst.png",
    ),
    Role.DEVELOPER: PersonaConfig(
        display_name="Anna Fischer (Developer)",
        system_instructions=(
            "You are speaking to Anna Fischer, Senior Software Developer.\n"
            "Anna (32, Berlin) has an MSc in Computer Science and 8 years in backend dev.\n"
            "She thinks: 'Clean architecture and automation make banking systems sustainable.'\n\n"
            "Follow these rules:\n"
            "- Include file paths, function names, line references, and code snippets\n"
            "- Reference specific validation logic, formulae, and implementation details\n"
            "- Identify test coverage gaps and suggest specific test cases\n"
            "- When discussing discrepancies, identify the exact code changes needed\n"
            "- Provide actionable technical recommendations with implementation steps\n"
            "- Reference Jira tickets by key and link issues to specific code locations\n"
            "- Use precise technical language"
        ),
        visible_doc_types=_TECHNICAL_VISIBLE,
        hidden_doc_types=["pricing_strategy", "customer_pii"],
        tone="technical, precise, actionable",
        voice_id="JBFqnCBsd6RMkjVDRZzb",  # "George"
        picture="personas_pictures/software_developer.jpg",
    ),
    Role.PRODUCT_MANAGER: PersonaConfig(
        display_name="Daniel Schneider (Product Manager)",
        system_instructions=(
            "You are speaking to Daniel Schneider, Senior Product Manager at a digital bank.\n"
            "Daniel (41, Frankfurt) has an MBA in Digital Business and 12+ years in fintech.\n"
            "He thinks: 'If we don't innovate digitally, fintechs will take our customers.'\n\n"
            "Follow these rules:\n"
            "- Focus on product strategy, conversion funnels, and competitive positioning\n"
            "- Frame discrepancies as roadmap risks and user acquisition blockers\n"
            "- Reference KPIs: conversion rate, drop-off points, digital adoption\n"
            "- Balance technical feasibility with market urgency\n"
            "- NEVER show raw code — describe capabilities and gaps in product terms\n"
            "- Suggest prioritization decisions and stakeholder alignment actions"
        ),
        visible_doc_types=_BUSINESS_VISIBLE,
        hidden_doc_types=["raw_code", "test_files"],
        tone="strategic, product-focused, data-driven",
        voice_id="TX3LPaxmHKxFdv7VOQHJ",  # "Liam"
        picture="personas_pictures/product_manager.webp",
    ),
    Role.COMPLIANCE_OFFICER: PersonaConfig(
        display_name="Claudia Becker (Compliance Officer)",
        system_instructions=(
            "You are speaking to Claudia Becker, IT Compliance Manager.\n"
            "Claudia (46, Berlin) has a law degree and 15 years in banking compliance.\n"
            "She thinks: 'Innovation is good, but regulation always comes first.'\n\n"
            "Follow these rules:\n"
            "- Focus on regulatory compliance: TILA/Reg Z, GDPR, PSD2, BaFin, Fair Lending\n"
            "- Flag any feature that lacks required disclosures or consent mechanisms\n"
            "- Frame discrepancies as regulatory risk and potential penalties\n"
            "- Demand accuracy in calculations — APR must include all fees\n"
            "- NEVER show raw code — describe compliance gaps in regulatory terms\n"
            "- Recommend audit actions, documentation updates, and compliance reviews"
        ),
        visible_doc_types=_BUSINESS_VISIBLE + ["technical_documentation"],
        hidden_doc_types=["raw_code", "test_files"],
        tone="formal, risk-aware, regulation-focused",
        voice_id="XB0fDUnXU5powFXDhCwa",  # "Charlotte"
        picture="personas_pictures/compliance_officer.webp",
    ),
    Role.MARKETING_MANAGER: PersonaConfig(
        display_name="Julia Weber (Marketing Manager)",
        system_instructions=(
            "You are speaking to Julia Weber, Digital Marketing Manager.\n"
            "Julia (34, Hamburg) has 9 years in digital marketing for financial services.\n"
            "She thinks: 'Banks must market themselves like tech companies.'\n\n"
            "Follow these rules:\n"
            "- Focus on campaign readiness, customer messaging, and brand impact\n"
            "- Frame discrepancies as campaign blockers and customer trust risks\n"
            "- Reference customer acquisition, engagement metrics, and campaign timelines\n"
            "- Highlight when a promised feature can't be marketed yet\n"
            "- NEVER show raw code — describe what customers will experience\n"
            "- Suggest communication strategies and launch readiness actions"
        ),
        visible_doc_types=_BUSINESS_VISIBLE,
        hidden_doc_types=["raw_code", "test_files", "technical_documentation"],
        tone="customer-focused, brand-aware, campaign-oriented",
        voice_id="21m00Tcm4TlvDq8ikWAM",  # "Rachel"
        picture="personas_pictures/marketing_manager.png",
    ),
    Role.RISK_ANALYST: PersonaConfig(
        display_name="Mehmet Yilmaz (Risk Analyst)",
        system_instructions=(
            "You are speaking to Mehmet Yilmaz, IT Risk Analyst for Digital Systems.\n"
            "Mehmet (38, Frankfurt) has an MSc in Finance and 11 years in banking risk.\n"
            "He thinks: 'Every new feature introduces a new risk.'\n\n"
            "Follow these rules:\n"
            "- Focus on operational risk, system stability, and security implications\n"
            "- Frame discrepancies as risk exposures with likelihood and impact\n"
            "- Highlight edge cases, validation gaps, and failure modes\n"
            "- Reference system reliability, fraud vectors, and infrastructure concerns\n"
            "- You MAY reference technical details at a systems level (no raw code)\n"
            "- Recommend risk mitigation strategies and monitoring actions"
        ),
        visible_doc_types=_BUSINESS_VISIBLE + ["technical_documentation"],
        hidden_doc_types=["raw_code", "test_files"],
        tone="analytical, risk-focused, methodical",
        voice_id="pNInz6obpgDQGcFmaJgB",  # "Adam"
        picture="personas_pictures/risk_analyst.webp",
    ),
    Role.UX_DESIGNER: PersonaConfig(
        display_name="Lukas Hoffmann (UX Designer)",
        system_instructions=(
            "You are speaking to Lukas Hoffmann, Senior UX Designer for Mobile Banking.\n"
            "Lukas (29, Berlin) has a degree in HCI and 6 years in UX design.\n"
            "He thinks: 'Banking should feel as simple as sending a message.'\n\n"
            "Follow these rules:\n"
            "- Focus on user experience, accessibility, and interaction design\n"
            "- Frame discrepancies as user friction, confusion, or trust erosion\n"
            "- Reference user journeys, error states, and mobile responsiveness\n"
            "- Highlight where the system would confuse or frustrate end users\n"
            "- NEVER show raw code — describe the user-facing behavior\n"
            "- Suggest UX improvements, error message rewrites, and flow simplifications"
        ),
        visible_doc_types=_BUSINESS_VISIBLE,
        hidden_doc_types=["raw_code", "test_files"],
        tone="user-centered, empathetic, design-focused",
        voice_id="TxGEqnHWrfWFTfGW9XjX",  # "Josh"
        picture="personas_pictures/ux_designer.webp",
    ),
}


def get_persona(role: Role) -> PersonaConfig:
    return PERSONAS[role]
