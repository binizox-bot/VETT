# VETT-Cricket v0.3 baseline experiment protocol

## Frozen order of operations

1. Run all methods on the 18-root development split.
2. Parse every final response into the common table JSON contract.
3. Report failures to parse as complete omissions, not discarded examples.
4. Compare methods on identical inputs, backbone, temperature and output budget.
5. Inspect errors by view and mechanism.
6. Modify difficulty only on development roots.
7. Freeze prompts and the next dataset version.
8. Run the 20-root test split once for the paper result.

## Method matrix

The first experiment uses one backbone and six prompting configurations:

- direct prompting without explicit reasoning;
- Direct-CoT;
- paper-style T3 tuples without source/version provenance, using the paper's
  direct-integration variant;
- provenance-enhanced T3;
- paper-style MapMake atomization/schema/update;
- scope-and-version-enhanced MapMake.

This separates a method family's original representational limitations from a
stronger cricket-aware adaptation. The enhanced variants must not be reported
as the original paper methods.

The paper's main T3 code-integration path is separately blocked until generated
Python can run in a reviewed, resource-limited and network-isolated sandbox.
The direct-integration result must not be relabeled as the main code variant.

## Difficulty curriculum

| Level | Input condition | Primary mechanism |
| --- | --- | --- |
| L1 | V1 | fixed state, direct evidence |
| L2 | V2 | provisional/corrected/stale claims |
| L3 | V3 without scoring derived cells | multi-source scope and latent schema |
| L4 | full V3 | global derivation plus cross-match distractor |
| L5 | future paired operator view | one additional operator at a time |

L5 may add source-authority conflict, longer-distance evidence, paraphrastic
numeric expression, extra distractor documents or schema variation, but only
one controlled operator per paired instance. Difficulty is accepted only when:

- human reviewers retain at least 90% cell accuracy;
- unique-solution and evidence-completeness checks pass;
- multiple method families degrade, not one hand-picked baseline;
- the effect reproduces on unseen development roots;
- construction-style classification does not become easier.

## Metrics

Report cell error, table exact, omission and hallucination for every method and
view. Also report revision accuracy, derived-cell accuracy, target-scope
accuracy, schema F1 and parse-failure rate. Never select a method's best
parseable subset.

## Reproducibility record

Each run must retain model identifier, provider, date, temperature, output
budget, prompt-template hash, input hash, raw stage outputs, normalized final
tables and parser logs. A run with missing raw outputs is not paper-grade.

## Current execution blocker

An isolated same-model three-root probe has now been completed and is recorded
in `experiments/v0.3_dev_baseline/ISOLATED_PROBE_RESULTS.md`. It is suitable for
difficulty and scorer calibration, but it is not an official paper baseline:
the sample has only three roots, all runs use one model family, and the T3
paper-style condition uses the direct-integration variant rather than the
generated-code main path. Full dev and test claims still require an independent
model endpoint or equivalent reproducible batch runner.
