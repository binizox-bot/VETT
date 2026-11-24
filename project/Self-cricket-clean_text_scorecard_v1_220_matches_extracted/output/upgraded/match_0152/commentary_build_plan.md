# match_0152 — Commentary Build Plan

**Highland Reserve** | 171/4 (20.0 Overs) vs 172/6 (19.3 Overs) | 4 wickets | POM: Miles Rowan

**Numeric Whitelist:** 0,1,2,3,4,5,6,7,9,19,20,168,169,171,172

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 3w+1nb+1b+2lb=7 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+7=171 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 24→86→89→106 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 4≠4→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 171, achieved 172/6 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+1nb+0b+3lb=9 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Miles Rowan — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 171−1(B)−2(LB)=168 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 172−0(B)−3(LB)=169 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 65 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]