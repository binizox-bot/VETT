# match_0188 — Commentary Build Plan

**Seabank** | 226/10 (44.4 Overs) vs 45/10 (16.1 Overs) | 181 runs | POM: Arjun Vale (Seabank)

**Numeric Whitelist:** 0,1,2,4,5,7,10,14,16,24,44,45,181,223,226

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 14w+7nb+1b+2lb=24 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+24=226 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 16→50→98→138→144→156→172→191→200→226 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 8≠10→2 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 226−45=181 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 4w+0nb+0b+1lb=5 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Arjun Vale (Seabank) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 226−1(B)−2(LB)=223 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 45−0(B)−1(LB)=44 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 48 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (15 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]