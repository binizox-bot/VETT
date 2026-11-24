# match_0140 — Commentary Build Plan

**Northshore Women** | 122/8 (20.0 Overs) vs 123/4 (17.2 Overs) | 6 wickets | POM: Clara Woods

**Numeric Whitelist:** 0,1,2,4,5,6,8,14,17,20,117,121,122,123

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 4w+0nb+0b+1lb=5 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+5=122 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 19→30→35→60→87→105→106→114 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠8→3 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 122, achieved 123/4 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 8w+0nb+1b+5lb=14 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Clara Woods — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 122−0(B)−1(LB)=121 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 123−1(B)−5(LB)=117 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 27 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]