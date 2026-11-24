# match_0094 — Commentary Build Plan

**Westvale** | 186/7 (20.0 Overs) vs 104/10 (19.1 Overs) | 82 runs | POM: Mason Clarke

**Numeric Whitelist:** 0,1,3,4,6,7,8,10,19,20,82,100,104,182,186

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 6w+0nb+1b+3lb=10 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+10=186 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 31→79→165→173→181→183→186 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠7→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 186−104=82 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+0b+4lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Mason Clarke — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 186−1(B)−3(LB)=182 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 104−0(B)−4(LB)=100 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 86 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]