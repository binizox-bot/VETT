# match_0040 — Commentary Build Plan

**Ridgeford A** | 293/9 (50.0 Overs) vs 142/10 (32.4 Overs) | 151 runs | POM: Elliot Vale

**Numeric Whitelist:** 0,1,2,4,7,9,10,11,13,17,32,50,139,142,151,290,293

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 13w+1nb+1b+2lb=17 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+17=293 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 92→135→154→226→251→263→274→284→291 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠9→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 293−142=151 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+1nb+2b+1lb=11 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Elliot Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 293−1(B)−2(LB)=290 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 142−2(B)−1(LB)=139 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 92 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (17 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]