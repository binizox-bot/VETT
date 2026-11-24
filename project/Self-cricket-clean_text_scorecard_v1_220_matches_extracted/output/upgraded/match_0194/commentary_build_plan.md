# match_0194 — Commentary Build Plan

**Bayport** | 281/10 (45.5 Overs) vs 55/10 (30.2 Overs) | 226 runs | POM: Finn Mercer (Bayport)

**Numeric Whitelist:** 0,1,2,3,5,6,10,23,26,30,45,53,55,226,279,281

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 23w+1nb+1b+1lb=26 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+26=281 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 55→125→151→188→204→237→259→272→274→281 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 281−55=226 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 3w+1nb+0b+2lb=6 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Finn Mercer (Bayport) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 281−1(B)−1(LB)=279 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 55−0(B)−2(LB)=53 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 70 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]