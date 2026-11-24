# match_0164 — Commentary Build Plan

**Meadowridge Women** | 108/6 (20.0 Overs) vs 109/4 (19.0 Overs) | 6 wickets | POM: Isla Rowan (Meadowridge Women)

**Numeric Whitelist:** 0,1,4,6,7,9,13,19,20,105,107,108,109

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 6w+0nb+0b+1lb=7 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+7=108 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 2→28→32→71→95→105 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠6→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 108, achieved 109/4 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 9w+0nb+0b+4lb=13 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Isla Rowan (Meadowridge Women) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 108−0(B)−1(LB)=107 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 109−0(B)−4(LB)=105 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 39 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]