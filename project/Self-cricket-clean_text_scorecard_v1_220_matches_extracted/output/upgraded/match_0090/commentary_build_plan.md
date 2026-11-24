# match_0090 — Commentary Build Plan

**Norchester** | 78/8 (20.0 Overs) vs 82/3 (10.1 Overs) | 7 wickets | POM: Daniel Hart

**Numeric Whitelist:** 0,1,2,3,5,6,7,8,10,11,14,20,75,78,81,82

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 11w+0nb+1b+2lb=14 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+14=78 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 14→25→32→38→43→55→63→72 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠8→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 78, achieved 82/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+0nb+0b+1lb=6 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Daniel Hart — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 78−1(B)−2(LB)=75 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 82−0(B)−1(LB)=81 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 14 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]