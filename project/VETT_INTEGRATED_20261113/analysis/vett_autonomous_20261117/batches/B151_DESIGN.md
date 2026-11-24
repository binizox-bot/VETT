# B151 ACC_llama_p320

- hypothesis: Isolated config trial: llama probe_wickets with num_predict=320 instead of 200 to test the reproducible length cap.
- rationale: 10 llama probe_wickets results hit done_reason=length at eval_count=200.
- created: 2026-11-19T15:44:02+08:00
- requests: 3 (external API 0)
- scoring: exact integer match; compare parse/length against the frozen 200-budget results
- sources: commentary.txt, scorecard.md

## Positions

- match_0021 innings 1
- match_0022 innings 1
- match_0027 innings 1

## Conditions

O

## Models

- llama3.1:8b

## Tasks

- match_0021 inn1 O llama3.1:8b (probe_wickets_p320) key=9a152c779b78
- match_0022 inn1 O llama3.1:8b (probe_wickets_p320) key=3b2a91b241ec
- match_0027 inn1 O llama3.1:8b (probe_wickets_p320) key=3d14a0926449

## Rejected candidates

- none
