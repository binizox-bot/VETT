# R26.11 request-bound response protocol

## Scope

This change addresses the `match_0067` Gate-4 transport failure without changing
the questions, public evidence, private gold, scorer, or evidence semantics.  It
does not retroactively make the failed response scoreable.

The evidence-role protocol remains `edge_derived_v3`.  A separate response-envelope
protocol, `request_bound_v2`, removes only the redundant top-level `instance_id`
from the model response.  The new evaluation contract is
`R26-C3-EDGE-5-REQUEST-BOUND`.

## Observed failure and causal change

The paid `match_0067` response returned all five requested question IDs and then
generated trailing whitespace until the 12,288-token limit.  Its constrained schema
still required a top-level `instance_id` after `decision_predictions`; closing the
object at that point was therefore illegal.  JSON repair added `}`, but the run
correctly remained `INVALID_OUTPUT` because it was truncated, repaired, and missing
the required legacy identity field.

`request_bound_v2` makes the model response contain only `decision_predictions`.
After the fifth prediction, `}` is a valid schema-complete termination.  Raising the
token limit is not the primary remedy because whitespace could consume any finite
increase while adding cost and no evidence content.

## Identity and anti-mixing guarantees

Removing the response copy of `instance_id` does not make identity implicit or
unverifiable:

1. The request record and public payload retain the exact `instance_id`.
2. The checkpoint path is namespaced by that expected instance.
3. The request hash covers the release path, instance, exact target-ID set, bounded
   response schema, prompts, and generation settings.
4. The response schema enumerates only the requested question IDs and requires the
   exact number of predictions.
5. Normalization rejects missing, duplicate, and unexpected question IDs, validates
   every cited public span and graph node, and rejects a conflicting legacy
   `instance_id` if a provider emits one anyway.
6. The final output row receives `instance_id` from the trusted request context, not
   from model text.

The protocol is deliberately allowed only for `r26_decision + edge_derived_v3`.
Existing configurations default to `explicit_instance_v1`, so archived contracts and
results do not change.

## Local acceptance gates

- Response schema has no top-level `instance_id` property or requirement.
- Request record and input payload still carry the expected instance identity.
- Prediction array has equal `minItems` and `maxItems`, and question IDs are an enum
  of the exact requested set.
- Missing response identity is accepted only under `request_bound_v2`; an explicitly
  conflicting identity remains invalid.
- Oracle execution produces five valid predictions, an `OK` checkpoint, contract
  metadata, and a final row bound to the expected match.
- Full regression remains green under the legacy default.

Local replay of the five normalized predictions preserved in the historical
`match_0067` checkpoint under `request_bound_v2` returns five targets with zero
structural validation errors.  This supports the diagnosis, but the historical run
remains invalid because the provider reported `finish_reason=length` and JSON closure
repair was required; replay is diagnostic evidence, not retroactive rescoring.

## Re-request decision rule

Do not resume the four-match run.  If the local gates pass, at most one new paid
request for `match_0067` is justified using
`eval_configs/r26_11_gate5_glm53_match0067_request_bound_v2.json`.  It has no automatic
retry, a distinct run/checkpoint namespace, a CNY 0.20 preflight ceiling, and a CNY
0.18 recorded-cost ceiling.  Only after this response is schema-complete and
scoreable should the remaining three previously approved matches be reconsidered.
