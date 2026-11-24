# match_0063 — Commentary Build Plan

**Brookfield** | 218/10 (43.2 Overs) vs 164/10 (39.1 Overs) | 54 runs | POM: Finn Grant

**Numeric Whitelist:** 0,1,2,3,4,10,15,19,20,25,39,43,54,160,164,215,218

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 19w+3nb+1b+2lb=25 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+25=218 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 20→41→120→163→173→174→184→199→215→218 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠10→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 218−164=54 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 15w+1nb+0b+4lb=20 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Finn Grant — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 218−1(B)−2(LB)=215 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 164−0(B)−4(LB)=160 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 79 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]