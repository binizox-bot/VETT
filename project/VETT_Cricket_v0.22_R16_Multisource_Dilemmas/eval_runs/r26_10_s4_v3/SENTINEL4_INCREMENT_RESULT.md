# R26.10 four-match GLM increment: stopped after first protocol failure

- Requested scope: four new matches using only `zai-org/GLM-5.3-Flash`
- Planned order: `match_0067`, `match_0021`, `match_0162`, `match_0220`
- Attempted: 1/4
- Officially scoreable: 0/4
- Stop policy: first terminal batch failure
- Actual cost: CNY 0.115863

## `match_0067`

- Evidence-role protocol: `edge_derived_v3`
- Requested/returned targets: 5/5
- Finish reason: `length`
- Output tokens: 12,288 (configured maximum)
- Provider truncation: yes
- JSON closure repair required: yes (`}`)
- Batch status: `INVALID_OUTPUT`
- Official score: none

The meaningful response content ended after the five-item `decision_predictions` array. The model
then emitted 14,959 trailing whitespace characters while the schema still required a top-level
`instance_id`, reached the output-token ceiling, and never closed the outer object. Because the
frozen contract excludes truncation and JSON repair, the output cannot be scored or recovered for
official or factual-diagnostic use.

The remaining three matches were not requested. Continuing unchanged would have risked repeated
paid truncations. Increasing the token limit, changing batch size, accepting closure repair, or
changing the response wrapper would alter the tested protocol and therefore was not done silently.
