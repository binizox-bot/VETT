# match_0181 — Commentary Build Plan

**Northbridge** | 96/10 (42.2 Overs) vs 98/4 (21.2 Overs) | 6 wickets | POM: Adrian Voss (Northbridge)

**Numeric Whitelist:** 0,1,2,4,6,9,10,12,15,21,42,95,96,97,98

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 9w+0nb+0b+1lb=10 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+10=96 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 28→34→34→36→48→56→73→83→91→96 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 96, achieved 98/4 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 12w+2nb+1b+0lb=15 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Adrian Voss (Northbridge) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 96−0(B)−1(LB)=95 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 98−1(B)−0(LB)=97 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 28 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]