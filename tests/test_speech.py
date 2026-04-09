from __future__ import annotations

import io
import unittest

from bridge.models import Role
from bridge.personas import get_persona
from bridge.speech import (
    OpenAISTT,
    StubSTT,
    StubTTS,
    transcribe_audio,
    transcribe_audio_bytes,
    get_voice_id,
    VOICE_MAP,
)


class FakeSTT:
    def __init__(self, transcript: str) -> None:
        self.transcript = transcript
        self.last_language: str | None = None
        self.last_mime_type: str | None = None

    def transcribe(
        self,
        audio_bytes: bytes,
        mime_type: str = "audio/wav",
        language: str | None = None,
    ) -> str:
        self.last_mime_type = mime_type
        self.last_language = language
        return self.transcript


class TestSpeechStubs(unittest.TestCase):
    def test_stub_tts_returns_empty_bytes(self):
        tts = StubTTS()
        result = tts.synthesize("Hello world", "some-voice-id")
        self.assertEqual(result, b"")

    def test_stub_stt_returns_fallback_text(self):
        stt = StubSTT()
        result = stt.transcribe(b"fake audio data")
        self.assertIn("unavailable", result.lower())

    def test_transcribe_audio_accepts_raw_bytes(self):
        stt = StubSTT()
        result = transcribe_audio(stt, b"fake audio data")
        self.assertEqual(result, "")

    def test_transcribe_audio_bytes_accepts_mime_type(self):
        stt = StubSTT()
        result = transcribe_audio_bytes(
            b"fake audio data",
            "audio/webm",
            stt_client=stt,
        )
        self.assertEqual(result, "")

    def test_transcribe_audio_bytes_defaults_to_english_language(self):
        stt = FakeSTT("hello from the bridge")
        result = transcribe_audio_bytes(
            b"fake audio data",
            "audio/webm",
            stt_client=stt,
        )
        self.assertEqual(result, "hello from the bridge")
        self.assertEqual(stt.last_language, "en")
        self.assertEqual(stt.last_mime_type, "audio/webm")

    def test_transcribe_audio_bytes_rejects_suspicious_hangul_for_english(self):
        stt = FakeSTT("안녕하세요")
        result = transcribe_audio_bytes(
            b"fake audio data",
            "audio/webm",
            stt_client=stt,
        )
        self.assertEqual(result, "")

    def test_transcribe_audio_bytes_accepts_explicit_language_override(self):
        stt = FakeSTT("bonjour")
        result = transcribe_audio_bytes(
            b"fake audio data",
            "audio/webm",
            language="fr",
            stt_client=stt,
        )
        self.assertEqual(result, "bonjour")
        self.assertEqual(stt.last_language, "fr")

    def test_transcribe_audio_accepts_file_like_objects(self):
        stt = StubSTT()
        audio_file = io.BytesIO(b"fake audio data")
        result = transcribe_audio(stt, audio_file)
        self.assertEqual(result, "")
        self.assertEqual(audio_file.tell(), 0)

    def test_voice_map_has_all_roles(self):
        for r in Role:
            self.assertIn(r.value, VOICE_MAP)

    def test_get_voice_id_returns_valid_for_known_roles(self):
        for r in Role:
            voice_id = get_voice_id(r.value)
            self.assertTrue(len(voice_id) > 0)

    def test_get_voice_id_fallback_for_unknown_role(self):
        voice_id = get_voice_id("nonexistent_role")
        self.assertTrue(len(voice_id) > 0)

    def test_persona_voice_ids_set(self):
        for r in Role:
            persona = get_persona(r)
            self.assertTrue(len(persona.voice_id) > 0)

    def test_persona_voice_ids_differ_per_role(self):
        ba = get_persona(Role.BUSINESS_ANALYST)
        dev = get_persona(Role.DEVELOPER)
        self.assertNotEqual(ba.voice_id, dev.voice_id)


class TestBuildFunctions(unittest.TestCase):
    def test_build_tts_without_key_returns_stub(self):
        import os
        old = os.environ.pop("ELEVENLABS_API_KEY", None)
        try:
            from bridge.speech import build_tts
            tts = build_tts()
            self.assertIsInstance(tts, StubTTS)
        finally:
            if old is not None:
                os.environ["ELEVENLABS_API_KEY"] = old

    def test_build_stt_without_key_returns_stub(self):
        import os
        old_gemini = os.environ.pop("GEMINI_API_KEY", None)
        old_openai = os.environ.pop("OPENAI_API_KEY", None)
        try:
            from bridge.speech import build_stt
            stt = build_stt()
            self.assertIsInstance(stt, StubSTT)
        finally:
            if old_gemini is not None:
                os.environ["GEMINI_API_KEY"] = old_gemini
            if old_openai is not None:
                os.environ["OPENAI_API_KEY"] = old_openai

    def test_build_stt_uses_openai_when_only_openai_key_exists(self):
        import os

        old_gemini = os.environ.pop("GEMINI_API_KEY", None)
        old_openai = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "test-openai-key"
        try:
            from bridge.speech import build_stt

            stt = build_stt()
            self.assertIsInstance(stt, OpenAISTT)
        finally:
            if old_gemini is not None:
                os.environ["GEMINI_API_KEY"] = old_gemini
            if old_openai is not None:
                os.environ["OPENAI_API_KEY"] = old_openai
            else:
                os.environ.pop("OPENAI_API_KEY", None)


if __name__ == "__main__":
    unittest.main()
