# match_0193 — Commentary Build Plan

**Eastport** | 66/10 (22.4 Overs) vs 67/6 (14.4 Overs) | 4 wickets | POM: Caleb Ross (Eastport)

**Numeric Whitelist:** 0,1,2,4,6,7,8,10,14,20,22,24,63,66,67

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 20w+1nb+1b+2lb=24 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+24=66 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 10→10→24→34→35→47→48→51→60→66 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 66, achieved 67/6 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+0nb+0b+1lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Caleb Ross (Eastport) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 66−1(B)−2(LB)=63 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 67−0(B)−1(LB)=66 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 14 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]