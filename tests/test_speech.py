from __future__ import annotations

import unittest

from bridge.models import Role
from bridge.personas import get_persona
from bridge.speech import (
    StubSTT,
    StubTTS,
    get_voice_id,
    VOICE_MAP,
)


class TestSpeechStubs(unittest.TestCase):
    def test_stub_tts_returns_empty_bytes(self):
        tts = StubTTS()
        result = tts.synthesize("Hello world", "some-voice-id")
        self.assertEqual(result, b"")

    def test_stub_stt_returns_fallback_text(self):
        stt = StubSTT()
        result = stt.transcribe(b"fake audio data")
        self.assertIn("unavailable", result.lower())

    def test_stub_stt_accepts_mime_type(self):
        stt = StubSTT()
        result = stt.transcribe(b"fake audio data", mime_type="audio/webm")
        self.assertIn("unavailable", result.lower())

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

    def test_build_stt_without_keys_returns_stub(self):
        import os
        old_el = os.environ.pop("ELEVENLABS_API_KEY", None)
        old_gem = os.environ.pop("GEMINI_API_KEY", None)
        try:
            from bridge.speech import build_stt
            stt = build_stt()
            self.assertIsInstance(stt, StubSTT)
        finally:
            if old_el is not None:
                os.environ["ELEVENLABS_API_KEY"] = old_el
            if old_gem is not None:
                os.environ["GEMINI_API_KEY"] = old_gem


if __name__ == "__main__":
    unittest.main()
