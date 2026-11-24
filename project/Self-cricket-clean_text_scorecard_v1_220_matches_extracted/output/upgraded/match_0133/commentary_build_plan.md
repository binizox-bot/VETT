# match_0133 — Commentary Build Plan

**Aurora XI** | 82/7 (8.0 Overs) vs 84/5 (7.5 Overs) | 5 wickets | POM: Milan Marsh

**Numeric Whitelist:** 0,1,3,4,5,7,8,82,83,84

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 3w+1nb+0b+0lb=4 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+4=82 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 9→17→39→68→73→74→82 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠7→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 82, achieved 84/5 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+1nb+1b+0lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Milan Marsh — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 82−0(B)−0(LB)=82 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 84−1(B)−0(LB)=83 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 29 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (10 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]