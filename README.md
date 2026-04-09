# Hackathon Demos

This repository now includes two small demo projects:

## 1. Ticket Copilot Demo

A single-page Streamlit app for business-tech collaboration around support and product tickets.

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Run the Streamlit app

```bash
./.venv/bin/streamlit run app.py
```

### Quick checks

```bash
PYTHONPYCACHEPREFIX=.pycache ./.venv/bin/python -m py_compile app.py components/sidebar_sections.py services/agent_client.py services/mock_data.py utils/state.py tests/test_app_import.py
./.venv/bin/python -m pytest tests/test_app_import.py
```

## 2. Loan Calculator

The original command-line calculator is still available:

```bash
python calculator.py
```

To run its tests:

```bash
python -m pytest test_calculator.py
```
