# match_0161 — Commentary Build Plan

**Harborline Women** | 157/4 (20.0 Overs) vs 61/6 (20.0 Overs) | 96 runs | POM: Clara Mason

**Numeric Whitelist:** 0,2,4,6,9,11,13,20,59,61,96,155,157

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 9w+2nb+0b+2lb=13 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+13=157 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 10→15→20→48 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 4≠4→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 157−61=96 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 9w+0nb+0b+2lb=11 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Clara Mason — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 157−0(B)−2(LB)=155 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 61−0(B)−2(LB)=59 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 109 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]