# match_0198 — Commentary Build Plan

**Westhaven** | 38/10 (21.3 Overs) vs 39/2 (5.2 Overs) | 8 wickets | POM: Miles Carter (Westhaven)

**Numeric Whitelist:** 0,1,2,3,4,5,8,10,15,21,33,38,39

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 10w+0nb+4b+1lb=15 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+15=38 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 1→4→10→14→15→15→22→27→36→38 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 38, achieved 39/2 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+1b+0lb=5 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Miles Carter (Westhaven) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 38−4(B)−1(LB)=33 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 39−1(B)−0(LB)=38 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 9 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]