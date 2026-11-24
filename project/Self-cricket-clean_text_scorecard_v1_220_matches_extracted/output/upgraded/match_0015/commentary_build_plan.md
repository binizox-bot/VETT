# match_0015 — Commentary Build Plan

**Ridge Falcons XI** | 344/8 (50.0 Overs) vs 279/10 (46.2 Overs) | 65 runs | POM: Caleb Rourke

**Numeric Whitelist:** 0,1,2,4,8,10,14,18,20,46,50,65,275,279,339,344

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 14w+1nb+1b+4lb=20 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+20=344 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 105→156→218→291→300→305→330→333 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 344−279=65 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 14w+0nb+2b+2lb=18 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Caleb Rourke — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 344−1(B)−4(LB)=339 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 279−2(B)−2(LB)=275 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 105 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]