# B021 B2_matched_control

- hypothesis: Length-matched non-evidence deletion controls for B003: NEI_OI matched to the 364-char other-innings sentence, NEI_WI matched to the 269-char mid-score sentence.
- rationale: B003 O/WI/OI lacked a closely length-matched non-evidence control; B013 OIC deleted only 234 chars vs OI 364.
- created: 2026-11-18T15:07:37+08:00
- requests: 6 (external API 0)
- scoring: exact integer match per field; pair NEI against historical O and against the corresponding WI/OI deletion
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0002 innings 2

## Conditions

NEI_OI, NEI_WI

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0002 inn2 NEI_OI qwen2.5:7b-instruct-q4_K_M (target2) key=4c6a3a79a38e
- match_0002 inn2 NEI_OI llama3.1:8b (target2) key=422b7f926235
- match_0002 inn2 NEI_OI gemma2:9b (target2) key=f47560a290ed
- match_0002 inn2 NEI_WI qwen2.5:7b-instruct-q4_K_M (target2) key=562015f8adf8
- match_0002 inn2 NEI_WI llama3.1:8b (target2) key=f95188185f3c
- match_0002 inn2 NEI_WI gemma2:9b (target2) key=fce141f4a8d8

## Rejected candidates

- none
