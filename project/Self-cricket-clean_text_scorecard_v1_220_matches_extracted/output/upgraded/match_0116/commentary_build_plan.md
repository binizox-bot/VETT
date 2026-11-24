# match_0116 — Commentary Build Plan

**Meadowvale Women** | 96/8 (20.0 Overs) vs 97/7 (19.2 Overs) | 3 wickets | POM: Sera Hart

**Numeric Whitelist:** 0,1,2,3,7,8,10,12,13,19,20,94,96,97

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 10w+0nb+1b+1lb=12 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+12=96 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 5→11→14→22→40→80→82→96 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 96, achieved 97/7 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 10w+0nb+1b+2lb=13 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Sera Hart — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 96−1(B)−1(LB)=94 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 97−1(B)−2(LB)=94 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 40 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]