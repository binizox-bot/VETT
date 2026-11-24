# R4 next evaluation protocol

## Frozen input

Use only `package/r4_blind_queries_6.jsonl`. The evaluator must not read the
construction specification, private manifest, scoring instances, gold tables,
oracle, ablations or earlier R3 predictions.

## First gate

Run one strong fixed-schema evaluator at temperature zero/equivalent and retain
raw output. Freeze the prediction SHA-256 before normalization and scoring.

- primary scalar target: at least 8 wrong of 36;
- omission: fewer than 4 of 36;
- errors: at least three joint-constraint mechanisms;
- composite results: reported separately and never used to pass the scalar gate.

If the strong gate fails, revise only the three construction roots and repeat a
fresh shortcut audit. Do not inspect or alter test roots.

## Six-condition matrix after the strong gate

1. Direct without explicit CoT;
2. Direct-CoT;
3. T3 paper direct-integration variant;
4. T3 provenance-enhanced;
5. Map&Make paper-style;
6. Map&Make scope/version-enhanced.

The T3 direct-integration condition must not be described as the paper's main
generated-code path. All conditions use the same backbone, context, output
budget and parser. At least three prompting families must reach 20% primary
scalar error before expansion to six unseen development roots.
