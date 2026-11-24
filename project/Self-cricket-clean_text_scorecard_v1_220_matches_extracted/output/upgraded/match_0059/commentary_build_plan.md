# match_0059 — Commentary Build Plan

**Northmoor** | 255/8 (50.0 Overs) vs 218/8 (43.0 Overs) | 22 runs | POM: Harvey Dean

**Numeric Whitelist:** 0,1,2,3,4,8,18,20,22,24,26,43,50,211,218,252,255

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 20w+1nb+1b+2lb=24 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+24=255 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 9→91→109→136→146→154→197→241 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 255−218=22 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 18w+1nb+4b+3lb=26 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Harvey Dean — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 255−1(B)−2(LB)=252 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 218−4(B)−3(LB)=211 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 82 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]