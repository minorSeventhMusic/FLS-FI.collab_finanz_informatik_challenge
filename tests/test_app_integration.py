from __future__ import annotations

import os

import pytest
from streamlit.testing.v1 import AppTest

_SKIP_LIVE = bool(os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"))
_SKIP_REASON = "Skipped with live API (init takes ~30s for embedding + alignment)"


@pytest.mark.skipif(_SKIP_LIVE, reason=_SKIP_REASON)
def test_chat_page_renders_without_errors():
    app = AppTest.from_file("pages/1_Chat.py")
    app.run(timeout=15)
    assert not app.exception


@pytest.mark.skipif(_SKIP_LIVE, reason=_SKIP_REASON)
def test_chat_page_has_role_selector():
    app = AppTest.from_file("pages/1_Chat.py")
    app.run(timeout=15)
    assert "Business Analyst" in app.selectbox[0].value


@pytest.mark.skipif(_SKIP_LIVE, reason=_SKIP_REASON)
def test_role_switch_to_developer():
    app = AppTest.from_file("pages/1_Chat.py")
    app.run(timeout=15)
    app.selectbox[0].set_value("Anna Fischer (Developer)").run(timeout=15)
    assert "Developer" in app.selectbox[0].value


@pytest.mark.skipif(_SKIP_LIVE, reason=_SKIP_REASON)
def test_role_switch_to_persona():
    app = AppTest.from_file("pages/1_Chat.py")
    app.run(timeout=15)
    app.selectbox[0].set_value("Daniel Schneider (Product Manager)").run(timeout=15)
    assert app.selectbox[0].value == "Daniel Schneider (Product Manager)"


@pytest.mark.skipif(_SKIP_LIVE, reason=_SKIP_REASON)
def test_dashboard_renders_without_errors():
    app = AppTest.from_file("pages/2_Dashboard.py")
    app.run(timeout=30)
    assert not app.exception


def test_reports_page_renders_without_errors():
    app = AppTest.from_file("pages/3_Reports.py")
    app.run(timeout=15)
    assert not app.exception


def test_landing_page_renders_without_errors():
    app = AppTest.from_file("FI.collab.py")
    app.run(timeout=20)
    assert not app.exception
