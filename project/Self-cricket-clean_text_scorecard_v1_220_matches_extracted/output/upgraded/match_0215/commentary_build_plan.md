# match_0215 — Commentary Build Plan

**Harborfield CC** | 151/10 (42.3 Overs) vs 152/7 (35.2 Overs) | 3 wickets | POM: Mason Hale

**Numeric Whitelist:** 0,1,2,3,7,10,14,16,18,35,42,148,151,152

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 14w+1nb+1b+2lb=18 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+18=151 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 7→25→49→52→65→82→123→141→143→151 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 151, achieved 152/7 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 14w+1nb+0b+1lb=16 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Mason Hale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 151−1(B)−2(LB)=148 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 152−0(B)−1(LB)=151 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 41 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]