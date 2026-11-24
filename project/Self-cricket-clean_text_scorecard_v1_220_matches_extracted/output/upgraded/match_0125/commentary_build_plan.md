# match_0125 — Commentary Build Plan

**Eastmoor** | 150/7 (20.0 Overs) vs 137/10 (19.4 Overs) | 13 runs | POM: Caleb Grant

**Numeric Whitelist:** 0,1,2,4,6,7,9,10,11,13,19,20,136,137,149,150

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 6w+2nb+0b+1lb=9 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+9=150 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 4→35→43→45→55→100→112 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 7≠7→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 150−137=13 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 10w+0nb+0b+1lb=11 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Caleb Grant — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 150−0(B)−1(LB)=149 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 137−0(B)−1(LB)=136 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 45 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]