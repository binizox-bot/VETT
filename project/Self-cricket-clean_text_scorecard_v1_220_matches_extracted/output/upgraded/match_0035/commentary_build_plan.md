# match_0035 — Commentary Build Plan

**Capeview** | 167/10 (32.5 Overs) vs 85/10 (20.1 Overs) | 82 runs | POM: Ethan Vale

**Numeric Whitelist:** 0,1,2,3,5,10,13,14,17,20,32,82,85,164,167

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 14w+0nb+1b+2lb=17 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+17=167 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 3→3→5→55→79→105→118→128→145→167 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 167−85=82 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 10w+0nb+0b+3lb=13 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Ethan Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 167−1(B)−2(LB)=164 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 85−0(B)−3(LB)=82 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 50 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]