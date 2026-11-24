# match_0112 — Commentary Build Plan

**Cresthaven Women** | 184/4 (20.0 Overs) vs 60/10 (16.2 Overs) | 124 runs | POM: Rowan Vale

**Numeric Whitelist:** 0,1,2,4,7,8,10,15,16,19,20,59,60,124,182,184

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 15w+2nb+1b+1lb=19 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+19=184 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 30→65→150→152 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 4≠4→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 184−60=124 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+0nb+1b+0lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Rowan Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 184−1(B)−1(LB)=182 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 60−1(B)−0(LB)=59 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 85 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]