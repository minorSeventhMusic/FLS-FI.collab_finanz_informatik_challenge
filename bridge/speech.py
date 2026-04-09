from __future__ import annotations

import io
import logging
import os
from dataclasses import dataclass
from typing import BinaryIO, Protocol, Union

from openai import OpenAI

logger = logging.getLogger(__name__)
OFFLINE_STT_MESSAGE = "(Speech-to-text unavailable in offline mode)"
DEFAULT_TRANSCRIPTION_LANGUAGE = "en"
TRANSCRIPTION_LANGUAGE_ENV = "SPEECH_TRANSCRIPTION_LANGUAGE"


class TTSClient(Protocol):
    def synthesize(self, text: str, voice_id: str) -> bytes:
        ...


class STTClient(Protocol):
    def transcribe(
        self,
        audio_bytes: bytes,
        mime_type: str = "audio/wav",
        language: str | None = None,
    ) -> str:
        ...


AudioFileInput = Union[bytes, bytearray, memoryview, BinaryIO]


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

    def transcribe(
        self,
        audio_bytes: bytes,
        mime_type: str = "audio/wav",
        language: str | None = None,
    ) -> str:
        from google.genai import types

        safe_language = _resolve_transcription_language(language)
        logger.info(
            "Gemini speech-to-text request mime_type=%s audio_size_bytes=%s language=%s",
            mime_type,
            len(audio_bytes),
            safe_language,
        )
        response = self._client.models.generate_content(
            model=self._model,
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                (
                    "Transcribe this audio exactly in the source language. "
                    f"The expected language is {safe_language}. "
                    "Return only the transcript text, with no translation and no extra commentary."
                ),
            ],
        )
        raw_transcript = response.text.strip()
        logger.info("Gemini speech-to-text raw transcript text: %s", raw_transcript)
        return raw_transcript


class OpenAISTT:
    def __init__(self, api_key: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = "gpt-4o-mini-transcribe"

    def transcribe(
        self,
        audio_bytes: bytes,
        mime_type: str = "audio/wav",
        language: str | None = None,
    ) -> str:
        safe_language = _resolve_transcription_language(language)
        file_buffer = io.BytesIO(audio_bytes)
        file_buffer.name = "voice-note"
        logger.info(
            "OpenAI speech-to-text request mime_type=%s audio_size_bytes=%s language=%s",
            mime_type,
            len(audio_bytes),
            safe_language,
        )
        transcript = self._client.audio.transcriptions.create(
            model=self._model,
            file=("voice-note", file_buffer, mime_type),
            language=safe_language,
            response_format="text",
        )
        raw_transcript = str(transcript).strip()
        logger.info("OpenAI speech-to-text raw transcript text: %s", raw_transcript)
        return raw_transcript


# ── Stubs for offline / testing ──────────────────────────────────────────


@dataclass
class StubTTS:
    def synthesize(self, text: str, voice_id: str) -> bytes:
        return b""


@dataclass
class StubSTT:
    def transcribe(
        self,
        audio_bytes: bytes,
        mime_type: str = "audio/wav",
        language: str | None = None,
    ) -> str:
        logger.warning(
            "Offline STT stub used for mime_type=%s language=%s because no live STT client was configured.",
            mime_type,
            _resolve_transcription_language(language),
        )
        return OFFLINE_STT_MESSAGE


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
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    configured_language = _resolve_transcription_language()

    print(
        "[speech] Startup diagnostic: "
        f"OPENAI_API_KEY present={bool(openai_key)} "
        f"GEMINI_API_KEY present={bool(gemini_key)} "
        f"transcription_language={configured_language}"
    )

    if openai_key and openai_key != "your-key-here":
        print("[speech] Using OpenAI STT client.")
        return OpenAISTT(openai_key)
    if gemini_key:
        print("[speech] Using Gemini STT client.")
        return GeminiSTT(gemini_key)

    print(
        "[speech] Falling back to offline STT stub because no speech API key "
        "was found in the current process."
    )
    return StubSTT()


def transcribe_audio_bytes(
    audio_bytes: bytes,
    mime_type: str,
    *,
    language: str | None = None,
    stt_client: STTClient | None = None,
) -> str:
    if not audio_bytes:
        logger.warning("Skipping transcription because the audio payload was empty.")
        return ""

    client = stt_client or build_stt()
    safe_mime_type = mime_type or "audio/webm"
    safe_language = _resolve_transcription_language(language)
    try:
        transcript = client.transcribe(
            audio_bytes,
            safe_mime_type,
            safe_language,
        ).strip()
    except Exception:
        logger.exception(
            "Speech-to-text failed using %s with mime_type=%s audio_size_bytes=%s language=%s.",
            type(client).__name__,
            safe_mime_type,
            len(audio_bytes),
            safe_language,
        )
        return ""

    if transcript == OFFLINE_STT_MESSAGE:
        logger.warning(
            "Speech-to-text returned the offline stub message. "
            "A live transcription API was not reached."
        )
        return ""

    if not transcript:
        logger.warning(
            "Speech-to-text returned an empty transcript using %s.",
            type(client).__name__,
        )
        return ""

    if _is_suspicious_transcript(transcript, safe_language):
        logger.warning(
            "Speech-to-text transcript was rejected as suspicious for language=%s raw_text=%s",
            safe_language,
            transcript,
        )
        return ""

    return transcript


def transcribe_audio(
    stt_client: STTClient,
    audio_file: AudioFileInput,
    *,
    language: str | None = None,
) -> str:
    audio_bytes = _read_audio_bytes(audio_file)
    return transcribe_audio_bytes(
        audio_bytes,
        "audio/wav",
        language=language,
        stt_client=stt_client,
    )


def _resolve_transcription_language(language: str | None = None) -> str:
    if language and language.strip():
        return language.strip()

    configured_language = os.getenv(TRANSCRIPTION_LANGUAGE_ENV, DEFAULT_TRANSCRIPTION_LANGUAGE)
    if configured_language.strip():
        return configured_language.strip()
    return DEFAULT_TRANSCRIPTION_LANGUAGE


def _is_suspicious_transcript(text: str, language: str) -> bool:
    normalized_text = text.strip()
    if not normalized_text:
        return True

    if language.lower().startswith("en"):
        hangul_count = sum(_is_hangul_character(char) for char in normalized_text)
        latin_count = sum(char.isascii() and char.isalpha() for char in normalized_text)
        if hangul_count >= 2 and latin_count == 0:
            return True

    return False


def _is_hangul_character(char: str) -> bool:
    code_point = ord(char)
    return (
        0x1100 <= code_point <= 0x11FF
        or 0x3130 <= code_point <= 0x318F
        or 0xAC00 <= code_point <= 0xD7AF
    )


def _read_audio_bytes(audio_file: AudioFileInput) -> bytes:
    if isinstance(audio_file, bytes):
        return audio_file
    if isinstance(audio_file, bytearray):
        return bytes(audio_file)
    if isinstance(audio_file, memoryview):
        return audio_file.tobytes()

    audio_bytes = audio_file.read()
    try:
        audio_file.seek(0)
    except (AttributeError, OSError):
        pass

    if isinstance(audio_bytes, bytes):
        return audio_bytes
    return bytes(audio_bytes)
