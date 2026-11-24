# match_0205 — Commentary Build Plan

**Ridgeway** | 58/10 (18.4 Overs) vs 60/1 (8.2 Overs) | 9 wickets | POM: Owen Vale (Ridgeway)

**Numeric Whitelist:** 0,1,2,4,8,9,10,11,12,13,18,56,58,59,60

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 10w+0nb+1b+1lb=12 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+12=58 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 4→4→7→13→15→20→20→42→49→58 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 58, achieved 60/1 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 11w+1nb+0b+1lb=13 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Owen Vale (Ridgeway) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 58−1(B)−1(LB)=56 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 60−0(B)−1(LB)=59 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 22 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]