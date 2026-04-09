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
    def transcribe(self, audio_bytes: bytes) -> str:
        ...


# ── ElevenLabs TTS ───────────────────────────────────────────────────────


class ElevenLabsTTS:
    def __init__(self, api_key: str) -> None:
        from elevenlabs import ElevenLabs

        self._client = ElevenLabs(api_key=api_key)

    def synthesize(self, text: str, voice_id: str) -> bytes:
        try:
            audio_iter = self._client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            return b"".join(audio_iter)
        except Exception:
            return b""


# ── Gemini STT ───────────────────────────────────────────────────────────


class GeminiSTT:
    def __init__(self, api_key: str) -> None:
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self._model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def transcribe(self, audio_bytes: bytes) -> str:
        from google.genai import types

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
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
    def transcribe(self, audio_bytes: bytes) -> str:
        return "(Speech-to-text unavailable in offline mode)"


# ── Voice mapping ────────────────────────────────────────────────────────

# ElevenLabs default voice IDs — replace with your preferred voices
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
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return GeminiSTT(key)
    return StubSTT()
