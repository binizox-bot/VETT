# match_0079 — Commentary Build Plan

**Northbay** | 268/8 (50.0 Overs) vs 200/10 (42.3 Overs) | 68 runs | POM: 

**Numeric Whitelist:** 0,1,2,3,4,8,10,11,12,17,18,42,50,68,195,200,262,268

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 11w+1nb+2b+4lb=18 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+18=268 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 22→39→39→127→219→229→247→267 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 268−200=68 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 12w+0nb+4b+1lb=17 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 |  — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [not_applicable] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 268−2(B)−4(LB)=262 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 200−4(B)−1(LB)=195 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 92 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (18 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]