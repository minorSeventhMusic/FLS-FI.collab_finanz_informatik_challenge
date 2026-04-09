from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

from bridge.config import MAX_CONTEXT_CHARS, MAX_CONVERSATION_HISTORY_TURNS
from bridge.models import ConversationEntry, Intent, Role, ScenarioBundle
from bridge.personas import get_persona


@dataclass
class ContextResult:
    context_string: str
    relevant_files: List[str]
    conversation_history_string: str


def _tokens(text: str) -> List[str]:
    stopwords = {
        "the", "and", "for", "with", "that", "this", "what", "does", "about",
        "from", "into", "have", "will", "would", "should", "there", "here",
        "your", "show", "tell", "how", "why", "can", "are", "was", "not",
    }
    return [
        t for t in re.findall(r"[a-zA-Z_]{3,}", text.lower())
        if t not in stopwords
    ]


def _select_relevant_files(question: str, repo_files: Dict[str, str]) -> List[str]:
    q_tokens = set(_tokens(question))
    scores = []
    for path, content in repo_files.items():
        haystack = f"{path} {content.lower()}"
        score = sum(1 for t in q_tokens if t in haystack)
        scores.append((score, path))
    scores.sort(key=lambda item: (-item[0], item[1]))
    chosen = [path for score, path in scores if score > 0][:4]
    if not chosen:
        chosen = list(repo_files.keys())[:2]
    return chosen


def _format_conversation_history(entries: List[ConversationEntry]) -> str:
    if not entries:
        return "(No prior conversation)"
    recent = entries[-MAX_CONVERSATION_HISTORY_TURNS:]
    lines = []
    for e in recent:
        lines.append(f"User: {e.user_message}")
        lines.append(f"Bridge: {e.assistant_response}")
    return "\n".join(lines)


def _build_code_summary(scenario: ScenarioBundle) -> str:
    return (
        "The repository contains a Python CLI loan calculator (calculator.py) that calculates "
        "monthly payments using the standard amortization formula. It validates that loan amount, "
        "duration, and interest rate are all greater than zero. A test suite (test_calculator.py) "
        "covers standard loan calculations and negative input validation but does not test 0% "
        "interest scenarios. The CLI offers a menu with monthly payment calculation (implemented) "
        "and loan term calculation (not yet implemented)."
    )


def assemble(
    role: Role,
    intent: Intent,
    scenario: ScenarioBundle,
    user_message: str,
    conversation_history: List[ConversationEntry],
) -> ContextResult:
    persona = get_persona(role)
    relevant_files = _select_relevant_files(user_message, scenario.repo_files)
    history_str = _format_conversation_history(conversation_history)

    sections = []

    # Business requirements — always included
    sections.append(f"=== BUSINESS REQUIREMENTS ===\n{scenario.business_requirements}")

    # Repository files — filtered by persona
    if "raw_code" in persona.hidden_doc_types:
        # BA gets a summary instead of code
        sections.append(f"=== REPOSITORY OVERVIEW ===\n{_build_code_summary(scenario)}")
        sections.append(f"=== TECHNICAL DOCUMENTATION ===\n{scenario.technical_documentation}")
    else:
        # Dev gets full code for relevant files
        file_sections = []
        for path in relevant_files:
            if path in scenario.repo_files:
                file_sections.append(f"--- {path} ---\n{scenario.repo_files[path]}")
        if file_sections:
            sections.append("=== REPOSITORY FILES ===\n" + "\n\n".join(file_sections))
        sections.append(f"=== TECHNICAL DOCUMENTATION ===\n{scenario.technical_documentation}")

    # Jira tickets — always included
    jira_text = "\n\n".join(t.description for t in scenario.jira_tickets)
    sections.append(f"=== JIRA TICKETS ===\n{jira_text}")

    # Stakeholder communications — always included (contains the lie to catch)
    all_comms = scenario.stakeholder_comms
    if scenario.additional_comms:
        all_comms += "\n\n---\n\n" + "\n\n---\n\n".join(scenario.additional_comms)
    sections.append(f"=== STAKEHOLDER COMMUNICATIONS ===\n{all_comms}")

    # Persona conflicts — always included
    sections.append(f"=== PERSONA CONFLICTS ===\n{scenario.persona_conflicts}")

    # Persona details — if available
    if scenario.persona_details:
        details = "\n\n".join(
            f"--- {name} ---\n{detail}"
            for name, detail in scenario.persona_details.items()
        )
        sections.append(f"=== PERSONA DETAILS ===\n{details}")

    context_string = "\n\n".join(sections)

    # Truncate if over budget
    if len(context_string) > MAX_CONTEXT_CHARS:
        context_string = context_string[:MAX_CONTEXT_CHARS] + "\n\n[... context truncated ...]"

    return ContextResult(
        context_string=context_string,
        relevant_files=relevant_files,
        conversation_history_string=history_str,
    )
