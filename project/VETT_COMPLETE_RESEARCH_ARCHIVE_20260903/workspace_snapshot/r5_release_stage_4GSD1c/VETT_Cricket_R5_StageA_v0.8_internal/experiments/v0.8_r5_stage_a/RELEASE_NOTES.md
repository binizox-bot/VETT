# VETT Cricket R5 Stage-A internal evaluation package

## Scope

This package contains 12 clean-room development instances for complete
fixed-schema cricket text-to-table reconstruction. It includes public source
packets and blank tables, private gold tables, private evidence graphs,
construction snapshots, a complete-table scorer, an oracle-format test and the
mechanical self-test report.

## Evaluation boundary

The public file is `package/r5_stage_a_public_12.jsonl`. Evaluators must not read
files containing `private`, the private manifest, readable gold tables, oracle
predictions or oracle scores before producing predictions.

The construction and audit processes know the gold state. Controlled display
ablations in the self-test measure failure mechanisms only. They are not model
accuracy results.

## Current decision

The package passes its structural, leakage, evidence-span, derivation-oracle and
scorer-oracle tests. It is approved for fresh blind model evaluation. It still
requires independent naturalness review and independent human full-table
recovery before any paper release or expansion to the full 220-root corpus.
