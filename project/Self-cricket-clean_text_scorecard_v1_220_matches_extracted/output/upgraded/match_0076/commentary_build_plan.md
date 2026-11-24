# match_0076 — Commentary Build Plan

**Coastport** | 181/10 (49.1 Overs) vs 182/3 (38.2 Overs) | 7 wickets | POM: Connor Blake

**Numeric Whitelist:** 1,2,3,7,9,10,15,18,22,38,49,178,181,182

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 18w+1nb+1b+2lb=22 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+22=181 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 31→76→91→133→133→145→157→157→180→181 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 181, achieved 182/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 9w+2nb+3b+1lb=15 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Connor Blake — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 181−1(B)−2(LB)=178 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 182−3(B)−1(LB)=178 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 45 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]