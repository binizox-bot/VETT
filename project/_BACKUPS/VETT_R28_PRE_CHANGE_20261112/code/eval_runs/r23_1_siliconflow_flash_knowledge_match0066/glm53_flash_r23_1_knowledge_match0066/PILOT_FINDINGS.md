# R23.1 One-Match GLM-5.3-Flash Findings

## Run scope and cost

- Model: `zai-org/GLM-5.3-Flash`
- Instance: `match_0066`
- Evaluated track: Track C only (five rule/text questions); Track D and the R22 probes were intentionally not run.
- Requests: one successful batch, no retry and no invalid output.
- Usage: 82,741 input tokens and 2,653 output tokens.
- Actual cost: CNY 0.073621, below the CNY 0.15 hard preflight ceiling.

## Results

- Rule-answer exact accuracy: 5/5 = 100%.
- Reasoning-atom micro F1: 100%.
- Decisive-span micro F1: 92.31% (one required span missed).
- Misleading-span micro F1: 40.00% (all two true misleading spans found, but six false-positive spans were added).
- Answer + reasoning + evidence joint exact: 2/5 = 40%.

Question outcomes were three `ANSWER_AND_REASONING_CORRECT_EVIDENCE_WRONG` cases at L1–L3 and two `FULLY_CORRECT` cases at L4–L5.

## Objective interpretation

The rule-answer component is currently too easy for this model on this sample: it is far above the intended strong-model fact-answer target of 65% or lower. The evidence component exposes a genuine weakness: the model repeatedly assigned correct evidence from other rule scenarios to the current question's misleading-evidence set, and on L2 also omitted one complementary decisive span. This is cross-question scope contamination rather than a cricket-law memory failure.

The 40% joint score should not be treated as sufficient proof of calibrated difficulty. It combines a useful evidence-scope failure with an exact-set criterion, and the sample contains only one question per level. The observed ordering (L4–L5 correct, L1–L3 incorrect) does not demonstrate monotonic five-level difficulty.

To remove a possible instruction ambiguity, the unified runner and future generated questions now state explicitly that evidence from another rule scenario is irrelevant rather than misleading and must be omitted. This run was not repeated after the clarification, so it remains an honest record of the original prompt.

## Decision

Do not expand this Track C design unchanged to 220 matches. Keep the text-embedding mechanism, but increase answer-level difficulty with more independent laws, multi-law interactions, exceptional conditions and locally scoped playing conditions. Then run a small multi-match calibration before full generation. Evidence-role metrics should remain separate from fact-answer accuracy so evidence difficulty cannot disguise an answer task that is too easy.
