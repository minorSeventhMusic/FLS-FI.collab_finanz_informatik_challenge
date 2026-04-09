from streamlit.testing.v1 import AppTest


def test_app_renders_without_errors():
    app = AppTest.from_file("app.py")
    app.run(timeout=10)

    assert not app.exception
    assert app.title[0].value == "Ticket Copilot Demo"
    assert app.radio[0].value == "Business Analyst"

    markdown_values = "\n".join(node.value for node in app.markdown)
    assert "User : Business Analyst" in markdown_values


def test_role_switch_updates_sidebar_role_label():
    app = AppTest.from_file("app.py")
    app.run(timeout=10)

    app.radio[0].set_value("Developer").run(timeout=10)

    updated_markdown = "\n".join(node.value for node in app.markdown)
    assert app.radio[0].value == "Developer"
    assert "User : Developer" in updated_markdown
