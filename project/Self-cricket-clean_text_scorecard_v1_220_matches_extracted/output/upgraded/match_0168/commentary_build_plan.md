# match_0168 — Commentary Build Plan

**Harbor Hawks** | 174/10 (46.2 Overs) vs 177/3 (24.5 Overs) | 7 wickets | POM: Noah Drake (Harbor Hawks)

**Numeric Whitelist:** 0,1,2,3,4,5,7,10,14,16,19,20,24,46,170,172,174,177

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 16w+0nb+3b+1lb=20 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+20=174 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 67→79→79→100→109→117→149→155→162→174 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 174, achieved 177/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 14w+0nb+4b+1lb=19 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Noah Drake (Harbor Hawks) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 174−3(B)−1(LB)=170 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 177−4(B)−1(LB)=172 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 67 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (18 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]