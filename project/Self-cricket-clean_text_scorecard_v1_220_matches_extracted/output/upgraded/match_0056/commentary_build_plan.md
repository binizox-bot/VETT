# match_0056 — Commentary Build Plan

**Northford** | 91/10 (34.4 Overs) vs 94/4 (16.1 Overs) | 6 wickets | POM: Jasper Vale

**Numeric Whitelist:** 0,1,2,3,4,6,10,13,15,16,34,88,91,93,94

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 10w+2nb+0b+3lb=15 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+15=91 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 11→20→24→25→68→68→72→72→83→91 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 91, achieved 94/4 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 13w+1nb+0b+1lb=15 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Jasper Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 91−0(B)−3(LB)=88 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 94−0(B)−1(LB)=93 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 43 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]