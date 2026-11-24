# R12 direct chain-recovery check

R12 extends the hallucination/evidence-chain idea from R11 to three independent roots and three different public topologies:

- `match_0042`: correction log
- `match_0100`: archive crosswalk
- `match_0069`: exception appendix

The public blind package contains 15 documents, 425 segments, 10,630 whitespace-tokenized words, 319 scored atomic cells, 957 false claims, and 319 true candidate claims. All public target cells are blank.

## Structural audit

`R12_SELFTEST.json` passes all checks:

- public/private cell IDs match;
- all public targets are null;
- all decoys differ from gold;
- every positive and negative segment exists;
- every cell has at least a three-hop evidence route;
- every route crosses multiple documents;
- candidate position is balanced;
- weak strategies fail as intended.

Weak strategy errors:

| Strategy | Errors / total | Error rate |
| --- | ---: | ---: |
| Oracle chain following | 0 / 319 | 0.00% |
| First mention | 319 / 319 | 100.00% |
| Latest mention | 319 / 319 | 100.00% |
| Source-blind majority | 319 / 319 | 100.00% |
| Always first candidate | 161 / 319 | 50.47% |
| Always second candidate | 158 / 319 | 49.53% |

## Direct recovery result

A direct recovery prediction was frozen before reading private gold:

- prediction file: `runs_gpt55/direct/predictions.json`
- SHA-256: `a110d25509dda744bf4b14fc4fe3e7a1f146cf2e8683b2a715e0526c6ea3bad8`
- freeze file: `GPT55_R12_DIRECT_FREEZE.json`

Strict exact-value scoring reports a large error rate because the frozen prediction serializes numeric cells as JSON numbers while the gold stores atomic values as strings.

| Metric | Strict exact score |
| --- | ---: |
| Correct cells | 29 / 319 |
| Cell error rate | 90.91% |
| Exact rows | 14 / 67 |
| Row exact rate | 20.90% |

This strict score is not a good factual-failure measure for this run. A string-normalized diagnostic comparison gives:

| Metric | String-normalized diagnostic |
| --- | ---: |
| Correct cells | 317 / 319 |
| Cell error rate | 0.63% |
| Exact rows | 65 / 67 |
| Row exact rate | 97.01% |

The two remaining errors are both output syntax errors where the final right parenthesis was dropped:

| Instance | Cell | Expected | Predicted |
| --- | --- | --- | --- |
| `r12_match_0100_archive_crosswalk` | `match_metadata.result.value` | `Southport Won By 7 Wickets (Winners)` | `Southport Won By 7 Wickets (Winners` |
| `r12_match_0069_exception_appendix` | `match_metadata.result.value` | `Northbridge Won by 96 Runs (D/L Method)` | `Northbridge Won by 96 Runs (D/L Method` |

## Interpretation

R12 succeeds as a mechanical hallucination-chain stress test but fails as a hard model benchmark. The generated documents still expose highly regular chain language:

- correction log: “first/second transcription” plus accepted log key;
- archive crosswalk: first/second digest entry plus blue/copper shelf;
- exception appendix: worksheet-traced first/second reading plus active appendix item.

Those phrases make the intended operator recoverable by a shallow symbolic parser. The decoys are numerous and locally plausible, but the adjudication language is too explicit and too repeated.

Therefore R12 should be treated as a useful negative result: adding more false claims and multi-hop chains is insufficient if the chain topology itself is machine-readable.

## R13 design target

R13 should keep the R12 strengths:

- multi-root design;
- atomic columns;
- 3:1 false-to-true claim ratio;
- multi-document positive and negative evidence;
- public/private separation;
- automatic evidence and uniqueness checks.

But R13 must remove the explicit selection grammar. Recommended changes:

1. Replace “first/second” with event-specific paraphrases such as “the leaf carrying the registration stamp,” “the update whose checksum matches the scorer envelope,” or “the entry whose over count survives the innings aggregate.”
2. Stop making every group share one topology-wide operator. Mix at least four adjudication operators inside each instance.
3. Add distractor authority claims that are authoritative for one table but not another, so global source ranking is insufficient.
4. Require at least one cross-row or cross-table conservation proof for 30%–40% of cells.
5. Score strings and numbers through a typed normalizer, while separately tracking serialization failures.
6. Do not count a run as a mainstream-model result unless the prediction is produced by an isolated non-scoring context and frozen before private read.

Current research judgment: R12 is mechanically sound but not benchmark-hard. R13 should prioritize naturalized adjudication and mixed operators over simply increasing hallucination density.
