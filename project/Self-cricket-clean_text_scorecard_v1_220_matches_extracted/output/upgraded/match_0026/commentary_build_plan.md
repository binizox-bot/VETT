# match_0026 — Commentary Build Plan

**Ridgeport** | 251/4 (31.0 Overs) vs 33/10 (17.5 Overs) | 218 runs | POM: Nathan Wells

**Numeric Whitelist:** 0,1,3,4,5,10,12,13,17,19,24,31,33,218,249,251

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 19w+3nb+1b+1lb=24 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+24=251 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 29→179→230→242 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 4≠4→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 251−33=218 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 12w+1nb+0b+0lb=13 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Nathan Wells — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 251−1(B)−1(LB)=249 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 33−0(B)−0(LB)=33 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 150 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]