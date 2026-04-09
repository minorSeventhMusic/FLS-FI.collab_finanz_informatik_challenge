import importlib
import os

from calculator import calculate_monthly_payment


def build_agent():
    """Build an ADK agent using the currently installed SDK version."""
    try:
        agent_class = importlib.import_module("google.adk").Agent
    except ImportError:
        return None, "Missing dependency: google.adk (pip install google-adk)"

    model_name = os.getenv("ADK_MODEL", "gemini-2.0-flash")
    try:
        agent = agent_class(
            name="PromotionChecker",
            model=model_name,
            instruction=(
                "You are a helpful banking assistant. "
                "Use the calculate_monthly_payment tool for any math. "
                "If the user asks for 0 percent interest, verify with the tool."
            ),
            tools=[calculate_monthly_payment],
        )
        return agent, None
    except Exception as exc:
        return None, f"Failed to initialize ADK agent: {exc}"


def run_local_cli():
    """Fallback calculator mode that always works without external services."""
    print("Running local calculator mode.")
    while True:
        choice = input("Type 'calc' to calculate or 'q' to quit: ").strip().lower()
        if choice == "q":
            print("Goodbye")
            break
        if choice != "calc":
            print("Invalid choice")
            continue

        try:
            amount = float(input("Loan amount: ").strip())
            months = int(input("Duration in months: ").strip())
            rate = float(input("Annual interest rate in percent: ").strip())
            result = calculate_monthly_payment(amount, months, rate)
            print(f"Monthly payment: {result['monthly_payment']:.2f}")
            print(f"Total payment: {result['total_payment']:.2f}")
            print(f"Total interest: {result['total_interest']:.2f}")
        except (ValueError, TypeError) as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    loan_bot, error = build_agent()

    if loan_bot is None:
        print(error)
        print("Falling back to local mode.")
    else:
        print("ADK agent initialized successfully.")
        print("For this mockup script, local mode is used for terminal interaction.")

    run_local_cli()