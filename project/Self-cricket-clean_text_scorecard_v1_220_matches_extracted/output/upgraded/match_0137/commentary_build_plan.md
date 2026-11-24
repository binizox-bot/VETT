# match_0137 — Commentary Build Plan

**Granite XI** | 136/9 (20.0 Overs) vs 138/5 (19.2 Overs) | 5 wickets | POM: Evan Cross

**Numeric Whitelist:** 0,1,2,4,5,6,7,9,19,20,134,136,137,138

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 4w+1nb+1b+1lb=7 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+7=136 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 21→30→67→67→85→112→125→133→134 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠9→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 136, achieved 138/5 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+0nb+0b+1lb=6 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Evan Cross — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 136−1(B)−1(LB)=134 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 138−0(B)−1(LB)=137 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 37 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]