# Error Analysis Report - calculator.py

**Generated**: 2026-04-09 16:22:05

## Summary

Total Errors Found: 3

## Error Details

### Error 1: ValueError

**Test Case Input**: 
```json
{'loan_amount': -1000, 'loan_duration_months': 12, 'annual_interest_rate': 5}
```

**Error Message**: 
```
loan_amount must be greater than 0
```

---

### Error 2: ValueError

**Test Case Input**: 
```json
{'loan_amount': 50000, 'loan_duration_months': 0, 'annual_interest_rate': 5}
```

**Error Message**: 
```
loan_duration_months must be greater than 0
```

---

### Error 3: ValueError

**Test Case Input**: 
```json
{'loan_amount': 50000, 'loan_duration_months': 12, 'annual_interest_rate': 20}
```

**Error Message**: 
```
annual_interest_rate must be less than or equal to 15
```

---

## AI Analysis

Analysis could not be completed due to API error.

## Next Steps

1. Review the recommended fixes above
2. Implement changes to calculator.py
3. Add comprehensive input validation
4. Expand test coverage
5. Document edge cases
