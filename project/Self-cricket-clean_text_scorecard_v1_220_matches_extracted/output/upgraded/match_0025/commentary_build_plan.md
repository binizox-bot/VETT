# match_0025 — Commentary Build Plan

**Harbor A Women** | 64/6 (9.0 Overs) vs 57/5 (9.0 Overs) | 7 runs | POM: Elena Frost

**Numeric Whitelist:** 0,1,3,4,5,6,7,8,9,56,57,62,64

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+1nb+1b+1lb=8 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+8=64 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 6→10→17→21→30→52 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠6→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 64−57=7 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 3w+0nb+1b+0lb=4 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Elena Frost — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 64−1(B)−1(LB)=62 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 57−1(B)−0(LB)=56 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 22 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]