# match_0217 — Commentary Build Plan

**Rivermere CC** | 197/10 (48.5 Overs) vs 119/10 (34.1 Overs) | 78 runs | POM: Oliver Reed

**Numeric Whitelist:** 0,1,2,5,10,12,13,15,17,34,48,78,116,119,194,197

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 13w+1nb+1b+2lb=17 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+17=197 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 12→30→58→108→146→154→171→189→194→197 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠10→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 197−119=78 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 12w+0nb+1b+2lb=15 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Oliver Reed — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 197−1(B)−2(LB)=194 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 119−1(B)−2(LB)=116 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 50 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]