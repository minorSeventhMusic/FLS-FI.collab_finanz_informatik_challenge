from __future__ import annotations

from bridge_mvp.types import ScenarioBundle


CALCULATOR_REQUIREMENTS = """Project Documentation: "FlexiLoan" Retail Engine
1. Executive Summary

FlexiLoan is a customer-facing digital tool designed to acquire new borrowers by providing instant, transparent loan quotes.

3. Legal & Regulatory Requirements (Crucial)

Truth in Lending (TILA/Reg Z): You cannot just show a "Monthly Payment." You must display the APR (Annual Percentage Rate), which includes origination fees.

4. Technical Requirements (The IT Project Specs)

A. Calculation Engine (The Code Logic)

The tool must calculate a Total Cost of Credit (TCC).
"""


CALCULATOR_CODE = '''"""
Loan Calculator v1.0 - Banking Hackathon Edition
"""

def calculate_monthly_payment(loan_amount, loan_duration_months, annual_interest_rate):
    if loan_amount <= 0:
        raise ValueError("loan_amount must be greater than 0")
    if loan_duration_months <= 0:
        raise ValueError("loan_duration_months must be greater than 0")
    if annual_interest_rate <= 0:
        raise ValueError("annual_interest_rate must be greater than 0")

    monthly_rate = annual_interest_rate / 12 / 100
    numerator = monthly_rate * (1 + monthly_rate) ** loan_duration_months
    denominator = (1 + monthly_rate) ** loan_duration_months - 1
    monthly_payment = loan_amount * (numerator / denominator)
    return monthly_payment
'''


CALCULATOR_JIRA = """JIRA-104: Handle Division by Zero for 0% Interest Rate Loans
Status: To Do
Priority: High

Description:
The calculator should support 0% promotional loans. The current logic raises a ValueError for annual_interest_rate <= 0.

Acceptance Criteria:
- Remove the ValueError restriction for an interest rate of exactly 0
- Ensure total_interest returns 0.00 for 0% loans
"""


STAKEHOLDER_UPDATE = """Subject: Update: Support for 0% Interest Loans now live

We have updated the Loan Calculator to support 0% interest promotional rates.
"""


PERSONA_CONFLICTS = """Product Manager: Wants a one-click experience.
Compliance: Wants legal accuracy and more disclosure.
Marketing: Wants a simple, engaging loan story.
Risk Analyst: Wants profitability-protecting rate logic.
UX Researcher: Wants low-friction inputs.
"""


SCENARIOS = {
    "calculator_0_apr": ScenarioBundle(
        scenario_id="calculator_0_apr",
        title="FlexiLoan 0% APR discrepancy",
        business_requirement=CALCULATOR_REQUIREMENTS,
        technical_context=CALCULATOR_CODE,
        repo_files={
            "READMEcalc.md": """# Loan Calculator - AI Hackathon

Version 1.0. A simple loan calculator from a banking environment.
Run with `python calculator.py`.
""",
            "mockup_calc_doc.md": """# Technical Documentation: Loan Calculator v1.0

The calculator is a Python CLI application that calculates monthly installments,
total repayment, and total interest using standard amortization logic.

Core function:
`calculate_monthly_payment(loan_amount, loan_duration_months, annual_interest_rate)`

Validation:
- loan_amount > 0
- loan_duration_months > 0
- annual_interest_rate > 0

CLI menu:
- [1] Calculate monthly payment
- [2] Calculate loan term (not yet implemented)
- [q] Quit
""",
            "calculator.py": CALCULATOR_CODE,
            "test_calculator.py": '''"""Unit tests for the loan calculator."""

def test_standard_loan():
    result = calculate_monthly_payment(25000, 60, 5.0)
    assert result["monthly_payment"] == 471.78

def test_small_loan():
    result = calculate_monthly_payment(1000, 12, 3.0)
    assert result["monthly_payment"] == 84.69

def test_large_loan():
    result = calculate_monthly_payment(500000, 360, 4.0)
    assert result["monthly_payment"] == 2387.08

def test_negative_rate_raises():
    with pytest.raises(ValueError):
        calculate_monthly_payment(10000, 60, -5.0)
''',
        },
        jira_ticket=CALCULATOR_JIRA,
        jira_ticket_key="JIRA-104",
        stakeholder_update=STAKEHOLDER_UPDATE,
        persona_conflicts=PERSONA_CONFLICTS,
    )
}


def get_scenario_bundle(scenario_id: str) -> ScenarioBundle:
    return SCENARIOS[scenario_id]
