# match_0127 — Commentary Build Plan

**Northvale** | 204/8 (20.0 Overs) vs 151/10 (18.5 Overs) | 53 runs | POM: Ronald Stone

**Numeric Whitelist:** 0,1,2,3,5,7,8,9,10,12,18,20,53,148,151,202,204

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 9w+1nb+0b+2lb=12 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+12=204 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 31→115→148→152→190→193→193→194 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 204−151=53 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+0nb+0b+3lb=10 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Ronald Stone — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 204−0(B)−2(LB)=202 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 151−0(B)−3(LB)=148 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 84 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]