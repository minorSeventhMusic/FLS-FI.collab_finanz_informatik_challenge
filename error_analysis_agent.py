"""
Error Analysis Agent

This agent:
1. Attempts to run calculator.py and capture any errors
2. Uses Google Gemini API to analyze the error
3. Generates a detailed markdown report with insights and recommendations
"""

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
import google.generativeai as genai


def load_api_key():
    """Load Google API key from .env file."""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        raise FileNotFoundError(".env file not found")
    
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("GOOGLE_API_KEY="):
                key = line.split("=", 1)[1].strip()
                return key
    
    raise ValueError("GOOGLE_API_KEY not found in .env")


def capture_calculator_errors():
    """Attempt to run calculator.py and capture any errors."""
    errors = []
    
    try:
        # Import calculator module
        import calculator
        
        # Test basic functionality - comprehensive test suite
        test_cases = [
            # Valid case
            {"loan_amount": 100000, "loan_duration_months": 360, "annual_interest_rate": 5, "desc": "Valid loan (€100k, 360 months, 5%)"},
            # Invalid loan amount cases
            {"loan_amount": -1000, "loan_duration_months": 12, "annual_interest_rate": 5, "desc": "Negative loan amount"},
            {"loan_amount": 0, "loan_duration_months": 12, "annual_interest_rate": 5, "desc": "Zero loan amount"},
            # Invalid duration cases
            {"loan_amount": 50000, "loan_duration_months": 0, "annual_interest_rate": 5, "desc": "Zero loan duration"},
            {"loan_amount": 50000, "loan_duration_months": -12, "annual_interest_rate": 5, "desc": "Negative loan duration"},
            # Invalid interest rate cases
            {"loan_amount": 50000, "loan_duration_months": 12, "annual_interest_rate": 0, "desc": "Zero interest rate"},
            {"loan_amount": 50000, "loan_duration_months": 12, "annual_interest_rate": -5, "desc": "Negative interest rate"},
            {"loan_amount": 50000, "loan_duration_months": 12, "annual_interest_rate": 20, "desc": "Interest rate above 15%"},
            {"loan_amount": 50000, "loan_duration_months": 12, "annual_interest_rate": 25, "desc": "Interest rate way above limit"},
        ]
        
        for i, test_case in enumerate(test_cases):
            desc = test_case.pop("desc", f"Test {i+1}")
            try:
                result = calculator.calculate_monthly_payment(**test_case)
                print(f"✓ {desc}: {result}")
            except ValueError as e:
                error_info = {
                    "test_case": i + 1,
                    "description": desc,
                    "inputs": test_case,
                    "error_type": "ValueError",
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                }
                errors.append(error_info)
                print(f"✗ {desc}: {str(e)}")
            except Exception as e:
                error_info = {
                    "test_case": i + 1,
                    "description": desc,
                    "inputs": test_case,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                }
                errors.append(error_info)
                print(f"✗ {desc}: {str(e)}")
    
    except Exception as e:
        error_info = {
            "test_case": "import",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc()
        }
        errors.append(error_info)
        print(f"✗ Import error: {str(e)}")
    
    return errors


def analyze_errors_with_gemini(api_key, errors):
    """Use Google Gemini API to analyze the errors."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
    
    error_summary = "\n".join([
        f"**Error {e['test_case']}**: {e['error_type']}\n"
        f"Message: {e['error_message']}\n"
        f"Inputs: {e['inputs']}"
        for e in errors
    ])
    
    prompt = f"""Analyze the following errors from a loan calculator Python module:

{error_summary}

Please provide:
1. A brief explanation of each error
2. Root cause analysis
3. Impact assessment
4. Recommended fixes
5. Best practices to prevent similar errors

Format your response as detailed markdown."""
    
    response = model.generate_content(prompt)
    return response.text


def create_error_report(errors, analysis):
    """Create a markdown error report."""
    report = f"""# Error Analysis Report - calculator.py

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

Total Errors Found: {len(errors)}

## Error Details

"""
    
    for i, error in enumerate(errors, 1):
        report += f"""### Error {i}: {error['error_type']}
**Test**: {error.get('description', 'N/A')}

**Input**: 
```json
{error['inputs']}
```

**Error Message**: 
```
{error['error_message']}
```

---

"""
    
    report += """## AI Analysis

""" + analysis + """

## Next Steps

1. Review the errors found above
2. Implement fixes to calculator.py
3. Add comprehensive input validation
4. Expand test coverage
5. Document edge cases
"""
    
    return report


def main():
    """Main execution flow."""
    print("\n" + "="*60)
    print("🤖 ERROR ANALYSIS AGENT")
    print("="*60)
    print()
    
    # Load API key
    print("📋 Step 1: Loading API key from .env...")
    try:
        api_key = load_api_key()
        print("✓ API key loaded successfully\n")
    except Exception as e:
        print(f"✗ Failed to load API key: {e}\n")
        return
    
    # Capture errors
    print("🔍 Step 2: Scanning calculator.py for errors...")
    print("-" * 60)
    errors = capture_calculator_errors()
    print("-" * 60)
    print()
    
    if not errors:
        print("✓ No errors found in calculator.py")
        report_content = "# Error Analysis Report\n\nNo errors were detected in calculator.py during testing."
    else:
        print(f"✓ Found {len(errors)} error(s)\n")
        
        # Analyze with Gemini
        print("🧠 Step 3: Analyzing errors with Google Gemini AI...")
        try:
            analysis = analyze_errors_with_gemini(api_key, errors)
            print("✓ Analysis complete\n")
        except Exception as e:
            print(f"⚠ Analysis skipped: {e}\n")
            analysis = "Analysis could not be completed due to API error."
        
        # Create report
        report_content = create_error_report(errors, analysis)
    
    # Write report
    output_path = Path(__file__).parent / "error_analysis_report.md"
    with open(output_path, "w") as f:
        f.write(report_content)
    
    print(f"📄 Step 4: Report generated")
    print(f"✓ Location: {output_path}")
    print()
    print("="*60)
    print("🎉 Error Analysis Complete!")
    print("="*60)
    print()


if __name__ == "__main__":
    main()
