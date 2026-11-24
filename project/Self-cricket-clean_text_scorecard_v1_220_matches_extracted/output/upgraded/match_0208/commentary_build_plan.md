# match_0208 — Commentary Build Plan

**Harborvale** | 172/10 (38.5 Overs) vs 149/10 (46.0 Overs) | 23 runs | POM: Lucas Hart

**Numeric Whitelist:** 0,1,2,5,10,14,16,18,20,23,38,46,146,149,169,172

## Core (7)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 1 | 14w+1nb+1b+2lb=18 | Extras paragraph — operands across three clauses | D2 [OK] |
| 2 | bat_sum+18=172 | Cross-paragraph: batting sum in extras para, total in innings close | D2 [OK] |
| 3 | 22→83→87→88→119→122→126→129→143→172 | Scattered across innings narrative at each wicket fall | D2 [OK] |
| 4 | 10≠10→0 non-bowler | Bowling summary paragraph — sum all bowler wicket counts | D2 [OK] |
| 5 | 172−149=23 | Closing paragraph — result margin calculation | D2 [OK] |
| 6 | 16w+1nb+1b+2lb=20 | Chase extras paragraph — same structure as Inn1 extras | D2 [OK] |
| 7 | Lucas Hart — verify contribution across both innings | Cross-innings: batting contribution in innings narrative, bowling in chase narrative | D3 [OK] |

## Hard (5)

| # | Trap | Placement | Difficulty |
|---|---|---|---|
| 8 | 172−1(B)−2(LB)=169 | Extras paragraph — rule implicit, never explained | D3 [OK] |
| 9 | 149−1(B)−2(LB)=146 | Chase extras paragraph — same implicit rule as Inn1 | D3 [OK] |
| 10 | 61 | Partnership description — identify max from all stand values | D2 [OK] |
| 11 | computed from max partnership | Partnership paragraph — detect striker+non-striker sum != partnership runs | D2 [OK] |
| 12 | ~30 numbers in text, ~22 canonical | Throughout text — ~30 non-canonical numbers, model must filter to canonical only | D3 [OK] [DIAGNOSTIC] |

## Verification

- Hard trap placement: [OK]
- Diagnostic downgrade (Trap12): [DIAGNOSTIC]
- Numeric whitelist complete: [OK] (16 values)
- Unsupported numbers: [OK] (zero)
- Chase target vs margin: [OK]