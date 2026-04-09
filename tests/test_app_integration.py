from __future__ import annotations

from streamlit.testing.v1 import AppTest


def test_chat_page_renders_without_errors():
    app = AppTest.from_file("pages/1_Chat.py")
    app.run(timeout=15)
    assert not app.exception


def test_chat_page_has_role_selector():
    app = AppTest.from_file("pages/1_Chat.py")
    app.run(timeout=15)
    assert "Business Analyst" in app.selectbox[0].value


def test_role_switch_to_developer():
    app = AppTest.from_file("pages/1_Chat.py")
    app.run(timeout=15)
    app.selectbox[0].set_value("Anna Fischer (Developer)").run(timeout=15)
    assert "Developer" in app.selectbox[0].value


def test_role_switch_to_persona():
    app = AppTest.from_file("pages/1_Chat.py")
    app.run(timeout=15)
    app.selectbox[0].set_value("Daniel Schneider (Product Manager)").run(timeout=15)
    assert app.selectbox[0].value == "Daniel Schneider (Product Manager)"


def test_dashboard_renders_without_errors():
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


def test_landing_page_renders_without_errors():
    app = AppTest.from_file("FI.collab.py")
    app.run(timeout=20)
    assert not app.exception
