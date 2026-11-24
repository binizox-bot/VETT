# match_0098 — Commentary Build Plan

**Harborview** | 181/5 (20.0 Overs) vs 99/9 (20.0 Overs) | 82 runs | POM: Adrian Cole

**Numeric Whitelist:** 0,1,2,3,4,5,8,9,10,13,15,20,82,94,99,176,181

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 8w+0nb+2b+3lb=13 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+13=181 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 68→86→110→158→170 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠5→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 181−99=82 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 10w+0nb+1b+4lb=15 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Adrian Cole — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 181−2(B)−3(LB)=176 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 99−1(B)−4(LB)=94 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 68 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]