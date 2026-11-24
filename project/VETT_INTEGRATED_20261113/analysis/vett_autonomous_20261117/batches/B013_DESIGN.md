# B013 B_cross_innings

- hypothesis: With the innings fixed explicitly, compare original, sufficient excerpt, deletion of the other-innings score, and a matched non-evidence deletion to test cross-innings binding.
- rationale: Field probe complete; move to cross-innings binding with explicit innings.
- created: 2026-11-18T14:52:31+08:00
- requests: 3 (external API 0)
- scoring: exact integer match per field; paired by root/model against O
- sources: commentary.txt variants, scorecard.md

## Positions

- match_0002 innings 2

## Conditions

OIC

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0002 inn2 OIC qwen2.5:7b-instruct-q4_K_M (target2) key=7dc9c3f9b1fc
- match_0002 inn2 OIC llama3.1:8b (target2) key=980a214d5dec
- match_0002 inn2 OIC gemma2:9b (target2) key=debb69d865c0

## Rejected candidates

- match_0002 O: duplicate_existing_identity
- match_0002 O: duplicate_existing_identity
- match_0002 O: duplicate_existing_identity
- match_0002 E: duplicate_existing_identity
- match_0002 E: duplicate_existing_identity
- match_0002 E: duplicate_existing_identity
- match_0002 OI: duplicate_existing_identity
- match_0002 OI: duplicate_existing_identity
- match_0002 OI: duplicate_existing_identity
