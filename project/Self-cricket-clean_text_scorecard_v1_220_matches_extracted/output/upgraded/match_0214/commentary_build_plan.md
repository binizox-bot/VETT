# match_0214 — Commentary Build Plan

**Valleygate CC** | 74/10 (24.5 Overs) vs 76/3 (10.2 Overs) | 7 wickets | POM: Mason Hale

**Numeric Whitelist:** 0,1,2,3,5,6,7,9,10,12,24,72,74,75,76

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 9w+1nb+1b+1lb=12 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+12=74 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 8→15→15→19→41→44→64→69→72→74 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 74, achieved 76/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+0nb+0b+1lb=6 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Mason Hale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 74−1(B)−1(LB)=72 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 76−0(B)−1(LB)=75 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 22 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]