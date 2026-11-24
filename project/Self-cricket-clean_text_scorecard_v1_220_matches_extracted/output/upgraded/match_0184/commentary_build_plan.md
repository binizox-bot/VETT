# match_0184 — Commentary Build Plan

**Meadowridge** | 72/10 (24.3 Overs) vs 73/7 (22.5 Overs) | 3 wickets | POM: Ethan Vale (Meadowridge)

**Numeric Whitelist:** 0,1,2,3,5,7,9,10,13,15,17,22,24,69,71,72,73

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 9w+3nb+1b+2lb=15 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+15=72 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 2→18→22→27→31→31→34→61→70→72 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 72, achieved 73/7 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 13w+2nb+0b+2lb=17 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Ethan Vale (Meadowridge) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 72−1(B)−2(LB)=69 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 73−0(B)−2(LB)=71 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 27 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]