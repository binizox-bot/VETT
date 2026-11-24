# match_0036 — Commentary Build Plan

**Eastport** | 128/10 (34.2 Overs) vs 130/3 (25.4 Overs) | 7 wickets | POM: Noah Reed

**Numeric Whitelist:** 0,2,3,4,7,10,12,16,25,34,122,128,130

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 10w+0nb+4b+2lb=16 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+16=128 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 3→16→21→39→82→89→102→114→126→128 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 128, achieved 130/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 10w+0nb+0b+2lb=12 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Noah Reed — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 128−4(B)−2(LB)=122 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 130−0(B)−2(LB)=128 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 43 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]