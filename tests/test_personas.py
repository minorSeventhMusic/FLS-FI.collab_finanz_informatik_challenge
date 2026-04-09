from __future__ import annotations

import unittest

from bridge.models import Role
from bridge.personas import PERSONAS, get_persona


class TestPersonas(unittest.TestCase):
    def test_all_roles_have_config(self):
        for role in Role:
            config = get_persona(role)
            self.assertTrue(config.display_name)
            self.assertTrue(config.system_instructions)

    def test_ba_hides_raw_code(self):
        config = get_persona(Role.BUSINESS_ANALYST)
        self.assertIn("raw_code", config.hidden_doc_types)

    def test_dev_sees_raw_code(self):
        config = get_persona(Role.DEVELOPER)
        self.assertIn("raw_code", config.visible_doc_types)

    def test_persona_instructions_differ(self):
        ba = get_persona(Role.BUSINESS_ANALYST)
        dev = get_persona(Role.DEVELOPER)
        self.assertNotEqual(ba.system_instructions, dev.system_instructions)

    def test_all_seven_roles_present(self):
        self.assertEqual(len(Role), 7)
        self.assertEqual(len(PERSONAS), 7)

    def test_non_technical_roles_hide_code(self):
        for r in [Role.PRODUCT_MANAGER, Role.COMPLIANCE_OFFICER,
                   Role.MARKETING_MANAGER, Role.UX_DESIGNER]:
            config = get_persona(r)
            self.assertIn("raw_code", config.hidden_doc_types,
                          f"{r.value} should hide raw_code")

    def test_all_personas_have_voice_id(self):
        for role in Role:
            config = get_persona(role)
            self.assertTrue(config.voice_id, f"{role.value} missing voice_id")


if __name__ == "__main__":
    unittest.main()
