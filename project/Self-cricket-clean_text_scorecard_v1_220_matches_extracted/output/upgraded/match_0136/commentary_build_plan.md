# match_0136 — Commentary Build Plan

**Bayport XI** | 124/9 (20.0 Overs) vs 125/4 (17.2 Overs) | 6 wickets | POM: Arlo Kane

**Numeric Whitelist:** 0,1,2,3,4,5,6,8,9,17,20,122,124,125

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+1nb+1b+1lb=8 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+8=124 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 0→18→33→43→63→98→109→121→123 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠9→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 124, achieved 125/4 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 3w+0nb+0b+0lb=3 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Arlo Kane — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 124−1(B)−1(LB)=122 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 125−0(B)−0(LB)=125 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 35 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]