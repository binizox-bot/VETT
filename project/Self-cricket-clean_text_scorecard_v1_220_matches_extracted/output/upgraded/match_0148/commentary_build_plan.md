# match_0148 — Commentary Build Plan

**Ridge A** | 157/8 (20.0 Overs) vs 158/5 (18.4 Overs) | 5 wickets | POM: Noah Vale

**Numeric Whitelist:** 0,1,2,4,5,6,7,8,18,20,155,156,157,158

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 4w+0nb+0b+2lb=6 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+6=157 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 10→12→80→92→130→130→139→149 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 157, achieved 158/5 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+1nb+0b+2lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Noah Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 157−0(B)−2(LB)=155 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 158−0(B)−2(LB)=156 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 68 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]