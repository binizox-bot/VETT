# match_0118 — Commentary Build Plan

**Valley Crest Women** | 77/9 (20.0 Overs) vs 52/2 (7.1 Overs) | 8 wickets | POM: Aria Cole

**Numeric Whitelist:** 0,1,2,4,5,6,7,8,9,20,51,52,76,77

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 4w+0nb+1b+0lb=5 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+5=77 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 10→35→54→54→54→66→66→69→72 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠9→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 77, achieved 52/2 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 6w+0nb+1b+0lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Aria Cole — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 77−1(B)−0(LB)=76 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 52−1(B)−0(LB)=51 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 25 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]