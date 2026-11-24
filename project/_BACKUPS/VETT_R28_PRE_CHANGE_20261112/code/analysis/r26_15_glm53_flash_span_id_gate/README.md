# R26.15 Edge-6 single-match gate

The authorized `match_0066` request completed normally and cost CNY 0.100569.
It returned all five requested objects with `finish_reason=stop` and no truncation,
but failed the exact-evidence-ID gate on one L3 question.

The earlier legacy-prefix defect is resolved: the response no longer rewrote all
public `s_...` identifiers as `r26:s_...`. Instead, the model emitted one
syntactically valid but nonexistent identifier,
`s_f5fabb32713c0a259c7efa6f`, apparently while trying to cite the public
Ward–Foster cross-reference whose actual ID is
`s_f5fab32713c0a259c7efa622`.

This is a genuine exact-copy/evidence-grounding failure by the tested model. The
raw response is preserved, no identifier was repaired, and there is no official
semantic score. A separate factual-only diagnostic reports 20% record macro
accuracy, 58.3333% decision-field accuracy, and 0% paired factual/counterfactual
exactness; these values are non-official and cannot be used as benchmark results.

No retry and no remaining Sentinel5 request are justified under the frozen gate.
Before spending more, the benchmark should preregister whether an unknown but
well-formed span ID invalidates the whole five-question batch or is retained as a
per-question semantic false positive. The observed response must not be
retroactively rescued under whichever policy is selected.
