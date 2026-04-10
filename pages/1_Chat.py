from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta

import streamlit as st

from bridge.config import DEFAULT_SCENARIO
from bridge.jira import JiraAdapter
from bridge.llm import build_llm_client
from bridge.models import Role
from bridge.personas import get_persona
from bridge.persistence import ProjectStateStore
from bridge.scenarios import get_scenario
from bridge.speech import build_stt, build_tts, get_voice_id
from bridge.workflow import compile_workflow, init_services

# ── Initialize ───────────────────────────────────────────────────────────

st.set_page_config(page_title="FI.collab — Chat", page_icon="\U0001f91d", layout="wide")

from bridge.styles import inject_shared_css
inject_shared_css()

if "store" not in st.session_state:
    st.session_state.store = ProjectStateStore()
if "llm" not in st.session_state:
    st.session_state.llm = build_llm_client()
if "jira" not in st.session_state:
    st.session_state.jira = JiraAdapter(st.session_state.store)
if "tts" not in st.session_state:
    st.session_state.tts = build_tts()
if "stt" not in st.session_state:
    st.session_state.stt = build_stt()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "pending_resume" not in st.session_state:
    st.session_state.pending_resume = False
if "active_ticket_key" not in st.session_state:
    st.session_state.active_ticket_key = None
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

init_services(
    llm=st.session_state.llm,
    store=st.session_state.store,
    jira=st.session_state.jira,
)
workflow = compile_workflow()

# Ensure tickets are seeded from data sources
_data = get_scenario(DEFAULT_SCENARIO)
st.session_state.jira.ensure_seed_tickets(_data)


def _get_recent_history(role: Role, hours: int = 1):
    convos = st.session_state.store.get_conversations(role)
    if not convos:
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent = []
    for c in convos:
        try:
            ts = datetime.fromisoformat(c.timestamp)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts >= cutoff:
                recent.append(c)
        except (ValueError, TypeError):
            recent.append(c)
    return recent


def _history_to_messages(convos):
    msgs = []
    for c in convos:
        msgs.append({"kind": "user", "content": c.user_message})
        msgs.append({"kind": "assistant", "content": c.assistant_response})
    return msgs


def _run_turn(prompt_text: str):
    """Execute a conversation turn and update session state."""
    st.session_state.pending_resume = False
    st.session_state.messages.append({"kind": "user", "content": prompt_text})

    # Show the user message immediately
    with st.chat_message("user"):
        st.markdown(prompt_text)

    import random
    import time

    # Spinner while LLM thinks
    _verbs = [
        "thinking", "pondering", "contemplating", "rummaging",
        "investigating", "deliberating", "analyzing", "scrutinizing",
        "deciphering", "connecting", "correlating", "untangling",
        "assembling", "cross-checking", "synthesizing",
    ]
    with st.chat_message("assistant"):
        with st.spinner(f"FI.collab is {random.choice(_verbs)}..."):
            result = workflow.invoke({
                "user_message": prompt_text,
                "role": role.value,
                "scenario_id": DEFAULT_SCENARIO,
            })
        response = result.get("final_response", result.get("raw_response", ""))

        # Generate TTS in parallel with text display prep
        audio_bytes = b""
        if voice_responses and response:
            persona = get_persona(role)
            voice_id = persona.voice_id or get_voice_id(role.value)
            audio_bytes = st.session_state.tts.synthesize(response, voice_id)

        # Typewriter effect — stream text word by word
        def _stream_words(text):
            for word in text.split(" "):
                yield word + " "
                time.sleep(0.03)

        st.write_stream(_stream_words(response))

    st.session_state.messages.append({"kind": "assistant", "content": response})
    st.session_state.last_result = result

    # Play audio after the message bubble — use st.audio which handles
    # browser autoplay policies better than raw HTML audio tags
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    # Auto-select newly created ticket in sidebar
    if result.get("jira_action") == "create":
        try:
            jp = json.loads(result.get("jira_payload", "{}"))
            if jp.get("key"):
                st.session_state.active_ticket_key = jp["key"]
        except json.JSONDecodeError:
            pass


# ── Sidebar ──────────────────────────────────────────────────────────────


# Role selector — pick up landing page selection if available
from bridge.personas import PERSONAS
_role_options = {p.display_name: r for r, p in PERSONAS.items()}
_role_names = list(_role_options.keys())
_default_idx = 0
if "selected_landing_role" in st.session_state:
    landing = st.session_state["selected_landing_role"]
    if landing in _role_names:
        _default_idx = _role_names.index(landing)

role_label = st.sidebar.selectbox(
    "Select Role (Mock SSO)",
    _role_names,
    index=_default_idx,
    help="Simulates single sign-on. FI.collab adapts its responses to your role.",
)
role = _role_options[role_label]

# Voice response toggle
voice_responses = st.sidebar.toggle(
    "Spoken responses",
    value=st.session_state.get("voice_responses", False),
    help="Read responses aloud using ElevenLabs",
)
st.session_state.voice_responses = voice_responses

# Handle role switch — new persona = new user logging in
if "current_role" not in st.session_state:
    st.session_state.current_role = role_label
if st.session_state.current_role != role_label:
    st.session_state.current_role = role_label
    st.session_state.last_result = None
    st.session_state.active_ticket_key = None
    st.session_state.last_audio = None
    st.session_state.messages = []
    st.session_state.pending_resume = False
    st.rerun()

st.sidebar.markdown("---")

# ── Ticket list ──────────────────────────────────────────────────────────

st.sidebar.markdown("### Tickets")

tickets = st.session_state.jira.list_tickets()
if tickets:
    active = [t for t in tickets if t.status != "Done"]
    resolved = [t for t in tickets if t.status == "Done"]

    if active:
        st.sidebar.caption(f"{len(active)} active ticket{'s' if len(active) != 1 else ''}")
        for ticket in active:
            status_icon = "\U0001f534" if ticket.priority == "High" else "\U0001f7e1"
            with st.sidebar.container(border=True):
                st.markdown(f"**{ticket.key}**: {ticket.title[:50]}")
                st.caption(f"{status_icon} {ticket.status} | {ticket.priority}")
                if ticket.external_url:
                    st.caption(f"[Open in tracker]({ticket.external_url})")
                is_selected = st.session_state.active_ticket_key == ticket.key
                if st.button(
                    "Discussing" if is_selected else "Open in chat",
                    key=f"ticket-{ticket.key}",
                    type="primary" if is_selected else "secondary",
                    use_container_width=True,
                ):
                    if is_selected:
                        # Deselect — clear ticket and chat
                        st.session_state.active_ticket_key = None
                        st.session_state.messages = []
                    else:
                        # Select — show ticket summary in chat
                        st.session_state.active_ticket_key = ticket.key
                        st.session_state.messages = [{
                            "kind": "assistant",
                            "content": (
                                f"**{ticket.key}**: {ticket.title}\n\n"
                                f"- **Status:** {ticket.status}\n"
                                f"- **Priority:** {ticket.priority}\n"
                                f"- **Assignee:** {ticket.assignee or 'Unassigned'}"
                            ),
                        }]
                    st.session_state.pending_resume = False
                    st.rerun()

    if resolved:
        with st.sidebar.expander(f"Resolved ({len(resolved)})"):
            for ticket in resolved:
                st.caption(f"**{ticket.key}**: {ticket.title[:40]}")
else:
    st.sidebar.info("No tickets yet.")

st.sidebar.markdown("---")

# ── Alignment score display ──────────────────────────────────────────────

if st.session_state.last_result:
    r = st.session_state.last_result
    score = r.get("alignment_score", 0)
    if score < 40:
        color_class = "score-low"
    elif score < 70:
        color_class = "score-mid"
    else:
        color_class = "score-high"

    st.sidebar.markdown("### Alignment Score")
    st.sidebar.progress(score / 100)
    st.sidebar.markdown(
        f'<span class="{color_class}">{score}%</span> — '
        f'{r.get("alignment_summary", "No analysis yet")}',
        unsafe_allow_html=True,
    )

    files = r.get("relevant_files", [])
    if files:
        st.sidebar.markdown("### Relevant Files")
        for f in files:
            st.sidebar.code(f, language=None)

    if r.get("jira_action") and r["jira_action"] != "none":
        st.sidebar.markdown("### Jira Update")
        try:
            jp = json.loads(r.get("jira_payload", "{}"))
            st.sidebar.success(f"**{jp.get('key', '')}**: {jp.get('title', '')}")
        except json.JSONDecodeError:
            pass

    if r.get("restricted"):
        st.sidebar.warning(f"**Handoff**: {r.get('handoff_reason', '')}")

# ── Main Chat Area ───────────────────────────────────────────────────────

st.markdown('<div style="color: #e30613; font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">Chat</div>', unsafe_allow_html=True)

# Show active context
active_key = st.session_state.active_ticket_key
if active_key:
    ticket = st.session_state.jira.get_ticket(active_key)
    if ticket:
        st.caption(
            f"Role: **{role_label}** | Ticket: **{ticket.key}** — {ticket.title} | "
            f"Status: **{ticket.status}**"
        )
    else:
        st.caption(f"Role: **{role_label}**")
else:
    st.caption(f"Role: **{role_label}**")

# Show/hide history button — context-sensitive to active ticket
_all_convos = st.session_state.store.get_conversations(role)
_active_key = st.session_state.active_ticket_key
if _active_key:
    # Filter to conversations that mention this ticket
    _relevant = [c for c in _all_convos if _active_key in c.user_message or _active_key in c.assistant_response]
else:
    _relevant = _all_convos

if _relevant:
    if not st.session_state.messages:
        if st.button("Show conversation history"):
            st.session_state.messages = _history_to_messages(_relevant[-10:])
            st.session_state["showing_history"] = True
            st.rerun()
    elif st.session_state.get("showing_history"):
        if st.button("Hide history"):
            st.session_state.messages = []
            st.session_state["showing_history"] = False
            st.rerun()

# Render message history
for msg in st.session_state.messages:
    with st.chat_message(msg["kind"]):
        st.markdown(msg["content"])


# ── Input area ───────────────────────────────────────────────────────────

from streamlit_mic_recorder import mic_recorder

col_mic, col_chat = st.columns([1, 20])
with col_mic:
    audio = mic_recorder(
        start_prompt="\U0001f3a4",
        stop_prompt="\u23f9",
        key="mic_recorder",
        format="webm",
    )
with col_chat:
    prompt = st.chat_input("Ask about alignment, discrepancies, tickets, or request a report...")

# Handle mic recording — track audio ID to avoid reprocessing on rerun
if audio and audio.get("bytes"):
    audio_id = audio.get("id", 0)
    last_id = st.session_state.get("_last_audio_id", 0)
    if audio_id != last_id:
        st.session_state["_last_audio_id"] = audio_id
        with st.spinner("Transcribing..."):
            transcription = st.session_state.stt.transcribe(
                audio["bytes"],
                mime_type="audio/webm",
            )
        if transcription and not transcription.startswith("("):
            _run_turn(transcription)
            st.rerun()
        elif transcription:
            st.warning("Could not transcribe audio. Please try again or type your question.")

# Handle text input
if prompt:
    _run_turn(prompt)
    st.rerun()
