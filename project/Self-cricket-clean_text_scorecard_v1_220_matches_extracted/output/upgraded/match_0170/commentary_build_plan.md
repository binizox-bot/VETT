# match_0170 — Commentary Build Plan

**Harborfield** | 183/10 (43.2 Overs) vs 184/4 (40.4 Overs) | 6 wickets | POM: Miles Carter (Harborfield)

**Numeric Whitelist:** 0,1,2,4,6,10,14,17,18,20,40,43,180,181,183,184

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 14w+1nb+1b+2lb=18 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+18=183 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 24→36→84→122→148→151→159→160→176→183 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠10→3 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 183, achieved 184/4 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 17w+0nb+2b+1lb=20 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Miles Carter (Harborfield) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 183−1(B)−2(LB)=180 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 184−2(B)−1(LB)=181 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 48 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]