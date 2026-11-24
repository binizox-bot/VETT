# match_0084 — Commentary Build Plan

**Coastal Ridge** | 87/10 (32.4 Overs) vs 88/3 (13.4 Overs) | 7 wickets | POM: 

**Numeric Whitelist:** 0,1,3,4,5,7,8,9,10,13,32,85,87,88

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+0nb+1b+1lb=7 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+7=87 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 2→6→16→32→35→44→44→48→84→87 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 87, achieved 88/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 8w+0nb+0b+1lb=9 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 |  — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [not_applicable] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 87−1(B)−1(LB)=85 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 88−0(B)−1(LB)=87 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 36 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]