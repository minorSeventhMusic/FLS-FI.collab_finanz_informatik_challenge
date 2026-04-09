Project Documentation: "FlexiLoan" Retail Engine
1. Executive Summary

FlexiLoan is a customer-facing digital tool designed to acquire new borrowers by providing instant, transparent loan quotes. It serves as the primary "Top-of-Funnel" lead generation asset for the bank’s personal lending division.

2. Market Trends & Challenges

Trend: "Price to Beat" Logic. Customers in 2026 use aggregators. The calculator must show "Competitive Comparison" metrics to prevent site abandonment.

Challenge: Rate Volatility. Central bank rates are fluctuating. The code must fetch the latest LPR (Loan Prime Rate) via API every 24 hours to ensure quotes are legally accurate.

3. Legal & Regulatory Requirements (Crucial)

Truth in Lending (TILA/Reg Z): You cannot just show a "Monthly Payment." You must display the APR (Annual Percentage Rate), which includes origination fees.

GDPR/CCPA: If the user enters a phone number to "Save Quote," the system must capture an explicit, time-stamped consent log.

Fair Lending Act: The algorithm must be "blind" to protected classes (Age, Gender, Race) to avoid biased pricing.

4. Technical Requirements (The IT Project Specs)

A. Calculation Engine (The Code Logic)

The tool must calculate a Total Cost of Credit (TCC).

B. API & Integration

Credit Bureau Soft-Pull: Integration with a credit API (e.g., Experian) to provide a "Personalized Rate" without impacting the user's credit score.

CRM Sync: Successful "Quotes" must push data to Salesforce for follow-up by the lending team.

5. Human Statistics (Target Market Profile)

Who is using this calculator?

Segment,Age Range,Household Profile,Goal
The Debt Consolidator,35–50,"Married, 2+ Children",Lowering monthly outgoings by merging credit card debts.
The Modern Starter,22–30,Single / No Children,"Financing tech, travel, or small home upgrades."
The Home Improver,40–60,Homeowners,Calculating ROI on solar panels or renovations.

6. UI/UX Design Requirements

"Visual Anchor": A large, dynamic donut chart showing the split between Principal Paid and Interest Paid.

Trust Signals: Badges from "Norton Secured" or "FCA Regulated" must be visible near the "Calculate" button.

Mobile Responsiveness: 70% of traffic is expected from mobile devices; the "Slider" inputs must be thumb-friendly.

7. Success Metrics (KPIs)

Conversion Rate: % of users who click "Apply Now" after calculating.

Drop-off Point: At which field (Amount? Term? Credit Score?) do users leave the page?

Calculation Accuracy: 0% variance between the calculator estimate and the final loan contract.
