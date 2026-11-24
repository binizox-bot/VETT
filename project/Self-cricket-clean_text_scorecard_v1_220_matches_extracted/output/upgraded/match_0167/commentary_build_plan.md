# match_0167 — Commentary Build Plan

**Bayport Women** | 124/7 (20.0 Overs) vs 87/10 (19.2 Overs) | 37 runs | POM: Mara Vale (Bayport Women)

**Numeric Whitelist:** 0,1,2,7,8,9,10,19,20,37,86,87,122,124

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 7w+0nb+1b+1lb=9 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+9=124 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 25→27→70→84→88→108→120 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠7→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 124−87=37 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+0nb+1b+0lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Mara Vale (Bayport Women) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 124−1(B)−1(LB)=122 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 87−1(B)−0(LB)=86 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 43 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]