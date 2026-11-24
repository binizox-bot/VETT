# B002 T2_hard_excerpt

- hypothesis: If hard-root failures come from long-context dilution, a 3-sentence evidence excerpt will recover both cells; otherwise the failure is field binding/localisation.
- rationale: Baseline saturated at 1.0; hard roots and a short excerpt are the next discriminator.
- created: 2026-11-17T21:40:38+08:00
- requests: 6 (external API 0)
- scoring: exact integer match per field; task correct iff both target cells correct
- sources: commentary.txt (excerpt), scorecard.md

## Positions

- match_0002 innings 2
- match_0003 innings 2

## Conditions

E

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0002 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=bc556ad3ee5d
- match_0002 inn2 E llama3.1:8b (target2) key=3b270ac8ffaa
- match_0002 inn2 E gemma2:9b (target2) key=d96956c2d63b
- match_0003 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=662260937605
- match_0003 inn2 E llama3.1:8b (target2) key=9327610c501b
- match_0003 inn2 E gemma2:9b (target2) key=77abaaedf797

## Rejected candidates

- none
