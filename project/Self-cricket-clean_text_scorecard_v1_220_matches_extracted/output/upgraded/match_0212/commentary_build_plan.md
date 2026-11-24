# match_0212 — Commentary Build Plan

**Silvergate CC** | 106/10 (31.2 Overs) vs 109/3 (21.2 Overs) | 7 wickets | POM: Noah Vale

**Numeric Whitelist:** 0,1,2,3,4,6,7,10,21,31,103,106,107,109

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 7w+0nb+1b+2lb=10 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+10=106 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 8→18→32→38→66→78→88→94→101→106 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 106, achieved 109/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+0b+2lb=6 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Noah Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 106−1(B)−2(LB)=103 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 109−0(B)−2(LB)=107 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 28 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]