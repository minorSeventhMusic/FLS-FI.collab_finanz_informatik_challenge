# The Bridge — Project Overview

## What We're Building

**The Bridge** is an AI-powered orchestration layer designed to synchronize technical development with business requirements and vice versa. It acts as an **intelligent router** (Head-Agent) that distributes requests to different Agents (roles) according to the needs and has access to the codebase (GitHub), jira tickets, documentation and previous discussions/requests.

The system facilitates natural language conversations tailored to the specific role of the user. It doesn't just provide information; it actively manages the project lifecycle by **accessing and creating Jira tasks and tickets** directly through the chat interface.

A typical session might look like this:
User (Role: Business Analyst) connects to UI
→ User sends: "Why is the interest calculation logic not matching our latest spec?"
→ Agent: Identifies role (BA) and intent (Discrepancy Check).
→ Agent: Compares GitHub code vs. Confluence documentation.
← AI Node: "The implementation uses a 360-day year instead of 365.
Would you like me to create a Jira ticket for the dev team?"
→ User sends: "Yes, prioritize it as High."
← AI Node: "Ticket LOAN-402 created: 'Fix Interest Day-Count Convention'.
Assigned to Lead Developer."

---

## Core Challenges

### 1. Role-Aware Natural Language Processing
The agent must adjust its vocabulary, depth of detail, and tone based on whether it is talking to a Business Analyst or a Developer. It must ensure technical complexity is translated into business value without losing precision and the other way around. 

### 2. Autonomous Jira Management
Integrating the ability to not only read but also **create and update Jira tickets** requires strict logic to ensure the AI has sufficient context before modifying the project backlog.

### 3. The "Concierge" Boundary Protocol
In a corporate environment, not all users should see raw code or sensitive strategy. The system enforces "Soft Barriers"—acknowledging a request but routing it to a human owner for approval or providing a summarized "Translation View" instead of raw data.

### 4. Real-time Semantic Drift Detection
Identifying when a developer’s commit fundamentally changes a business rule. This requires the AI to monitor "Significance" (e.g., a change in a rounding formula) rather than just checking if the code compiles.

---

## Workload Breakdown

| Area | What it covers | Effort |
|------|---------------|--------|
| **Head-Agent Logic** | LangGraph routing, intent detection, role-switching | Medium |
| **Business Node** | Technical-to-Plain-English translation, BA-specific prompting | Medium |
| **Tech Node** | Code analysis, unit test suggestions, architectural impact | Medium |
| **Jira Integration** | API connectivity for reading, creating, and updating tickets | Large |
| **Concierge Protocol** | Boundary detection and handoff request logging | Medium |
| **UI Development** | Streamlit dashboard, role toggles, Jira status visualizations | Small |
| **Alignment Engine** | LLM-based semantic scoring and "Drift" alerts | Large |

---

## Key Decisions

1. **Active Task Management** — The AI is a participant in the workflow, capable of generating Jira tasks to bridge gaps found between code and requirements.
2. **Mock SSO** — Using a sidebar toggle in Streamlit to simulate identity for the hackathon demo.
3. **State Persistence** — Using a local `project_state.json` to store "Handoffs" and pending Jira actions.
4. **Hero Feature** — Focusing on the "Automated Jira Creation" and the "Significance Warning" during the pitch.

---

## Technical Constraints

- **Language:** Python 3.10+
- **Orchestration:** LangGraph (for multi-agent cycles)
- **Frontend:** Streamlit (for rapid prototyping)
- **Primary Model:** ChatGPT 5.4
- **Architecture:** Event-driven agentic workflow
- **Integration:** GitHub (Source Code) and Jira (Task Management)

---

## Required Features

### Authentication & Roles
- **Mock SSO Toggle:** Seamlessly switch between "Business Analyst" and "Developer."
- **Context Awareness:** The AI maintains role-specific memory across the session.

### The Bridge Mechanics
- **Semantic Progress Bar:** Visualizes how much of a Jira requirement is reflected in the actual code.
- **Jira Automation:** Native ability to create, assign, and query project tickets via chat.
- **Alerts:** Visual warnings when things diverge from the agreed upon goals. 

### Messaging & Insights
- **Natural Language Chat:** Adaptive interface that speaks the "language" of the user.
- **Handoff System:** Automatically flags restricted technical info for review by the appropriate owner and follows up automatically. 

---

## Key References

- **Prompt Engineering:** Specific personas for e.g. "Business Analyst", "Developer", "Controller", "Product Owner", "Compliance Officer", "UX Designer", and "Senior Systems Engineer."
- **LangGraph Documentation:** For managing the Head-Agent state machine and tool-calling.
- **Project Data Schema:** `project_state.json` for managing cross-role state and ticket history.