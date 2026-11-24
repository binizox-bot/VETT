# VETT-Cricket R18 Adversarial Hardening Pilot

## Release decision

**PASS** — 6/6 instances passed every machine gate.

## Hardening results

- Direct answers are distributed across at least five documents per instance.
- Maximum direct-answer concentration in one document: 21.43%
- Identifier-normalized unique five-word openings: 80.23%
- Most common normalized opening: 1.16%
- Claim values must be stated in their hashed public span.
- Quoted or negated edge phrases are rejected.

| Public-only shortcut | Correct | Accuracy |
| --- | ---: | ---: |
| sealed_genre_or_text | 0/84 | 0.00% |
| fixed_t32 | 0/84 | 0.00% |
| latest_amendment | 18/84 | 21.43% |
| single_span_amendment | 0/84 | 0.00% |
| amendment_template_family | 0/84 | 0.00% |
| terminal_lexicon | 0/84 | 0.00% |

These deterministic attacks are release gates, not proof that a language model cannot solve the task. No external blind model run or human naturalness audit was performed.
