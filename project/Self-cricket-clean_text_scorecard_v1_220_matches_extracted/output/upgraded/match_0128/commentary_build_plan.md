# match_0128 — Commentary Build Plan

**Ironvale** | 154/5 (18.0 Overs) vs 156/6 (17.4 Overs) | 4 wickets | POM: Theo Marsh

**Numeric Whitelist:** 0,1,2,4,5,6,7,8,17,18,152,154,155,156

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+1nb+0b+2lb=8 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+8=154 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 53→82→87→96→148 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 4≠5→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 154, achieved 156/6 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+0b+1lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Theo Marsh — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 154−0(B)−2(LB)=152 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 156−0(B)−1(LB)=155 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 53 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]