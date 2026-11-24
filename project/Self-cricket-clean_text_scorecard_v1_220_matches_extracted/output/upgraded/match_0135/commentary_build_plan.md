# match_0135 — Commentary Build Plan

**Cedarbridge XI** | 194/9 (20.0 Overs) vs 152/9 (20.0 Overs) | 42 runs | POM: Arman Reed

**Numeric Whitelist:** 0,1,2,3,6,8,9,10,12,20,42,151,152,191,194

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 6w+3nb+1b+2lb=12 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+12=194 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 18→27→79→120→134→160→190→190→194 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠9→3 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 194−152=42 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 8w+1nb+0b+1lb=10 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Arman Reed — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 194−1(B)−2(LB)=191 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 152−0(B)−1(LB)=151 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 52 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]