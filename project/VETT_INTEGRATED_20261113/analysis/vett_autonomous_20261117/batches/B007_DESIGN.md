# B007 T5_hard_fulltext

- hypothesis: When a hard root has no explicit total sentence, the excerpt variant is unavailable; full-text O on unused hard roots tests whether the failure is excerpt-specific or a genuinely unanswerable field.
- rationale: No remaining hard root has an explicit total sentence for E; run full-text O on unused hard roots instead.
- created: 2026-11-17T21:43:41+08:00
- requests: 6 (external API 0)
- scoring: exact integer match per field; task correct iff both target cells correct
- sources: commentary.txt, scorecard.md

## Positions

- match_0009 innings 2
- match_0010 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0009 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=9bc5be920282
- match_0009 inn2 O llama3.1:8b (target2) key=83c965aed484
- match_0009 inn2 O gemma2:9b (target2) key=66ce31293a1f
- match_0010 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=3e6740201e7f
- match_0010 inn2 O llama3.1:8b (target2) key=f826da7345c6
- match_0010 inn2 O gemma2:9b (target2) key=eb06546d3893

## Rejected candidates

- match_0002 *: root_already_used
- match_0003 *: root_already_used
- match_0008 *: root_already_used
