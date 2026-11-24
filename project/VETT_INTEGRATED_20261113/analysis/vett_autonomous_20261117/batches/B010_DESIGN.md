# B010 T1_baseline_o

- hypothesis: Target cells on development roots are near ceiling under original text; this is the baseline for escalation.
- rationale: Hard full-text fallback complete; expand the baseline to the remaining unused development roots.
- created: 2026-11-17T21:47:51+08:00
- requests: 6 (external API 0)
- scoring: exact integer match per field; task correct iff both target cells correct
- sources: commentary.txt, scorecard.md

## Positions

- match_0165 innings 1
- match_0021 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0165 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=e3c6d64d255b
- match_0165 inn1 O llama3.1:8b (target2) key=6a5722ba3528
- match_0165 inn1 O gemma2:9b (target2) key=4d631d3dfb0e
- match_0021 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=4d5aa4360221
- match_0021 inn1 O llama3.1:8b (target2) key=53860df14514
- match_0021 inn1 O gemma2:9b (target2) key=20c88a28fb27

## Rejected candidates

- match_0066 *: root_already_used
- match_0085 *: root_already_used
- match_0087 *: root_already_used
- match_0096 *: root_already_used
