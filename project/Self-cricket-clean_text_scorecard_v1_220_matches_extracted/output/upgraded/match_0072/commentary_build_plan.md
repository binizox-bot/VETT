# match_0072 — Commentary Build Plan

**Northbank** | 290/8 (50.0 Overs) vs 188/10 (28.4 Overs) | 23 runs | POM: Ethan Cross

**Numeric Whitelist:** 0,1,2,3,4,6,8,10,11,18,23,28,50,186,188,285,290

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 11w+2nb+2b+3lb=18 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+18=290 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 21→23→148→201→259→269→276→289 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 290−188=23 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+1b+1lb=6 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Ethan Cross — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 290−2(B)−3(LB)=285 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 188−1(B)−1(LB)=186 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 125 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]