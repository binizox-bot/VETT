# match_0053 — Commentary Build Plan

**Northbrook** | 97/10 (18.1 Overs) vs 98/2 (15.3 Overs) | 8 wickets | POM: Caleb Foster

**Numeric Whitelist:** 0,1,2,3,8,10,12,13,15,18,96,97,98

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 13w+1nb+0b+1lb=15 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+15=97 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 9→17→22→35→49→59→67→79→83→97 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 97, achieved 98/2 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 12w+2nb+1b+0lb=15 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Caleb Foster — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 97−0(B)−1(LB)=96 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 98−1(B)−0(LB)=97 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 14 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]