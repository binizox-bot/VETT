# R26.15 exact span-ID protocol correction

## Outcome of the authorized check

The authorized Sentinel5 run stopped after two provider requests, exactly as required
by the fail-closed contract. `match_0021` was structurally valid. `match_0066`
returned all five questions, with `finish_reason=stop` and no truncation, but was
correctly rejected because every cited `s_<24hex>` public span ID had been rewritten
as `r26:s_<24hex>`.

The two requests cost CNY 0.225815 in total. The remaining three matches were not
requested. This stopped run must not be reported as a five-match difficulty result.

## Root cause

The runner's R26 system prompt retained a legacy statement that every evidence ID
must begin with `r25` or `r26`. The current R26.15 release instead uses role-neutral
IDs of the exact form `s_<24 lowercase hexadecimal characters>`. The model's hidden
reasoning explicitly noticed this contradiction, while its constrained final output
nevertheless added `r26:`. This is an evaluation-protocol defect, not evidence that
the dataset is too hard and not a gold-label conflict.

## Correction

The prompt now requires byte-for-byte copying from
`documents[].spans[].span_id`, forbids adding or removing release prefixes, and
states the neutral ID shape only when all public IDs in the actual request have that
shape. The instruction is derived solely from public input and reveals no private
evidence roles. For role-neutral requests, the constrained response schema is also
narrowed to `s_<24hex>` evidence IDs plus the exact requested query/decision nodes,
so a provider cannot satisfy the schema with an invented `r26:s_...` node.

Because prompt semantics changed, the contract version is now
`R26-C3-EDGE-6-EXACT-SPAN-ID-COPY`. Historical Edge-5 responses are preserved but
must not be pooled with Edge-6 results. The evaluator continues to reject unknown
IDs; it does not silently strip `r26:` or otherwise repair model semantics.

## Economical recheck

The authorized Edge-6 `match_0066` gate made one request, cost CNY 0.100569, and
returned all five objects without truncation. It no longer produced the erroneous
`r26:s_...` prefix. It did, however, invent one well-formed but nonexistent `s_...`
identifier in the L3 evidence chain, so the strict validator correctly returned
`INVALID_OUTPUT`. No retry or remaining Sentinel5 request was made.

This gate separates the two causes: the mass prefix rewrite was a runner defect and
is fixed; the remaining one-ID hallucination is a model exact-copy/evidence-grounding
failure. The response remains unmodified and has no official semantic score.

The direct R26 analysis entry point is now protocol-aware as well: invalid instances
are reported as excluded coverage rather than being silently counted as wrong model
answers. The one valid historical match remains available only as an exploratory
diagnostic; it is not pooled with corrected-contract results.
