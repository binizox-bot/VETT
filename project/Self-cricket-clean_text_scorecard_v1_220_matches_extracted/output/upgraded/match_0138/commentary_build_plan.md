# match_0138 — Commentary Build Plan

**Ashford XI** | 144/8 (20.0 Overs) vs 145/6 (19.3 Overs) | 4 wickets | POM: Jonah Vale

**Numeric Whitelist:** 0,1,2,3,4,5,6,8,10,19,20,140,143,144,145

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+1nb+1b+3lb=10 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+10=144 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 0→20→37→60→86→100→100→108 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 6≠8→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 144, achieved 145/6 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 3w+0nb+0b+2lb=5 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Jonah Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 144−1(B)−3(LB)=140 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 145−0(B)−2(LB)=143 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 36 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]