# match_0204 — Commentary Build Plan

**Moorland** | 119/10 (39.3 Overs) vs 120/8 (30.2 Overs) | 2 wickets | POM: Arjun Reed (Moorland)

**Numeric Whitelist:** 0,1,2,3,8,9,10,11,20,24,30,39,117,119,120

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 20w+2nb+1b+1lb=24 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+24=119 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 2→21→43→51→63→63→82→104→104→119 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 119, achieved 120/8 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 9w+1nb+0b+1lb=11 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Arjun Reed (Moorland) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 119−1(B)−1(LB)=117 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 120−0(B)−1(LB)=119 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 22 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]