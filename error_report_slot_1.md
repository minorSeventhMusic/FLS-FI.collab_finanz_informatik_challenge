# 🤖 Error Analysis Report

**Slot**: 1/3 (Overwrites oldest)
**Generated at**: 2026-04-09 18:14:47

## 🧠 AI Analysis
Analysis could not be completed due to API/model error.

Captured exception: Gemini analysis failed for all models: 404 models/gemini-pro is not found for API version v1beta, or is not supported for generateContent. Call ListModels to see the list of available models and their supported methods.

## 🛠 Captured Errors
### Suite_1 (Negative loan)
- **Type**: ValueError
- **Message**: loan_amount must be greater than 0

### Suite_2 (Zero duration)
- **Type**: ValueError
- **Message**: loan_duration_months must be greater than 0

### Suite_3 (Rate too high)
- **Type**: ValueError
- **Message**: annual_interest_rate must be less than or equal to 15

