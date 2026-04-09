from __future__ import annotations

import io
import logging
import os
from dataclasses import dataclass

from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)
TRANSCRIPTION_MODEL = "gpt-4o-mini-transcribe"
DEFAULT_TRANSCRIPTION_LANGUAGE = "en"
TRANSCRIPTION_LANGUAGE_ENV = "SPEECH_TRANSCRIPTION_LANGUAGE"
SUPPORTED_AUDIO_CONTENT_TYPES = {
    "audio/flac",
    "audio/m4a",
    "audio/mp3",
    "audio/mp4",
    "audio/mpeg",
    "audio/ogg",
    "audio/wav",
    "audio/webm",
    "audio/x-m4a",
    "audio/x-wav",
}


@dataclass
class TranscriptionServiceError(Exception):
    status_code: int
    message: str

    def __str__(self) -> str:
        return self.message


def validate_audio_upload(audio_bytes: bytes, content_type: str | None) -> None:
    if not audio_bytes:
        raise TranscriptionServiceError(
            status_code=400,
            message="The uploaded audio file is empty.",
        )

    if not content_type:
        raise TranscriptionServiceError(
            status_code=415,
            message="The uploaded file is missing an audio content type.",
        )

    if content_type not in SUPPORTED_AUDIO_CONTENT_TYPES:
        raise TranscriptionServiceError(
            status_code=415,
            message=(
                "Unsupported audio content type. "
                f"Received '{content_type}'."
            ),
        )


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error(
            "Speech backend could not create an OpenAI client because "
            "OPENAI_API_KEY is missing in the current process."
        )
        raise TranscriptionServiceError(
            status_code=500,
            message="OPENAI_API_KEY is not set in the environment.",
        )

    return OpenAI(api_key=api_key)


def resolve_transcription_language(language: str | None = None) -> str:
    if language and language.strip():
        return language.strip()

    configured_language = os.getenv(TRANSCRIPTION_LANGUAGE_ENV, DEFAULT_TRANSCRIPTION_LANGUAGE)
    if configured_language.strip():
        return configured_language.strip()
    return DEFAULT_TRANSCRIPTION_LANGUAGE


def is_suspicious_transcript(text: str, language: str) -> bool:
    normalized_text = text.strip()
    if not normalized_text:
        return True

    if language.lower().startswith("en"):
        hangul_count = sum(_is_hangul_character(char) for char in normalized_text)
        latin_count = sum(char.isascii() and char.isalpha() for char in normalized_text)
        if hangul_count >= 2 and latin_count == 0:
            return True

    return False


def transcribe_audio_file(
    *,
    audio_bytes: bytes,
    filename: str,
    content_type: str,
    language: str | None = None,
) -> str:
    validate_audio_upload(audio_bytes, content_type)

    client = get_openai_client()
    safe_filename = filename or "audio-upload"
    safe_language = resolve_transcription_language(language)
    file_buffer = io.BytesIO(audio_bytes)
    file_buffer.name = safe_filename
    logger.info(
        "Backend transcription request mime_type=%s audio_size_bytes=%s language=%s",
        content_type,
        len(audio_bytes),
        safe_language,
    )

    try:
        transcript = client.audio.transcriptions.create(
            model=TRANSCRIPTION_MODEL,
            file=(safe_filename, file_buffer, content_type),
            language=safe_language,
            response_format="text",
        )
    except OpenAIError as exc:
        logger.exception(
            "OpenAI transcription request failed for filename=%s content_type=%s.",
            safe_filename,
            content_type,
        )
        raise TranscriptionServiceError(
            status_code=502,
            message="OpenAI transcription failed. Please try again.",
        ) from exc
    except Exception as exc:
        logger.exception(
            "Unexpected backend transcription failure for filename=%s content_type=%s.",
            safe_filename,
            content_type,
        )
        raise TranscriptionServiceError(
            status_code=500,
            message="Unexpected transcription error.",
        ) from exc

    text = str(transcript).strip()
    logger.info("Backend transcription raw transcript text: %s", text)
    if not text:
        raise TranscriptionServiceError(
            status_code=502,
            message="The transcription service returned an empty result.",
        )

    if is_suspicious_transcript(text, safe_language):
        logger.warning(
            "Backend transcription rejected suspicious transcript for language=%s raw_text=%s",
            safe_language,
            text,
        )
        raise TranscriptionServiceError(
            status_code=422,
            message="The transcription service could not produce a reliable transcript.",
        )

    return text


def _is_hangul_character(char: str) -> bool:
    code_point = ord(char)
    return (
        0x1100 <= code_point <= 0x11FF
        or 0x3130 <= code_point <= 0x318F
        or 0xAC00 <= code_point <= 0xD7AF
    )
