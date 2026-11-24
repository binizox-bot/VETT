# match_0014 — Commentary Build Plan

**Harbor Peninsula XI** | 225/8 (36.0 Overs) vs 226/7 (35.2 Overs) | 3 wickets | POM: Aiden Mercer

**Numeric Whitelist:** 0,1,2,3,7,8,11,12,15,17,35,36,221,223,225,226

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 12w+1nb+1b+3lb=17 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+17=225 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 24→39→108→121→161→207→212→225 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 225, achieved 226/7 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 11w+1nb+1b+2lb=15 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Aiden Mercer — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 225−1(B)−3(LB)=221 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 226−1(B)−2(LB)=223 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 69 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]