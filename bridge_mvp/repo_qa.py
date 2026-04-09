from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

from bridge_mvp.types import Role, ScenarioBundle


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "what",
    "does",
    "about",
    "from",
    "into",
    "have",
    "will",
    "would",
    "should",
    "there",
    "here",
    "your",
    "show",
    "tell",
}


@dataclass(frozen=True)
class RepoAnswer:
    answer: str
    relevant_files: List[str]


def _tokens(text: str) -> List[str]:
    return [
        token
        for token in re.findall(r"[a-zA-Z_]{3,}", text.lower())
        if token not in STOPWORDS
    ]


def select_relevant_files(question: str, repo_files: Dict[str, str]) -> List[str]:
    q_tokens = set(_tokens(question))
    scores = []
    for path, content in repo_files.items():
        haystack = f"{path} {content.lower()}"
        score = sum(1 for token in q_tokens if token in haystack)
        scores.append((score, path))
    scores.sort(key=lambda item: (-item[0], item[1]))
    chosen = [path for score, path in scores if score > 0][:3]
    if not chosen:
        chosen = ["READMEcalc.md", "calculator.py"]
    return chosen


def build_repo_answer(role: Role, question: str, scenario: ScenarioBundle) -> RepoAnswer:
    lowered = question.lower()
    files = select_relevant_files(question, scenario.repo_files)

    if any(token in lowered for token in ("run", "start", "launch", "cli")):
        answer = (
            "The loan calculator repo is a Python CLI app. The entry point is `calculator.py`, and "
            "the README says to start it with `python calculator.py`. In the menu, option `1` calculates "
            "monthly payment, option `2` is reserved for loan-term calculation and is not implemented yet, "
            "and `q` exits."
        )
        return RepoAnswer(answer=answer, relevant_files=["READMEcalc.md", "calculator.py"])

    if any(token in lowered for token in ("formula", "monthly payment", "calculate", "calculation", "amortization")):
        answer = (
            "The core calculation lives in `calculate_monthly_payment` in `calculator.py`. It uses the "
            "standard amortization formula with `monthly_rate = annual_interest_rate / 12 / 100`, then "
            "returns `monthly_payment`, `total_payment`, and `total_interest` rounded to two decimals."
        )
        return RepoAnswer(answer=answer, relevant_files=["calculator.py", "mockup_calc_doc.md"])

    if any(token in lowered for token in ("validate", "validation", "error", "invalid", "negative", "zero duration")):
        answer = (
            "Input validation is strict in `calculator.py`: `loan_amount` must be greater than 0, "
            "`loan_duration_months` must be greater than 0, and `annual_interest_rate` must be greater than 0. "
            "Invalid values raise `ValueError`, and the CLI catches `ValueError` and `TypeError` so bad input "
            "does not crash the program."
        )
        return RepoAnswer(answer=answer, relevant_files=["calculator.py", "mockup_calc_doc.md"])

    if any(token in lowered for token in ("test", "coverage", "covered", "assert")):
        answer = (
            "The current tests cover several repayment cases and some validation behavior. In `test_calculator.py` "
            "there are checks for standard, small, and large loans, plus assertions that negative rates raise. "
            "The remote test file does not yet cover 0% interest handling."
        )
        return RepoAnswer(answer=answer, relevant_files=["test_calculator.py", "calculator.py"])

    if any(token in lowered for token in ("0%", "0 percent", "zero interest", "zero rate")):
        answer = (
            "Right now the codebase does not support 0% interest loans. In `calculator.py`, "
            "`annual_interest_rate <= 0` raises `ValueError`, so a promotional 0% loan is rejected before any "
            "special-case calculation can happen."
        )
        return RepoAnswer(answer=answer, relevant_files=["calculator.py", "test_calculator.py"])

    if any(token in lowered for token in ("repo", "overview", "what does", "support", "features")):
        if role == Role.BUSINESS_ANALYST:
            answer = (
                "The current repo is a narrow MVP for loan repayment estimates. It supports one implemented user "
                "journey: entering amount, duration, and interest rate to get monthly payment, total repayment, "
                "and total interest. Loan-term calculation is mentioned in the menu but not implemented."
            )
        else:
            answer = (
                "The repo is a small Python CLI app centered on `calculate_monthly_payment` in `calculator.py`. "
                "It exposes a loop-based menu in `main()`, supports monthly-payment calculation, and leaves "
                "loan-term calculation as a placeholder."
            )
        return RepoAnswer(answer=answer, relevant_files=["READMEcalc.md", "calculator.py", "mockup_calc_doc.md"])

    if role == Role.BUSINESS_ANALYST:
        answer = (
            "Based on the current calculator repo, the implemented capability is basic monthly loan estimation. "
            "The strongest evidence is in `calculator.py` and the technical doc: the app calculates monthly payment, "
            "total payment, and total interest, while more advanced product behavior is not present yet."
        )
    else:
        answer = (
            "From the current repo snapshot, the main implementation is a single calculation path in `calculator.py` "
            "plus a CLI wrapper and a small test module. The most relevant files for your question are "
            + ", ".join(files)
            + "."
        )
    return RepoAnswer(answer=answer, relevant_files=files)
