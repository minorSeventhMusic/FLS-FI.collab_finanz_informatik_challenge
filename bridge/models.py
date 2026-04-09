from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, TypedDict


class Role(str, Enum):
    BUSINESS_ANALYST = "business_analyst"
    DEVELOPER = "developer"


class Intent(str, Enum):
    DISCREPANCY_CHECK = "discrepancy_check"
    CODE_QUESTION = "code_question"
    BUSINESS_QUESTION = "business_question"
    CREATE_TICKET = "create_ticket"
    UPDATE_TICKET = "update_ticket"
    TICKET_STATUS = "ticket_status"
    ALIGNMENT_REPORT = "alignment_report"
    GENERAL = "general"


@dataclass
class JiraTicketData:
    key: str
    title: str
    status: str
    priority: str
    description: str
    assignee: Optional[str] = None
    external_url: str = ""
    history: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ScenarioBundle:
    scenario_id: str
    title: str
    description: str
    repo_files: Dict[str, str]
    business_requirements: str
    technical_documentation: str
    jira_tickets: List[JiraTicketData]
    stakeholder_comms: str
    persona_conflicts: str
    known_discrepancies: List[str]


@dataclass
class ConversationEntry:
    role: str
    user_message: str
    assistant_response: str
    intent: str
    alignment_score: Optional[int] = None
    timestamp: str = ""


@dataclass
class DiscrepancyItem:
    id: str
    severity: str
    category: str
    description: str
    evidence_sources: List[str]
    business_impact: str
    technical_detail: str


@dataclass
class AlignmentResult:
    discrepancies: List[DiscrepancyItem]
    overall_score: int
    summary: str


@dataclass
class HandoffRecord:
    role: str
    reason: str
    original_message: str
    timestamp: str


@dataclass
class TurnResult:
    role: Role
    intent: Intent
    response: str
    alignment: Optional[AlignmentResult]
    relevant_files: List[str]
    handoff_required: bool
    handoff_reason: Optional[str]
    jira_updates: List[JiraTicketData]


class BridgeState(TypedDict, total=False):
    user_message: str
    role: str
    scenario_id: str
    intent: str
    assembled_context: str
    relevant_files: List[str]
    conversation_history: str
    restricted: bool
    handoff_reason: str
    raw_response: str
    alignment_discrepancies: str
    alignment_score: int
    alignment_summary: str
    jira_action: str
    jira_payload: str
    final_response: str
