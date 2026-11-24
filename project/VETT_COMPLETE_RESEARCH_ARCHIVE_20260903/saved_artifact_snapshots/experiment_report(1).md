# Versioned-event Text-to-Table pilot v0.4

Date: 2026-07-23

## Dataset instance

- canonical target-match events: 72
- visible multi-source mentions: 162
- revision chains: 30
- duplicate/replay mentions: 24
- stale replay mentions after final rulings: 18
- out-of-scope youth/archive mentions: 18
- output fields: 109 across five tables
- final event state: uniquely specified by the authoritative scorer rulings

The visible text contains no event IDs. The hidden event graph stores mention,
event, source, role, arrival order, initial state and final state.

## Self-test results

The best result for each method is selected from two reasonable strict
no-state policies.

| Method | Variant | Correct | Error fields | Field error rate | Table EM |
| --- | --- | ---: | ---: | ---: | ---: |
| T³ | count every flat tuple | 10 / 109 | 99 | 90.83% | 0 |
| T³ | deduplicate identical flat tuples | 15 / 109 | 94 | **86.24%** | 0 |
| Map&Make | keep first proposition per event | 23 / 109 | 86 | 78.90% | 0 |
| Map&Make | keep last proposition per event | 26 / 109 | 83 | **76.15%** | 0 |

Both methods exceed the requested 60% field-error threshold even after choosing
their better tested policy.

## Best-variant error distribution

| Table | T³ errors | Map&Make errors |
| --- | ---: | ---: |
| Summary | 3 | 3 |
| Batting | 15 | 8 |
| Bowling | 14 | 10 |
| Fall of wickets | 15 | 15 |
| Partnerships | 47 | 47 |
| **Total** | **94** | **83** |

## T³ protocol

The strict generalized tuple representation retains:

- batter;
- bowler;
- event outcome.

It discards:

- event identity;
- source;
- arrival versus canonical order;
- INITIAL/DUPLICATE/FINAL/STALE/OUT_OF_SCOPE role;
- revision links.

Two integration policies were tested:

1. count all extracted flat tuples;
2. remove exact duplicate tuples before counting.

The second policy performs better but also removes real repeated events that
share the same batter, bowler and outcome. Neither flat tuple multiset supports
reconstruction of canonical FOW or partnership order.

## Map&Make protocol

To avoid understating Map&Make, the diagnostic gives it hidden oracle alignment
between propositions and canonical events. It still receives no versioned
event state.

Two iterative filling policies were tested:

1. retain the first proposition for each event;
2. retain the last proposition for each event.

The first policy preserves obsolete initial reports. The last policy is harmed
by stale replay packets arriving after final rulings. Without an explicit
version/source hierarchy, neither simple monotonic policy recovers final state.

The resulting independent event facts also lack a recovered canonical event
sequence, leaving FOW and partnership tables unresolved.

## Interpretation

The v0.3 numerical reconciliation benchmark favored T³ because generated code
could solve a clean tuple matrix. v0.4 moves the bottleneck before numerical
integration:

1. decide whether a mention is a new event or a replay;
2. determine target-match scope;
3. link revisions to their event;
4. distinguish final rulings from stale later packets;
5. reconstruct canonical event order;
6. only then aggregate tables.

Code generation cannot repair identity, version and ordering information after
the Text-to-Tuple representation has discarded it. Proposition-by-proposition
table filling similarly cannot implement non-monotonic state replacement
without an event/version layer.

## Important limitation

These numbers are controlled process self-tests, not executions of the authors'
exact model/API configurations.

- T³ is intentionally constrained to the flat tuple representation described
  by its official prompting framework.
- Map&Make is represented by two strict no-state update policies rather than an
  independent API model sample.
- The commentary is controlled synthetic text, not yet human-paraphrased
  natural commentary.

Therefore 86.24% and 76.15% demonstrate that the constructed representation
stress case exceeds the requested threshold. They are not yet publishable
population estimates for the named methods.

## Next validation

1. Generate at least 30 independently seeded v0.4 instances.
2. Human-paraphrase correction and replay mentions without changing event
   links.
3. Run official prompts with the same external backbone and decoding budget.
4. Add enhanced T³ tuples with event/source/version fields as an ablation.
5. Add Map&Make with oracle version links as an ablation.
6. Report mean, standard deviation, confidence intervals and per-operator
   errors.
