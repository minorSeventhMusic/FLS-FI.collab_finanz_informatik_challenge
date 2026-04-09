# Agent Documentation

## Purpose
This project combines a loan calculator with an error-handling agent.

- The calculator performs loan payment calculations.
- If calculation input is invalid, the calculator logs the error.
- After logging, it triggers the agent automatically.
- The agent generates a Jira-style analysis and a customer-facing update.

## Main Files
- calculator.py: CLI calculator, input validation, error logging, automatic agent trigger.
- mockup_agent.py: Agent logic for analysis and customer messaging.
- error_log.json: Runtime error log created by calculator.py.
- test_calculator.py: Unit tests for calculation and validation behavior.

## Runtime Flow
### 1) Calculator starts
Run:

```bash
python calculator.py
```

The calculator shows a menu and lets the user choose an action.

### 2) Normal calculation path
When values are valid:
- calculate_monthly_payment runs.
- Monthly payment, total payment, and total interest are printed.
- No agent call is made.

### 3) Error path (automatic)
When invalid input causes ValueError or TypeError:
- The calculator prints the error.
- The error is appended to error_log.json with timestamp and input snapshot.
- The calculator launches the agent automatically using a one-shot subprocess call:

```bash
python mockup_agent.py --auto-error "<latest error message>"
```

This is automatic and does not require manual interaction.

## Agent Behavior
The agent supports two modes:

### A) Auto one-shot mode
Triggered by calculator.py with --auto-error.

Steps:
- Receives the error text from CLI argument.
- Loads calculator.py source.
- Derives findings for the promo/0% issue pattern.
- Produces a Jira-style ticket text.
- Produces a short customer update.

If Google ADK and API key are available, agent-generated text is attempted.
If not available, local fallback text is used.

### B) Interactive mode
Run:

```bash
python mockup_agent.py
```

Menu options:
- calc: manual loan calculation test
- promo: fixed promo scenario (1200, 12, 0.0)
- customer: reprint last customer update
- q: quit

## Important Clarification
The current implementation does not continuously watch terminal output in parallel.

Instead, it is event-driven:
- Calculator detects an error.
- Calculator invokes agent once for that error.
- Agent exits.

## Dependencies
Optional ADK path in mockup_agent.py expects:
- google-adk
- google-genai

Optional environment variables:
- GEMINI_API_KEY or GOOGLE_API_KEY
- ADK_MODEL (default: gemini-2.0-flash)

Without these, the fallback local analysis still works.

## Logging and Artifacts
- error_log.json is generated during calculator error events.
- It is used to preserve error context and latest error message.
- Generated runtime artifacts are ignored by .gitignore.

## Testing
Run tests with:

```bash
python -m pytest -q
```

Current test scope validates calculation outputs and input validation behavior.
