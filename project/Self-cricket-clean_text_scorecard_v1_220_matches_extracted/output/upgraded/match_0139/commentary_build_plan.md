# match_0139 — Commentary Build Plan

**Harborview XI** | 196/5 (20.0 Overs) vs 147/9 (20.0 Overs) | 49 runs | POM: Rohan Vale

**Numeric Whitelist:** 0,1,2,4,5,7,8,9,20,49,145,147,193,196

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 4w+1nb+1b+2lb=8 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+8=196 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 82→124→175→182→192 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 4≠5→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 196−147=49 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+0nb+0b+2lb=9 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Rohan Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 196−1(B)−2(LB)=193 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 147−0(B)−2(LB)=145 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 82 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]