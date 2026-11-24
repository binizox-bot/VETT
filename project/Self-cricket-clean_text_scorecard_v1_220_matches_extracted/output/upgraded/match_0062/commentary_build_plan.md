# match_0062 — Commentary Build Plan

**Meadowridge** | 47/10 (18.2 Overs) vs 49/1 (9.4 Overs) | 9 wickets | POM: Riley Nash

**Numeric Whitelist:** 0,1,2,4,5,7,9,10,12,14,18,45,47,48,49

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 12w+0nb+1b+1lb=14 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+14=47 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 2→16→22→24→25→30→36→37→37→47 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 47, achieved 49/1 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+1nb+0b+1lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Riley Nash — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 47−1(B)−1(LB)=45 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 49−0(B)−1(LB)=48 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 14 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]