# match_0052 — Commentary Build Plan

**Crestbrook** | 139/10 (32.1 Overs) vs 93/10 (31.5 Overs) | 46 runs | POM: Gareth Porter

**Numeric Whitelist:** 0,1,2,3,5,10,16,19,21,24,31,32,46,90,93,137,139

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 21w+1nb+0b+2lb=24 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+24=139 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 46→58→77→107→115→125→127→132→136→139 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 139−93=46 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 16w+0nb+0b+3lb=19 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Gareth Porter — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 139−0(B)−2(LB)=137 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 93−0(B)−3(LB)=90 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 46 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]