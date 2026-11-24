# match_0068 — Commentary Build Plan

**Northbridge** | 331/7 (50.0 Overs) vs 45/10 (20.2 Overs) | 286 runs | POM: Caleb Sutton

**Numeric Whitelist:** 0,1,2,4,5,7,10,19,20,24,44,45,50,286,328,331

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 19w+2nb+1b+2lb=24 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+24=331 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 76→254→254→269→303→316→328 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠7→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 331−45=286 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+0b+1lb=5 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Caleb Sutton — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 331−1(B)−2(LB)=328 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 45−0(B)−1(LB)=44 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 178 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]