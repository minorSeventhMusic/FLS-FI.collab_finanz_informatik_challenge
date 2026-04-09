from __future__ import annotations

import base64
import binascii
import json
from datetime import datetime, timedelta, timezone
from typing import Any, TypedDict

import streamlit as st

from bridge.config import DEFAULT_SCENARIO
from bridge.jira import JiraAdapter
from bridge.llm import build_llm_client
from bridge.models import Role
from bridge.personas import PERSONAS
from bridge.persistence import ProjectStateStore
from bridge.scenarios import get_scenario
from bridge.speech import build_stt, transcribe_audio_bytes
from bridge.workflow import compile_workflow, init_services
from components.voice_recorder import VoiceRecorderResult, render_voice_recorder

CHAT_INPUT_KEY = "chat_composer"
VOICE_COMPONENT_KEY = "chat_voice_recorder"

VOICE_STATE_IDLE = "idle"
VOICE_STATE_RECORDING = "recording"
VOICE_STATE_TRANSCRIBING = "transcribing"
VOICE_STATE_SENDING = "sending"


class PendingAudio(TypedDict):
    bytes: bytes
    format: str
    sequence: int


# ── Initialize ───────────────────────────────────────────────────────────

st.set_page_config(page_title="The Bridge — Chat", page_icon="🌉", layout="wide")

if "store" not in st.session_state:
    st.session_state.store = ProjectStateStore()
if "llm" not in st.session_state:
    st.session_state.llm = build_llm_client()
if "jira" not in st.session_state:
    st.session_state.jira = JiraAdapter(st.session_state.store)
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
if "draft_text" not in st.session_state:
    st.session_state.draft_text = ""
if "pending_audio" not in st.session_state:
    st.session_state.pending_audio = None
if "pending_transcript" not in st.session_state:
    st.session_state.pending_transcript = None
if "voice_ui_state" not in st.session_state:
    st.session_state.voice_ui_state = VOICE_STATE_IDLE
if "voice_error_message" not in st.session_state:
    st.session_state.voice_error_message = None
if "last_processed_voice_sequence" not in st.session_state:
    st.session_state.last_processed_voice_sequence = 0
if CHAT_INPUT_KEY not in st.session_state:
    st.session_state[CHAT_INPUT_KEY] = ""

init_services(
    llm=st.session_state.llm,
    store=st.session_state.store,
    jira=st.session_state.jira,
)
workflow = compile_workflow()

# Ensure tickets are seeded from data sources
_data = get_scenario(DEFAULT_SCENARIO)
st.session_state.jira.ensure_seed_tickets(_data)


def _get_recent_history(role: Role, hours: int = 1) -> list[Any]:
    convos = st.session_state.store.get_conversations(role)
    if not convos:
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent = []
    for convo in convos:
        try:
            timestamp = datetime.fromisoformat(convo.timestamp)
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            if timestamp >= cutoff:
                recent.append(convo)
        except (TypeError, ValueError):
            recent.append(convo)
    return recent


def _history_to_messages(convos: list[Any]) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for convo in convos:
        messages.append({"kind": "user", "content": convo.user_message})
        messages.append({"kind": "assistant", "content": convo.assistant_response})
    return messages


def _set_draft_text(text: str) -> None:
    st.session_state.draft_text = text
    st.session_state[CHAT_INPUT_KEY] = text


def _sync_draft_text_from_widget() -> None:
    widget_value = st.session_state.get(CHAT_INPUT_KEY)
    if isinstance(widget_value, str) and widget_value != st.session_state.draft_text:
        st.session_state.draft_text = widget_value


def _clear_voice_state(*, clear_error: bool = True) -> None:
    st.session_state.pending_audio = None
    st.session_state.pending_transcript = None
    st.session_state.voice_ui_state = VOICE_STATE_IDLE
    if clear_error:
        st.session_state.voice_error_message = None


def _run_turn(prompt_text: str) -> None:
    st.session_state.pending_resume = False
    st.session_state.messages.append({"kind": "user", "content": prompt_text})

    with st.spinner("The Bridge is thinking..."):
        result = workflow.invoke(
            {
                "user_message": prompt_text,
                "role": role.value,
                "scenario_id": DEFAULT_SCENARIO,
            }
        )

    response = result.get("final_response", result.get("raw_response", ""))
    st.session_state.messages.append({"kind": "assistant", "content": response})
    st.session_state.last_result = result


def send_message(prompt_text: str, *, clear_draft: bool = True) -> None:
    cleaned_prompt = prompt_text.strip()
    if not cleaned_prompt:
        return

    _run_turn(cleaned_prompt)
    if clear_draft:
        _set_draft_text("")


def _decode_voice_payload(payload: dict[str, Any]) -> PendingAudio | None:
    encoded_audio = payload.get("base64")
    mime_type = payload.get("mime_type", "audio/webm")
    sequence = payload.get("sequence", 0)

    if not isinstance(encoded_audio, str) or not encoded_audio:
        st.session_state.voice_error_message = (
            "The recording came back empty. Please try recording again."
        )
        st.toast("No audio was captured.", icon=":material/error:")
        return None

    try:
        audio_bytes = base64.b64decode(encoded_audio, validate=True)
    except (binascii.Error, ValueError):
        st.session_state.voice_error_message = (
            "We could not decode that recording. Please try again."
        )
        st.toast("That recording could not be processed.", icon=":material/error:")
        return None

    if not audio_bytes:
        st.session_state.voice_error_message = (
            "The recording was empty. Please try again."
        )
        st.toast("No audio was captured.", icon=":material/error:")
        return None

    try:
        safe_sequence = int(sequence)
    except (TypeError, ValueError):
        safe_sequence = 0

    return {
        "bytes": audio_bytes,
        "format": mime_type if isinstance(mime_type, str) else "audio/webm",
        "sequence": safe_sequence,
    }


def _handle_voice_error(error_event: dict[str, Any] | None) -> bool:
    if not isinstance(error_event, dict):
        return False

    message = error_event.get("message")
    if not isinstance(message, str) or not message:
        message = "We couldn't use the microphone just now. Please try again."

    st.session_state.voice_error_message = message
    st.session_state.voice_ui_state = VOICE_STATE_IDLE
    st.session_state.pending_audio = None
    st.session_state.pending_transcript = None
    st.toast(message, icon=":material/error:")
    return True


def _sync_voice_status(component_status: str | None) -> None:
    if st.session_state.voice_ui_state in {VOICE_STATE_TRANSCRIBING, VOICE_STATE_SENDING}:
        return

    if component_status == VOICE_STATE_RECORDING:
        st.session_state.voice_ui_state = VOICE_STATE_RECORDING
        st.session_state.voice_error_message = None
        return

    if component_status == VOICE_STATE_IDLE:
        st.session_state.voice_ui_state = VOICE_STATE_IDLE


def _handle_voice_payload(payload: dict[str, Any]) -> bool:
    decoded_payload = _decode_voice_payload(payload)
    if decoded_payload is None:
        st.session_state.voice_ui_state = VOICE_STATE_IDLE
        st.session_state.pending_audio = None
        st.session_state.pending_transcript = None
        return False

    sequence = decoded_payload["sequence"]
    if sequence <= st.session_state.last_processed_voice_sequence:
        return False

    st.session_state.last_processed_voice_sequence = sequence
    st.session_state.pending_audio = decoded_payload
    st.session_state.pending_transcript = None
    st.session_state.voice_error_message = None
    st.session_state.voice_ui_state = VOICE_STATE_TRANSCRIBING

    with st.status("Transcribing voice note...", expanded=False) as status:
        transcript = transcribe_audio_bytes(
            decoded_payload["bytes"],
            decoded_payload["format"],
            stt_client=st.session_state.stt,
        )

        if not transcript:
            st.session_state.voice_ui_state = VOICE_STATE_IDLE
            st.session_state.pending_audio = None
            st.session_state.pending_transcript = None
            st.session_state.voice_error_message = (
                "We couldn't transcribe that recording. Please try again."
            )
            status.update(label="Transcription failed", state="error")
            st.toast("Voice transcription failed.", icon=":material/error:")
            return False

        st.session_state.pending_transcript = transcript
        st.session_state.voice_ui_state = VOICE_STATE_SENDING
        status.update(label="Sending voice note to The Bridge...", state="running")
        send_message(transcript, clear_draft=False)
        status.update(label="Voice note sent", state="complete")

    _clear_voice_state()
    st.toast("Voice message sent.", icon=":material/send:")
    return True


def _render_chat_composer() -> None:
    _sync_draft_text_from_widget()

    mic_col, _ = st.columns([1, 14], vertical_alignment="bottom")
    with mic_col:
        voice_result: VoiceRecorderResult = render_voice_recorder(
            key=VOICE_COMPONENT_KEY,
            disabled=st.session_state.voice_ui_state in {VOICE_STATE_TRANSCRIBING, VOICE_STATE_SENDING},
        )
    st.session_state[CHAT_INPUT_KEY] = st.session_state.draft_text
    prompt_text = st.chat_input(
        "Ask about alignment, discrepancies, tickets, or request a report...",
        key=CHAT_INPUT_KEY,
    )

    _sync_voice_status(voice_result.get("status"))

    if _handle_voice_error(voice_result.get("error_event")):
        st.rerun()

    audio_payload = voice_result.get("audio_payload")
    if isinstance(audio_payload, dict) and _handle_voice_payload(audio_payload):
        st.rerun()

    if prompt_text:
        send_message(prompt_text)
        st.rerun()


# ── Sidebar ──────────────────────────────────────────────────────────────

st.sidebar.title("🌉 The Bridge")
st.sidebar.markdown("---")

_role_options = {persona.display_name: role_value for role_value, persona in PERSONAS.items()}
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
    help="Simulates single sign-on. The Bridge adapts its responses to your role.",
)
role = _role_options[role_label]

if "current_role" not in st.session_state:
    st.session_state.current_role = role_label
if st.session_state.current_role != role_label:
    st.session_state.current_role = role_label
    st.session_state.last_result = None
    st.session_state.active_ticket_key = None
    _clear_voice_state()

    recent = _get_recent_history(role)
    if recent:
        st.session_state.messages = _history_to_messages(recent)
        st.session_state.pending_resume = False
    else:
        all_convos = st.session_state.store.get_conversations(role)
        st.session_state.messages = []
        st.session_state.pending_resume = bool(all_convos)
    st.rerun()

st.sidebar.markdown("---")

# ── Ticket list ──────────────────────────────────────────────────────────

st.sidebar.markdown("### Tickets")

tickets = st.session_state.jira.list_tickets()
if tickets:
    active = [ticket for ticket in tickets if ticket.status != "Done"]
    resolved = [ticket for ticket in tickets if ticket.status == "Done"]

    if active:
        st.sidebar.caption(f"{len(active)} active ticket{'s' if len(active) != 1 else ''}")
        for ticket in active:
            status_icon = "🔴" if ticket.priority == "High" else "🟡"
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
                    st.session_state.active_ticket_key = ticket.key
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
    result = st.session_state.last_result
    score = result.get("alignment_score", 0)
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
        f'{result.get("alignment_summary", "No analysis yet")}',
        unsafe_allow_html=True,
    )

    files = result.get("relevant_files", [])
    if files:
        st.sidebar.markdown("### Relevant Files")
        for file_path in files:
            st.sidebar.code(file_path, language=None)

    if result.get("jira_action") and result["jira_action"] != "none":
        st.sidebar.markdown("### Jira Update")
        try:
            jira_payload = json.loads(result.get("jira_payload", "{}"))
            st.sidebar.success(f"**{jira_payload.get('key', '')}**: {jira_payload.get('title', '')}")
        except json.JSONDecodeError:
            pass

    if result.get("restricted"):
        st.sidebar.warning(f"**Handoff**: {result.get('handoff_reason', '')}")

# ── Main Chat Area ───────────────────────────────────────────────────────

st.title("💬 Chat")

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

if st.session_state.pending_resume:
    st.info("You have a previous conversation on file. Would you like to resume?")
    resume_col, fresh_col = st.columns(2)
    with resume_col:
        if st.button("Resume previous session", type="primary"):
            all_convos = st.session_state.store.get_conversations(role)
            st.session_state.messages = _history_to_messages(all_convos[-10:])
            st.session_state.pending_resume = False
            st.rerun()
    with fresh_col:
        if st.button("Start fresh"):
            st.session_state.pending_resume = False
            st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["kind"]):
        st.markdown(message["content"])

_render_chat_composer()
