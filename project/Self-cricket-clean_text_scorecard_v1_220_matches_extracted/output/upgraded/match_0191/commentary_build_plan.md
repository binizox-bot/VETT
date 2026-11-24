# match_0191 — Commentary Build Plan

**Ashford** | 34/10 (24.4 Overs) vs 35/0 (4.2 Overs) | 10 wickets | POM: Leo Marsh (Ashford)

**Numeric Whitelist:** 0,1,2,3,4,5,9,10,13,24,32,34,35

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 9w+2nb+1b+1lb=13 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+13=34 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 1→6→13→17→18→20→20→23→31→34 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠10→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 34, achieved 35/0 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 3w+1nb+0b+1lb=5 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Leo Marsh (Ashford) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 34−1(B)−1(LB)=32 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 35−0(B)−1(LB)=34 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 8 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (13 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]