# match_0108 — Commentary Build Plan

**Bayview Royals Women** | 219/2 (20.0 Overs) vs 55/10 (16.5 Overs) | 164 runs | POM: Nora Vale

**Numeric Whitelist:** 0,1,2,3,5,7,8,10,12,16,18,20,54,55,164,216,219

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 12w+3nb+1b+2lb=18 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+18=219 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 164→195 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 1≠2→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 219−55=164 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+0nb+1b+0lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Nora Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 219−1(B)−2(LB)=216 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 55−1(B)−0(LB)=54 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 164 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]