# match_0218 — Commentary Build Plan

**Lakeshore CC** | 86/10 (27.3 Overs) vs 89/3 (18.2 Overs) | 7 wickets | POM: Caleb Rowan

**Numeric Whitelist:** 0,1,2,3,6,7,9,10,11,18,27,84,86,88,89

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 9w+0nb+1b+1lb=11 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+11=86 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 5→8→18→19→30→35→39→69→84→86 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 86, achieved 89/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+0b+1lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Caleb Rowan — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 86−1(B)−1(LB)=84 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 89−0(B)−1(LB)=88 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 30 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]