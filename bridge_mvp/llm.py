from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol


class LLMClient(Protocol):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        ...


@dataclass
class StubLLMClient:
    """Deterministic local fallback for demo and tests."""

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        marker = "Draft response:"
        if marker in user_prompt:
            return user_prompt.split(marker, 1)[1].strip()
        return f"{system_prompt}\n\n{user_prompt}"


class OpenAIChatLLMClient:
    def __init__(self) -> None:
        from openai import OpenAI  # type: ignore

        self._model = os.getenv("OPENAI_MODEL", "gpt-5.4")
        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.responses.create(
            model=self._model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.output_text


def build_llm_client() -> LLMClient:
    if os.getenv("OPENAI_API_KEY"):
        return OpenAIChatLLMClient()
    return StubLLMClient()
