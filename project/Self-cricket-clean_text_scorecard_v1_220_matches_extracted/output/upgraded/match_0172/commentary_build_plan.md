# match_0172 — Commentary Build Plan

**Ridge Falcons** | 196/8 (50.0 Overs) vs 199/7 (36.4 Overs) | 3 wickets | POM: Leo Grant (Ridge Falcons)

**Numeric Whitelist:** 0,1,2,3,4,7,8,9,14,21,36,50,191,196,198,199

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 14w+2nb+3b+2lb=21 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+21=196 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 12→40→41→86→107→126→188→196 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠8→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 196, achieved 199/7 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 8w+0nb+0b+1lb=9 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Leo Grant (Ridge Falcons) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 196−3(B)−2(LB)=191 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 199−0(B)−1(LB)=198 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 62 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]