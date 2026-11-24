# B005 T2_hard_excerpt

- hypothesis: If hard-root failures come from long-context dilution, a 3-sentence evidence excerpt will recover both cells; otherwise the failure is field binding/localisation.
- rationale: Full-table validation complete; expand coverage on the next unused hard roots.
- created: 2026-11-17T21:42:40+08:00
- requests: 3 (external API 0)
- scoring: exact integer match per field; task correct iff both target cells correct
- sources: commentary.txt (excerpt), scorecard.md

## Positions

- match_0008 innings 2

## Conditions

E

## Models

- qwen2.5:7b-instruct-q4_K_M
- llama3.1:8b
- gemma2:9b

## Tasks

- match_0008 inn2 E qwen2.5:7b-instruct-q4_K_M (target2) key=8323def0edbe
- match_0008 inn2 E llama3.1:8b (target2) key=8f32662e54af
- match_0008 inn2 E gemma2:9b (target2) key=6fa33250992b

## Rejected candidates

- match_0002 *: root_already_used
- match_0003 *: root_already_used
- match_0009 E: variant_unavailable
- match_0010 E: variant_unavailable
- match_0011 E: variant_unavailable
- match_0013 E: variant_unavailable
- match_0015 E: variant_unavailable
