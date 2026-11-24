# match_0103 — Commentary Build Plan

**Harborline** | 154/6 (20.0 Overs) vs 157/5 (17.2 Overs) | 5 wickets | POM: Victor Hale

**Numeric Whitelist:** 0,1,2,5,6,7,9,10,13,17,20,152,154,155,157

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 10w+1nb+1b+1lb=13 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+13=154 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 24→28→45→67→106→139 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠6→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 154, achieved 157/5 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+0nb+0b+2lb=9 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Victor Hale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 154−1(B)−1(LB)=152 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 157−0(B)−2(LB)=155 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 39 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]