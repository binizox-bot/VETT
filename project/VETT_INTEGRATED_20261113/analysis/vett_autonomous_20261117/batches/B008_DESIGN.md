# B008 T1_baseline_o

- hypothesis: Target cells on development roots are near ceiling under original text; this is the baseline for escalation.
- rationale: Hard full-text fallback complete; expand the baseline to the remaining unused development roots.
- created: 2026-11-17T21:44:09+08:00
- requests: 6 (external API 0)
- scoring: exact integer match per field; task correct iff both target cells correct
- sources: commentary.txt, scorecard.md

## Positions

- match_0087 innings 1
- match_0096 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0087 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=b02208f4c13b
- match_0087 inn1 O llama3.1:8b (target2) key=36aad653ada6
- match_0087 inn1 O gemma2:9b (target2) key=ae6cfea2b0dd
- match_0096 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=2a69ca71de9e
- match_0096 inn1 O llama3.1:8b (target2) key=9d827fd16d3c
- match_0096 inn1 O gemma2:9b (target2) key=3a63ce828b76

## Rejected candidates

- match_0066 *: root_already_used
- match_0085 *: root_already_used
