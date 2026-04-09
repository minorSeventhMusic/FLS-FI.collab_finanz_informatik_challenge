"""
Error Analysis Agent
1. Runs calculator.py test suite
2. Analyzes errors via Gemini API
3. Persists reports to rotating slots (max 3 files)
"""

import os
import sys
import traceback
import json
from datetime import datetime
from pathlib import Path
import google.generativeai as genai

# Configuration
MAX_GENERATED_REPORTS = 3

def load_api_key():
    """Load Google API key from .env file."""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        raise FileNotFoundError(".env file not found. Please create one with GOOGLE_API_KEY=your_key")
    
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("GOOGLE_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise ValueError("GOOGLE_API_KEY not found in .env")

def load_errors_from_log():
    """Load errors from error_log.json."""
    log_file = Path(__file__).parent / "error_log.json"
    if not log_file.exists():
        return []
    
    try:
        with open(log_file, "r") as f:
            log_entries = json.load(f)
        
        errors = []
        for i, entry in enumerate(log_entries, 1):
            errors.append({
                "test_case": f"User_Log_{i}",
                "error_type": entry.get("error_type", "Unknown"),
                "error_message": entry.get("error_message", ""),
                "inputs": entry.get("inputs", {}),
            })
        return errors
    except Exception:
        return []

def capture_calculator_errors():
    """Import calculator and run test suite."""
    errors = []
    try:
        import calculator
        test_cases = [
            {"loan_amount": -1000, "loan_duration_months": 12, "annual_interest_rate": 5, "desc": "Negative loan"},
            {"loan_amount": 50000, "loan_duration_months": 0, "annual_interest_rate": 5, "desc": "Zero duration"},
            {"loan_amount": 50000, "loan_duration_months": 12, "annual_interest_rate": 25, "desc": "Rate too high"},
        ]
        
        for i, test in enumerate(test_cases):
            desc = test.pop("desc")
            try:
                calculator.calculate_monthly_payment(**test)
            except Exception as e:
                errors.append({
                    "test_case": f"Suite_{i+1} ({desc})",
                    "inputs": test,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                })
    except ImportError:
        errors.append({"test_case": "System", "error_type": "ImportError", "error_message": "calculator.py not found", "inputs": {}})
    return errors

def analyze_errors_with_gemini(api_key, errors):
    """Analyze the combined batch of errors with Gemini."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
    
    summary = "\n".join([f"- {e['test_case']}: {e['error_type']} ({e['error_message']})" for e in errors])
    prompt = f"Analyze these Python calculator errors and suggest fixes:\n\n{summary}"
    
    response = model.generate_content(prompt)
    return response.text

def write_report_markdown(analysis_text, errors):
    """Persist error report to rotating slots (max 3 files)."""
    # 1. Logic to determine the next slot
    # We check the directory for existing files to 'remember' the count between runs
    output_dir = Path(__file__).parent
    existing_slots = list(output_dir.glob("error_report_slot_*.md"))
    
    # Use function attribute to track counter, initialized by existing file count
    if not hasattr(write_report_markdown, "_counter"):
        write_report_markdown._counter = len(existing_slots)

    counter = write_report_markdown._counter
    slot = (counter % MAX_GENERATED_REPORTS) + 1
    write_report_markdown._counter = counter + 1

    # 2. Prepare File Path and Content
    ticket_file = output_dir / f"error_report_slot_{slot}.md"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format individual error entries for the markdown
    error_section = ""
    for err in errors:
        error_section += f"### {err['test_case']}\n- **Type**: {err['error_type']}\n- **Message**: {err['error_message']}\n\n"

    markdown_content = (
        f"# 🤖 Error Analysis Report\n\n"
        f"**Slot**: {slot}/{MAX_GENERATED_REPORTS} (Overwrites oldest)\n"
        f"**Generated at**: {generated_at}\n\n"
        "## 🧠 AI Analysis\n"
        f"{analysis_text}\n\n"
        "## 🛠 Captured Errors\n"
        f"{error_section}"
    )

    # 3. Write/Overwrite the slot
    ticket_file.write_text(markdown_content, encoding="utf-8")
    return ticket_file

def main():
    print("\n" + "="*40)
    print("🤖 STARTING ERROR ANALYSIS AGENT")
    print("="*40)

    try:
        key = load_api_key()
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Gather Errors
    logged = load_errors_from_log()
    suite = capture_calculator_errors()
    all_errors = logged + suite

    # Clear JSON log if it exists
    log_file = Path(__file__).parent / "error_log.json"
    if log_file.exists():
        log_file.unlink()

    if not all_errors:
        print("✓ No errors found to analyze.")
    else:
        print(f"🔍 Found {len(all_errors)} issues. Requesting AI analysis...")
        try:
            analysis = analyze_errors_with_gemini(key, all_errors)
            
            # Use the rotating slot logic to save the report
            report_path = write_report_markdown(analysis, all_errors)
            
            print(f"✓ Success! Report saved to: {report_path.name}")
        except Exception as e:
            print(f"✗ Analysis failed: {e}")

    print("="*40)
    print("🎉 Run Complete. Check slot files for details.")

    # Cleanup: Delete all error report files after program ends
    output_dir = Path(__file__).parent
    for report_file in output_dir.glob("error_report_slot_*.md"):
        report_file.unlink()
        print(f"🗑 Cleaned up: {report_file.name}")

if __name__ == "__main__":
    main()