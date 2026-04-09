#!/usr/bin/env python3
"""Interactive loan calculator"""

from calculator import calculate_monthly_payment

print("=" * 50)
print("LOAN PAYMENT CALCULATOR")
print("=" * 50)

try:
    loan_amount = float(input("\nEnter loan amount (€): "))
    months = int(input("Enter loan duration (months): "))
    interest_rate = float(input("Enter annual interest rate (%): "))
    
    result = calculate_monthly_payment(loan_amount, months, interest_rate)
    
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Monthly Payment: €{result['monthly_payment']}")
    print(f"Total Payment: €{result['total_payment']}")
    print(f"Total Interest: €{result['total_interest']}")
    print("=" * 50)
    
except ValueError as e:
    print(f"\nError: {e}")
except Exception as e:
    print(f"\nUnexpected error: {e}")
