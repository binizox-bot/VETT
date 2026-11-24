# CoT self-test summary

## Protocol

The official T³ paper's zero-shot CoT baseline adds:

> Let's think step by step! At last, please output a table ...

to the direct full-text-to-table prompt and uses temperature 0.

This local test uses the same full visible `v04_case.txt` and the same
109-field schema as the previous T³ and Map&Make diagnostics. It is a
current-model, deterministic, executable reasoning upper bound rather than an
independent API sample of the paper's historical models.

The compact reasoning policy was:

1. retain only target-match primary passages;
2. treat delayed replays as duplicate mentions rather than new events;
3. index the 72 primary passages by over and within-over position;
4. apply all 30 authoritative final scorer rulings to those indexed passages;
5. reject stale cache, youth and archive packets;
6. project the recovered ordered event sequence into summary, batting,
   bowling, fall-of-wickets and partnership tables.

The prediction was written before the scorer opened `v04_gold.json`.

## Result

| Method | Correct | Errors | Field error rate | Table EM |
| --- | ---: | ---: | ---: | ---: |
| Current-model structured CoT upper bound | 109 / 109 | 0 | **0.00%** | 1 |

## Interpretation

Version 0.4 is not difficult enough for a strong reasoner that retains the
full text. The text explicitly supplies all three pieces needed to recover the
final state:

- authoritative source identity;
- exact revision address (`over + ordinal passage`);
- explicit labels for duplicates, stale material and out-of-scope packets.

The high T³ and Map&Make proxy error rates therefore diagnose loss of
identity/version/order in their restricted intermediate representations. They
do not establish that the underlying instance is hard for unrestricted CoT.

## Required v0.5 changes

To challenge CoT without making the gold ambiguous, the next dataset should
remove local shortcut labels and make the final state recoverable only through
global evidence:

1. replace explicit `final`, `stale`, `different match` labels with
   source-specific reliability rules learned from demonstrations;
2. replace exact over/ordinal revision addresses with semantic references
   spanning several mentions;
3. interleave passages so chronological order must be reconstructed from
   clocks, score deltas and strike continuity;
4. include mutually incompatible but locally plausible event graphs;
5. make only one graph satisfy innings totals, batter totals, bowler totals,
   wickets, partnerships and source constraints simultaneously;
6. include counterfactual distractors that share players, venue and near-equal
   timestamps, preventing keyword-based scope filtering;
7. evaluate both answer fields and intermediate event-link/version decisions.

The target should be measured on an independently sampled model run. A
self-authored deterministic solver can be used for validation, but not as the
sole publishable CoT baseline.
