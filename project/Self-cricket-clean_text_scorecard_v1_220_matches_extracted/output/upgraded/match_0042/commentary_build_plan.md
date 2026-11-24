# match_0042 — Commentary Build Plan

**Westmere** | 298/8 (50.0 Overs) vs 272/8 (50.0 Overs) | 26 runs | POM: Declan Vale

**Numeric Whitelist:** 0,1,3,4,8,13,16,19,26,50,269,272,293,298

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 13w+1nb+1b+4lb=19 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+19=298 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 29→37→43→152→228→246→273→296 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 298−272=26 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 16w+0nb+0b+3lb=19 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Declan Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 298−1(B)−4(LB)=293 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 272−0(B)−3(LB)=269 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 109 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]