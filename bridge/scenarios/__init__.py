from __future__ import annotations

from bridge.scenarios.calculator_0_apr import CALCULATOR_0_APR_SCENARIO
from bridge.models import ScenarioBundle

SCENARIOS = {"calculator_0_apr": CALCULATOR_0_APR_SCENARIO}


def get_scenario(scenario_id: str) -> ScenarioBundle:
    return SCENARIOS[scenario_id]
