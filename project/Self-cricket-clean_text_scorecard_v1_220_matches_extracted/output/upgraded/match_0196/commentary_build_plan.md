# match_0196 — Commentary Build Plan

**Ashford** | 36/10 (29.4 Overs) vs 37/0 (4.3 Overs) | 10 wickets | POM: Arjun Blake (Ashford)

**Numeric Whitelist:** 0,1,3,4,5,10,14,16,29,35,36,37

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 14w+1nb+1b+0lb=16 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+16=36 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 6→10→10→15→16→18→18→23→34→36 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 36, achieved 37/0 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+0b+1lb=5 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Arjun Blake (Ashford) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 36−1(B)−0(LB)=35 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 37−0(B)−1(LB)=36 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 11 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (12 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]