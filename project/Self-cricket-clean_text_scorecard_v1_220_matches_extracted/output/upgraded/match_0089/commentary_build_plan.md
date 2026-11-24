# match_0089 — Commentary Build Plan

**Rivermark** | 206/9 (50.0 Overs) vs 208/4 (40.2 Overs) | 6 wickets | POM: Ethan Cole

**Numeric Whitelist:** 0,1,2,3,4,6,8,9,13,40,50,202,206,208

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 8w+1nb+1b+3lb=13 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+13=206 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 40→75→87→123→123→141→169→195→196 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠9→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 206, achieved 208/4 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+0b+2lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Ethan Cole — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 206−1(B)−3(LB)=202 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 208−0(B)−2(LB)=206 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 40 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]