# match_0009 — Commentary Build Plan

**Coral Bay XI** | 184/10 (46.5 Overs) vs 187/5 (34.2 Overs) | 5 wickets | POM: Noah Reed

**Numeric Whitelist:** 0,1,2,3,5,10,11,13,14,19,34,46,180,184,186,187

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 14w+1nb+1b+3lb=19 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+19=184 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 9→25→32→84→96→105→129→129→146→184 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 184, achieved 187/5 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 11w+1nb+0b+1lb=13 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Noah Reed — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 184−1(B)−3(LB)=180 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 187−0(B)−1(LB)=186 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 52 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]