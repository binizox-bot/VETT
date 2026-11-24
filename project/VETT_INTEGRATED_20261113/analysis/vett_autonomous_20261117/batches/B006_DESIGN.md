# B006 T3_matched_deletion

- hypothesis: If deleting the same-innings mid-score (WI) costs more than deleting a matched unrelated sentence (OIC) or the other-innings total (OI), the target cell depends on that specific sentence.
- rationale: Excerpt still fails at 0.833; matched deletion controls on the failing hard root.
- created: 2026-11-17T21:42:54+08:00
- requests: 3 (external API 0)
- scoring: exact integer match per field; paired comparison is treatment minus O on the same root/model/field
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0008 innings 2

## Conditions

O, WI, OI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0008 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=8295933a57de
- match_0008 inn2 O llama3.1:8b (target2) key=70b72796ad10
- match_0008 inn2 O gemma2:9b (target2) key=b52c2ec3699a

## Rejected candidates

- match_0008 WI: variant_unavailable
- match_0008 OI: variant_unavailable
