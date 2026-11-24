# match_0165 — Commentary Build Plan

**Aurora Bay Women** | 142/5 (20.0 Overs) vs 38/10 (14.5 Overs) | 104 runs | POM: Mira Lawson (Aurora Bay Women)

**Numeric Whitelist:** 0,1,2,3,5,6,9,10,14,20,34,38,104,139,142

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 6w+0nb+2b+1lb=9 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+9=142 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 37→41→51→76→82 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠5→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 142−38=104 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+3b+1lb=10 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Mira Lawson (Aurora Bay Women) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 142−2(B)−1(LB)=139 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 38−3(B)−1(LB)=34 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 60 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]