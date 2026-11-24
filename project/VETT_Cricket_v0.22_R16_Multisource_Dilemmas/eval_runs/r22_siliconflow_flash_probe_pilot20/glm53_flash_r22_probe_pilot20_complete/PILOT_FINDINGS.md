# R22 GLM-5.3-Flash Pilot Findings

## Scope

- Model: `zai-org/GLM-5.3-Flash`
- Provider: SiliconFlow OpenAI-compatible Chat Completions API
- Dataset: R22 pilot, 20 matches
- Evaluated track: Track B only, 500 evidence probes
- Matrix: 5 difficulty levels x 5 target families x 20 matches
- Track A table reconstruction was intentionally not run in this cost-controlled pilot.

## Reproducibility settings

- Temperature: 0.1
- Top-p: 0.95
- Thinking enabled; thinking budget: 8,192
- One batch of 25 probes per match
- Automatic retries: disabled
- Primary maximum output: 24,576 tokens
- `match_0220` recovery maximum output: 32,768 tokens after the primary response was truncated
- Recorded successful-call cost: CNY 3.365486
- A failed truncated attempt returned no usable usage object, so its provider-side charge is not included in the recorded total.

## Main results

| Metric | Result |
| --- | ---: |
| Fact answer macro / exact accuracy | 57.20% (286/500) |
| Answer plus decisive-proof exact (ASP) | 13.20% (66/500) |
| Decisive span F1 | 69.67% |
| Decisive edge F1 | 61.22% |
| Provenance span F1 | 2.15% |
| Provenance edge F1 | 0.86% |
| Brier score | 0.412633 |

The strong-model fact ceiling criterion of 65% is met for this economical proxy model.

## Difficulty-level calibration

| Level | Fact accuracy | ASP |
| --- | ---: | ---: |
| L1 | 79.00% | 39.00% |
| L2 | 63.00% | 14.00% |
| L3 | 67.00% | 12.00% |
| L4 | 46.00% | 1.00% |
| L5 | 31.00% | 0.00% |

| Adjacent pair | Accuracy drop | Required |
| --- | ---: | ---: |
| L1 to L2 | 16 points | >= 8 points |
| L2 to L3 | -4 points | >= 8 points |
| L3 to L4 | 21 points | >= 8 points |
| L4 to L5 | 15 points | >= 8 points |

Overall difficulty passes, but adjacent-level calibration fails because L3 is four points easier than L2. The next revision should harden L3 rather than simplify L2, preserving the no-regression requirement.

## Target-family calibration

| Target family | Fact accuracy | ASP |
| --- | ---: | ---: |
| cell_value | 93.00% | 7.00% |
| consistency_provenance | 25.00% | 11.00% |
| derived_indicator | 60.00% | 14.00% |
| entity_scope | 74.00% | 19.00% |
| event_state | 34.00% | 15.00% |

Fact extraction and proof construction are measuring different capabilities: cell values are usually recovered, but their complete decisive proofs are rarely produced. Consistency/provenance and event-state answers are already very difficult. The low provenance F1 shows that the model frequently confuses minimal decisive proof with non-decisive source-history context.

## Decision

R22 is sufficiently difficult overall and its proof metrics reveal failures hidden by answer accuracy. It is not yet fully calibrated as a five-level benchmark because L2 and L3 are inverted and target-family difficulty is imbalanced.

Recommended R23-compatible adjustment without reducing existing difficulty:

1. Harden L3 `cell_value`, `derived_indicator`, and `event_state` probes with branch-dependent resolution, qualifier-dependent computation, and multiple locally plausible terminal values.
2. Keep L4 and L5 contracts unchanged; their separation is already strong.
3. Preserve the difficult consistency/provenance probes, but report family-stratified scores so they do not dominate a single undifferentiated average.
4. Standardize future runs on a 32,768-token maximum output to avoid truncated structured responses.
5. Validate the revised pilot on at least one flagship model in addition to the economical Flash proxy before making a paper-level strong-model claim.
