# R26.8 protocol-v2 repair report

Date: 2026-10-19

## Scope and spending

This revision changes only local schemas, validation, diagnostic recovery, panel reporting, tests and future-run configuration. It made no model API request and added no external cost. The cumulative recorded external cost remains CNY 0.094473 from the earlier staged gates.

## Failure converted into a regression contract

The GLM gate returned all five targets without truncation, but one `rejected_evidence_spans` array contained `"],"` followed by seven copies of `"state"`. A minimal exact fragment is now stored in `tests/fixtures/r26_glm53_rejected_array_corruption.json`.

The regression requires all of the following detections:

1. repeated rejected-evidence IDs;
2. IDs absent from the public dossier;
3. disagreement between `rejected_evidence_spans` and the targets of `rejects` edges.

## Protocol hardening

- The per-request schema now fixes the exact `instance_id`, exact requested question-ID enum and exact target count.
- R26 span IDs must match the R25/R26 identifier grammar. JSON property names, prose and empty strings cannot satisfy the schema.
- Local validation independently checks public-span membership even if a provider ignores its JSON Schema.
- Evidence-edge endpoints must be a public span, the current question node or its declared decision sink.
- The rejected-span set must equal the set of targets reached by `rejects` edges.
- Positive spans, rejected spans and edges are non-empty, unique and bounded.
- Decision records, counterfactual records, state objects, confidence and explanation are validated locally for exact field sets, types, enums and array bounds.
- The prompt explicitly forbids field names and padding inside evidence arrays and instructs the model to close each array once.
- Successful per-batch checkpoints are the authoritative analysis source. A missing or damaged aggregate `predictions.jsonl` can no longer turn a valid checkpoint into a false model zero; inconsistent or missing checkpoints fail with `LOCAL_ARTIFACT_INTEGRITY` instead.

## Strict official/diagnostic separation

An invalid batch remains invalid. It is never promoted to an official score merely because some fields are readable.

A factual-only diagnostic is permitted only when every condition holds:

- provider returned every requested target;
- no output truncation;
- no parse error;
- every validation error belongs to an explicit evidence-only allowlist;
- normalized factual and state structures are complete.

The resulting diagnostic excludes all evidence metrics, does not increment `models_scoreable`, does not enter difficulty gates and is labelled non-official in JSON and Markdown reports. Unknown future validation errors fail closed and prohibit diagnostic recovery.

Applied to the saved GLM response, the official coverage remains 0/1 while the non-official factual diagnostic reports 20% full-record accuracy and 75% decision-field accuracy.

## Verification

- Targeted repair tests: pass.
- Full test suite: 118/118 pass in 40.713 seconds.
- Python compilation check: pass.
- Twenty-match local Oracle gate: 20/20 batches valid, 100/100 questions fully correct.
- Oracle factual, counterfactual, positive-span, rejected-span, typed-edge and complete-chain metrics: all 100%.

## Prepared but not executed

`eval_configs/r26_8_gate3_glm53_flash_match0066_protocol_v2.json` is a new-run-ID single-match gate. Its conservative zero-cache estimate is CNY 0.1419 and its hard ceiling is CNY 0.20. It has not been sent to the provider.

The next paid request is not necessary until the user explicitly resumes testing. Expanding to four more GLM matches, adding other paid models, changing dataset difficulty and scaling R26.7 to 220 matches remain gated on a fully valid strong-model response.
