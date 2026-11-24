# t14 smoke2 diagnosis (8 items)

Run: `runs/t14_smoke2` — 22 model calls, 5.886 s, 224.26 calls/min, 0 cloud, ¥0.

## T1 (frozen T1v1, stratified)

| class | n | visible=true | agreement |
|---|---:|---:|---:|
| POS_OVERRIDE | 3 | 3/3 | 1.0 |
| NEG_PROVENANCE_ADJACENT | 4 | 0/4 | 1.0 |
| NEG_PLAIN | 1 | 0/1 | 1.0 |

Overall 8/8. The D2 dose=1 review-lock item (r28q_0193) correctly falls in NEG_PROV and is answered false.

## T2 (frozen T2.naturalness_pair.v1, ordinal preference)

- 6/8 preference correct; 1 tie, 1 inverted.
- Per corruptor: duplicate_tokens 2/2, shuffle_middle 2/2, function_word_swap 2/2, **half_splice 0/2**.
- Absolute scores (descriptive only): clean mean 3.75, degraded mean 2.5.
- Both failures are `half_splice` on **two-sentence** excerpts:

`r28q_0193` natural = sentence A + sentence B; half_splice at word midpoint swaps at the
sentence boundary, so the "corrupted" text is just B + A — fully natural. Model scores 4/4 (tie).
`r28q_0305` same: two parallel-incident sentences; swapped halves stay natural; model 3/4.

The corruptor is not doing what the construct check needs on multi-sentence excerpts.
Recommendation: for `half_splice`, use a **single long span** (one sentence) so the midpoint
swap breaks grammar; keep the other three as-is, re-audit (no GPU), rerun this 8-item smoke
(8 T2 calls), then full. This preserves the four t18 corruption types but makes half_splice a
real unnaturalness manipulation.

## S1 (frozen S1v4 + mechanical PROVENANCE)

- 5 OK model labels (BOWLING 1, DISMISSAL 1, IDENTITY 1, RUNS 2)
- 2 mechanical PROVENANCE (authority_policy spans)
- 1 DEGRADED `PARSE_FAILURE`: model echoed the enum literal
  `{"topic": "RUNS|DISMISSAL|BOWLING|IDENTITY"}` instead of choosing; parser correctly refused,
  event has reason_code + fallback_used. No silent skip.

## Decision needed

(a) fix half_splice to single-span excerpts, re-audit + rerun 8-item smoke, then full; or
(b) run full as-is and report per-corruptor (half_splice will remain an invalid manipulation).
