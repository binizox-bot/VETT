# match_0032 — Commentary Build Plan

**Harborline** | 136/8 (35.0 Overs) vs 137/6 (32.1 Overs) | 4 wickets | POM: Evan Vale

**Numeric Whitelist:** 0,1,4,6,8,12,14,21,22,32,35,134,136,137

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 12w+0nb+1b+1lb=14 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+14=136 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 18→48→104→111→114→122→126→131 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 136, achieved 137/6 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 21w+0nb+0b+1lb=22 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Evan Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 136−1(B)−1(LB)=134 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 137−0(B)−1(LB)=136 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 56 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]