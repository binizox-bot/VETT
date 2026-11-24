# R21 Economy Evaluation Plan

## Objective

Measure answer and evidence-chain quality without spending tokens on repeated context,
unbounded reasoning, or blind retries. Cost controls are part of the evaluation contract;
they do not remove targets or relax scoring.

## Primary model protocol

- Model: `zai-org/GLM-5.3-Flash`
- Provider: SiliconFlow Chat Completions
- Target batch size: 60 for the full release
- Thinking budget: 8,192 tokens per batch
- Final-output ceiling: 24,576 tokens per batch
- Automatic retries: disabled
- Resume: enabled through request-hashed batch checkpoints
- Preflight cost ceiling: CNY 1 for one-match calibration and CNY 30 for all 20

## Token controls

1. Public documents precede requested targets in the serialized prompt. The long prefix is
   identical across batches and is therefore eligible for provider prompt caching.
2. A 100-target calibration batch reduced repeated input but omitted one requested target.
   The full-release setting therefore uses 60 targets per batch. Repeated document prefixes
   remain cacheable, so the reliability improvement costs much less than a zero-cache estimate.
3. Thinking is bounded at 8,192 tokens. The flagship calibration used about 128,835
   reasoning tokens across four batches; most of that output spend did not appear in the
   submitted evidence graph.
4. `max_retries=0` prevents a timeout or malformed response from silently causing another
   paid request. Failures are reviewed before resubmission.
5. Every successful batch is saved immediately with a SHA-256 fingerprint. An interrupted
   run resumes completed batches without calling the model again. Changing the model,
   prompt, schema, or generation parameters invalidates the checkpoint.

## Preflight and release stages

1. Run `estimate`; it assumes zero cache hits and blocks a run above its configured CNY
   ceiling.
2. Calibrate on `match_0066` and compare against the completed GLM-5.3 flagship result.
3. Calibrate the conflict-heavy `match_0067`; the completed run cost CNY 0.265698,
   achieved 66.53% answer accuracy, and revealed one omitted target at 100 targets per batch.
4. If answer accuracy, evidence F1, and JSON reliability are acceptable, run the 20-match
   Flash evaluation.
5. Retain the flagship GLM-5.3 only as a three-match upper-bound experiment: easy,
   conflict-heavy, and maximum-length.

## Commands

```powershell
$env:PYTHONPATH = "src"
python -m vett_eval.cli estimate --config eval_configs/r21_siliconflow_glm53_flash_economy_one.json
python -m vett_eval.cli run --config eval_configs/r21_siliconflow_glm53_flash_economy_one.json
```

The estimate is conservative and is not a provider quote. Final reports use the provider's
returned usage fields and the prices recorded in the run configuration.
