from __future__ import annotations

import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv() -> bool:
        return False

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4")
STATE_FILE = os.getenv("BRIDGE_STATE_FILE", "project_state.json")
DEFAULT_SCENARIO = "calculator_0_apr"
MAX_CONTEXT_CHARS = 12000
MAX_CONVERSATION_HISTORY_TURNS = 10
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
