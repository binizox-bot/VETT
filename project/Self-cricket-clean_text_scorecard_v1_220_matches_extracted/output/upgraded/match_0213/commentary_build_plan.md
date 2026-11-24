# match_0213 — Commentary Build Plan

**Harborfield CC** | 272/8 (50.0 Overs) vs 114/10 (34.2 Overs) | 158 runs | POM: Elias Grant

**Numeric Whitelist:** 0,1,2,3,8,10,11,21,27,34,50,111,114,158,268,272

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 21w+2nb+1b+3lb=27 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+27=272 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 20→51→105→212→236→252→264→271 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 272−114=158 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 8w+0nb+2b+1lb=11 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Elias Grant — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 272−1(B)−3(LB)=268 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 114−2(B)−1(LB)=111 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 107 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]