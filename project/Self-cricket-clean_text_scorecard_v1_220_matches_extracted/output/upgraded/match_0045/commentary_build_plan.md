# match_0045 — Commentary Build Plan

**Ridgecrest** | 307/10 (50.0 Overs) vs 253/10 (46.2 Overs) | 54 runs | POM: Kyle Rowan

**Numeric Whitelist:** 0,1,2,4,5,9,10,13,20,46,50,54,250,253,298,307

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 10w+1nb+4b+5lb=20 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+20=307 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 30→58→128→153→194→258→270→283→297→307 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠10→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 307−253=54 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 9w+1nb+2b+1lb=13 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Kyle Rowan — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 307−4(B)−5(LB)=298 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 253−2(B)−1(LB)=250 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 70 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]