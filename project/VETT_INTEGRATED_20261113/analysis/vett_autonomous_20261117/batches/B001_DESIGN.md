# B001 A_field_probe

- hypothesis: On the same evidence sentence, asking runs only, wickets only, or both separates field confusion from evidence localisation.
- rationale: smoke test branch A
- created: 2026-11-18T14:49:52+08:00
- requests: 18 (external API 0)
- scoring: exact integer match per field; compare runs-only vs wickets-only vs both by root/model
- sources: commentary.txt (excerpt), scorecard.md

## Positions

- match_0066 innings 1
- match_0085 innings 1

## Conditions

E

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0066 inn1 E qwen2.5:7b-instruct-q4_K_M (probe_runs) key=2c54f7ddbfe8
- match_0066 inn1 E llama3.1:8b (probe_runs) key=c71962169879
- match_0066 inn1 E gemma2:9b (probe_runs) key=fe8175874614
- match_0066 inn1 E qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=0dc1a49d6c4c
- match_0066 inn1 E llama3.1:8b (probe_wickets) key=8901948b3dbb
- match_0066 inn1 E gemma2:9b (probe_wickets) key=ad201e7a14f7
- match_0066 inn1 E qwen2.5:7b-instruct-q4_K_M (probe_both) key=ffe4ed44179a
- match_0066 inn1 E llama3.1:8b (probe_both) key=2156a7ba278e
- match_0066 inn1 E gemma2:9b (probe_both) key=c4bf6b653651
- match_0085 inn1 E qwen2.5:7b-instruct-q4_K_M (probe_runs) key=9e150605c822
- match_0085 inn1 E llama3.1:8b (probe_runs) key=c9c9e4dc369b
- match_0085 inn1 E gemma2:9b (probe_runs) key=a49126dca866
- match_0085 inn1 E qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=2b8f62dfe175
- match_0085 inn1 E llama3.1:8b (probe_wickets) key=8d10406a502f
- match_0085 inn1 E gemma2:9b (probe_wickets) key=55be5b692082
- match_0085 inn1 E qwen2.5:7b-instruct-q4_K_M (probe_both) key=2a86a90b6154
- match_0085 inn1 E llama3.1:8b (probe_both) key=35dc7063150b
- match_0085 inn1 E gemma2:9b (probe_both) key=0ce76b0ed675

## Rejected candidates

- none
