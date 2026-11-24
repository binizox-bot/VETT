# match_0061 — Commentary Build Plan

**Brookfield** | 93/10 (27.4 Overs) vs 96/2 (12.4 Overs) | 8 wickets | POM: Jasper Cole

**Numeric Whitelist:** 0,1,2,4,8,10,12,13,14,18,27,89,93,95,96

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 13w+1nb+2b+2lb=18 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+18=93 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 8→35→36→53→56→61→85→85→85→93 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 93, achieved 96/2 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 12w+1nb+0b+1lb=14 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Jasper Cole — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 93−2(B)−2(LB)=89 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 96−0(B)−1(LB)=95 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 27 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]