# match_0211 — Commentary Build Plan

**Cedarbridge Falcons** | 304/8 (50.0 Overs) vs 72/10 (29.3 Overs) | 232 runs | POM: Ethan Vale

**Numeric Whitelist:** 0,1,2,3,5,7,8,10,20,26,29,50,70,72,232,300,304

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 20w+2nb+1b+3lb=26 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+26=304 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 22→35→151→190→257→277→288→294 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 304−72=232 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+0nb+1b+1lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Ethan Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 304−1(B)−3(LB)=300 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 72−1(B)−1(LB)=70 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 116 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]