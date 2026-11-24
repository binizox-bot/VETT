# match_0187 — Commentary Build Plan

**Brookport** | 64/10 (26.2 Overs) vs 65/1 (7.1 Overs) | 9 wickets | POM: Finn Carter (Brookport)

**Numeric Whitelist:** 0,1,2,4,6,7,9,10,12,26,62,64,65

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 10w+0nb+1b+1lb=12 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+12=64 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 5→8→8→22→29→39→42→49→58→64 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 64, achieved 65/1 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+1nb+0b+1lb=6 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Finn Carter (Brookport) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 64−1(B)−1(LB)=62 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 65−0(B)−1(LB)=64 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 14 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]