# match_0178 — Commentary Build Plan

**Shoreline Rangers** | 282/10 (47.2 Overs) vs 74/10 (24.4 Overs) | 208 runs | POM: Aaron Miles (Shoreline Rangers)

**Numeric Whitelist:** 0,1,2,3,4,10,12,16,17,21,24,47,71,74,208,279,282

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 17w+1nb+2b+1lb=21 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+21=282 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 62→62→138→144→169→184→252→258→265→282 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 282−74=208 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 12w+1nb+0b+3lb=16 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Aaron Miles (Shoreline Rangers) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 282−2(B)−1(LB)=279 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 74−0(B)−3(LB)=71 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 76 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]