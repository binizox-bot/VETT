# match_0110 — Commentary Build Plan

**Coral Ridge Women** | 82/10 (19.3 Overs) vs 84/6 (18.2 Overs) | 4 wickets | POM: Isla Morgan

**Numeric Whitelist:** 0,1,2,3,4,5,6,9,10,12,18,19,79,82,83,84

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 9w+0nb+1b+2lb=12 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+12=82 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 12→26→54→60→61→64→68→76→76→82 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 82, achieved 84/6 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+1b+0lb=5 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Isla Morgan — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 82−1(B)−2(LB)=79 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 84−1(B)−0(LB)=83 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 28 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]