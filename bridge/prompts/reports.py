from __future__ import annotations

REPORT_GENERATION_PROMPT = """\
Generate a {report_type} for the current project state.

The report is being prepared for a **{role_display_name}**.

Project context:
{assembled_context}

Alignment analysis:
{alignment_json}

Recent conversation history:
{conversation_history}

Adapt the report language and focus to the recipient's role:
- For Business Analysts: focus on business impact, customer risk, action items, and \
plain-language explanations. Avoid code snippets or function names.
- For Developers: focus on technical gaps, specific code changes needed, test coverage, \
file paths, and function signatures.

Structure the report with these sections (keep the entire report under 400 words):
1. **Executive Summary** — 2 sentences max
2. **Key Findings** — 3-5 bullet points, one line each
3. **Top Discrepancies** — top 3 only, one sentence each with severity
4. **Recommended Actions** — 3 prioritized next steps, one line each
5. **Jira Status** — one-line summary of open tickets

Be direct and professional. No filler. No repetition."""
