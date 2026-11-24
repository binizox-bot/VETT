# match_0121 — Commentary Build Plan

**Duneford** | 181/4 (20.0 Overs) vs 178/8 (20.0 Overs) | 3 runs | POM: Evan Vale

**Numeric Whitelist:** 0,1,3,4,7,8,11,20,175,178,179,181

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 4w+1nb+1b+1lb=7 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+7=181 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 29→96→145→173 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 4≠4→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 181−178=3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+1nb+0b+3lb=11 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Evan Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 181−1(B)−1(LB)=179 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 178−0(B)−3(LB)=175 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 67 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (12 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]