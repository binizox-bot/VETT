# match_0085 — Commentary Build Plan

**Metrovale** | 226/9 (50.0 Overs) vs 229/8 (48.5 Overs) | 2 wickets | POM: Milo Bell

**Numeric Whitelist:** 0,1,2,5,6,8,9,11,15,17,18,48,50,219,226,227,229

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 11w+0nb+1b+6lb=18 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+18=226 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 5→56→118→121→130→161→179→224→226 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠9→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 226, achieved 229/8 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 15w+0nb+0b+2lb=17 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Milo Bell — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 226−1(B)−6(LB)=219 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 229−0(B)−2(LB)=227 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 62 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]