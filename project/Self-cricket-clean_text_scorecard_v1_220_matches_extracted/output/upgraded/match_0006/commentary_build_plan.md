# match_0006 — Commentary Build Plan

**Ridgeway XI** | 211/8 (50.0 Overs) vs 214/6 (45.2 Overs) | 4 wickets | POM: Mason Vale

**Numeric Whitelist:** 0,1,2,4,6,8,11,16,18,45,50,206,210,211,214

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 11w+2nb+1b+4lb=18 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+18=211 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 42→65→106→118→138→170→191→192 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 211, achieved 214/6 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 11w+1nb+0b+4lb=16 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Mason Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 211−1(B)−4(LB)=206 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 214−0(B)−4(LB)=210 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 42 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]