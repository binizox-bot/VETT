# match_0151 — Commentary Build Plan

**Meridian A** | 187/8 (20.0 Overs) vs 139/8 (20.0 Overs) | 48 runs | POM: Rowan Hale

**Numeric Whitelist:** 0,1,2,4,5,6,8,9,20,48,137,139,184,187

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+1nb+1b+2lb=9 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+9=187 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 76→83→121→127→165→174→176→176 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠8→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 187−139=48 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+0b+2lb=6 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Rowan Hale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 187−1(B)−2(LB)=184 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 139−0(B)−2(LB)=137 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 76 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]