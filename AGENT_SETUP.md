# Error Analysis Agent Setup

## Overview

The `error_analysis_agent.py` is an AI-powered agent that:
1. Captures errors from `calculator.py` by running test cases
2. Uses Google Gemini API (with your API key from `.env`) to analyze the errors
3. Generates a comprehensive markdown report with insights and recommendations

## Prerequisites

- Python 3.8+
- Google API Key in `.env` file (already present)

## Installation

```bash
pip install google-generativeai
```

## Usage

Run the agent from your workspace directory:

```bash
python error_analysis_agent.py
```

This will:
- Load your Google API key from `.env`
- Test calculator.py with various inputs
- Capture any validation errors
- Send error details to Google Gemini for AI analysis
- Generate `error_analysis_report.md` with detailed findings

## Output

The agent creates `error_analysis_report.md` containing:
- Summary of errors found
- Detailed error information
- AI-powered analysis from Google Gemini
- Root cause analysis
- Recommended fixes
- Best practices

## Files

- `error_analysis_agent.py` - Main agent script
- `error_analysis_report.md` - Generated report (created after running)
