# match_0132 — Commentary Build Plan

**Aurora XI** | 82/7 (8.0 Overs) vs 84/5 (7.5 Overs) | 5 wickets | POM: Milan Marsh

**Numeric Whitelist:** 0,1,4,5,6,7,8,81,82,83,84

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 4w+1nb+0b+1lb=6 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+6=82 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 10→23→31→62→65→75→82 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠7→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 82, achieved 84/5 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+1nb+1b+0lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Milan Marsh — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 82−0(B)−1(LB)=81 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 84−1(B)−0(LB)=83 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 31 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (11 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]