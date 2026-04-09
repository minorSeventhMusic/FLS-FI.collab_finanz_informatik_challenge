from __future__ import annotations

from streamlit.testing.v1 import AppTest


def test_chat_page_renders_without_errors():
    app = AppTest.from_file("pages/1_Chat.py")
    app.run(timeout=15)
    assert not app.exception


def test_chat_page_has_role_selector():
    app = AppTest.from_file("pages/1_Chat.py")
    app.run(timeout=15)
    assert app.radio[0].value == "Business Analyst"


def test_role_switch_to_developer():
    app = AppTest.from_file("pages/1_Chat.py")
    app.run(timeout=15)
    app.radio[0].set_value("Developer").run(timeout=15)
    assert app.radio[0].value == "Developer"


def test_dashboard_renders_without_errors():
    # Dashboard runs alignment analysis on load which calls LLM.
    # Skip in CI — covered by unit tests for alignment + persistence.
    import os
    if os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"):
        import pytest
        pytest.skip("Dashboard integration test skipped when LLM API key is set (makes live calls)")
    app = AppTest.from_file("pages/2_Dashboard.py")
    app.run(timeout=30)
    assert not app.exception


def test_reports_page_renders_without_errors():
    app = AppTest.from_file("pages/3_Reports.py")
    app.run(timeout=15)
    assert not app.exception
