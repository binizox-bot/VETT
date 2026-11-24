# match_0091 — Commentary Build Plan

**Norchester** | 136/5 (20.0 Overs) vs 43/10 (16.1 Overs) | 93 runs | POM: Daniel Hart

**Numeric Whitelist:** 0,1,2,5,8,10,11,14,16,20,41,43,93,134,136

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 11w+1nb+0b+2lb=14 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+14=136 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 14→18→40→55→91 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 5≠5→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 136−43=93 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 8w+0nb+1b+1lb=10 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Daniel Hart — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 136−0(B)−2(LB)=134 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 43−1(B)−1(LB)=41 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 45 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]