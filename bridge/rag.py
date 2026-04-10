from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Chunk:
    id: str
    label: str
    text: str
    vector: List[float] = field(default_factory=list)


class VectorStore:
    """Simple in-memory vector store using Gemini embeddings."""

    def __init__(self) -> None:
        self._chunks: List[Chunk] = []
        self._client = None
        self._model = "gemini-embedding-001"

    def _get_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        return self._client

    def _embed(self, texts: List[str]) -> List[List[float]]:
        client = self._get_client()
        # Batch embed — API supports up to 100 at once
        result = client.models.embed_content(
            model=self._model,
            contents=texts,
        )
        return [e.values for e in result.embeddings]

    def add_chunks(self, chunks: List[Chunk]) -> None:
        """Embed and store chunks. Skip if already populated."""
        if self._chunks:
            return

        texts = [c.text for c in chunks]
        vectors = self._embed(texts)
        for chunk, vec in zip(chunks, vectors):
            chunk.vector = vec
            self._chunks.append(chunk)

    def query(self, question: str, top_k: int = 5) -> List[Chunk]:
        """Return the top_k most relevant chunks for the question."""
        if not self._chunks:
            return []

        q_vec = self._embed([question])[0]
        scored = []
        for chunk in self._chunks:
            score = _cosine_similarity(q_vec, chunk.vector)
            scored.append((score, chunk))

        scored.sort(key=lambda x: -x[0])
        return [chunk for _, chunk in scored[:top_k]]

    @property
    def size(self) -> int:
        return len(self._chunks)


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def build_chunks_from_scenario(scenario) -> List[Chunk]:
    """Split scenario data into embeddable chunks."""
    chunks = []

    # Business requirements — split by section
    for i, section in enumerate(scenario.business_requirements.split("\n\n")):
        section = section.strip()
        if section and len(section) > 30:
            chunks.append(Chunk(
                id=f"biz-{i}",
                label="Business Requirements",
                text=section,
            ))

    # Repo files — one chunk per file
    for path, content in scenario.repo_files.items():
        chunks.append(Chunk(
            id=f"repo-{path}",
            label=f"Repository: {path}",
            text=f"File: {path}\n{content[:2000]}",
        ))

    # Technical documentation — as one chunk
    if scenario.technical_documentation:
        chunks.append(Chunk(
            id="tech-doc",
            label="Technical Documentation",
            text=scenario.technical_documentation[:2000],
        ))

    # Jira tickets — one per ticket
    for t in scenario.jira_tickets:
        chunks.append(Chunk(
            id=f"jira-{t.key}",
            label=f"Jira: {t.key}",
            text=f"{t.key}: {t.title}\nStatus: {t.status} | Priority: {t.priority}\n{t.description[:1000]}",
        ))

    # Stakeholder communications
    if scenario.stakeholder_comms:
        chunks.append(Chunk(
            id="stakeholder-comms",
            label="Stakeholder Communications",
            text=scenario.stakeholder_comms,
        ))

    # Additional comms
    for i, comm in enumerate(scenario.additional_comms):
        chunks.append(Chunk(
            id=f"comms-{i}",
            label="Additional Communication",
            text=comm,
        ))

    # Persona conflicts
    if scenario.persona_conflicts:
        chunks.append(Chunk(
            id="persona-conflicts",
            label="Persona Conflicts",
            text=scenario.persona_conflicts,
        ))

    # Persona details — one per persona
    for name, detail in scenario.persona_details.items():
        chunks.append(Chunk(
            id=f"persona-{name}",
            label=f"Persona: {name}",
            text=detail,
        ))

    return chunks


def build_context_from_chunks(
    chunks: List[Chunk],
    persona_instructions: str = "",
) -> str:
    """Build a compact context string from retrieved chunks."""
    sections = []
    for chunk in chunks:
        sections.append(f"[{chunk.label}]\n{chunk.text}")
    return "\n\n---\n\n".join(sections)
