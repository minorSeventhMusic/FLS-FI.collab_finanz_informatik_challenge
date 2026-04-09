from __future__ import annotations

from typing import TypedDict, cast

import streamlit.components.v2 as components_v2


class VoiceAudioPayload(TypedDict):
    sequence: int
    base64: str
    mime_type: str


class VoiceErrorEvent(TypedDict):
    code: str
    message: str


class VoiceRecorderResult(TypedDict, total=False):
    status: str
    audio_payload: VoiceAudioPayload | None
    error_event: VoiceErrorEvent | None


_VOICE_RECORDER_HTML = """
<div class="voice-recorder">
  <button class="voice-button" type="button" aria-label="Start recording" title="Start recording">
    <span class="voice-icon voice-icon-idle" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none">
        <path d="M12 15a3 3 0 0 0 3-3V7a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Z"></path>
        <path d="M18 11a6 6 0 1 1-12 0"></path>
        <path d="M12 17v4"></path>
      </svg>
    </span>
    <span class="voice-icon voice-icon-recording" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="4.5"></circle>
      </svg>
    </span>
  </button>
</div>
"""

_VOICE_RECORDER_CSS = """
.voice-recorder {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  min-height: 2.65rem;
}

.voice-recorder.is-floating {
  min-height: 0;
  pointer-events: none;
  position: fixed;
  z-index: 200;
}

.voice-button {
  align-items: center;
  background: var(--st-secondary-background-color, #f4f6fb);
  border: 1px solid var(--st-border-color, rgba(49, 51, 63, 0.2));
  border-radius: 999px;
  color: var(--st-primary-color, #4257ff);
  cursor: pointer;
  display: inline-flex;
  height: 2.65rem;
  justify-content: center;
  padding: 0;
  transition: border-color 120ms ease, background 120ms ease, transform 120ms ease;
  width: 2.65rem;
}

.voice-recorder.is-floating .voice-button {
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.12);
  pointer-events: auto;
}

.voice-button:hover {
  border-color: var(--st-primary-color, #4257ff);
  transform: translateY(-1px);
}

.voice-button:focus-visible {
  outline: 2px solid var(--st-primary-color, #4257ff);
  outline-offset: 2px;
}

.voice-button:disabled,
.voice-button.is-disabled {
  cursor: not-allowed;
  opacity: 0.55;
  transform: none;
}

.voice-button.is-recording {
  background: rgba(217, 45, 32, 0.08);
  border-color: #d92d20;
  color: #d92d20;
}

.voice-icon {
  display: none;
  height: 1.2rem;
  width: 1.2rem;
}

.voice-icon svg {
  display: block;
  height: 100%;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
  width: 100%;
}

.voice-button .voice-icon-idle {
  display: block;
}

.voice-button.is-recording .voice-icon-idle {
  display: none;
}

.voice-button.is-recording .voice-icon-recording {
  display: block;
}
"""

_VOICE_RECORDER_JS = """
const MIME_TYPES = [
  "audio/webm;codecs=opus",
  "audio/webm",
  "audio/mp4",
  "audio/ogg;codecs=opus"
];

function pickMimeType() {
  if (typeof MediaRecorder === "undefined") {
    return "";
  }

  for (const mimeType of MIME_TYPES) {
    if (typeof MediaRecorder.isTypeSupported !== "function") {
      return mimeType;
    }
    if (MediaRecorder.isTypeSupported(mimeType)) {
      return mimeType;
    }
  }

  return "";
}

export default function(component) {
  const { data, parentElement, setStateValue, setTriggerValue } = component;
  const wrapper = parentElement.querySelector(".voice-recorder");
  const button = parentElement.querySelector(".voice-button");
  const state = parentElement.__voiceRecorderState ?? {
    chunks: [],
    mimeType: "",
    recorder: null,
    sequence: 0,
    stream: null
  };
  parentElement.__voiceRecorderState = state;
  const isFloating = Boolean(data?.floating);
  const bottomOffset = Number(data?.bottom_offset ?? 18);
  const leftInset = Number(data?.left_inset ?? 12);
  const leftShift = Number(data?.left_shift ?? 54);
  let resizeObserver = parentElement.__voiceRecorderResizeObserver ?? null;

  function updateFloatingLayout() {
    if (!wrapper || !isFloating) {
      return;
    }

    const bounds = parentElement.getBoundingClientRect();
    const left = Math.max(bounds.left + leftInset - leftShift, 12);
    wrapper.style.left = `${left}px`;
    wrapper.style.bottom = `${bottomOffset}px`;
  }

  function stopStreamTracks() {
    if (!state.stream) {
      return;
    }

    state.stream.getTracks().forEach((track) => track.stop());
    state.stream = null;
  }

  function resetRecorderState() {
    state.chunks = [];
    state.mimeType = "";
    state.recorder = null;
    stopStreamTracks();
  }

  function updateButton() {
    const isRecording = Boolean(
      state.recorder && state.recorder.state === "recording"
    );
    const isDisabled = Boolean(data?.disabled);

    button.disabled = isDisabled;
    button.classList.toggle("is-disabled", isDisabled);
    button.classList.toggle("is-recording", isRecording);
    button.title = isRecording ? "Stop recording" : "Start recording";
    button.setAttribute(
      "aria-label",
      isRecording ? "Stop recording" : "Start recording"
    );

    wrapper.classList.toggle("is-floating", isFloating);
    updateFloatingLayout();
  }

  function emitError(code, message) {
    resetRecorderState();
    setStateValue("status", "idle");
    setTriggerValue("error_event", { code, message });
    updateButton();
  }

  async function startRecording() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      emitError(
        "unsupported_browser",
        "This browser does not support microphone recording."
      );
      return;
    }

    try {
      state.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (error) {
      emitError(
        "permission_denied",
        "Microphone access was denied. Please allow access and try again."
      );
      return;
    }

    state.chunks = [];
    const preferredMimeType = pickMimeType();

    try {
      state.recorder = preferredMimeType
        ? new MediaRecorder(state.stream, { mimeType: preferredMimeType })
        : new MediaRecorder(state.stream);
    } catch (error) {
      emitError(
        "recorder_unavailable",
        "Your browser could not start audio recording."
      );
      return;
    }

    state.mimeType = state.recorder.mimeType || preferredMimeType || "audio/webm";

    state.recorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        state.chunks.push(event.data);
      }
    };

    state.recorder.onerror = () => {
      emitError(
        "recording_failed",
        "Recording stopped unexpectedly. Please try again."
      );
    };

    state.recorder.onstop = () => {
      const recordedChunks = state.chunks.slice();
      const mimeType = state.mimeType || "audio/webm";
      const sequence = state.sequence + 1;
      const blob = new Blob(recordedChunks, { type: mimeType });

      resetRecorderState();
      updateButton();

      if (!blob.size) {
        setStateValue("status", "idle");
        setTriggerValue("error_event", {
          code: "empty_audio",
          message: "No audio was captured. Please try again."
        });
        return;
      }

      const reader = new FileReader();
      reader.onloadend = () => {
        const result = reader.result;

        if (typeof result !== "string" || !result.includes(",")) {
          setStateValue("status", "idle");
          setTriggerValue("error_event", {
            code: "encoding_failed",
            message: "We could not process that recording. Please try again."
          });
          return;
        }

        const base64 = result.split(",", 2)[1];
        if (!base64) {
          setStateValue("status", "idle");
          setTriggerValue("error_event", {
            code: "empty_audio",
            message: "No audio was captured. Please try again."
          });
          return;
        }

        state.sequence = sequence;
        setStateValue("status", "idle");
        setTriggerValue("audio_payload", {
          base64,
          mime_type: blob.type || mimeType,
          sequence
        });
      };

      reader.readAsDataURL(blob);
    };

    try {
      state.recorder.start();
      setStateValue("status", "recording");
      updateButton();
    } catch (error) {
      emitError(
        "recording_failed",
        "Recording could not be started. Please try again."
      );
    }
  }

  function stopRecording() {
    if (!state.recorder || state.recorder.state !== "recording") {
      return;
    }

    try {
      state.recorder.stop();
    } catch (error) {
      emitError(
        "recording_failed",
        "Recording could not be stopped cleanly. Please try again."
      );
    }
  }

  button.onclick = async (event) => {
    event.preventDefault();

    if (button.disabled) {
      return;
    }

    const isRecording = Boolean(
      state.recorder && state.recorder.state === "recording"
    );

    if (isRecording) {
      stopRecording();
    } else {
      await startRecording();
    }
  };

  if (isFloating) {
    parentElement.style.minHeight = "1px";
    parentElement.style.height = "1px";
    parentElement.style.overflow = "visible";
    updateFloatingLayout();

    if (!resizeObserver && typeof ResizeObserver !== "undefined") {
      resizeObserver = new ResizeObserver(() => {
        updateFloatingLayout();
      });
      resizeObserver.observe(parentElement);
      parentElement.__voiceRecorderResizeObserver = resizeObserver;
    }

    window.addEventListener("resize", updateFloatingLayout);
  }

  updateButton();

  return () => {
    button.onclick = null;
    if (isFloating) {
      window.removeEventListener("resize", updateFloatingLayout);
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
    }
  };
}
"""

_voice_recorder_component = components_v2.component(
    "bridge_voice_recorder",
    html=_VOICE_RECORDER_HTML,
    css=_VOICE_RECORDER_CSS,
    js=_VOICE_RECORDER_JS,
)


def render_voice_recorder(
    *,
    key: str,
    disabled: bool = False,
    floating: bool = False,
    bottom_offset: int = 18,
    left_inset: int = 12,
    left_shift: int = 54,
) -> VoiceRecorderResult:
    result = _voice_recorder_component(
        key=key,
        data={
            "disabled": disabled,
            "floating": floating,
            "bottom_offset": bottom_offset,
            "left_inset": left_inset,
            "left_shift": left_shift,
        },
        default={"status": "idle"},
        width="stretch" if floating else "content",
        height=1 if floating else 52,
        on_status_change=lambda: None,
        on_audio_payload_change=lambda: None,
        on_error_event_change=lambda: None,
    )
    return cast(VoiceRecorderResult, dict(result))
