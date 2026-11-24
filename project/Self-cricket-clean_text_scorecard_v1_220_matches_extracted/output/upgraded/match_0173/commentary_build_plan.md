# match_0173 — Commentary Build Plan

**Crestview** | 92/10 (42.2 Overs) vs 96/0 (8.1 Overs) | 10 wickets | POM: Nolan Pierce (Crestview)

**Numeric Whitelist:** 0,1,2,4,7,8,10,11,12,42,91,92,94,96

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 11w+0nb+0b+1lb=12 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+12=92 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 41→44→44→47→58→66→66→73→73→92 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 92, achieved 96/0 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+1nb+0b+2lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Nolan Pierce (Crestview) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 92−0(B)−1(LB)=91 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 96−0(B)−2(LB)=94 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 41 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]