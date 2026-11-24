# match_0029 — Commentary Build Plan

**Bayfront** | 220/8 (35.0 Overs) vs 126/10 (34.5 Overs) | 94 runs | POM: Tyler Stone

**Numeric Whitelist:** 0,1,2,3,4,5,8,9,10,12,17,19,34,35,94,119,126,215,220

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 12w+0nb+1b+4lb=17 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+17=220 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 24→84→152→161→174→206→209→215 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 220−126=94 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 9w+3nb+2b+5lb=19 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Tyler Stone — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 220−1(B)−4(LB)=215 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 126−2(B)−5(LB)=119 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 68 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (19 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]