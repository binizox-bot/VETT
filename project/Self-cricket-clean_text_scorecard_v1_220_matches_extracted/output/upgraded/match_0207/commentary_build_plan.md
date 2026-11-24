# match_0207 — Commentary Build Plan

**Harborvale** | 132/10 (37.2 Overs) vs 133/4 (32.3 Overs) | 6 wickets | POM: Leo Mason (Harborvale)

**Numeric Whitelist:** 0,1,2,3,4,5,6,7,8,10,12,32,37,129,132,133

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 8w+1nb+1b+2lb=12 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+12=132 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 4→56→60→61→69→84→98→109→126→132 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 132, achieved 133/4 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+1nb+0b+1lb=7 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Leo Mason (Harborvale) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 132−1(B)−2(LB)=129 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 133−0(B)−1(LB)=132 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 52 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]