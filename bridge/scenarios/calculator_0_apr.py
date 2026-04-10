from __future__ import annotations

from bridge.models import JiraTicketData, ScenarioBundle


# === Repository Files (from origin/mockup_tech) ===

CALCULATOR_PY = '''\
"""
Loan Calculator v1.0 – Banking Hackathon Edition

Currently supports:
  - Monthly payment calculation

"""

import math


# ── Core Calculation ─────────────────────────────────────────────────────────


def calculate_monthly_payment(loan_amount, loan_duration_months, annual_interest_rate):
    """Calculate the monthly payment for a loan.

    Formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]

    Args:
        loan_amount:          Total loan amount in € (must be > 0)
        loan_duration_months: Loan duration in months (must be > 0, integer)
        annual_interest_rate: Annual interest rate in % (must be > 0)

    Returns:
        dict with monthly_payment, total_payment, total_interest
    """
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

    total_payment = monthly_payment * loan_duration_months
    total_interest = total_payment - loan_amount

    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
    }


# ── CLI ──────────────────────────────────────────────────────────────────────


def main():
    print("\\n\\U0001f3e6 LOAN CALCULATOR v1.0\\n")

    while True:
        print("  [1] Calculate monthly payment")
        print("  [2] Calculate loan term (not yet implemented)")
        print("  [q] Quit\\n")

        choice = input("Choice: ").strip().lower()

        if choice == "1":
            try:
                amount = float(input("  Loan amount (€): "))
                months = int(input("  Duration (months): "))
                rate = float(input("  Annual interest rate (%): "))

                result = calculate_monthly_payment(amount, months, rate)

                print(f"\\n  Monthly payment: € {result[\'monthly_payment\']:,.2f}")
                print(f"  Total payment:   € {result[\'total_payment\']:,.2f}")
                print(f"  Total interest:  € {result[\'total_interest\']:,.2f}\\n")

            except (ValueError, TypeError) as e:
                print(f"\\n  ⚠ Error: {e}\\n")

        elif choice == "2":
            print("\\n  ⚠ Not yet implemented. See BUSINESS_REQUIREMENT.md\\n")

        elif choice == "q":
            print("Goodbye! \\U0001f44b\\n")
            break

        else:
            print("\\n  ⚠ Invalid choice.\\n")


if __name__ == "__main__":
    main()
'''

TEST_CALCULATOR_PY = '''\
"""Unit tests for the loan calculator."""

import pytest
from calculator import calculate_monthly_payment


# ── Correct calculations ─────────────────────────────────────────────────────

def test_standard_loan():
    result = calculate_monthly_payment(25000, 60, 5.0)
    assert result["monthly_payment"] == 471.78

def test_small_loan():
    result = calculate_monthly_payment(1000, 12, 3.0)
    assert result["monthly_payment"] == 84.69

def test_large_loan():
    result = calculate_monthly_payment(500000, 360, 4.0)
    assert result["monthly_payment"] == 2387.08

def test_total_interest_is_positive():
    result = calculate_monthly_payment(10000, 24, 5.0)
    assert result["total_interest"] > 0

def test_total_payment_exceeds_loan():
    result = calculate_monthly_payment(10000, 24, 5.0)
    assert result["total_payment"] > 10000


# ── Input validation ─────────────────────────────────────────────────────────

def test_negative_amount_raises():
    with pytest.raises(ValueError):
        calculate_monthly_payment(-10000, 60, 5.0)

def test_zero_duration_raises():
    with pytest.raises(ValueError):
        calculate_monthly_payment(10000, 0, 5.0)

def test_negative_rate_raises():
    with pytest.raises(ValueError):
        calculate_monthly_payment(10000, 60, -5.0)
'''

README_CALC_MD = """\
# Loan Calculator – AI Hackathon

**Version 1.0** – A simple loan calculator from a banking environment.

## What It Does (v1.0)

The user enters a **loan amount**, **duration**, and **interest rate** → the system calculates the **monthly payment**.

```
python calculator.py
```
"""

MOCKUP_CALC_DOC_MD = """\
# Technical Documentation: Loan Calculator v1.0

## 1. System Overview
The **Loan Calculator** is a Python-based command-line interface (CLI) application designed to \
facilitate basic banking calculations. It specifically allows users to calculate monthly loan \
installments, total repayment amounts, and total interest paid over the life of a loan using \
standard amortization logic.

## 2. Mathematical Model
The application utilizes the standard formula for calculating a fixed-rate monthly payment:

M = P * r(1+r)^n / ((1+r)^n - 1)

### Variable Definitions:
* **M**: Monthly payment
* **P**: Principal loan amount
* **r**: Monthly interest rate (Annual Rate / 12 / 100)
* **n**: Total number of payments (loan duration in months)

## 3. Component Analysis

### 3.1. Core Logic: `calculate_monthly_payment`
This function serves as the calculation engine. It takes three numerical inputs and returns a \
structured dictionary of results.

**Function Signature:**
`calculate_monthly_payment(loan_amount, loan_duration_months, annual_interest_rate)`

**Input Validation:**
The function performs strict validation to ensure financial integrity:
* `loan_amount` must be > 0.
* `loan_duration_months` must be > 0.
* `annual_interest_rate` must be > 0.

**Return Object:**
A dictionary containing:
* `monthly_payment`: The amount due each month.
* `total_payment`: The sum of all payments over the term.
* `total_interest`: The cost of borrowing (Total - Principal).

### 3.2. User Interface: `main()`
The `main()` function implements a loop-based CLI menu.

* **Execution Flow:** The program displays a menu and waits for user input.
* **Choice [1]:** Prompts for loan details, executes the calculation, and prints a formatted summary.
* **Choice [2]:** Reserved for future functionality (Loan Term calculation).
* **Choice [q]:** Terminates the program execution.
* **Error Handling:** Uses a `try-except` block to catch `ValueError` or `TypeError`, ensuring \
that invalid user inputs do not crash the script.

## 4. Execution Example
**Inputs:**
- Loan Amount: €10,000
- Duration: 12 months
- Interest Rate: 5%

**Output:**
Monthly payment: € 856.07
Total payment:   € 10,272.84
Total interest:  € 272.84
"""


# === Jira Ticket (from origin/mockup_tech) ===

MOCKUP_JIRA_MD = """\
### JIRA-104: Handle Division by Zero for 0% Interest Rate Loans

**Status:** To Do
**Priority:** High
**Component:** Core Logic / `calculator.py`
**Reporter:** Gemini (AI Collaborator)

#### Description
Currently, the `calculate_monthly_payment` function requires the `annual_interest_rate` to be \
greater than 0. If a user attempts to input a 0% interest rate (e.g., for a promotional \
"Interest-Free" banking product), the current mathematical formula will result in a \
**division by zero error** because the denominator (1+r)^n - 1 becomes zero.

The application needs to be updated to handle 0% interest scenarios using a simple linear \
division (Principal / Months) instead of the amortization formula.

#### Current Constraints
* Function currently raises a `ValueError` if `annual_interest_rate <= 0`.
* Documentation explicitly identifies "Division by Zero" as a known technical constraint.

#### Proposed Implementation
Modify the logic in `calculate_monthly_payment` to include a conditional check:
1. **If interest rate > 0:** Use the existing amortization formula.
2. **If interest rate == 0:** Calculate `monthly_payment = loan_amount / loan_duration_months`.

#### Acceptance Criteria
* [ ] Remove the `ValueError` restriction for an interest rate of exactly 0.
* [ ] Ensure `total_interest` returns `0.00` for 0% loans.
* [ ] Verify the CLI correctly displays results for a €10,000 loan over 10 months at 0% (Result: €1,000/mo).
* [ ] Update the **Technical Constraints** section in `documentation.md` to reflect that 0% interest is now supported.
"""


# === Stakeholder Communication — THE LIE (from origin/mockup_tech) ===

STAKEHOLDER_EMAIL = """\
Subject: **Update: Support for 0% Interest Loans now live**

Dear [Client Name],

We have updated the Loan Calculator to support **0% interest promotional rates**.

**Key Changes:**
* **0% Support:** The system now calculates "Interest-Free" loans without errors.
* **Simple Logic:** For 0% rates, the calculator simply divides the total amount by the \
duration (e.g., €1,200 over 12 months = €100/month).
* **Clearer Data:** Reports exactly **€0.00** for total interest, ensuring your marketing \
is transparent and compliant.
* **Safety:** The tool remains protected against invalid data (like negative numbers).

The system is now fully ready for your 0% APR marketing campaigns.

Best regards,

[Your Name]
Product Owner
"""


# === Business Requirements (from origin/business) ===

BUSINESS_REQUIREMENTS = """\
Project Documentation: "FlexiLoan" Retail Engine

1. Executive Summary
FlexiLoan is a customer-facing digital tool designed to acquire new borrowers by providing \
instant, transparent loan quotes. It serves as the primary "Top-of-Funnel" lead generation \
asset for the bank's personal lending division.

2. Market Trends & Challenges
Trend: "Price to Beat" Logic. Customers in 2026 use aggregators. The calculator must show \
"Competitive Comparison" metrics to prevent site abandonment.
Challenge: Rate Volatility. Central bank rates are fluctuating. The code must fetch the \
latest LPR (Loan Prime Rate) via API every 24 hours to ensure quotes are legally accurate.

3. Legal & Regulatory Requirements (Crucial)
Truth in Lending (TILA/Reg Z): You cannot just show a "Monthly Payment." You must display \
the APR (Annual Percentage Rate), which includes origination fees.
GDPR/CCPA: If the user enters a phone number to "Save Quote," the system must capture an \
explicit, time-stamped consent log.
Fair Lending Act: The algorithm must be "blind" to protected classes (Age, Gender, Race) to \
avoid biased pricing.

4. Technical Requirements (The IT Project Specs)
A. Calculation Engine (The Code Logic)
The tool must calculate a Total Cost of Credit (TCC).

B. API & Integration
Credit Bureau Soft-Pull: Integration with a credit API (e.g., Experian) to provide a \
"Personalized Rate" without impacting the user's credit score.
CRM Sync: Successful "Quotes" must push data to Salesforce for follow-up by the lending team.

5. Human Statistics (Target Market Profile)
Segment: The Debt Consolidator (35-50, married), The Modern Starter (22-30, single), \
The Home Improver (40-60, homeowners).

6. UI/UX Design Requirements
"Visual Anchor": A large, dynamic donut chart showing the split between Principal Paid and \
Interest Paid.
Trust Signals: Badges from "Norton Secured" or "FCA Regulated" must be visible near the \
"Calculate" button.
Mobile Responsiveness: 70% of traffic is expected from mobile devices.

7. Success Metrics (KPIs)
Conversion Rate: % of users who click "Apply Now" after calculating.
Drop-off Point: At which field do users leave the page?
Calculation Accuracy: 0% variance between the calculator estimate and the final loan contract.

8. Feature Roadmap — Version 2.0 Requirements
The calculator must be extended with a Loan Term Calculation feature:
- V1.0 (current): Input (Loan Amount, Interest Rate, Loan Duration) → Output (Monthly Payment)
- V2.0 (required): Input (Loan Amount, Interest Rate, Monthly Payment) → Output (Loan Duration)

The V2.0 feature allows customers to answer: "If I can afford €X per month, how long will it \
take to pay off my loan?" This is a critical conversion feature — competitors already offer it.

Implementation should use the inverse amortization formula:
n = -log(1 - (P * r) / M) / log(1 + r)
where P = loan amount, M = monthly payment, r = monthly interest rate.

The V2.0 feature must also handle 0% interest (simple division: loan_amount / monthly_payment).
The CLI menu option [2] is already reserved for this feature ("Calculate loan term - not yet implemented").

Acceptance Criteria:
- User can select option [2] in the CLI to calculate loan term
- Given loan amount, interest rate, and monthly payment, returns duration in months
- Handles 0% interest correctly (simple division)
- Validates that monthly payment exceeds minimum interest-only payment
- Unit tests cover standard, edge, and 0% cases
- Technical documentation updated
"""


# === Persona Conflicts (from origin/business) ===

PERSONA_CONFLICTS = """\
| Persona | Priority | Conflict Source |
| :--- | :--- | :--- |
| **Product Manager** | Conversion | Wants a "one-click" experience; Compliance wants 5 pages of legal text. |
| **Compliance** | Accuracy | Wants the most complex math; Marketing wants it to look "simple." |
| **Marketing** | Engagement | Wants to capture user data; UX wants to keep it anonymous for trust. |
| **Risk Analyst** | Profitability | Wants high rates; Product Manager wants low rates to beat the market. |
| **UX Researcher** | Simplicity | Wants no sliders; Tech needs inputs for the calculation to work. |
"""


# === Persona Detail Files (from origin/business personas/) ===

PERSONA_BUSINESS_ANALYST = """\
Name: Tobias Klein | Age: 37 | Location: Frankfurt am Main
Role: Senior Business Analyst – Digital Banking Transformation

Background: Degree in Business Information Systems. 12 years in banking and financial IT.
Responsibilities: Translates business requirements into technical specifications. Works between \
business stakeholders and development teams. Defines user stories and functional requirements.
Goals: Align IT solutions with business objectives. Improve efficiency of banking processes. \
Enable successful delivery of digital transformation projects.
Pain Points: Misalignment between technical and business teams. Constantly changing stakeholder \
requirements. Complex banking processes and legacy systems.
Tools: Jira/Confluence, BPMN modeling tools, Excel/data analysis, requirement management systems.
Mindset: "The best IT solutions come from understanding both technology and business."
"""

PERSONA_SOFTWARE_DEVELOPER = """\
Name: Anna Fischer | Age: 32 | Location: Berlin
Role: Senior Software Developer – Digital Banking Platform

Background: MSc in Computer Science. 8 years in backend development. Fintech startup experience.
Responsibilities: Develops and maintains backend services for mobile and online banking. \
Implements APIs and integrates with core banking platforms. Ensures code quality and security.
Goals: Build reliable and scalable banking software. Reduce technical debt. Implement modern \
development practices (CI/CD, microservices).
Pain Points: Complex legacy banking infrastructure. Long release cycles due to compliance. \
Balancing technical quality with delivery deadlines.
Tools: Java/Kotlin/Spring Boot, Git/GitHub, Docker/Kubernetes, Jira/Confluence, CI/CD pipelines.
Mindset: "Clean architecture and automation make banking systems sustainable."
"""

PERSONA_PRODUCT_MANAGER = """\
Name: Daniel Schneider | Age: 41 | Location: Frankfurt am Main
Role: Senior Product Manager – Digital Banking Platform

Background: MBA in Digital Business. 12+ years in fintech and banking.
Responsibilities: Defines product strategy, prioritizes roadmap with engineering, aligns \
stakeholders across IT/compliance/business, oversees product lifecycle and KPIs.
Goals: Deliver secure and scalable digital banking services. Increase digital adoption. \
Reduce operational costs through automation.
Pain Points: Slow decision-making due to regulatory reviews. Legacy core banking systems. \
Conflicting stakeholder priorities.
Tools: Jira/Confluence, Figma, Productboard, Looker/Tableau.
Mindset: "If we don't innovate digitally, fintechs will take our customers."
"""

PERSONA_COMPLIANCE_OFFICER = """\
Name: Claudia Becker | Age: 46 | Location: Berlin
Role: IT Compliance Manager

Background: Law degree with specialization in financial regulation. 15 years in banking compliance. \
Deep knowledge of BaFin regulations, GDPR, PSD2.
Responsibilities: Ensures IT systems comply with banking regulations. Reviews new digital products \
for regulatory risk. Works with legal, security, and risk teams. Conducts internal audits.
Goals: Avoid regulatory penalties. Maintain strong regulatory reputation. Ensure transparent \
compliance processes.
Pain Points: Fast-moving tech teams deploying features quickly. Translating regulations into \
technical requirements. Pressure from management to accelerate innovation.
Tools: GRC platforms, documentation systems, audit tracking tools.
Mindset: "Innovation is good, but regulation always comes first."
"""

PERSONA_MARKETING_MANAGER = """\
Name: Julia Weber | Age: 34 | Location: Hamburg
Role: Digital Marketing Manager – Banking Products

Background: Degree in Marketing & Communications. 9 years in digital marketing. Experienced \
in fintech and financial services campaigns.
Responsibilities: Launch marketing campaigns for digital banking products. Manage customer \
acquisition channels. Analyze campaign performance and user behavior.
Goals: Increase app adoption and digital engagement. Improve customer acquisition cost. \
Strengthen the bank's modern brand image.
Pain Points: Strict financial advertising regulations. Limited customer data due to privacy \
restrictions. Slow campaign approvals.
Tools: Google Analytics/Adobe Analytics, Salesforce CRM, marketing automation, A/B testing.
Mindset: "Banks must market themselves like tech companies."
"""

PERSONA_RISK_ANALYST = """\
Name: Mehmet Yilmaz | Age: 38 | Location: Frankfurt am Main
Role: IT Risk Analyst – Digital Systems

Background: MSc in Finance and Risk Management. 11 years in banking risk analysis. Strong \
experience in cybersecurity and operational risk.
Responsibilities: Identify IT and operational risks in digital banking systems. Conduct risk \
assessments for new technologies. Monitor fraud and system vulnerabilities.
Goals: Prevent financial and operational losses. Ensure stable banking infrastructure. \
Strengthen cybersecurity posture.
Pain Points: Increasing cyber threats. Complexity of integrated banking systems. Balancing \
innovation with risk control.
Tools: Risk assessment platforms, security monitoring systems, data analysis tools.
Mindset: "Every new feature introduces a new risk."
"""

PERSONA_UX_DESIGNER = """\
Name: Lukas Hoffmann | Age: 29 | Location: Berlin
Role: Senior UX Designer – Mobile Banking

Background: Degree in Human-Computer Interaction. 6 years in UX design. Previously worked \
at a fintech startup.
Responsibilities: Design intuitive digital banking interfaces. Conduct usability testing. \
Work with product managers and developers. Ensure accessibility.
Goals: Simplify complex financial tasks. Reduce friction in digital onboarding. Improve \
mobile banking usability.
Pain Points: Legacy design constraints. Security requirements affecting usability. Too many \
stakeholders reviewing designs.
Tools: Figma, Miro, user testing platforms, analytics tools.
Mindset: "Banking should feel as simple as sending a message."
"""


# === Sales Complaint (from origin/mockup_tech + origin/business) ===

SALES_COMPLAINT = """\
From: Sales & Marketing Team
To: Product Manager

Subject: Help! We can't set up our "Interest-Free" laptop deals

We are trying to launch our big "Back to School" sale. We want to tell customers: \
"Buy a €1,200 laptop today, pay €100 a month for a year, and pay zero fees."
It is not working!

Can you fix this?

[Customer Name]
"""


# === Scenario Bundle ===

JIRA_104 = JiraTicketData(
    key="JIRA-104",
    title="Handle Division by Zero for 0% Interest Rate Loans",
    status="To Do",
    priority="High",
    description=MOCKUP_JIRA_MD,
    assignee="Daniel Schneider",
    external_url="https://jira.example.com/browse/JIRA-104",
    history=["Created by AI Collaborator during initial review", "Assigned to Daniel Schneider (Product Manager)"],
)

CALCULATOR_0_APR_SCENARIO = ScenarioBundle(
    scenario_id="calculator_0_apr",
    title="FlexiLoan 0% APR Discrepancy",
    description=(
        "A loan calculator where the business requires 0% promotional loan support, "
        "but the code rejects 0% interest rates. A stakeholder email falsely claims "
        "the fix is already live."
    ),
    repo_files={
        "calculator.py": CALCULATOR_PY,
        "test_calculator.py": TEST_CALCULATOR_PY,
        "READMEcalc.md": README_CALC_MD,
        "mockup_calc_doc.md": MOCKUP_CALC_DOC_MD,
    },
    business_requirements=BUSINESS_REQUIREMENTS,
    technical_documentation=MOCKUP_CALC_DOC_MD,
    jira_tickets=[JIRA_104],
    stakeholder_comms=STAKEHOLDER_EMAIL,
    persona_conflicts=PERSONA_CONFLICTS,
    persona_details={
        "business_analyst": PERSONA_BUSINESS_ANALYST,
        "developer": PERSONA_SOFTWARE_DEVELOPER,
        "product_manager": PERSONA_PRODUCT_MANAGER,
        "compliance_officer": PERSONA_COMPLIANCE_OFFICER,
        "marketing_manager": PERSONA_MARKETING_MANAGER,
        "risk_analyst": PERSONA_RISK_ANALYST,
        "ux_designer": PERSONA_UX_DESIGNER,
    },
    additional_comms=[SALES_COMPLAINT],
    known_discrepancies=[
        "Stakeholder email says 0% APR is live but code rejects rate <= 0 and JIRA-104 is To Do",
        "Amortization formula divides by zero when rate is 0 but email claims it works",
        "Validation docs say rate must be > 0 but email says 0 is supported",
        "JIRA-104 status 'To Do' contradicts email subject 'now live'",
        "No tests exist for the 0% interest scenario",
        "Business requirements describe complex system (TCC, APIs, CRM) but code is basic CLI",
        "Persona conflicts (PM vs Compliance vs Marketing vs Risk vs UX) unresolved in technical scope",
        "JIRA acceptance criteria reference 'Technical Constraints' section that doesn't exist in docs",
        "Sales team complaint confirms real users are blocked by the 0% issue — not just theoretical",
        "V2.0 Loan Term Calculation is required by business but CLI menu option [2] says 'not yet implemented'",
    ],
)
