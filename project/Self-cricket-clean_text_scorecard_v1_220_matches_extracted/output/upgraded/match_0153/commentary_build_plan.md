# match_0153 — Commentary Build Plan

**Ridgefront A** | 179/5 (20.0 Overs) vs 111/7 (20.0 Overs) | 68 runs | POM: Kian Mercer

**Numeric Whitelist:** 0,1,3,5,6,7,9,10,11,20,68,108,111,178,179

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 9w+1nb+0b+1lb=11 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+11=179 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 13→16→82→109→124 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠5→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 179−111=68 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+1nb+0b+3lb=10 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Kian Mercer — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 179−0(B)−1(LB)=178 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 111−0(B)−3(LB)=108 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 66 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]