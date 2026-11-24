# match_0146 — Commentary Build Plan

**Silver Coast Women** | 152/5 (20.0 Overs) vs 154/7 (19.3 Overs) | 3 wickets | POM: Maya Rowan

**Numeric Whitelist:** 0,1,2,3,4,5,6,7,9,12,19,20,150,151,152,154

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 4w+0nb+0b+2lb=6 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+6=152 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 58→80→82→124→140 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠5→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 152, achieved 154/7 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 9w+0nb+2b+1lb=12 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Maya Rowan — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 152−0(B)−2(LB)=150 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 154−2(B)−1(LB)=151 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 58 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]