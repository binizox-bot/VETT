# match_0055 — Commentary Build Plan

**Eastford** | 81/10 (30.5 Overs) vs 82/3 (14.3 Overs) | 7 wickets | POM: Gavin Stone

**Numeric Whitelist:** 0,1,2,3,5,7,10,14,16,17,30,78,81,82

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 14w+0nb+1b+2lb=17 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+17=81 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 5→17→21→23→29→44→69→78→81→81 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 81, achieved 82/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 14w+1nb+0b+1lb=16 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Gavin Stone — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 81−1(B)−2(LB)=78 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 82−0(B)−1(LB)=81 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 25 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]