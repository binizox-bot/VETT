# match_0157 — Commentary Build Plan

**Harborline XI** | 176/5 (20.0 Overs) vs 70/10 (16.2 Overs) | 106 runs | POM: Ronan Vale

**Numeric Whitelist:** 0,1,2,3,5,6,7,10,16,20,68,70,106,175,176

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 6w+0nb+0b+1lb=7 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+7=176 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 24→57→117→120→125 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 4≠5→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 176−70=106 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 3w+0nb+0b+2lb=5 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Ronan Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 176−0(B)−1(LB)=175 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 70−0(B)−2(LB)=68 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 60 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]