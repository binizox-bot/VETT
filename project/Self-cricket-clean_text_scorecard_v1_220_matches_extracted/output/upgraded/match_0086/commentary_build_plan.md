# match_0086 — Commentary Build Plan

**Dune** | 201/10 (48.2 Overs) vs 190/10 (49.1 Overs) | 11 runs | POM: Jordon Pierce

**Numeric Whitelist:** 0,1,2,9,10,11,12,13,14,48,49,189,190,198,201

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 9w+1nb+1b+2lb=13 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+13=201 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 12→54→78→79→94→152→169→175→185→201 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 201−190=11 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 12w+1nb+0b+1lb=14 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Jordon Pierce — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 201−1(B)−2(LB)=198 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 190−0(B)−1(LB)=189 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 58 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]