# match_0100 — Commentary Build Plan

**Southport** | 138/8 (20.0 Overs) vs 139/3 (17.2 Overs) | 7 wickets | POM: Daniel Mercer

**Numeric Whitelist:** 0,1,2,3,7,8,9,10,11,17,20,135,137,138,139

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 7w+0nb+1b+2lb=10 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+10=138 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 0→62→75→100→118→123→125→126 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 138, achieved 139/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 9w+0nb+0b+2lb=11 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Daniel Mercer — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 138−1(B)−2(LB)=135 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 139−0(B)−2(LB)=137 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 62 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]