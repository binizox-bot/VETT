# match_0185 — Commentary Build Plan

**Ridgefield** | 36/10 (20.3 Overs) vs 37/1 (3.3 Overs) | 9 wickets | POM: Noah Vance (Ridgefield)

**Numeric Whitelist:** 0,1,2,3,7,9,10,12,14,20,35,36,37

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 12w+1nb+0b+1lb=14 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+14=36 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 0→1→11→12→24→24→26→30→35→36 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 36, achieved 37/1 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+2nb+0b+0lb=9 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Noah Vance (Ridgefield) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 36−0(B)−1(LB)=35 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 37−0(B)−0(LB)=37 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 12 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]