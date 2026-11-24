# match_0115 — Commentary Build Plan

**Crownvale Women** | 158/5 (20.0 Overs) vs 76/10 (18.4 Overs) | 82 runs | POM: Iris Turner

**Numeric Whitelist:** 0,1,4,5,7,10,12,18,20,74,76,82,156,158

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 4w+1nb+1b+1lb=7 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+7=158 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 18→72→128→142→158 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 3≠5→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 158−76=82 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 10w+0nb+1b+1lb=12 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Iris Turner — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 158−1(B)−1(LB)=156 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 76−1(B)−1(LB)=74 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 56 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]