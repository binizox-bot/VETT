# match_0082 — Commentary Build Plan

**Northshore** | 58/10 (24.3 Overs) vs 62/0 (8.4 Overs) | 10 wickets | POM: Nathan Price

**Numeric Whitelist:** 0,1,2,3,4,8,10,12,24,56,58,62

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 10w+0nb+1b+1lb=12 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+12=58 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 10→16→20→26→26→36→43→49→56→58 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 58, achieved 62/0 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 2w+0nb+0b+0lb=2 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Nathan Price — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 58−1(B)−1(LB)=56 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 62−0(B)−0(LB)=62 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 10 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (12 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]