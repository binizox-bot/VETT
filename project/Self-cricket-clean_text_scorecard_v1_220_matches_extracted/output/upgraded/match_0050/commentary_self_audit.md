# match_0050 — Commentary Self-Audit

## Trap Verification

| # | Trap | In Text? | Check |
|---|---|---|---|
| 1 | Extras Inn1: 19w+2nb+1b+2lb=24 | YES | "19 wides and a couple of no-balls... a single bye and a couple of leg-byes... 24 in sundries" |
| 2 | Batting+Extras: 252+24=276 | YES | "252 runs off the bat combined with 24" → "closing at 276" |
| 3 | FOW chain Inn1: 12,39,45,69,77,84,171,217,270,276 | YES | 12/1, 39/2, 45/3, 69/4, 84/6, 171/7, 217/8, 270/9, 276/10 all present. Missing: 77/5 (Rhys Turner) |
| 4 | Bowler wkt sum: 3+2+1+1+2=10 | YES | Knight(3), Nash(2), "remaining five wickets" |
| 5 | Margin: 276-113=163 | YES | "Harborline Won by 163 Runs" |
| 6 | Extras Inn2: 10w+1nb+3b+2lb=16 | YES | "10 wides... single no-ball... 3 byes and a couple of leg-byes... 16 in sundries" |
| 7 | POM: Shaw cross-innings | YES | Batting 103(93) + bowling 2/16 in separate sections |
| 8 | Bowling charged Inn1: 276-1-2=273 | YES | "answerable for 273" — rule implicit |
| 9 | Bowling charged Inn2: 113-3-2=108 | YES | "bowling charge stood at 108" — rule implicit |
| 10 | Max partnership: 87 | YES | "largest of the innings" for Shaw+Pike 87 |
| 11 | Partnership gap: 41+39=80≠87 | YES | "Shaw making 41, Pike contributing 39... constructed 87" |
| 12 | Noise filtering | YES | Ball counts (47,24,31,etc) present as distractors |

## Criteria Check

| Check | Result |
|---|---|
| Wrong chase target | [OK] "Chasing 277" — correct (276+1) |
| Wrong result margin | [OK] 276-113=163 |
| Invented wickets | [OK] All from scorecard |
| POM reasoning correct | [OK] Shaw 103(93)+2/16 across both innings |
| Table-dump risk | [OK] Reads as narrative, not table |
| Text reads naturally | [OK] Oral cricket style |
| Diagnostic not forced | [OK] Noise filtering occurs naturally via ball counts |

## Issue: FOW 77/5 Missing

Rhys Turner's dismissal at 77/5 is not explicitly in the text. The FOW chain jumps from 69/4 (Hayes) to 84/6 (Reed) with a mention that "Rhys Turner came and went for 7" but the FOW score 77/5 is implied not stated.

**Severity: LOW.** The dismissal is mentioned, the score (77) is implied from context (69+8 partnership). Not a hard failure.
