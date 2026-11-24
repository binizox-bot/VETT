# B003 T3_matched_deletion

- hypothesis: If deleting the same-innings mid-score (WI) costs more than deleting a matched unrelated sentence (OIC) or the other-innings total (OI), the target cell depends on that specific sentence.
- rationale: Excerpt still fails at 0.833; matched deletion controls on the failing hard root.
- created: 2026-11-17T21:41:06+08:00
- requests: 9 (external API 0)
- scoring: exact integer match per field; paired comparison is treatment minus O on the same root/model/field
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0002 innings 2

## Conditions

O, WI, OI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0002 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=8a04091cd698
- match_0002 inn2 O llama3.1:8b (target2) key=a5907e1a0336
- match_0002 inn2 O gemma2:9b (target2) key=60991ce0fa84
- match_0002 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=f0637438c580
- match_0002 inn2 WI llama3.1:8b (target2) key=58a3db2c792e
- match_0002 inn2 WI gemma2:9b (target2) key=5b91129768c3
- match_0002 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=7eda944f2379
- match_0002 inn2 OI llama3.1:8b (target2) key=45fa8d92a12f
- match_0002 inn2 OI gemma2:9b (target2) key=7224adc26e1b

## Rejected candidates

- none
