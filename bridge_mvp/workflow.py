from __future__ import annotations

from typing import Dict, Literal

from langgraph.graph import END, StateGraph

from bridge_mvp.types import BridgeState, Intent, Role


def _mentions_any(message: str, *tokens: str) -> bool:
    return any(token in message for token in tokens)


def infer_intent(message: str) -> Intent:
    lowered = message.lower()
    if "ticket" in lowered and _mentions_any(lowered, "create", "open", "raise", "make"):
        return Intent.CREATE_TICKET
    if _mentions_any(lowered, "ticket status", "status of", "jira status", "is jira", "what's the status"):
        return Intent.TICKET_STATUS
    if _mentions_any(lowered, "why", "mismatch", "discrepancy", "drift", "difference", "not matching"):
        return Intent.DISCREPANCY_CHECK
    return Intent.GENERAL


def compute_alignment_score(business_requirement: str, technical_context: str) -> int:
    score = 82
    requirement_mentions_zero = "0%" in business_requirement or "0% interest" in business_requirement
    code_rejects_zero = "annual_interest_rate <= 0" in technical_context
    if requirement_mentions_zero and code_rejects_zero:
        score -= 37
    elif code_rejects_zero:
        score -= 15
    return max(0, min(score, 100))


def hydrate_context(state: BridgeState) -> Dict[str, object]:
    return {
        "intent": infer_intent(state["user_message"]).value,
        "alignment_score": compute_alignment_score(
            state["business_requirement"], state["technical_context"]
        ),
    }


def concierge_gate(state: BridgeState) -> Dict[str, object]:
    restricted = False
    reason = ""
    lowered = state["user_message"].lower()
    if state["role"] == Role.BUSINESS_ANALYST.value and any(
        token in lowered for token in ("raw code", "full code", "stack trace", "source")
    ):
        restricted = True
        reason = "Business users receive a translated technical summary instead of raw code."
    return {"restricted": restricted, "handoff_reason": reason}


def route_role(state: BridgeState) -> Literal["business_response", "developer_response"]:
    if state["role"] == Role.BUSINESS_ANALYST.value:
        return "business_response"
    return "developer_response"


def build_business_response(state: BridgeState) -> Dict[str, object]:
    lowered = state["user_message"].lower()
    if state["restricted"]:
        response = (
            "The implementation currently rejects 0% promotional loans, which conflicts with the "
            "demo requirement. I have logged this as a business-safe handoff for technical review."
        )
    elif state["intent"] == Intent.TICKET_STATUS.value:
        response = (
            f"{state['ticket_key']} remains open because the calculator still blocks 0% loans. "
            f"Current alignment score: {state['alignment_score']}%."
        )
    elif state["intent"] == Intent.CREATE_TICKET.value:
        response = (
            "I can create a follow-up ticket for the mismatch between the product promise and the "
            "calculator implementation, with a business-facing summary for engineering."
        )
    elif _mentions_any(lowered, "impact", "business risk", "customer", "customer impact"):
        response = (
            "Customer-facing impact is immediate: a promotional 0% loan could be advertised, but the "
            "current calculator would reject it, creating drop-off and trust risk."
        )
    elif _mentions_any(lowered, "fix", "resolve", "solution", "what should we do"):
        response = (
            "The business-safe fix is to support 0% promotional loans explicitly, keep negative-rate "
            "validation, and confirm the quote still reports zero interest transparently."
        )
    elif _mentions_any(lowered, "email", "stakeholder", "update", "client"):
        response = (
            "Stakeholder update: the issue is understood, the needed change is limited to 0% loan handling, "
            "and once implemented it will unblock promotional campaigns without changing normal-rate behavior."
        )
    else:
        response = (
            "There is a business-to-technical mismatch in the seeded calculator scenario: the product "
            "needs support for promotional 0% loans, but the current logic rejects them. "
            f"Alignment is {state['alignment_score']}%."
        )
    return {"final_response": response}


def build_developer_response(state: BridgeState) -> Dict[str, object]:
    lowered = state["user_message"].lower()
    if state["intent"] == Intent.TICKET_STATUS.value:
        response = (
            f"{state['ticket_key']} is still To Do. Root cause: "
            "`annual_interest_rate <= 0` raises before the amortization branch can handle 0%."
        )
    elif state["intent"] == Intent.CREATE_TICKET.value:
        response = (
            "Recommended ticket: add a zero-interest branch using `loan_amount / loan_duration_months`, "
            "keep negative-rate validation, and cover the change with tests."
        )
    elif _mentions_any(lowered, "fix", "resolve", "solution", "implement"):
        response = (
            "Implement a zero-rate branch before the amortization formula: allow `annual_interest_rate == 0`, "
            "return straight-line payments, keep negative-rate rejection, and add regression tests."
        )
    elif _mentions_any(lowered, "test", "tests", "coverage"):
        response = (
            "Add tests for 0% APR monthly payment, zero total interest, and preserving validation for negative "
            "rates and zero duration."
        )
    elif _mentions_any(lowered, "code", "function", "validation", "root cause"):
        response = (
            "The root cause is in `calculate_monthly_payment`: validation rejects `annual_interest_rate <= 0`, "
            "so the function never reaches a branch that could support 0% APR."
        )
    elif _mentions_any(lowered, "business", "impact", "stakeholder"):
        response = (
            "From engineering's perspective, the defect blocks a valid promotional product and creates a gap "
            "between documented behavior and runtime behavior."
        )
    else:
        response = (
            "The calculator rejects 0% APR because validation raises on "
            "`annual_interest_rate <= 0`. The technical fix is a dedicated zero-rate path and a test "
            "that confirms zero total interest."
        )
    return {"final_response": response}


def compile_workflow():
    graph = StateGraph(BridgeState)
    graph.add_node("hydrate_context", hydrate_context)
    graph.add_node("concierge_gate", concierge_gate)
    graph.add_node("business_response", build_business_response)
    graph.add_node("developer_response", build_developer_response)

    graph.set_entry_point("hydrate_context")
    graph.add_edge("hydrate_context", "concierge_gate")
    graph.add_conditional_edges(
        "concierge_gate",
        route_role,
        {
            "business_response": "business_response",
            "developer_response": "developer_response",
        },
    )
    graph.add_edge("business_response", END)
    graph.add_edge("developer_response", END)
    return graph.compile()
