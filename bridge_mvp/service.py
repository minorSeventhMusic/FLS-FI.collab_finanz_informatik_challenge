from __future__ import annotations

from dataclasses import dataclass

from bridge_mvp.adapters import CodeContextAdapter, JiraAdapter
from bridge_mvp.llm import LLMClient, build_llm_client
from bridge_mvp.persistence import ProjectStateStore
from bridge_mvp.repo_qa import build_repo_answer
from bridge_mvp.types import Intent, Role, TurnResult
from bridge_mvp.workflow import compile_workflow


DEFAULT_SCENARIO_ID = "calculator_0_apr"


@dataclass
class BridgeService:
    store: ProjectStateStore
    jira: JiraAdapter
    code_context: CodeContextAdapter
    llm: LLMClient

    def run_turn(self, role: Role, message: str, scenario_id: str = DEFAULT_SCENARIO_ID) -> TurnResult:
        scenario = self.code_context.get_scenario(scenario_id)
        ticket = self.jira.ensure_seed_ticket(scenario)
        repo_answer = build_repo_answer(role, message, scenario)

        workflow = compile_workflow()
        state = workflow.invoke(
            {
                "user_message": message,
                "role": role.value,
                "scenario_id": scenario_id,
                "business_requirement": scenario.business_requirement,
                "technical_context": scenario.technical_context,
                "jira_ticket_text": scenario.jira_ticket,
                "persona_conflicts": scenario.persona_conflicts,
                "stakeholder_update": scenario.stakeholder_update,
                "ticket_key": ticket.key,
            }
        )

        handoff_required = bool(state["restricted"])
        workflow_response = state["final_response"]
        if handoff_required:
            final_draft = workflow_response
        else:
            final_draft = (
                f"{repo_answer.answer}\nRelevant files: {', '.join(repo_answer.relevant_files)}."
            )

        response = self._render_response(role, message, final_draft, scenario.title)
        self.store.append_conversation(role, message, response)

        if handoff_required:
            self.store.append_handoff(role, state["handoff_reason"], message)

        intent = Intent(state["intent"])
        active_ticket = ticket
        if intent == Intent.CREATE_TICKET:
            active_ticket = self.jira.create_ticket(
                title="Bridge follow-up: calculator 0% APR gap",
                description="Track the mismatch between the 0% APR business requirement and the current validation logic.",
                priority="High",
            )

        return TurnResult(
            role=role,
            intent=intent,
            response=response,
            alignment_score=int(state["alignment_score"]),
            relevant_files=repo_answer.relevant_files,
            handoff_required=handoff_required,
            handoff_reason=state["handoff_reason"] or None,
            jira_ticket=active_ticket,
        )

    def _render_response(
        self, role: Role, message: str, workflow_response: str, scenario_title: str
    ) -> str:
        system_prompt = (
            f"You are The Bridge speaking to a {role.value}. Keep the answer concise and tie it to the scenario."
        )
        user_prompt = (
            f"Scenario: {scenario_title}\n"
            f"User message: {message}\n"
            f"Draft response: {workflow_response}"
        )
        return self.llm.generate(system_prompt, user_prompt)


def build_default_service(state_path: str = "project_state.json") -> BridgeService:
    store = ProjectStateStore(state_path)
    return BridgeService(
        store=store,
        jira=JiraAdapter(store),
        code_context=CodeContextAdapter(),
        llm=build_llm_client(),
    )
