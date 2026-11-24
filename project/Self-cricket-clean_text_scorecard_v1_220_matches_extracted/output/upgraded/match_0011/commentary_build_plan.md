# match_0011 — Commentary Build Plan

**Harborstone XI** | 282/8 (50.0 Overs) vs 132/6 (30.0 Overs) | 47 runs | POM: Owen Vale

**Numeric Whitelist:** 0,1,2,3,6,8,11,13,16,30,47,50,129,132,279,282

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 13w+0nb+1b+2lb=16 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+16=282 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 7→23→85→109→186→218→265→273 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 282−132=47 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 8w+0nb+0b+3lb=11 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Owen Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 282−1(B)−2(LB)=279 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 132−0(B)−3(LB)=129 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 77 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]