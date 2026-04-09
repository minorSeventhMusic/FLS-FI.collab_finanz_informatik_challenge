"""
Loan Calculator v1.0 – Banking Hackathon Edition

Currently supports:
  - Monthly payment calculation

"""

import math


# ── Core Calculation ─────────────────────────────────────────────────────────


def calculate_monthly_payment(loan_amount, loan_duration_months, annual_interest_rate):
    """Calculate the monthly payment for a loan.

    Formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]

    Args:
        loan_amount:          Total loan amount in € (must be > 0)
        loan_duration_months: Loan duration in months (must be > 0, integer)
        annual_interest_rate: Annual interest rate in % (must be > 0)

    Returns:
        dict with monthly_payment, total_payment, total_interest
    """
    if loan_amount <= 0:
        raise ValueError("loan_amount must be greater than 0")
    if loan_duration_months <= 0:
        raise ValueError("loan_duration_months must be greater than 0")
    if annual_interest_rate <= 0:
        raise ValueError("annual_interest_rate must be greater than 0")

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


def main():
    print("\n🏦 LOAN CALCULATOR v1.0\n")

    while True:
        print("  [1] Calculate monthly payment")
        print("  [2] Calculate loan term (not yet implemented)")
        print("  [q] Quit\n")

        choice = input("Choice: ").strip().lower()

        if choice == "1":
            try:
                amount = float(input("  Loan amount (€): "))
                months = int(input("  Duration (months): "))
                rate = float(input("  Annual interest rate (%): "))

                result = calculate_monthly_payment(amount, months, rate)

                print(f"\n  Monthly payment: € {result['monthly_payment']:,.2f}")
                print(f"  Total payment:   € {result['total_payment']:,.2f}")
                print(f"  Total interest:  € {result['total_interest']:,.2f}\n")

            except (ValueError, TypeError) as e:
                print(f"\n  ⚠ Error: {e}\n")

        elif choice == "2":
            print("\n  ⚠ Not yet implemented. See BUSINESS_REQUIREMENT.md\n")

        elif choice == "q":
            print("Goodbye! 👋\n")
            break

        else:
            print("\n  ⚠ Invalid choice.\n")


if __name__ == "__main__":
    main()
