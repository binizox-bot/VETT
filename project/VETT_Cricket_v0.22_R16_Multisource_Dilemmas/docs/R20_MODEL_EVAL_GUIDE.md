# R20/R21 Unified Model Evaluation Guide

The runner keeps model execution separate from scoring. Each run preserves raw responses,
normalized predictions, batch failures, latency and the exact model identifier supplied by
the evaluator.

The same runner auto-detects R20 value-only releases and R21 value-plus-evidence releases.

## Adapters

- `openai_responses`: calls the Responses API with strict Structured Outputs.
- `command`: sends one JSON request to an external command on standard input and expects
  one JSON response on standard output. This is the provider-neutral integration point.
- `oracle`: reads private gold and is permitted only with `test_only: true`; it is for
  pipeline verification and must never be reported as a model result.

The OpenAI adapter follows the official recommendation to use JSON Schema Structured
Outputs rather than unconstrained JSON. It records incomplete calls as batch failures and
does not silently substitute missing predictions.

## Run

```powershell
$env:PYTHONPATH = "src"
python -m vett_eval.cli run --config eval_configs/r20_openai_example.json
python -m vett_eval.cli analyze-r20 `
  --release dataset_r20_220 `
  --run eval_runs/r20_models/<run_id>

python -m vett_eval.cli run --config eval_configs/r21_openai_example.json
python -m vett_eval.cli analyze-r21 `
  --release r21_pilot `
  --run eval_runs/r21_models/<run_id>
```

Replace the exact model ID and set the API key environment variable before a real run.
Model availability and reasoning options are account-dependent. Never put a key in the
configuration file.

## External command protocol

The configured command receives a JSON object containing `system_prompt`, `user_prompt`,
`response_schema`, `instance_id`, `target_ids`, and batch metadata. It must return:

```json
{
  "instance_id": "match_0001",
  "predictions": [
    {"target_id": "match_0001.I1.batting.r001.r", "value": "17"}
  ]
}
```

## Error taxonomy

- `STALE_REVISION`: selected a value explicitly superseded in the evidence graph.
- `ROW_MISALIGNMENT`: copied a valid value from another row in the same table/column.
- `CROSS_INNINGS_CONFUSION`: copied a corresponding value from another innings.
- `FORMAT_ONLY`: semantically equal after conservative case/punctuation normalization.
- `UNSUPPORTED_VALUE`: no controlled explanation above applies.
- `MISSING_CELL` / `EXTRA_CELL`: output completeness failures.

Always publish the exact prompt, model ID, reasoning effort, batch size, retry policy,
failure count and whether tools were permitted.
