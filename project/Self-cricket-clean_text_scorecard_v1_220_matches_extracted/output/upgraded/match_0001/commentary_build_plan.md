# match_0001 — Commentary Build Plan

**Brookfield XI** | 144/10 (35.3 Overs) vs 145/5 (33.2 Overs) | 5 wickets | POM: Nolan Hart

**Numeric Whitelist:** 0,1,2,3,5,7,10,15,21,33,35,139,143,144,145

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 15w+1nb+2b+3lb=21 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+21=144 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 21→38→46→48→93→111→128→132→132→144 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 144, achieved 145/5 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+1nb+0b+2lb=10 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Nolan Hart — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 144−2(B)−3(LB)=139 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 145−0(B)−2(LB)=143 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 45 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]