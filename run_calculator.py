#!/usr/bin/env python3
"""Interactive loan calculator with error logging"""

import json
import traceback
from datetime import datetime
from pathlib import Path
from calculator import calculate_monthly_payment

def log_error(error_type, error_message, inputs):
    """Log error to error_log.json for the agent to monitor."""
    print(f"DEBUG: log_error called with: {error_type}, {error_message}, {inputs}")
    log_file = Path(__file__).parent / "error_log.json"
    print(f"DEBUG: log_file path: {log_file}")
    
    error_entry = {
        "timestamp": datetime.now().isoformat(),
        "error_type": error_type,
        "error_message": error_message,
        "inputs": inputs
    }
    print(f"DEBUG: error_entry: {error_entry}")
    
    try:
        # Read existing logs if file exists
        if log_file.exists():
            with open(log_file, "r") as f:
                logs = json.load(f)
            print(f"DEBUG: Read existing logs: {logs}")
        else:
            logs = []
            print("DEBUG: No existing log file, starting fresh")
        
        # Add new error
        logs.append(error_entry)
        print(f"DEBUG: Added error, logs now: {logs}")
        
        # Write back to file
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
        print(f"DEBUG: Wrote to file {log_file}")
    except Exception as e:
        print(f"Warning: Could not log error: {e}")
        print(f"DEBUG: Exception in log_error: {e}")

print("=" * 50)
print("LOAN PAYMENT CALCULATOR")
print("=" * 50)

# Collect inputs safely
inputs = {}
try:
    loan_amount = float(input("\nEnter loan amount (€): "))
    inputs["loan_amount"] = loan_amount
    
    months = int(input("Enter loan duration (months): "))
    inputs["loan_duration_months"] = months
    
    interest_rate = float(input("Enter annual interest rate (%): "))
    inputs["annual_interest_rate"] = interest_rate
    
    # Now try to calculate
    result = calculate_monthly_payment(loan_amount, months, interest_rate)
    
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Monthly Payment: €{result['monthly_payment']}")
    print(f"Total Payment: €{result['total_payment']}")
    print(f"Total Interest: €{result['total_interest']}")
    print("=" * 50)
    
except ValueError as e:
    error_message = str(e)
    print(f"\n⚠ Error: {error_message}")
    print(f"DEBUG: About to log error with inputs: {inputs}")
    log_error("ValueError", error_message, inputs)
    print("DEBUG: Error logged")
except Exception as e:
    error_message = str(e)
    print(f"\n⚠ Unexpected error: {error_message}")
    print(f"DEBUG: About to log exception with inputs: {inputs}")
    log_error(type(e).__name__, error_message, inputs)
    print("DEBUG: Exception logged")
