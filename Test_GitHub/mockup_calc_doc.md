# Technical Documentation: Loan Calculator v1.0

## 1. System Overview
The **Loan Calculator** is a Python-based command-line interface (CLI) application designed to facilitate basic banking calculations. It specifically allows users to calculate monthly loan installments, total repayment amounts, and total interest paid over the life of a loan using standard amortization logic.

## 2. Mathematical Model
The application utilizes the standard formula for calculating a fixed-rate monthly payment:

$$M = P \frac{r(1+r)^n}{(1+r)^n - 1}$$

### Variable Definitions:
* **M**: Monthly payment
* **P**: Principal loan amount
* **r**: Monthly interest rate (Annual Rate / 12 / 100)
* **n**: Total number of payments (loan duration in months)

## 3. Component Analysis

### 3.1. Core Logic: `calculate_monthly_payment`
This function serves as the calculation engine. It takes three numerical inputs and returns a structured dictionary of results.

**Function Signature:**
`calculate_monthly_payment(loan_amount, loan_duration_months, annual_interest_rate)`

**Input Validation:**
The function performs strict validation to ensure financial integrity:
* `loan_amount` must be > 0.
* `loan_duration_months` must be > 0.
* `annual_interest_rate` must be > 0.

**Return Object:**
A dictionary containing:
* `monthly_payment`: The amount due each month.
* `total_payment`: The sum of all payments over the term.
* `total_interest`: The cost of borrowing (Total - Principal).

### 3.2. User Interface: `main()`
The `main()` function implements a loop-based CLI menu.

* **Execution Flow:** The program displays a menu and waits for user input.
* **Choice [1]:** Prompts for loan details, executes the calculation, and prints a formatted summary.
* **Choice [2]:** Reserved for future functionality (Loan Term calculation).
* **Choice [q]:** Terminates the program execution.
* **Error Handling:** Uses a `try-except` block to catch `ValueError` or `TypeError`, ensuring that invalid user inputs (like alphabetic characters in numeric fields) do not crash the script.

## 4. Execution Example
**Inputs:**
- Loan Amount: €10,000
- Duration: 12 months
- Interest Rate: 5%

**Output:**
```text
Monthly payment: € 856.07
Total payment:   € 10,272.84
Total interest:  € 272.84