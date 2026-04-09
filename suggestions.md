# The Bridge — Status, Suggestions & Roadmap

## Current App Status

**Codebase:** 34 Python files, ~3,166 lines | **Tests:** 47 passed, 1 skipped | **Branch:** `claude-dev`

### What's Built

| Module | Status | Description |
|---|---|---|
| LangGraph Workflow | Working | 6-node graph: intent classification, context assembly, concierge gate, response gen, alignment analysis, side effects |
| LLM Integration | Working | Gemini 2.5 Flash (primary), OpenAI GPT-5.4 (fallback), StubLLM (offline) |
| Alignment Engine | Working | Detects 8 discrepancies, catches stakeholder lie, qualitative + numeric scoring |
| Persona System | Working | BA (no raw code, business language) vs Developer (full code, technical detail) |
| Concierge Gate | Working | BA asking for raw code gets a translated handoff |
| Jira Adapter | Working | Seed tickets, create/update/search, JSON persistence |
| Cross-Session Memory | Working | Conversations persist by role, auto-loaded on role switch |
| Speech — TTS | Working | ElevenLabs with per-persona voices (Sarah for BA, George for Dev) |
| Speech — STT | Working | Gemini audio transcription via mic input |
| Chat Page | Working | Role selector, voice toggle, ticket list, alignment sidebar, chat |
| Dashboard | Working | Metrics, discrepancy cards, ticket list, handoff log, alignment history |
| Reports | Working | LLM-generated persona-adapted reports with download |

---

## Pros

1. **LLM-first architecture** — No hardcoded keyword matching for production; GPT/Gemini reasons dynamically over all context
2. **"Catch the lie" demo moment** — The stakeholder email contradiction is surfaced automatically across all 3 sources (email claims live, code rejects, Jira says To Do)
3. **Genuine persona differentiation** — Same question produces fundamentally different answers (not just tone), with visibility gating
4. **Voice conversation** — Speak to The Bridge, hear it respond with role-appropriate voice. Unique demo feature
5. **Robust offline mode** — StubLLM, StubTTS, StubSTT all work deterministically without any API keys
6. **Cross-session memory** — Judges can see "The Bridge remembers what was discussed" across restarts
7. **47 tests** — Unit + integration tests covering workflow, alignment, context, personas, persistence, jira, speech, and Streamlit pages
8. **Multi-provider LLM** — Gemini, OpenAI, or offline — switch with one env var
9. **Clean architecture** — Modules are loosely coupled, scenarios are pluggable, personas are extensible

---

## Cons / Known Issues

1. **JSON file persistence** — `project_state.json` has race conditions if multiple Streamlit sessions write simultaneously. Fine for demo, not production
2. **Prompt injection risk** — User messages flow directly into LLM prompts via `.format()`. A malicious user could inject instructions. Low risk for hackathon demo but needs sandboxing for production
3. **No real GitHub integration** — Repo files are bundled inline. The "repo-aware" claim is based on pre-loaded scenario data
4. **No real Jira integration** — All tickets are local JSON. Impressive for demo but would need API work
5. **Single scenario** — Only the calculator 0% APR scenario. Architecture supports more but none exist yet
6. **Python 3.9** — Works but triggers deprecation warnings from google-auth. Not a blocker
7. **Dashboard runs alignment on every page load** — Calls the LLM each time. Should cache results
8. **`unsafe_allow_html=True`** — Used for CSS styling. The HTML is all hardcoded (not user-sourced), so XSS risk is minimal, but worth noting

---

## Security Considerations

| Issue | Severity | Detail |
|---|---|---|
| Prompt injection | Medium | User messages are interpolated into LLM prompts. Could be exploited to override system instructions |
| JSON race conditions | Low | Multiple Streamlit sessions writing to `project_state.json` simultaneously could corrupt state |
| API keys in .env | OK | Keys are in `.env` which is in `.gitignore`. No keys in source code |
| unsafe_allow_html | Low | All HTML is hardcoded CSS/badges, not user-sourced. No XSS vector currently |
| Error handling | Low | API errors in LLM/TTS/STT are caught with fallbacks. Some edge cases in persistence may not be handled |

---

## UI Improvement Suggestions (from design review)

### Color Palette — Professional Banking Theme

- **Primary:** `#1a3a52` (Deep Banking Blue) — trust, stability
- **Secondary:** `#00a86b` (Emerald Green) — alignment/success
- **Accent:** `#f39c12` (Golden Orange) — alerts, warnings
- **Critical:** `#dc3545` (Red) — critical discrepancies
- **Neutral:** `#f8f9fa` (Light Grey) — backgrounds
- **Borders:** `#e0e0e0` — clean separation

### Chat Page

- Add a dark context bar above chat showing active ticket/scenario
- Style user messages with blue left border, assistant with green
- Better chat input focus states
- Voice controls integrated cleanly below chat

### Dashboard

- Replace flat metrics with gradient card design with hover effects
- Add severity pill summary (Critical: 2, High: 2, Medium: 2, Low: 2) above discrepancy list
- Convert discrepancy table to card view with expanders for full details
- Color-coded progress bar gradient (primary to secondary)

### Reports Page

- Wrap generated report in a document-style container (white bg, borders, header)
- Add report meta info (recipient role, generation date)
- Professional download button layout

### Sidebar

- Enhanced typography: uppercase section headers with letter-spacing
- Better alignment score display: large number + color-coded border + label
- Improved ticket card styling with gradient backgrounds
- Cleaner dividers

### General Polish

- Gradient primary buttons (`linear-gradient(135deg, #1a3a52, #00a86b)`)
- Hover effects on metric cards (`box-shadow` on hover)
- Better font hierarchy (800 weight headers, 600 subheaders)
- Progress bar gradient styling
- Rounded badge styling with inline-block display

---

## Pre-Demo Checklist

- [ ] Apply CSS improvements from design review
- [ ] Cache alignment results on Dashboard (use `st.session_state`)
- [ ] Delete `project_state.json` before demo — start with fresh state
- [ ] Test voice mode with both roles — confirm different voices play
- [ ] Prepare 3-4 good demo questions for each role
- [ ] Enable LangSmith tracing (set `LANGSMITH_TRACING=true`) to show reasoning chain
- [ ] Have backup: if API fails, StubLLM still works

---

## Future Extensions

| Extension | Effort | Impact | Description |
|---|---|---|---|
| More scenarios | Medium | High | Add 2-3 scenario bundles (API rate limiting, compliance gap) — shows The Bridge is general-purpose |
| Real GitHub API | Medium | High | Replace inline bundles with `git show` or GitHub REST API — "connects to your actual repo" |
| Real Jira API | Medium | High | Replace JSON adapter with Jira Cloud REST API — live ticket creation in demo |
| Persona.md files | Small | Medium | Load role definitions from markdown files — "add a new stakeholder role in 30 seconds" |
| Semantic drift detection | Large | Very High | Monitor git commits, flag when code changes contradict requirements — the killer feature from project draft |
| Streaming responses | Small | Medium | Stream LLM output token-by-token into chat — feels more responsive |
| PDF report export | Small | Medium | Generate downloadable PDF instead of markdown — professional touch |
| LangSmith dashboard | Tiny | High | One env var enables full reasoning chain visibility — judges love "under the hood" |
| Multi-user sessions | Large | Medium | Database persistence + auth instead of JSON — needed for production |
| Confluence/Notion sync | Medium | Medium | Pull business requirements from real doc platforms — extends "source of truth" beyond code |
| Slack/Teams integration | Medium | High | Bridge notifications in team channels when discrepancies are detected |
| Automated PR review | Large | Very High | Hook into GitHub PRs, auto-comment when a PR conflicts with business requirements |

### Most Impactful Next Steps

1. **Apply the CSS improvements** — transforms visual impression from "prototype" to "product"
2. **Add one more scenario** — proves The Bridge is a platform, not a one-trick demo
3. **Enable LangSmith** — free tracing that shows the full reasoning chain live
