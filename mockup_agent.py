import importlib
import os
import sys
from pathlib import Path

from calculator import calculate_monthly_payment

APP_NAME = "fls_bridge_challenge"
USER_ID = "local_user"

def _load_calculator_source():
    """Load calculator source for issue analysis."""
    calculator_file = Path(__file__).with_name("calculator.py")
    return calculator_file.read_text(encoding="utf-8")


def _analyze_calculator_for_promo_issue(source_text):
    """Derive structured findings relevant to promo 0% failures."""
    findings = []

    if "annual_interest_rate <= 0" in source_text:
        findings.append("Input validation rejects annual_interest_rate == 0")
    if "raise ValueError(\"annual_interest_rate must be greater than 0\")" in source_text:
        findings.append("Raised error message is 'annual_interest_rate must be greater than 0'")
    if "denominator = (1 + monthly_rate) ** loan_duration_months - 1" in source_text:
        findings.append("Amortization denominator becomes zero at 0% if guard is removed")
    if "def calculate_monthly_payment" in source_text:
        findings.append("Issue located in calculate_monthly_payment in calculator.py")

    return findings


def _build_local_jira_ticket(error_text, findings):
    """Construct a Jira ticket using local analysis when ADK is unavailable."""
    finding_lines = "\n".join(f"- {item}" for item in findings) if findings else "- No findings"

    return (
        "JIRA Title: Promo 0% interest flow fails in monthly payment calculator\n"
        "Priority: High\n"
        "Component: Core Calculation\n"
        "\n"
        "Summary:\n"
        "Promo mode intentionally calls calculate_monthly_payment with 0% interest, "
        "but the calculator rejects that input and raises a ValueError.\n"
        "\n"
        f"Observed Error:\n- {error_text}\n"
        "\n"
        "Code Analysis Findings:\n"
        f"{finding_lines}\n"
        "\n"
        "Proposed Fix:\n"
        "- Update calculate_monthly_payment to support annual_interest_rate == 0 using simple division\n"
        "- Keep annual_interest_rate < 0 as invalid input\n"
        "- Add tests for 0% promotional cases\n"
        "\n"
        "Acceptance Criteria:\n"
        "- Promo path no longer raises an exception for 0%\n"
        "- 0% loans return total_interest = 0.00\n"
        "- Existing non-zero interest tests remain passing\n"
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


def _build_local_customer_message(criteria):
    """Create a short, easy-language customer update from acceptance criteria."""
    if criteria:
        return (
            "Short customer update:\n"
            "We found the issue in our loan calculator and fixed it. "
            "You can now use the promo flow without this error. "
            "0% loans are handled correctly, show 0.00 interest, and normal loan cases still work."
        )

    return (
        "Short customer update:\n"
        "We found the issue and fixed it. "
        "The promo loan flow now works as expected."
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


def _customer_agent_from_jira_ticket(ticket_text, customer_agent=None, adk_runtime=None):
    """Create a customer-friendly explanation from Jira acceptance criteria."""
    criteria = _extract_acceptance_criteria(ticket_text)
    customer_message = None

    print("--- customer_agent Output ---")

    has_api_key = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    if customer_agent is not None and adk_runtime is not None and has_api_key:
        try:
            prompt = (
                "Use these acceptance criteria to write a very short explanation in easy language "
                "for a customer. The message must clearly say the issue has been fixed. "
                "Keep it to 2-3 sentences.\n\n"
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

    customer_message = _build_local_customer_message(criteria)
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
        findings = _analyze_calculator_for_promo_issue(source_text)
    except OSError as file_exc:
        print(f"jira_agent could not load calculator source: {file_exc}")

    print("\n--- jira_agent Output (Jira Ticket) ---")

    has_api_key = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))

    ticket_text = None

    if jira_agent is not None and adk_runtime is not None and source_text and has_api_key:
        try:
            prompt = (
                "Create a Jira ticket in plain text using this information. "
                f"Observed promo error: {exc}. "
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
        ticket_text = _build_local_jira_ticket(str(exc), findings)
        print(ticket_text)
        print("--- End jira_agent Output ---\n")

    return _customer_agent_from_jira_ticket(
        ticket_text, customer_agent=customer_agent, adk_runtime=adk_runtime
    )


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