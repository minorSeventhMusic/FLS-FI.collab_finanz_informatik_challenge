import importlib
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from calculator import calculate_monthly_payment

APP_NAME = "fls_bridge_challenge"
USER_ID = "local_user"


def _now_in_app_timezone():
    """Return current datetime in configured app timezone (default Europe/Berlin)."""
    tz_name = os.getenv("APP_TIMEZONE", "Europe/Berlin")
    try:
        return datetime.now(ZoneInfo(tz_name))
    except Exception:
        # Fallback to system local time if timezone configuration is invalid.
        return datetime.now().astimezone()


def _write_ticket_markdown(ticket_text, error_text):
    """Write one Jira ticket, capping total files at 3 by overwriting the oldest."""
    now = _now_in_app_timezone()
    generated_at = now.strftime("%Y-%m-%d-%H%M")
    timestamp_for_name = generated_at

    base_dir = Path(__file__).parent
    existing = sorted(
        base_dir.glob("jira_ticket_*.md"),
        key=lambda p: p.stat().st_mtime,
    )

    # Keep at most 3 files total: create new if under limit, else replace oldest.
    if len(existing) < 3:
        ticket_file = base_dir / f"jira_ticket_{timestamp_for_name}.md"
    else:
        oldest = existing[0]
        try:
            oldest.unlink()
        except OSError:
            pass
        ticket_file = base_dir / f"jira_ticket_{timestamp_for_name}.md"

    content = (
        "# Jira Ticket\n\n"
        f"- Generated at: {generated_at}\n"
        f"- Source error: {error_text}\n\n"
        "## Jira Content\n\n"
        "```text\n"
        f"{ticket_text.strip()}\n"
        "```\n"
    )
    ticket_file.write_text(content, encoding="utf-8")
    return ticket_file


def _write_fix_summary_markdown(ticket_text, customer_message, ticket_path, error_text):
    """Create an easy-language summary markdown from Jira acceptance criteria."""
    criteria = _extract_acceptance_criteria(ticket_text)
    subject = _extract_jira_title(ticket_text)
    suffix = ticket_path.stem.replace("jira_ticket_", "")
    base_dir = Path(__file__).parent
    existing = sorted(
        base_dir.glob("fix_summary_*.md"),
        key=lambda p: p.stat().st_mtime,
    )

    # Keep at most 3 summary files total: create new if under limit, else overwrite oldest.
    if len(existing) < 3:
        summary_file = base_dir / f"fix_summary_{suffix}.md"
    else:
        summary_file = existing[0]

    criteria_lines = "\n".join(f"- {item}" for item in criteria) if criteria else "- No acceptance criteria found"
    message_body = customer_message.strip().removeprefix("Short customer update:\n").strip()

    content = (
        f"# {subject}\n\n"
        "## Error Description\n\n"
        f"- {error_text}\n\n"
        f"{message_body}\n\n"
        "## What Was Fixed\n\n"
        f"{criteria_lines}\n"
    )
    summary_file.write_text(content, encoding="utf-8")
    return summary_file


def _extract_jira_title(ticket_text):
    """Extract Jira title line from ticket text and return only the title value."""
    for raw_line in ticket_text.splitlines():
        line = raw_line.strip()
        if line.lower().startswith("jira title:"):
            return line.split(":", 1)[1].strip() or "Fix Summary"
    return "Fix Summary"

def _load_calculator_source():
    """Load calculator source for issue analysis."""
    calculator_file = Path(__file__).with_name("calculator.py")
    return calculator_file.read_text(encoding="utf-8")


def _extract_validation_rules(source_text):
    """Extract ValueError validation rules from calculator source code."""
    rules = []
    lines = source_text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if stripped.startswith("if ") and stripped.endswith(":"):
            condition = stripped[3:-1].strip()
            message = None
            i += 1

            while i < len(lines):
                block_line = lines[i]
                block_stripped = block_line.lstrip()
                block_indent = len(block_line) - len(block_stripped)

                # End of this if-block.
                if block_stripped and block_indent <= indent:
                    break

                match = re.search(r'error_message\s*=\s*"([^"]+)"', block_line)
                if match:
                    message = match.group(1).strip()

                i += 1

            if message:
                rules.append({"condition": condition, "message": message})
            continue

        i += 1

    return rules


def _find_rule_for_error(error_text, rules):
    """Find a matching validation rule by exact ValueError message."""
    for rule in rules:
        if rule["message"] == error_text.strip():
            return rule
    return None


def _analyze_calculator_for_issue(source_text, error_text):
    """Derive structured findings relevant to the observed runtime error."""
    findings = []
    rules = _extract_validation_rules(source_text)
    matched_rule = _find_rule_for_error(error_text, rules)

    if "def calculate_monthly_payment" in source_text:
        findings.append("Issue located in calculate_monthly_payment in calculator.py")

    findings.append(f"Found {len(rules)} ValueError validation rule(s) in source")

    if matched_rule:
        findings.append(
            f"Matched validation rule: if {matched_rule['condition']} -> ValueError('{matched_rule['message']}')"
        )
    else:
        findings.append("No exact validation rule matched the observed error message")

    return findings


def _build_issue_details(error_text, source_text):
    """Build dynamic Jira details based on matching validation rule in source code."""
    rules = _extract_validation_rules(source_text)
    matched_rule = _find_rule_for_error(error_text, rules)

    if matched_rule:
        field = matched_rule["message"].split(" ", 1)[0]
        condition = matched_rule["condition"]
        message = matched_rule["message"]

        return {
            "title": f"Validation error for {field}",
            "summary": f"The calculator rejected input because the validation condition `{condition}` evaluated to True.",
            "proposed_fix": [
                f"Confirm the business rule represented by `{condition}` for `{field}`",
                f"Ensure user input guidance clearly communicates: '{message}'",
                "Add regression tests for valid, boundary, and invalid values around this rule",
            ],
            "criteria": [
                f"Inputs that satisfy `not ({condition})` are accepted",
                f"Inputs that satisfy `{condition}` are rejected with message '{message}'",
                "Automated tests cover this validation boundary and remain passing",
            ],
        }

    return {
        "title": "Runtime validation error in loan calculator",
        "summary": "The calculator raised a runtime validation error, but no exact source validation rule could be matched.",
        "proposed_fix": [
            "Review the failing input and expected business rule",
            "Align validation and user-facing guidance",
            "Add regression coverage for this failure pattern",
        ],
        "criteria": [
            "Failure can be reproduced and explained",
            "Expected behavior is implemented and documented",
            "Regression test covers the observed error",
        ],
    }


def _build_local_jira_ticket(error_text, findings, source_text):
    """Construct a Jira ticket using local analysis when ADK is unavailable."""
    issue = _build_issue_details(error_text, source_text)
    finding_lines = "\n".join(f"- {item}" for item in findings) if findings else "- No findings"
    proposed_fix_lines = "\n".join(f"- {item}" for item in issue["proposed_fix"])
    criteria_lines = "\n".join(f"- {item}" for item in issue["criteria"])

    return (
        f"JIRA Title: {issue['title']}\n"
        "Priority: High\n"
        "Component: Core Calculation\n"
        "\n"
        "Summary:\n"
        f"{issue['summary']}\n"
        "\n"
        f"Observed Error:\n- {error_text}\n"
        "\n"
        "Code Analysis Findings:\n"
        f"{finding_lines}\n"
        "\n"
        "Proposed Fix:\n"
        f"{proposed_fix_lines}\n"
        "\n"
        "Acceptance Criteria:\n"
        f"{criteria_lines}\n"
    )


def _extract_acceptance_criteria(ticket_text):
    """Extract acceptance criteria bullet points from Jira ticket text."""
    lines = ticket_text.splitlines()
    criteria = []
    in_section = False

    for raw_line in lines:
        line = raw_line.strip()
        if line == "Acceptance Criteria:":
            in_section = True
            continue
        if in_section and line.startswith("-"):
            criteria.append(line.lstrip("- ").strip())
            continue
        if in_section and line and not line.startswith("-"):
            break

    return criteria


def _build_local_customer_message(criteria, error_text):
    """Create a short, easy-language customer update from acceptance criteria."""
    return (
        "Short customer update:\n"
        f"We found this issue in our loan calculator: '{error_text}'. We fixed it."
    )


def _run_agent_prompt(agent, prompt, adk_runtime):
    """Run a one-shot prompt through an ADK agent and return text output."""
    runner = adk_runtime["Runner"](
        app_name=APP_NAME,
        agent=agent,
        session_service=adk_runtime["InMemorySessionService"](),
    )
    session = runner.session_service.create_session_sync(app_name=APP_NAME, user_id=USER_ID)
    message = adk_runtime["types"].Content(role="user", parts=[adk_runtime["types"].Part(text=prompt)])
    events = runner.run(user_id=USER_ID, session_id=session.id, new_message=message)
    return _extract_text_from_events(events)


def _extract_text_from_events(events):
    """Extract plain text from ADK event stream."""
    collected = []
    for event in events:
        content = getattr(event, "content", None)
        if content is None:
            continue
        parts = getattr(content, "parts", None) or []
        for part in parts:
            text = getattr(part, "text", None)
            if text:
                collected.append(text)
    return "\n".join(collected).strip()


def _customer_agent_from_jira_ticket(ticket_text, error_text, customer_agent=None, adk_runtime=None):
    """Create a customer-friendly explanation from Jira acceptance criteria."""
    criteria = _extract_acceptance_criteria(ticket_text)
    customer_message = None

    print("--- customer_agent Output ---")

    has_api_key = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    if customer_agent is not None and adk_runtime is not None and has_api_key:
        try:
            prompt = (
                "Write exactly this style and keep it concise: "
                "We found this issue in our loan calculator: '<error>'. We fixed it. "
                "Use the observed error text in place of <error>. "
                "No extra sentences.\n\n"
                f"Observed Error:\n- {error_text}\n\n"
                f"Acceptance Criteria:\n- "
                + "\n- ".join(criteria)
            )
            response_text = _run_agent_prompt(customer_agent, prompt, adk_runtime)
            if response_text:
                customer_message = response_text.strip()
                print(customer_message)
                print("--- End customer_agent Output ---\n")
                return customer_message
        except Exception as run_exc:
            print(f"customer_agent unavailable, using local fallback: {run_exc}")
    elif customer_agent is not None and adk_runtime is not None and not has_api_key:
        print("customer_agent skipped: no API key configured. Using local fallback.")

    customer_message = _build_local_customer_message(criteria, error_text)
    print(customer_message)
    print("--- End customer_agent Output ---\n")
    return customer_message


def jira_agent_handle_promo_error(exc, jira_agent=None, customer_agent=None, adk_runtime=None):
    """Delegate promo failure handling to Jira ticket generation."""
    print(f"Error: {exc}")

    source_text = None
    findings = []

    try:
        source_text = _load_calculator_source()
        findings = _analyze_calculator_for_issue(source_text, str(exc))
    except OSError as file_exc:
        print(f"jira_agent could not load calculator source: {file_exc}")

    print("\n--- jira_agent Output (Jira Ticket) ---")

    has_api_key = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))

    ticket_text = None

    if jira_agent is not None and adk_runtime is not None and source_text and has_api_key:
        try:
            prompt = (
                "Create a Jira ticket in plain text using this information. "
                f"Observed runtime validation error: {exc}. "
                "Analyze the calculator source and include root cause, impact, proposed fix, and acceptance criteria.\n\n"
                f"Calculator source:\n{source_text}\n\n"
                f"Precomputed findings:\n{chr(10).join(findings)}"
            )
            response_text = _run_agent_prompt(jira_agent, prompt, adk_runtime)

            if response_text:
                print(response_text)
                ticket_text = response_text
                print("--- End jira_agent Output ---\n")
        except Exception as run_exc:
            print(f"jira_agent unavailable, using local fallback: {run_exc}")
    elif jira_agent is not None and adk_runtime is not None and source_text and not has_api_key:
        print("jira_agent skipped: no API key configured. Using local fallback.")

    if not ticket_text:
        ticket_text = _build_local_jira_ticket(str(exc), findings, source_text or "")
        print(ticket_text)
        print("--- End jira_agent Output ---\n")

    ticket_path = _write_ticket_markdown(ticket_text, str(exc))
    print(f"Ticket persisted to: {ticket_path.name}\n")

    customer_message = _customer_agent_from_jira_ticket(
        ticket_text,
        str(exc),
        customer_agent=customer_agent,
        adk_runtime=adk_runtime,
    )

    summary_path = _write_fix_summary_markdown(ticket_text, customer_message, ticket_path, str(exc))
    print(f"Fix summary persisted to: {summary_path.name}\n")

    return customer_message


def build_agents():
    """Build promotion, jira, and customer ADK agents using current SDK version."""
    try:
        adk_module = importlib.import_module("google.adk")
        session_module = importlib.import_module("google.adk.sessions")
        types_module = importlib.import_module("google.genai.types")
    except ImportError:
        return None, None, None, None, "Missing dependency: google.adk (pip install google-adk)"

    model_name = os.getenv("ADK_MODEL", "gemini-2.0-flash")

    try:
        promotion_agent = adk_module.Agent(
            name="PromotionChecker",
            model=model_name,
            instruction=(
                "You are a helpful banking assistant. "
                "Use the calculate_monthly_payment tool for any math. "
                "If the user asks for 0 percent interest, still call the tool with 0 "
                "and report the exact result or error message."
            ),
            tools=[calculate_monthly_payment],
        )

        jira_agent = adk_module.Agent(
            name="JiraAgent",
            model=model_name,
            instruction=(
                "You are jira_agent. "
                "Given an observed runtime error and calculator code, create a concise Jira ticket "
                "with title, priority, root cause, impact, proposed fix, and acceptance criteria."
            ),
        )

        customer_agent = adk_module.Agent(
            name="CustomerAgent",
            model=model_name,
            instruction=(
                "You are customer_agent. "
                "Use Jira acceptance criteria to create a very short customer explanation in easy language. "
                "Clearly state the issue is fixed and avoid technical terms."
            ),
        )

        adk_runtime = {
            "Runner": adk_module.Runner,
            "InMemorySessionService": session_module.InMemorySessionService,
            "types": types_module,
        }

        return promotion_agent, jira_agent, customer_agent, adk_runtime, None
    except Exception as exc:
        return None, None, None, None, f"Failed to initialize ADK agents: {exc}"


def run_local_cli(jira_agent=None, customer_agent=None, adk_runtime=None):
    """Fallback calculator mode that always works without external services."""
    print("Running local calculator mode.")
    last_customer_message = None
    while True:
        choice = input(
            "Type 'calc', 'promo' (0 percent test), 'customer' (repeat update), or 'q' to quit: "
        ).strip().lower()
        if choice == "q":
            print("Goodbye")
            break
        if choice == "customer":
            if last_customer_message:
                print("\n--- Last customer update ---")
                print(last_customer_message)
                print("--- End last customer update ---\n")
            else:
                print("No customer update yet. Run 'promo' first.")
            continue
        if choice == "promo":
            amount = 1200.0
            months = 12
            rate = 0.0
            print(
                f"Running promo test with amount={amount:.2f}, months={months}, rate={rate:.1f}%"
            )
            try:
                print("Trying calculation with 0 percent interest...")
                result = calculate_monthly_payment(amount, months, rate)
                print(f"Monthly payment: {result['monthly_payment']:.2f}")
                print(f"Total payment: {result['total_payment']:.2f}")
                print(f"Total interest: {result['total_interest']:.2f}")
            except (ValueError, TypeError) as exc:
                last_customer_message = jira_agent_handle_promo_error(
                    exc, jira_agent, customer_agent, adk_runtime
                )
            continue
        if choice != "calc":
            print("Invalid choice")
            continue

        try:
            amount = float(input("Loan amount: ").strip())
            months = int(input("Duration in months: ").strip())
            rate = float(input("Annual interest rate in percent: ").strip())
            if rate == 0:
                print("Trying calculation with 0 percent interest...")
            result = calculate_monthly_payment(amount, months, rate)
            print(f"Monthly payment: {result['monthly_payment']:.2f}")
            print(f"Total payment: {result['total_payment']:.2f}")
            print(f"Total interest: {result['total_interest']:.2f}")
        except (ValueError, TypeError) as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    promotion_agent, jira_agent, customer_agent, adk_runtime, error = build_agents()

    if len(sys.argv) >= 3 and sys.argv[1] == "--auto-error":
        auto_error_text = " ".join(sys.argv[2:]).strip()
        jira_agent_handle_promo_error(
            Exception(auto_error_text),
            jira_agent=jira_agent,
            customer_agent=customer_agent,
            adk_runtime=adk_runtime,
        )
        sys.exit(0)

    if promotion_agent is None:
        print(error)
        print("Falling back to local mode.")
    else:
        print("ADK agents initialized successfully.")
        print("For this mockup script, local mode is used for terminal interaction.")

    run_local_cli(jira_agent=jira_agent, customer_agent=customer_agent, adk_runtime=adk_runtime)