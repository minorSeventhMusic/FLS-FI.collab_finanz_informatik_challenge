from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Literal, Optional, TypedDict


class Role(str, Enum):
    BUSINESS_ANALYST = "business_analyst"
    DEVELOPER = "developer"


class Intent(str, Enum):
    DISCREPANCY_CHECK = "discrepancy_check"
    CREATE_TICKET = "create_ticket"
    TICKET_STATUS = "ticket_status"
    GENERAL = "general"


@dataclass(frozen=True)
class ScenarioBundle:
    scenario_id: str
    title: str
    business_requirement: str
    technical_context: str
    repo_files: Dict[str, str]
    jira_ticket: str
    jira_ticket_key: str
    stakeholder_update: str
    persona_conflicts: str


@dataclass
class JiraTicket:
    key: str
    title: str
    status: str
    priority: str
    description: str
    history: List[str] = field(default_factory=list)


@dataclass
class TurnResult:
    role: Role
    intent: Intent
    response: str
    alignment_score: int
    relevant_files: List[str]
    handoff_required: bool
    handoff_reason: Optional[str]
    jira_ticket: Optional[JiraTicket]


class BridgeState(TypedDict, total=False):
    user_message: str
    role: str
    scenario_id: str
    business_requirement: str
    technical_context: str
    jira_ticket_text: str
    persona_conflicts: str
    stakeholder_update: str
    intent: str
    restricted: bool
    handoff_reason: str
    alignment_score: int
    final_response: str
    jira_action: Dict[str, str]
    ticket_key: str


RoleName = Literal["business_analyst", "developer"]
