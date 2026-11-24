# match_0145 — Commentary Build Plan

**Harborlight Women** | 112/8 (20.0 Overs) vs 115/0 (14.4 Overs) | 10 wickets | POM: Lina Vale

**Numeric Whitelist:** 0,1,4,5,6,8,10,14,20,111,112,113,115

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+0nb+0b+1lb=6 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+6=112 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 0→24→42→49→64→68→93→94 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠8→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 112, achieved 115/0 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+1b+1lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Lina Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 112−0(B)−1(LB)=111 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 115−1(B)−1(LB)=113 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 25 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]