# FI.collab Demo Script — Loan Term Calculation Workflow

## Setup

1. Delete `project_state.json` before demo (fresh state)
2. Start app: `.fls/bin/streamlit run FI.collab.py`
3. Wait for "Loading chat module" spinner to finish

---

## Act 1 — Product Manager identifies the gap

**Sign in as:** Daniel Schneider (Product Manager)

### Question 1: Check current capabilities
> Does our calculator support loan term calculation? Can customers find out how long they need to repay a loan?

*Expected: System identifies feature is "not yet implemented", frames as competitive risk and conversion blocker.*

### Question 2: Check what exists
> What features does the calculator currently support?

*Expected: V1.0 monthly payment calculation, menu option [2] reserved but not implemented.*

### Question 3: Create a ticket
> Create a ticket for Anna Fischer to implement the loan term calculation feature. This is high priority — competitors already offer this.

*Expected: JIRA ticket created with proper title, assigned to Anna Fischer, appears in sidebar.*

---

## Act 2 — Compliance Officer reviews

**Switch to:** Claudia Becker (Compliance Officer)

### Question 4: Check compliance
> Are there any compliance concerns with the current calculator?

*Expected: TILA/Reg Z APR disclosure gap, GDPR consent gap, stakeholder email contradicts reality.*

### Question 5: Review the new feature request
> I see there's a new ticket for loan term calculation. Are there any regulatory considerations?

*Expected: Notes that APR disclosure, accuracy requirements, and input validation apply to the new feature too.*

---

## Act 3 — Developer implements

**Switch to:** Anna Fischer (Developer)

### Question 6: Check assigned tickets
> Are there any tickets assigned to me?

*Expected: Shows the loan term calculation ticket created by Daniel.*

### Question 7: Get implementation plan
> How should I implement the loan term calculation? What code changes are needed in calculator.py?

*Expected: Complete code with calculate_loan_term function, inverse amortization formula, 0% handling, CLI integration.*

### Question 8: Generate test cases
> Generate test cases for the loan term calculation feature.

*Expected: Runnable pytest code covering standard loans, 0% interest, edge cases, validation errors.*

### Question 9: Check for related issues
> Are there any other open issues I should be aware of before implementing this?

*Expected: References JIRA-104 (0% APR bug) — the loan term feature needs 0% handling too, so both issues are related.*

---

## Act 4 — Marketing Manager checks launch readiness

**Switch to:** Julia Weber (Marketing Manager)

### Question 10: Campaign readiness
> Is the loan term calculation feature ready? Can we start promoting it to customers?

*Expected: Marketing-language response about feature status, campaign implications, and any blockers.*

### Question 11: Customer messaging
> How should we communicate the new loan term feature to our customers?

*Expected: Customer-focused messaging suggestions, brand-appropriate language, campaign angle.*

---

## Act 5 — Business Analyst closes the loop

**Switch to:** Tobias Klein (Business Analyst)

### Question 12: Validate and close
> The loan term calculation has been implemented and tested. Please mark JIRA-104 as done.

*Expected: JIRA-104 updated to Done. Sidebar reflects the new status. The full lifecycle is complete — from requirement to implementation to closure, across 5 different stakeholder perspectives.*

---

## Key Demo Moments

| Moment | What it shows |
|---|---|
| PM asks, gets business language | Role-aware responses |
| Ticket created with assignee | Jira automation from natural language |
| Dev gets code with formula | Technical translation from requirements |
| Test cases generated | Automatic test generation (challenge slide 2) |
| Compliance flags regulations | Multi-stakeholder awareness |
| Same question, different answers | Persona-adaptive communication |
| Marketing closes the ticket | Full lifecycle: requirement → implementation → closure |
| Voice input/output (optional) | "Spoken responses" toggle for wow factor |

---

## Optional Voice Demo

At any point, toggle **Spoken responses** in the sidebar and use the **mic button** to ask a question by voice. Each persona has a unique voice. Best for a short, punchy question like:

> (as Daniel) Are there any urgent tickets for me?

The system will respond with Daniel's voice (Liam) and typewriter the text.
