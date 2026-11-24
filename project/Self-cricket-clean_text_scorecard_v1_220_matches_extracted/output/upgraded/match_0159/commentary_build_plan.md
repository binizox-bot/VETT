# match_0159 — Commentary Build Plan

**Coastvale A** | 198/5 (20.0 Overs) vs 176/8 (20.0 Overs) | 22 runs | POM: Darian Holt

**Numeric Whitelist:** 0,1,2,4,5,6,7,8,20,22,174,176,196,198

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 4w+1nb+0b+2lb=7 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+7=198 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 123→167→172→172→186 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠5→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 198−176=22 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+1b+1lb=6 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Darian Holt — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 198−0(B)−2(LB)=196 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 176−1(B)−1(LB)=174 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 123 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]