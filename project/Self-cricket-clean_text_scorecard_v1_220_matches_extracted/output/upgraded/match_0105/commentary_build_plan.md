# match_0105 — Commentary Build Plan

**Sandridge Royals Women** | 73/10 (18.2 Overs) vs 74/3 (11.1 Overs) | 7 wickets | POM: Mira Calder

**Numeric Whitelist:** 0,1,2,3,6,7,10,11,13,16,18,72,73,74

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 13w+2nb+1b+0lb=16 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+16=73 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 3→27→32→40→46→53→57→57→62→73 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 73, achieved 74/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+0b+0lb=6 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Mira Calder — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 73−1(B)−0(LB)=72 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 74−0(B)−0(LB)=74 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 24 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]