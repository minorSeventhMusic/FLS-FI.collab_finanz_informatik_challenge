from __future__ import annotations

from typing import Dict, List, Optional

from bridge.models import JiraTicketData, ScenarioBundle
from bridge.scenarios.calculator_0_apr import CALCULATOR_0_APR_SCENARIO

SCENARIOS = {"calculator_0_apr": CALCULATOR_0_APR_SCENARIO}


def get_scenario(scenario_id: str) -> ScenarioBundle:
    return SCENARIOS[scenario_id]


def build_github_scenario(
    repo_files: Dict[str, str],
    owner: str,
    repo: str,
    commit_history: str = "",
) -> ScenarioBundle:
    """Build a lightweight scenario from live GitHub repo files."""
    # Extract README as business context if available
    readme = ""
    for path, content in repo_files.items():
        if path.lower() in ("readme.md", "readme.txt", "readme"):
            readme = content
            break

    # Use all files as technical documentation + commit history
    tech_doc = "\n\n".join(
        f"=== {path} ===\n{content[:2000]}"
        for path, content in repo_files.items()
    )
    if commit_history:
        tech_doc += f"\n\n=== GIT COMMIT HISTORY ===\n{commit_history}"

    scenario = ScenarioBundle(
        scenario_id=f"github_{owner}_{repo}",
        title=f"{owner}/{repo} (GitHub)",
        description=f"Live repository from GitHub: {owner}/{repo}",
        repo_files=repo_files,
        business_requirements=readme or f"Repository: {owner}/{repo}. No README found.",
        technical_documentation=tech_doc[:8000],
        jira_tickets=[],
        stakeholder_comms="",
        persona_conflicts="",
        known_discrepancies=[],
    )

    # Register it so get_scenario can find it
    scenario_id = scenario.scenario_id
    SCENARIOS[scenario_id] = scenario
    return scenario
