# match_0142 — Commentary Build Plan

**Harborlight Women** | 194/6 (20.0 Overs) vs 119/8 (20.0 Overs) | 75 runs | POM: Sophie Lane

**Numeric Whitelist:** 0,1,2,6,7,8,9,20,75,118,119,192,194

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 6w+1nb+0b+2lb=9 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+9=194 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 31→46→64→108→172→180 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠6→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 194−119=75 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+0b+1lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Sophie Lane — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 194−0(B)−2(LB)=192 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 119−0(B)−1(LB)=118 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 64 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]