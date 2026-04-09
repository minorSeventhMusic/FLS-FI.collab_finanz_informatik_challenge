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


if __name__ == "__main__":
    unittest.main()
