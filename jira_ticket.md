# Jira Tickets

Auto-generated tickets from calculator runtime errors.

## Ticket Entry

- Generated at: 2026-04-09 18:51:51
- Source error: loan_amount must be greater than 0

### Jira Ticket

```text
JIRA Title: Promo 0% interest flow fails in monthly payment calculator
Priority: High
Component: Core Calculation

Summary:
Promo mode intentionally calls calculate_monthly_payment with 0% interest, but the calculator rejects that input and raises a ValueError.

Observed Error:
- loan_amount must be greater than 0

Code Analysis Findings:
- Input validation rejects annual_interest_rate == 0
- Raised error message is 'annual_interest_rate must be greater than 0'
- Amortization denominator becomes zero at 0% if guard is removed
- Issue located in calculate_monthly_payment in calculator.py

Proposed Fix:
- Update calculate_monthly_payment to support annual_interest_rate == 0 using simple division
- Keep annual_interest_rate < 0 as invalid input
- Add tests for 0% promotional cases

Acceptance Criteria:
- Promo path no longer raises an exception for 0%
- 0% loans return total_interest = 0.00
- Existing non-zero interest tests remain passing
```
