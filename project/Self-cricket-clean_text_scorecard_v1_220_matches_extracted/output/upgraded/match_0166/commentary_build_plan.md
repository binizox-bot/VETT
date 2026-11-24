# match_0166 — Commentary Build Plan

**** | 91/9 (20.0 Overs) vs 32/0 (3.2 Overs) | None no_result | POM: 
**NO RESULT** — margin/POM traps not_applicable

**Numeric Whitelist:** 0,1,2,3,4,9,11,15,20,32,88,91

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 11w+1nb+2b+1lb=15 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+15=91 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 9→38→55→58→60→66→79→81→91 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠9→3 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 91, achieved 32/0 | Closing paragraph — result margin calculation | D2 [not_applicable] [not_applicable: No Result] |
| 6 | 4w+0nb+0b+0lb=4 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 |  — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [not_applicable] [not_applicable: No Result] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 91−2(B)−1(LB)=88 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 32−0(B)−0(LB)=32 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 29 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (12 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]
- No Result handling: [OK] (traps 5,7 not_applicable)