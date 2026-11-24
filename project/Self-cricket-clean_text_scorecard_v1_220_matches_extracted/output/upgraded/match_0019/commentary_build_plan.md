# match_0019 — Commentary Build Plan

**** | 282/9 (42.0 Overs) vs 43/6 (9.3 Overs) | None no_result | POM: 
**NO RESULT** — margin/POM traps not_applicable

**Numeric Whitelist:** 0,1,2,3,6,8,9,12,42,43,279,282

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 8w+1nb+1b+2lb=12 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+12=282 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 73→81→85→197→232→234→242→271→279 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠9→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 282, achieved 43/6 | Closing paragraph — result margin calculation | D2 [not_applicable] [not_applicable: No Result] |
| 6 | 1w+0nb+0b+0lb=1 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 |  — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [not_applicable] [not_applicable: No Result] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 282−1(B)−2(LB)=279 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 43−0(B)−0(LB)=43 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 112 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (12 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]
- No Result handling: [OK] (traps 5,7 not_applicable)