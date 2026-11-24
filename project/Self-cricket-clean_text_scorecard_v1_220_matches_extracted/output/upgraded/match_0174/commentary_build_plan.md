# match_0174 — Commentary Build Plan

**Coastline** | 112/10 (40.4 Overs) vs 114/4 (22.5 Overs) | 6 wickets | POM: Aaron Vale (Coastline)

**Numeric Whitelist:** 0,1,4,5,6,7,8,10,22,40,110,112,114

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 6w+0nb+1b+1lb=8 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+8=112 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 52→62→64→69→69→83→85→87→96→112 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 112, achieved 114/4 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 7w+1nb+0b+0lb=8 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Aaron Vale (Coastline) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 112−1(B)−1(LB)=110 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 114−0(B)−0(LB)=114 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 52 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]