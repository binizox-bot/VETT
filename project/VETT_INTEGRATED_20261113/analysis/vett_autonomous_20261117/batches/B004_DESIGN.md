# B004 T4_full_table

- hypothesis: If target cells saturate on an excerpt but the 43-field table does not, the model has collateral field loss that target cells hide.
- rationale: WI 0.0 < OI 0.5; deletion-specific damage, validate the full table on original text.
- created: 2026-11-17T21:41:48+08:00
- requests: 3 (external API 0)
- scoring: exact match per field; report 43-field accuracy and target-cell subset
- sources: commentary.txt, scorecard.md

## Positions

- match_0002 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0002 inn2 O qwen2.5:7b-instruct-q4_K_M (full43) key=82cad8c713bb
- match_0002 inn2 O llama3.1:8b (full43) key=fc5f1f345bfb
- match_0002 inn2 O gemma2:9b (full43) key=43bb9e2fe0d1

## Rejected candidates

- none
