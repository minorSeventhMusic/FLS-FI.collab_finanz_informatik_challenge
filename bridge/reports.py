from __future__ import annotations

import json
from dataclasses import asdict

from bridge.alignment import analyze_alignment
from bridge.context import assemble
from bridge.llm import LLMClient
from bridge.models import Intent, Role, ScenarioBundle
from bridge.personas import get_persona
from bridge.persistence import ProjectStateStore
from bridge.prompts.reports import REPORT_GENERATION_PROMPT
from bridge.scenarios import get_scenario


REPORT_SYSTEM = (
    "You are a professional report writer for FI.collab. "
    "Generate clear, structured reports adapted to the recipient's role."
)


def generate_report(
    role: Role,
    report_type: str,
    scenario_id: str,
    llm: LLMClient,
    store: ProjectStateStore,
) -> str:
    scenario = get_scenario(scenario_id)
    history = store.get_conversations(role)
    ctx = assemble(role, Intent.ALIGNMENT_REPORT, scenario, "", history)
    alignment = analyze_alignment(ctx.context_string, llm)
    persona = get_persona(role)

    prompt = REPORT_GENERATION_PROMPT.format(
        report_type=report_type,
        role_display_name=persona.display_name,
        assembled_context=ctx.context_string,
        alignment_json=json.dumps(asdict(alignment), indent=2),
        conversation_history=ctx.conversation_history_string,
    )
    return llm.generate(REPORT_SYSTEM, prompt)
