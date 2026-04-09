from __future__ import annotations

import json
from typing import Any, Dict, List

from bridge.llm import LLMClient
from bridge.models import AlignmentResult, DiscrepancyItem
from bridge.prompts.alignment import ALIGNMENT_ANALYSIS_PROMPT


ALIGNMENT_SYSTEM = (
    "You are a meticulous alignment analyst. Respond only with valid JSON, no markdown fences."
)


def analyze_alignment(assembled_context: str, llm: LLMClient) -> AlignmentResult:
    prompt = ALIGNMENT_ANALYSIS_PROMPT.format(assembled_context=assembled_context)
    raw = llm.generate(ALIGNMENT_SYSTEM, prompt)
    result = _parse_alignment_json(raw)
    return _normalize_score(result)


def _parse_alignment_json(raw: str) -> AlignmentResult:
    # Strip markdown code fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return AlignmentResult(
            discrepancies=[],
            overall_score=50,
            summary="Alignment analysis inconclusive — could not parse LLM response.",
        )

    discrepancies = []
    for d in data.get("discrepancies", []):
        discrepancies.append(DiscrepancyItem(
            id=d.get("id", "?"),
            severity=d.get("severity", "medium"),
            category=d.get("category", "unknown"),
            description=d.get("description", ""),
            evidence_sources=d.get("evidence_sources", []),
            business_impact=d.get("business_impact", ""),
            technical_detail=d.get("technical_detail", ""),
        ))

    return AlignmentResult(
        discrepancies=discrepancies,
        overall_score=max(0, min(100, data.get("score", 50))),
        summary=data.get("summary", ""),
    )


def _normalize_score(result: AlignmentResult) -> AlignmentResult:
    has_critical = any(d.severity == "critical" for d in result.discrepancies)
    if has_critical and result.overall_score > 60:
        result.overall_score = 60

    # Check for the "catch the lie" pattern: comms claim live + code rejects
    for d in result.discrepancies:
        if d.severity == "critical" and "code_vs_comms" in d.category:
            if result.overall_score > 35:
                result.overall_score = 35
            break

    return result
