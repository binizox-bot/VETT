# match_0030 — Commentary Build Plan

**Harborfield** | 52/10 (19.2 Overs) vs 53/1 (8.1 Overs) | 9 wickets | POM: Logan Vale

**Numeric Whitelist:** 0,1,2,8,9,10,12,19,21,51,52,53

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 19w+1nb+1b+0lb=21 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+21=52 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 9→33→34→41→43→44→48→49→49→52 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 52, achieved 53/1 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 12w+0nb+0b+0lb=12 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Logan Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 52−1(B)−0(LB)=51 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 53−0(B)−0(LB)=53 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 24 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (12 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]