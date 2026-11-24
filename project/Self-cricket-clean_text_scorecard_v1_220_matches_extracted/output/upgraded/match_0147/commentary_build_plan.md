# match_0147 — Commentary Build Plan

**Jade Women** | 172/6 (20.0 Overs) vs 174/2 (19.1 Overs) | 8 wickets | POM: Clara Vale

**Numeric Whitelist:** 0,1,2,3,4,6,7,8,19,20,169,170,172,174

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 4w+0nb+1b+2lb=7 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+7=172 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 49→67→100→143→148→171 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠6→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 172, achieved 174/2 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+1b+3lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Clara Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 172−1(B)−2(LB)=169 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 174−1(B)−3(LB)=170 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 49 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]