from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Protocol

from dotenv import load_dotenv

load_dotenv()


class TTSClient(Protocol):
    def synthesize(self, text: str, voice_id: str) -> bytes:
        ...


class STTClient(Protocol):
    def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
        ...


# ── ElevenLabs TTS ───────────────────────────────────────────────────────


class ElevenLabsTTS:
    def __init__(self, api_key: str) -> None:
        from elevenlabs import ElevenLabs

        self._client = ElevenLabs(api_key=api_key)

    def synthesize(self, text: str, voice_id: str) -> bytes:
        try:
            audio_iter = self._client.text_to_speech.stream(
                voice_id=voice_id,
                text=text,
                model_id="eleven_flash_v2_5",
                output_format="mp3_22050_32",
                optimize_streaming_latency=3,
            )
            return b"".join(audio_iter)
        except Exception:
            return b""


# ── ElevenLabs STT ───────────────────────────────────────────────────────


class ElevenLabsSTT:
    def __init__(self, api_key: str) -> None:
        from elevenlabs import ElevenLabs

        self._client = ElevenLabs(api_key=api_key)

    def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
        try:
            result = self._client.speech_to_text.convert(
                model_id="scribe_v2",
                file=("recording.webm", audio_bytes, mime_type),
                language_code="en",
            )
            return result.text.strip()
        except Exception as e:
            import streamlit as st
            st.error(f"ElevenLabs STT error: {e.__class__.__name__}: {str(e)[:100]}")
            return ""


# ── Gemini STT (fallback) ────────────────────────────────────────────────


class GeminiSTT:
    def __init__(self, api_key: str) -> None:
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self._model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
        from google.genai import types

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                    "Transcribe this audio exactly. Return only the transcription text, nothing else.",
                ],
            )
            return response.text.strip()
        except Exception:
            return ""


# ── Stubs for offline / testing ──────────────────────────────────────────


@dataclass
class StubTTS:
    def synthesize(self, text: str, voice_id: str) -> bytes:
        return b""


@dataclass
class StubSTT:
    def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
        return "(Speech-to-text unavailable in offline mode)"


# ── Voice mapping ────────────────────────────────────────────────────────

VOICE_MAP = {
    "business_analyst": "EXAVITQu4vr4xnSDxMaL",   # "Sarah"
    "developer": "JBFqnCBsd6RMkjVDRZzb",           # "George"
    "product_manager": "TX3LPaxmHKxFdv7VOQHJ",     # "Liam"
    "compliance_officer": "XB0fDUnXU5powFXDhCwa",   # "Charlotte"
    "marketing_manager": "EXAVITQu4vr4xnSDxMaL",   # "Sarah"
    "risk_analyst": "JBFqnCBsd6RMkjVDRZzb",        # "George"
    "ux_designer": "TX3LPaxmHKxFdv7VOQHJ",         # "Liam"
}


def get_voice_id(role: str) -> str:
    return VOICE_MAP.get(role, "EXAVITQu4vr4xnSDxMaL")


# ── Factory functions ────────────────────────────────────────────────────


def build_tts() -> TTSClient:
    key = os.getenv("ELEVENLABS_API_KEY")
    if key and key != "your-elevenlabs-key-here":
        return ElevenLabsTTS(key)
    return StubTTS()


def build_stt() -> STTClient:
    # ElevenLabs STT first (same key as TTS), then Gemini fallback
    el_key = os.getenv("ELEVENLABS_API_KEY")
    if el_key and el_key != "your-elevenlabs-key-here":
        return ElevenLabsSTT(el_key)
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        return GeminiSTT(gemini_key)
    return StubSTT()
