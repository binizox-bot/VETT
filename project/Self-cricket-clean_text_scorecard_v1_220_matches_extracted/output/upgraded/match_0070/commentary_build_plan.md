# match_0070 — Commentary Build Plan

**Kingsport** | 164/10 (48.2 Overs) vs 121/0 (16.2 Overs) | 10 wickets | POM: Isaac Rowan

**Numeric Whitelist:** 0,2,3,4,10,16,18,24,48,121,160,164

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 18w+2nb+0b+4lb=24 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+24=164 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 8→14→60→98→98→128→140→146→154→164 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 164, achieved 121/0 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 3w+0nb+0b+0lb=3 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Isaac Rowan — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 164−0(B)−4(LB)=160 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 121−0(B)−0(LB)=121 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 46 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (12 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]