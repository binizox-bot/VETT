# Baseline execution protocol

The prompt templates preserve the published decomposition of T³ and
Map&Make while adapting the domain ontology and output contract to cricket.

Required controls:

1. use the same model backbone and context/output budgets;
2. temperature 0 for deterministic evaluation;
3. freeze prompts on the calibration split;
4. store raw model output, normalized output, prompt hash, model version and run date;
5. never allow T³ integration code to re-read source documents;
6. parsers may repair JSON formatting only, never values;
7. report fixed-schema and latent-schema settings separately;
8. label proxy or self-simulation results explicitly; do not describe them as
   official reproductions.
9. run V1, V2 and V3 separately and report deltas rather than only a pooled
   score;
10. report cell accuracy/error, table exact, schema F1, row alignment,
    hallucination, omission, revision accuracy, derived-cell accuracy and
    target-scope accuracy;
11. do not tune prompts on the frozen test split or change test instances after
    inspecting method outputs.

Predictions must be JSONL with one object per line:

```json
{
  "instance_id": "match_0128.V3",
  "method": "mapmake_cricket_adapted",
  "model": "MODEL_VERSION",
  "tables": []
}
```

The files named `diag_*` under `validation/` are controlled oracle ablations.
They measure the consequence of deleting a capability and must not be listed
as T³, Map&Make or Direct-CoT performance.
