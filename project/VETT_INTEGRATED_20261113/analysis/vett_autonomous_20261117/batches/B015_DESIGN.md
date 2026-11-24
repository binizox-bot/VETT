# B015 T3_matched_deletion

- hypothesis: If deleting the same-innings mid-score (WI) costs more than deleting a matched unrelated sentence (OIC) or the other-innings total (OI), the target cell depends on that specific sentence.
- rationale: Baseline below 0.90 at 0.833; drill into the failing roots with matched deletion controls.
- created: 2026-11-18T14:53:23+08:00
- requests: 9 (external API 0)
- scoring: exact integer match per field; paired comparison is treatment minus O on the same root/model/field
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0003 innings 2

## Conditions

O, OI, WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0003 inn2 O qwen2.5:7b-instruct-q4_K_M (target2) key=5126e2f561da
- match_0003 inn2 O llama3.1:8b (target2) key=4ed3f4aa40ff
- match_0003 inn2 O gemma2:9b (target2) key=0c30a80b7e30
- match_0003 inn2 WI qwen2.5:7b-instruct-q4_K_M (target2) key=9ffd0b891a49
- match_0003 inn2 WI llama3.1:8b (target2) key=5642cfc13e20
- match_0003 inn2 WI gemma2:9b (target2) key=7653622bf4fa
- match_0003 inn2 OI qwen2.5:7b-instruct-q4_K_M (target2) key=000497040248
- match_0003 inn2 OI llama3.1:8b (target2) key=d48df02f7921
- match_0003 inn2 OI gemma2:9b (target2) key=010b2133b7cf

## Rejected candidates

- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 O: duplicate_existing_task
- match_0184 WI: variant_unavailable
- match_0184 OI: variant_unavailable
- match_0002 O: duplicate_existing_identity
- match_0002 O: duplicate_existing_identity
- match_0002 O: duplicate_existing_identity
- match_0002 WI: duplicate_existing_identity
- match_0002 WI: duplicate_existing_identity
- match_0002 WI: duplicate_existing_identity
- match_0002 OI: duplicate_existing_identity
- match_0002 OI: duplicate_existing_identity
- match_0002 OI: duplicate_existing_identity
