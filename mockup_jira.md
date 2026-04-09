Based on the **Technical Constraints** section of the documentation, here is a mock JIRA ticket for a critical missing feature: the handling of 0% interest rate loans.

---

### **JIRA-104: Handle Division by Zero for 0% Interest Rate Loans**

**Status:** To Do
**Priority:** High
**Component:** Core Logic / `calculator.py`
**Reporter:** Gemini (AI Collaborator)

#### **Description**
Currently, the `calculate_monthly_payment` function requires the `annual_interest_rate` to be greater than 0. If a user attempts to input a 0% interest rate (e.g., for a promotional "Interest-Free" banking product), the current mathematical formula will result in a **division by zero error** because the denominator $(1+r)^n - 1$ becomes zero. 

The application needs to be updated to handle 0% interest scenarios using a simple linear division ($Principal / Months$) instead of the amortization formula.

#### **Current Constraints**
* Function currently raises a `ValueError` if `annual_interest_rate <= 0`.
* Documentation explicitly identifies "Division by Zero" as a known technical constraint.

#### **Proposed Implementation**
Modify the logic in `calculate_monthly_payment` to include a conditional check:
1.  **If interest rate > 0:** Use the existing amortization formula.
2.  **If interest rate == 0:** Calculate `monthly_payment = loan_amount / loan_duration_months`.

#### **Acceptance Criteria**
* [ ] Remove the `ValueError` restriction for an interest rate of exactly 0.
* [ ] Ensure `total_interest` returns `0.00` for 0% loans.
* [ ] Verify the CLI correctly displays results for a €10,000 loan over 10 months at 0% (Result: €1,000/mo).
* [ ] Update the **Technical Constraints** section in `documentation.md` to reflect that 0% interest is now supported.