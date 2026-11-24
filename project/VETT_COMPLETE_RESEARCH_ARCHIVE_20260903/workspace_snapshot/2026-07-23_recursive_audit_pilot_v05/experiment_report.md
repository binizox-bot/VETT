# Recursive-audit Text-to-Table pilot v0.5

Date: 2026-07-23

## Outcome

The v0.5 single-match sample exceeds the requested 60% error threshold for
all three controlled baseline families while remaining exactly solvable by the
complete recursive oracle.

| Method | Best tested variant | Correct / 397 | Full error | Core 109-field error | Exact match |
| --- | --- | ---: | ---: | ---: | ---: |
| Complete oracle | full recursive event state | 397 / 397 | **0.00%** | **0.00%** | 1 |
| T³ | count all flat claims | 9 / 397 | **97.73%** | **91.74%** | 0 |
| Map&Make | first claim per oracle-aligned slot | 139 / 397 | **64.99%** | **71.56%** | 0 |
| CoT proxy | packet-first one-pass reasoning | 139 / 397 | **64.99%** | **71.56%** | 0 |
| CoT proxy | recursive source, omitted outcome state | 116 / 397 | **70.78%** | **74.31%** | 0 |
| CoT proxy | state reset at each slot | 91 / 397 | **77.08%** | **78.90%** | 0 |

The core score uses only the original summary, batting, bowling,
fall-of-wickets and partnership tables. Therefore, the high error rates are not
an artifact of adding the 72-row accepted-claim audit table.

## Instance

- target match events: 72;
- conflicting target claims: 288, four per event;
- counterfactual rehearsal packets: 12;
- visible packets: 84, shuffled into arrival order;
- accepted sources: exactly 18 each from Amber, Blue, Cedar and Delta;
- traditional output fields: 109;
- accepted-claim audit fields: 288;
- total scored fields: 397;
- gold final state: uniquely recoverable;
- oracle output: byte-for-byte equal to the gold JSON.

## Construction

Every target slot has four mutually conflicting claims. The accepted source is
not fixed and cannot be selected from local recency or majority. Instead it is
computed sequentially:

```text
accepted source code =
    (previous accepted source code
     + over
     + passage
     + packet nonce
     + previous accepted outcome state value) mod 4
```

The selected claim changes both the previous source and previous outcome state
used at the next slot. This creates a 72-step dependency chain. Packets are
shown out of order, so a system must first recover target scope and canonical
slot order, then execute the chain without dropping provenance.

The HARBOR-7R rehearsal packets use the same venue, players, slot notation and
source vocabulary. Their chain identity must be retained to prevent them from
entering the target score.

## Why T³ fails

The strict T³ diagnostic extracts generalized batter/bowler/outcome tuples.
That representation removes:

- target versus rehearsal chain;
- slot identity and chronological position;
- source identity;
- claim ID;
- packet nonce;
- the link between the accepted claim and the next state.

Counting all flat tuples grossly overcounts mutually exclusive claims.
Deduplicating identical tuples removes genuine repeated cricket events while
still lacking the state needed to select one claim per slot. Code integration
cannot reconstruct fields discarded before the code-generation stage.

## Why Map&Make fails

Map&Make receives optimistic oracle grouping of claims by target slot and the
correct chronological slot order. It still lacks the recursive state-selection
layer. First-claim, last-claim and four fixed-source policies were tested. The
best variant reaches 64.99% full-field error and 71.56% error on the original
five tables.

The failure is non-local: selecting the wrong event changes the score,
individual batter and bowler rows, wicket position and every later partnership
boundary. A monotonic cell-filling process cannot safely revise all dependent
cells without maintaining an event graph and recomputing projections.

## Why one-pass CoT fails

The CoT diagnostics retain target scope, packet grouping and chronological
slot order, making them stronger than the restricted T³ representation. They
test:

1. resetting state at every slot;
2. carrying previous source but omitting previous outcome state;
3. packet-first and packet-last shortcuts;
4. four static-source preferences.

All tested shortcuts exceed 60% error. Even the source-recursive variant
reaches 70.78% full error because omitting the previous accepted outcome
changes later source decisions.

This demonstrates a long-horizon state-tracking failure mode. It does not prove
that every LLM given unlimited reasoning or executable code will fail. The
complete recursive solver reaches 0% error, as it must for a valid benchmark.

## Error propagation for the best conservative variants

| Output table | T³ errors | Map&Make errors | CoT errors |
| --- | ---: | ---: | ---: |
| Summary | 6 / 7 | 5 / 7 | 5 / 7 |
| Batting | 13 / 21 | 13 / 21 | 13 / 21 |
| Bowling | 18 / 18 | 17 / 18 | 17 / 18 |
| Fall of wickets | 15 / 15 | 8 / 15 | 8 / 15 |
| Partnerships | 48 / 48 | 35 / 48 | 35 / 48 |
| Accepted-claim audit | 288 / 288 | 180 / 288 | 180 / 288 |
| **Total** | **388 / 397** | **258 / 397** | **258 / 397** |

## Scientific limitation

These are controlled, deterministic process diagnostics. They are not official
author-code or independent API executions.

- T³ is intentionally restricted to the generalized flat tuple representation.
- Map&Make is represented by optimistic oracle-aligned local update policies.
- CoT is represented by reproducible one-pass/state-ablation policies, not by
  a separately sampled frontier model.
- The audit language is controlled synthetic English rather than naturally
  collected commentary.

The valid claim at this stage is: the constructed information topology causes
the tested T³, Map&Make and CoT process families to exceed 60% error, while a
complete event-state method exactly recovers the answer.

## Next validation

1. Generate at least 30 seeds with different innings, packet orders and nonce
   chains.
2. Paraphrase packets with human annotators while preserving the hidden graph.
3. Run direct, paper-style CoT, self-consistency, T³ and Map&Make using the
   same external backbone, token budget and temperature.
4. Add a code-enabled CoT/Program-of-Thought baseline.
5. Ablate source provenance, slot identity, recursive source state and outcome
   state one at a time.
6. Report core-table error separately from audit-table error, with confidence
   intervals and exact-match rate.
