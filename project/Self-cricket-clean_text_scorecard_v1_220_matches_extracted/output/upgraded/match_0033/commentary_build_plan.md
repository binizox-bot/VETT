# match_0033 — Commentary Build Plan

**Harborline** | 262/5 (35.0 Overs) vs 71/10 (25.4 Overs) | 191 runs | POM: Ethan Clarke

**Numeric Whitelist:** 0,1,2,3,4,5,10,14,20,22,25,28,35,65,71,191,259,262

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 22w+3nb+2b+1lb=28 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+28=262 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 139→214→246→251→255 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠5→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 262−71=191 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 14w+0nb+4b+2lb=20 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Ethan Clarke — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 262−2(B)−1(LB)=259 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 71−4(B)−2(LB)=65 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 139 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (18 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]