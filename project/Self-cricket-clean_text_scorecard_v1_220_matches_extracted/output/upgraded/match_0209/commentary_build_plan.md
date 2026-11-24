# match_0209 — Commentary Build Plan

**Ridgefield** | 306/8 (50.0 Overs) vs 74/10 (29.3 Overs) | 232 runs | POM: Lucas Bennett

**Numeric Whitelist:** 0,1,2,3,4,5,7,8,10,21,28,29,50,72,74,232,301,306

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 21w+2nb+1b+4lb=28 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+28=306 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 15→24→96→172→264→277→302→302 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 306−74=232 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+0nb+1b+1lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Lucas Bennett — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 306−1(B)−4(LB)=301 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 74−1(B)−1(LB)=72 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 92 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (18 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]