# B011 T5_hard_fulltext

- hypothesis: When a hard root has no explicit total sentence, the excerpt variant is unavailable; full-text O on unused hard roots tests whether the failure is excerpt-specific or a genuinely unanswerable field.
- rationale: Baseline saturated at 1.0; hard roots and a short excerpt are the next discriminator. | fallback: T2_hard_excerpt produced no eligible task; executed T5_hard_fulltext.
- created: 2026-11-17T21:49:32+08:00
- requests: 3 (external API 0)
- scoring: exact integer match per field; task correct iff both target cells correct
- sources: commentary.txt, scorecard.md

## Positions

- match_0015 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0015 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=c3a470fed7e6
- match_0015 inn2 O llama3.1:8b (target2) key=c6b5fde79b7e
- match_0015 inn2 O gemma2:9b (target2) key=5962978a3b26

## Rejected candidates

- match_0002 *: root_already_used
- match_0003 *: root_already_used
- match_0008 *: root_already_used
- match_0009 *: root_already_used
- match_0010 *: root_already_used
- match_0011 *: root_already_used
- match_0013 *: root_already_used
- match_0015 E: variant_unavailable
- match_0002 *: root_already_used
- match_0003 *: root_already_used
- match_0008 *: root_already_used
- match_0009 *: root_already_used
- match_0010 *: root_already_used
- match_0011 *: root_already_used
- match_0013 *: root_already_used
