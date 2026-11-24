# match_0176 — Commentary Build Plan

**Coastline** | 84/10 (34.2 Overs) vs 86/2 (17.4 Overs) | 8 wickets | POM: Ronan Cross (Coastline)

**Numeric Whitelist:** 0,1,2,4,7,8,9,10,17,34,82,84,86

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 7w+0nb+1b+1lb=9 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+9=84 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 20→20→45→67→75→76→77→78→82→84 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 84, achieved 86/2 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+0b+0lb=4 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Ronan Cross (Coastline) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 84−1(B)−1(LB)=82 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 86−0(B)−0(LB)=86 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 25 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]