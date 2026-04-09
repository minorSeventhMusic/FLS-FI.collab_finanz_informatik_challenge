"""
Loan Calculator v1.0 – Banking Hackathon Edition

Currently supports:
  - Monthly payment calculation

"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# ── Core Calculation ─────────────────────────────────────────────────────────


def calculate_monthly_payment(loan_amount, loan_duration_months, annual_interest_rate):
    """Calculate the monthly payment for a loan.

    Formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]

    Args:
        loan_amount:          Total loan amount in € (must be > 0)
        loan_duration_months: Loan duration in months (must be > 0, integer)
        annual_interest_rate: Annual interest rate in % (must be > 0 and <= 15)

    Returns:
        dict with monthly_payment, total_payment, total_interest
    """
    if loan_amount <= 0:
        raise ValueError("loan_amount must be greater than 0")
    if loan_duration_months <= 0:
        raise ValueError("loan_duration_months must be greater than 0")
    if annual_interest_rate <= 0:
        raise ValueError("annual_interest_rate must be greater than 0")
    if annual_interest_rate > 15:
        raise ValueError("annual_interest_rate must be less than or equal to 15")

    monthly_rate = annual_interest_rate / 12 / 100

    numerator = monthly_rate * (1 + monthly_rate) ** loan_duration_months
    denominator = (1 + monthly_rate) ** loan_duration_months - 1
    monthly_payment = loan_amount * (numerator / denominator)

    total_payment = monthly_payment * loan_duration_months
    total_interest = total_payment - loan_amount

    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
    }


# ── CLI ──────────────────────────────────────────────────────────────────────


def _log_error_for_agent(error_type, error_message, inputs):
    """Append one runtime error entry to error_log.json."""
    log_file = Path(__file__).parent / "error_log.json"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "error_type": error_type,
        "error_message": error_message,
        "inputs": inputs,
    }

    try:
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
            if not isinstance(logs, list):
                logs = []
        else:
            logs = []

        logs.append(entry)
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
    except Exception as log_exc:
        print(f"  ⚠ Could not write error log: {log_exc}")


def _trigger_error_analysis_agent():
    """Run mockup_agent.py in one-shot mode so error handling happens automatically."""
    agent_file = Path(__file__).parent / "mockup_agent.py"
    if not agent_file.exists():
        print("  ⚠ Agent file not found: mockup_agent.py")
        return

    log_file = Path(__file__).parent / "error_log.json"
    latest_error = "unknown error"
    try:
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
            if isinstance(logs, list) and logs:
                latest_error = logs[-1].get("error_message", latest_error)
    except Exception:
        pass

    try:
        result = subprocess.run(
            [sys.executable, str(agent_file), "--auto-error", latest_error],
            cwd=str(Path(__file__).parent),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

        if result.returncode != 0:
            print("  ⚠ Agent run failed. Check mockup_agent.py output.")
            return

        # Keep calculator UX compact, but indicate automatic handling happened.
        if "jira title:" in result.stdout.lower() or "customer update" in result.stdout.lower():
            print("  ✓ Agent handled the error automatically.")
        else:
            print("  ⚠ Agent ran, but no analysis confirmation was found.")
    except Exception as run_exc:
        print(f"  ⚠ Could not run error analysis agent: {run_exc}")


def main():
    print("\n🏦 LOAN CALCULATOR v1.0\n")

    while True:
        print("  [1] Calculate monthly payment")
        print("  [2] Calculate loan term (not yet implemented)")
        print("  [q] Quit\n")

        choice = input("Choice: ").strip().lower()

        if choice == "1":
            inputs = {}
            try:
                amount = float(input("  Loan amount (€): "))
                inputs["loan_amount"] = amount
                months = int(input("  Duration (months): "))
                inputs["loan_duration_months"] = months
                rate = float(input("  Annual interest rate (%): "))
                inputs["annual_interest_rate"] = rate

                result = calculate_monthly_payment(amount, months, rate)

                print(f"\n  Monthly payment: € {result['monthly_payment']:,.2f}")
                print(f"  Total payment:   € {result['total_payment']:,.2f}")
                print(f"  Total interest:  € {result['total_interest']:,.2f}\n")

            except (ValueError, TypeError) as e:
                print(f"\n  ⚠ Error: {e}\n")
                _log_error_for_agent(type(e).__name__, str(e), inputs)
                _trigger_error_analysis_agent()

        elif choice == "2":
            print("\n  ⚠ Not yet implemented. See BUSINESS_REQUIREMENT.md\n")

        elif choice == "q":
            print("Goodbye! 👋\n")
            break

        else:
            print("\n  ⚠ Invalid choice.\n")


if __name__ == "__main__":
    main()
