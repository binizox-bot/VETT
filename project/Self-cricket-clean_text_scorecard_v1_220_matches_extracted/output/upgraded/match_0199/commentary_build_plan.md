# match_0199 — Commentary Build Plan

**Seabrook** | 24/10 (17.4 Overs) vs 25/0 (1.5 Overs) | 10 wickets | POM: Marcus Dale (Seabrook)

**Numeric Whitelist:** 0,1,3,4,5,8,9,10,17,23,24,25

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 8w+0nb+0b+1lb=9 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+9=24 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 3→3→9→10→13→13→15→22→22→24 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 24, achieved 25/0 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 3w+0nb+0b+0lb=3 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Marcus Dale (Seabrook) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 24−0(B)−1(LB)=23 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 25−0(B)−0(LB)=25 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 7 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (12 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]