# match_0047 — Commentary Build Plan

**Ridgefield** | 337/8 (50.0 Overs) vs 222/10 (41.2 Overs) | 115 runs | POM: Marcus Ward

**Numeric Whitelist:** 0,1,2,3,4,5,7,8,10,11,15,18,41,50,115,214,222,331,337

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 11w+1nb+4b+2lb=18 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+18=337 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 116→134→182→192→203→303→315→324 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 337−222=115 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+0nb+3b+5lb=15 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Marcus Ward — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 337−4(B)−2(LB)=331 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 222−3(B)−5(LB)=214 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 116 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (19 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]