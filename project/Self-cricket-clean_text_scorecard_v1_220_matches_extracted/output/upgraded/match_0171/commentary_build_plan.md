# match_0171 — Commentary Build Plan

**Coastal Rangers** | 146/10 (43.1 Overs) vs 140/10 (41.5 Overs) | 6 runs | POM: Leo Hart (Coastal Rangers)

**Numeric Whitelist:** 0,1,2,5,6,10,11,12,17,21,41,43,137,140,145,146

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 11w+0nb+0b+1lb=12 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+12=146 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 46→84→96→102→102→112→125→133→143→146 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 9≠10→1 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 146−140=6 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 17w+1nb+2b+1lb=21 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Leo Hart (Coastal Rangers) — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 146−0(B)−1(LB)=145 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 140−2(B)−1(LB)=137 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 46 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]