# match_0075 — Commentary Build Plan

**** | 246/9 (50.0 Overs) vs 116/6 (22.2 Overs) | None no_result | POM: 
**NO RESULT** — margin/POM traps not_applicable

**Numeric Whitelist:** 0,1,2,6,9,20,22,24,50,115,116,243,246

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 20w+1nb+1b+2lb=24 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+24=246 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 78→81→111→113→195→202→214→216→224 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠9→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 246, achieved 116/6 | Closing paragraph — result margin calculation | D2 [not_applicable] [not_applicable: No Result] |
| 6 | 6w+2nb+0b+1lb=9 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 |  — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [not_applicable] [not_applicable: No Result] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 246−1(B)−2(LB)=243 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 116−0(B)−1(LB)=115 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 82 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]
- No Result handling: [OK] (traps 5,7 not_applicable)