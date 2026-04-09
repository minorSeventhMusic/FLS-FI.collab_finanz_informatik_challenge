# FLS-Bridge-Challenge

Minimal MVP scaffold for "The Bridge", a role-aware orchestration demo for business and technical collaboration.

## What Is Included

- LangGraph workflow with role-aware routing
- Mock Jira and code-context adapters
- Local JSON persistence for handoffs and ticket history
- Seeded calculator/Jira demo scenario derived from the remote draft branches
- Streamlit UI for interactive demo runs

## Run

Use the existing virtual environment:

```bash
.fls/bin/python -m unittest discover -s tests
.fls/bin/streamlit run streamlit_app.py
```

The app persists runtime state in `project_state.json`.
