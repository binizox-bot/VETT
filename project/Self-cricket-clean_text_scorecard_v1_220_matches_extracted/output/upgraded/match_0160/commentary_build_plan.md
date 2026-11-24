# match_0160 — Commentary Build Plan

**Highland Bay A** | 137/7 (20.0 Overs) vs 138/3 (18.1 Overs) | 7 wickets | POM: Marcus Vale

**Numeric Whitelist:** 0,1,2,3,4,5,7,8,18,20,134,135,137,138

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+0nb+1b+2lb=8 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+8=137 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 3→14→16→18→68→109→110 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠7→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 137, achieved 138/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+0b+3lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Marcus Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 137−1(B)−2(LB)=134 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 138−0(B)−3(LB)=135 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 50 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]