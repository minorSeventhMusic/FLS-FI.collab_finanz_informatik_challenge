from __future__ import annotations

import json
from typing import Any, Dict, Literal

from langgraph.graph import END, START, StateGraph

from bridge.alignment import analyze_alignment
from bridge.config import DEFAULT_SCENARIO
from bridge.context import assemble
from bridge.jira import JiraAdapter
from bridge.llm import LLMClient, build_llm_client
from bridge.models import (
    BridgeState,
    ConversationEntry,
    HandoffRecord,
    Intent,
    Role,
)
from bridge.personas import get_persona
from bridge.persistence import ProjectStateStore
from bridge.prompts.system import (
    CONCIERGE_GATE_PROMPT,
    HANDOFF_RESPONSE_PROMPT,
    INTENT_CLASSIFICATION_PROMPT,
    RESPONSE_SYSTEM_PROMPT,
)
from bridge.scenarios import get_scenario


# Module-level singletons, initialized via init_services()
_llm: LLMClient = None  # type: ignore[assignment]
_store: ProjectStateStore = None  # type: ignore[assignment]
_jira: JiraAdapter = None  # type: ignore[assignment]


def init_services(
    llm: LLMClient = None,
    store: ProjectStateStore = None,
    jira: JiraAdapter = None,
) -> None:
    global _llm, _store, _jira
    _llm = llm or build_llm_client()
    _store = store or ProjectStateStore()
    _jira = jira or JiraAdapter(_store)


def _ensure_services() -> None:
    if _llm is None:
        init_services()


# ── Node Functions ───────────────────────────────────────────────────────


def classify_intent(state: BridgeState) -> Dict[str, Any]:
    _ensure_services()
    prompt = INTENT_CLASSIFICATION_PROMPT.format(
        role=state["role"],
        user_message=state["user_message"],
    )
    raw = _llm.generate(prompt, state["user_message"])
    raw_clean = raw.strip().lower().replace(" ", "_")

    try:
        intent = Intent(raw_clean)
    except ValueError:
        intent = Intent.GENERAL

    return {"intent": intent.value}


def assemble_context(state: BridgeState) -> Dict[str, Any]:
    _ensure_services()
    role = Role(state["role"])
    intent = Intent(state["intent"])
    scenario_id = state.get("scenario_id", DEFAULT_SCENARIO)
    scenario = get_scenario(scenario_id)

    # Seed Jira tickets
    _jira.ensure_seed_tickets(scenario)

    # Load conversation history
    history = _store.get_conversations(role)

    result = assemble(role, intent, scenario, state["user_message"], history)

    return {
        "assembled_context": result.context_string,
        "relevant_files": result.relevant_files,
        "conversation_history": result.conversation_history_string,
    }


def concierge_gate(state: BridgeState) -> Dict[str, Any]:
    _ensure_services()
    prompt = CONCIERGE_GATE_PROMPT.format(
        role=state["role"],
        user_message=state["user_message"],
        intent=state["intent"],
    )
    raw = _llm.generate(prompt, state["user_message"])

    try:
        data = json.loads(raw.strip())
        restricted = bool(data.get("restricted", False))
        reason = data.get("reason", "")
    except (json.JSONDecodeError, AttributeError):
        restricted = False
        reason = ""

    return {"restricted": restricted, "handoff_reason": reason}


def route_after_gate(state: BridgeState) -> Literal["generate_response", "generate_handoff_response"]:
    if state.get("restricted", False):
        return "generate_handoff_response"
    return "generate_response"


def generate_response(state: BridgeState) -> Dict[str, Any]:
    _ensure_services()
    role = Role(state["role"])
    persona = get_persona(role)

    system = RESPONSE_SYSTEM_PROMPT.format(
        role_display_name=persona.display_name,
        persona_instructions=persona.system_instructions,
        assembled_context=state["assembled_context"],
        conversation_history=state.get("conversation_history", ""),
    )
    raw = _llm.generate(system, state["user_message"])
    return {"raw_response": raw}


def generate_handoff_response(state: BridgeState) -> Dict[str, Any]:
    _ensure_services()
    role = Role(state["role"])
    persona = get_persona(role)

    system = HANDOFF_RESPONSE_PROMPT.format(
        role_display_name=persona.display_name,
        user_message=state["user_message"],
        handoff_reason=state.get("handoff_reason", ""),
        assembled_context=state.get("assembled_context", ""),
    )
    raw = _llm.generate(system, state["user_message"])

    # Persist handoff
    _store.append_handoff(HandoffRecord(
        role=state["role"],
        reason=state.get("handoff_reason", ""),
        original_message=state["user_message"],
        timestamp="",
    ))

    return {
        "raw_response": raw,
        "final_response": raw,
        "alignment_score": 0,
        "alignment_summary": "",
        "alignment_discrepancies": "[]",
    }


def run_alignment(state: BridgeState) -> Dict[str, Any]:
    _ensure_services()
    result = analyze_alignment(state["assembled_context"], _llm)

    return {
        "alignment_discrepancies": json.dumps([
            {
                "id": d.id,
                "severity": d.severity,
                "category": d.category,
                "description": d.description,
                "evidence_sources": d.evidence_sources,
                "business_impact": d.business_impact,
                "technical_detail": d.technical_detail,
            }
            for d in result.discrepancies
        ]),
        "alignment_score": result.overall_score,
        "alignment_summary": result.summary,
    }


def handle_side_effects(state: BridgeState) -> Dict[str, Any]:
    _ensure_services()
    role = Role(state["role"])
    intent = Intent(state["intent"])
    response = state.get("raw_response", "")
    jira_action = "none"
    jira_payload = "{}"
    scenario_id = state.get("scenario_id", DEFAULT_SCENARIO)

    # Create ticket if requested
    if intent == Intent.CREATE_TICKET:
        ticket = _jira.create_ticket(
            title="Bridge follow-up: alignment gap detected",
            description=(
                "Automated ticket created by The Bridge.\n\n"
                f"User ({state['role']}): {state['user_message']}\n\n"
                f"Alignment score: {state.get('alignment_score', 'N/A')}%\n"
                f"Summary: {state.get('alignment_summary', 'N/A')}"
            ),
            priority="High",
        )
        jira_action = "create"
        jira_payload = json.dumps({"key": ticket.key, "title": ticket.title})
        response += f"\n\nTicket **{ticket.key}** has been created: \"{ticket.title}\""

    # Persist conversation
    _store.append_conversation(ConversationEntry(
        role=state["role"],
        user_message=state["user_message"],
        assistant_response=response,
        intent=state["intent"],
        alignment_score=state.get("alignment_score"),
        timestamp="",
    ))

    # Persist alignment snapshot
    score = state.get("alignment_score", 0)
    try:
        disc_count = len(json.loads(state.get("alignment_discrepancies", "[]")))
    except (json.JSONDecodeError, TypeError):
        disc_count = 0
    _store.append_alignment_snapshot(score, disc_count, scenario_id)

    return {
        "final_response": response,
        "jira_action": jira_action,
        "jira_payload": jira_payload,
    }


# ── Graph Compilation ────────────────────────────────────────────────────


def compile_workflow():
    graph = StateGraph(BridgeState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("assemble_context", assemble_context)
    graph.add_node("concierge_gate", concierge_gate)
    graph.add_node("generate_response", generate_response)
    graph.add_node("generate_handoff_response", generate_handoff_response)
    graph.add_node("run_alignment", run_alignment)
    graph.add_node("handle_side_effects", handle_side_effects)

    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", "assemble_context")
    graph.add_edge("assemble_context", "concierge_gate")
    graph.add_conditional_edges(
        "concierge_gate",
        route_after_gate,
        {
            "generate_response": "generate_response",
            "generate_handoff_response": "generate_handoff_response",
        },
    )
    graph.add_edge("generate_response", "run_alignment")
    graph.add_edge("run_alignment", "handle_side_effects")
    graph.add_edge("handle_side_effects", END)
    graph.add_edge("generate_handoff_response", END)

    return graph.compile()
