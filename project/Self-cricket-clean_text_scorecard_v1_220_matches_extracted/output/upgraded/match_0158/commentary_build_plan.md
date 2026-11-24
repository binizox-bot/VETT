# match_0158 — Commentary Build Plan

**Harborline A** | 142/8 (20.0 Overs) vs 145/3 (17.1 Overs) | 7 wickets | POM: Ronan Vale

**Numeric Whitelist:** 0,1,2,3,5,6,7,8,17,20,139,142,144,145

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 5w+0nb+1b+2lb=8 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+8=142 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 18→40→42→88→106→108→117→131 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠8→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | Target 142, achieved 145/3 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 5w+0nb+0b+1lb=6 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Ronan Vale — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 142−1(B)−2(LB)=139 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 145−0(B)−1(LB)=144 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 46 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (14 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]