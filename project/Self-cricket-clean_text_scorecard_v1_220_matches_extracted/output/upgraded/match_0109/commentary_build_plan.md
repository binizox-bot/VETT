# match_0109 — Commentary Build Plan

**Ridgewood Women** | 93/8 (20.0 Overs) vs 94/5 (15.1 Overs) | 5 wickets | POM: Amina Kade

**Numeric Whitelist:** 0,1,2,3,5,8,15,17,20,22,28,89,93,94

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 22w+2nb+3b+1lb=28 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+28=93 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 7→37→64→66→68→72→86→93 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠8→3 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 93, achieved 94/5 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 17w+0nb+0b+0lb=17 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Amina Kade — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 93−3(B)−1(LB)=89 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 94−0(B)−0(LB)=94 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 30 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]