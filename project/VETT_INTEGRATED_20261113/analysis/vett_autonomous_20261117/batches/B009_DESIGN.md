# B009 T5_hard_fulltext

- hypothesis: When a hard root has no explicit total sentence, the excerpt variant is unavailable; full-text O on unused hard roots tests whether the failure is excerpt-specific or a genuinely unanswerable field.
- rationale: Baseline saturated at 0.917; hard roots and a short excerpt are the next discriminator. | fallback: T2_hard_excerpt produced no eligible task; executed T5_hard_fulltext.
- created: 2026-11-17T21:47:23+08:00
- requests: 6 (external API 0)
- scoring: exact integer match per field; task correct iff both target cells correct
- sources: commentary.txt, scorecard.md

## Positions

- match_0011 innings 2
- match_0013 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0011 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=b8e724789c7d
- match_0011 inn2 O llama3.1:8b (target2) key=af8adafa6adb
- match_0011 inn2 O gemma2:9b (target2) key=dd95d6d41f24
- match_0013 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=7afb1e48aad4
- match_0013 inn2 O llama3.1:8b (target2) key=ed485aa3e65a
- match_0013 inn2 O gemma2:9b (target2) key=bf4851d64c28

## Rejected candidates

- match_0002 *: root_already_used
- match_0003 *: root_already_used
- match_0008 *: root_already_used
- match_0009 *: root_already_used
- match_0010 *: root_already_used
- match_0011 E: variant_unavailable
- match_0013 E: variant_unavailable
- match_0015 E: variant_unavailable
- match_0002 *: root_already_used
- match_0003 *: root_already_used
- match_0008 *: root_already_used
- match_0009 *: root_already_used
- match_0010 *: root_already_used
