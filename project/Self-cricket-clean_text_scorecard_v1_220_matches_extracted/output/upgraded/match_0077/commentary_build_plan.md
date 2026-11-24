# match_0077 — Commentary Build Plan

**Seacoast** | 164/10 (46.3 Overs) vs 165/3 (27.1 Overs) | 7 wickets | POM: Ryan Cross

**Numeric Whitelist:** 0,1,2,3,7,10,12,14,19,27,46,160,163,164,165

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 14w+1nb+1b+3lb=19 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+19=164 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 12→30→39→52→56→126→133→139→148→164 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 164, achieved 165/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 12w+0nb+0b+2lb=14 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Ryan Cross — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 164−1(B)−3(LB)=160 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 165−0(B)−2(LB)=163 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 70 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]