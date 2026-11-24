# match_0183 — Commentary Build Plan

**Seabrook** | 306/7 (50.0 Overs) vs 101/10 (38.2 Overs) | 205 runs | POM: Oliver Kent (Seabrook)

**Numeric Whitelist:** 0,1,2,3,4,7,10,22,23,28,32,38,50,94,101,205,303,306

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 22w+3nb+1b+2lb=28 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+28=306 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 37→191→213→227→255→287→302 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠7→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 306−101=205 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 23w+2nb+3b+4lb=32 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Oliver Kent (Seabrook) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 306−1(B)−2(LB)=303 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 101−3(B)−4(LB)=94 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 154 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (18 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]