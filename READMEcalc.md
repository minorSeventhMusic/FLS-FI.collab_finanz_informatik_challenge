# 🏦 Loan Calculator – AI Hackathon

**Version 1.0** – A simple loan calculator from a banking environment.

## What It Does (v1.0)

The user enters a **loan amount**, **duration**, and **interest rate** → the system calculates the **monthly payment**.

```
python calculator.py
```

## Runtime Error Handling

If invalid input triggers an error:
- The error is logged in error_log.json.
- The calculator triggers mockup_agent.py automatically in one-shot mode.
- The agent creates:
	- jira_ticket_YYYY-MM-DD-HHMM.md
	- fix_summary_YYYY-MM-DD-HHMM.md

If Google ADK or API keys are not available, the script uses a local fallback path.

## Local Development Commands

Run calculator:

```bash
/workspaces/FLS-Bridge-Challenge/.venv/bin/python calculator.py
```

Run tests:

```bash
/workspaces/FLS-Bridge-Challenge/.venv/bin/python -m pytest -q
```

Run non-interactive agent smoke test:

```bash
/workspaces/FLS-Bridge-Challenge/.venv/bin/python mockup_agent.py --auto-error "annual_interest_rate must be greater than 0"
```

## Notes

- On calculator exit, generated Jira/Fix markdown files are cleaned up automatically.
- error_log.json is reset to an empty list on calculator exit.
- APP_TIMEZONE controls timestamp generation (default: Europe/Berlin).
