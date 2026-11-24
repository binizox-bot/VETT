# B124 P_field_sweep

- hypothesis: Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.
- rationale: Condition sweep exhausted; field-probe coverage takes over.
- created: 2026-11-19T03:31:29+08:00
- requests: 36 (external API 0)
- scoring: exact integer match per field; coverage group kept separate from diagnostic branches
- sources: commentary.txt, scorecard.md

## Positions

- match_0036 innings 1
- match_0036 innings 2
- match_0037 innings 1
- match_0037 innings 2

## Conditions

O

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0036 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=b33492808a6b
- match_0036 inn1 O llama3.1:8b (probe_runs) key=0b208e4c2299
- match_0036 inn1 O gemma2:9b (probe_runs) key=396eb4d269d4
- match_0036 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=012718f03f89
- match_0036 inn1 O llama3.1:8b (probe_wickets) key=c0469e0f2bb4
- match_0036 inn1 O gemma2:9b (probe_wickets) key=43670d9e33b9
- match_0036 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=d158ea222784
- match_0036 inn1 O llama3.1:8b (probe_both) key=f612c5946656
- match_0036 inn1 O gemma2:9b (probe_both) key=fd0b0b691e49
- match_0036 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=e2fa2d3786c9
- match_0036 inn2 O llama3.1:8b (probe_runs) key=0cf57f653754
- match_0036 inn2 O gemma2:9b (probe_runs) key=12026cdce0d6
- match_0036 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=b8f4f72a125c
- match_0036 inn2 O llama3.1:8b (probe_wickets) key=9b5cc64a5c70
- match_0036 inn2 O gemma2:9b (probe_wickets) key=8638c65e5a0d
- match_0036 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=715557b44a30
- match_0036 inn2 O llama3.1:8b (probe_both) key=8a790ed15009
- match_0036 inn2 O gemma2:9b (probe_both) key=c74282f4e737
- match_0037 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=55266a318525
- match_0037 inn1 O llama3.1:8b (probe_runs) key=b2cf856a6fde
- match_0037 inn1 O gemma2:9b (probe_runs) key=b34e08b92c51
- match_0037 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=86236a0a572a
- match_0037 inn1 O llama3.1:8b (probe_wickets) key=cfc0741157e8
- match_0037 inn1 O gemma2:9b (probe_wickets) key=33b65e91e861
- match_0037 inn1 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=26891ca1680c
- match_0037 inn1 O llama3.1:8b (probe_both) key=376b8abdeb81
- match_0037 inn1 O gemma2:9b (probe_both) key=d905a9702390
- match_0037 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_runs) key=a853ffefdd63
- match_0037 inn2 O llama3.1:8b (probe_runs) key=786787a91736
- match_0037 inn2 O gemma2:9b (probe_runs) key=b5e5b3d2f680
- match_0037 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_wickets) key=59ad9a1f9858
- match_0037 inn2 O llama3.1:8b (probe_wickets) key=45750412804e
- match_0037 inn2 O gemma2:9b (probe_wickets) key=3be51a1c2777
- match_0037 inn2 O qwen2.5:7b-instruct-q4_K_M (probe_both) key=a87f2bed359a
- match_0037 inn2 O llama3.1:8b (probe_both) key=915e67e51506
- match_0037 inn2 O gemma2:9b (probe_both) key=dc00c7e72588

## Rejected candidates

- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
- match_0035 O: duplicate_existing_task
