# match_0134 — Commentary Build Plan

**Harborlight XI** | 84/10 (19.0 Overs) vs 86/1 (5.5 Overs) | 9 wickets | POM: Arlen Clarke

**Numeric Whitelist:** 0,1,5,6,9,10,19,83,84,86

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+0nb+0b+1lb=6 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+6=84 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 14→22→27→42→47→50→51→80→84→84 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 84, achieved 86/1 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+0nb+0b+0lb=5 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Arlen Clarke — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 84−0(B)−1(LB)=83 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 86−0(B)−0(LB)=86 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 29 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (10 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]