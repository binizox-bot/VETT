# match_0095 — Commentary Build Plan

**Ridgegate** | 188/7 (20.0 Overs) vs 151/8 (20.0 Overs) | 37 runs | POM: Mason Clarke

**Numeric Whitelist:** 0,1,2,5,6,7,8,9,12,13,20,37,144,151,185,188

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 9w+0nb+1b+2lb=12 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+12=188 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 31→79→165→173→181→183→186 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠7→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 188−151=37 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+2b+5lb=13 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Mason Clarke — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 188−1(B)−2(LB)=185 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 151−2(B)−5(LB)=144 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 86 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]