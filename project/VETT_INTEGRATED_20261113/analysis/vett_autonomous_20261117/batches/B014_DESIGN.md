# B014 T1_baseline_o

- hypothesis: Target cells on development roots are near ceiling under original text; this is the baseline for escalation.
- rationale: Cross-innings branch complete; expand the baseline to remaining development roots.
- created: 2026-11-18T14:52:49+08:00
- requests: 6 (external API 0)
- scoring: exact integer match per field; task correct iff both target cells correct
- sources: commentary.txt, scorecard.md

## Positions

- match_0183 innings 1
- match_0184 innings 1

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0183 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=10f18bd953ba
- match_0183 inn1 O llama3.1:8b (target2) key=912e563e9820
- match_0183 inn1 O gemma2:9b (target2) key=1b9d805cb287
- match_0184 inn1 O qwen2.5:7b-instruct-q4_K_M (target2) key=979fa597e334
- match_0184 inn1 O llama3.1:8b (target2) key=e7ee60d8e881
- match_0184 inn1 O gemma2:9b (target2) key=aee3814ef8e7

## Rejected candidates

- match_0066 *: root_already_used
- match_0085 *: root_already_used
- match_0087 *: root_already_used
- match_0096 *: root_already_used
- match_0165 *: root_already_used
- match_0021 *: root_already_used
