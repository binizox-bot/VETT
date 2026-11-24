# Natural dense-reconciliation Text-to-Table pilot

Date: 2026-07-22

## Result

Strict Map&Make-process self-test:

- correct fields: **71 / 109**
- field accuracy: **65.14%**
- field error rate: **34.86%**
- supported-cell blank rate: **34.86%**
- table exact match: **0**

All 38 errors were supported-but-unresolved blanks rather than unsupported
cells.

## Error distribution

| Table | Errors |
| --- | ---: |
| Summary | 2 |
| Batting runs | 7 |
| Bowling runs conceded | 6 |
| Fall-of-wicket scores | 5 |
| Partnership runs/extras/end scores | 18 |
| **Total** | **38** |

The 71 correct fields were the parts invariant to OCR selection: legal balls,
balls faced, wickets, dismissal identities, bowler wicket credits, partnership
participants and partnership boundaries.

## Sample construction

- 12 overs and 72 legal deliveries
- 24 OCR-conflicted delivery clips
- two readings per conflicted clip
- 24 natural scorer-reconciliation statements
- evidence types:
  - combined totals across selected overs;
  - combined totals across selected half-overs;
  - combined totals in marked delivery cells;
  - grouped batter runs;
  - grouped bowler chargeable runs;
  - grouped leg-bye totals.

The reconciliation coefficient matrix has full rank 24. Therefore the public
input has one real solution and one binary solution. The blank cells are not
caused by incomplete or ambiguous gold evidence.

## Map&Make protocol

The prediction followed:

1. atomic proposition extraction;
2. schema construction;
3. proposition-by-proposition table filling.

It did not add a matrix solver, SAT/ILP solver, versioned event ledger,
NEW/DUPLICATE/REVISE classifier or post-hoc consistency repair.

This follows the high-level pipeline in the official
[Map&Make paper](https://aclanthology.org/2025.acl-long.1460/), but the reported
number is a fixed-current-model self-test. It is **not** an execution of the
authors' exact model/API configuration.

## Difficulty calibration

The earlier natural-checkpoint v0.1 instance used 20 conflicted clips and 15
mostly temporal checkpoints. It scored 109/109, or 0% field error. Those
constraints could be eliminated progressively.

The dense v0.3 instance kept the same table size but changed the evidence
topology. Its 24 equations overlap across non-local event groups, causing the
strict proposition-by-proposition pipeline to leave 38 downstream cells blank.

The observed failure is therefore associated with **global constraint
topology**, not merely longer input.

## Required next validation

Before making a paper-level performance claim:

- generate at least 30 samples per difficulty point;
- sweep 16, 20, 24, 28 and 32 conflicted events;
- fix model versions, prompts, temperature and output budget;
- run the authors' official prompts with the same backbone as competing
  methods;
- repeat each instance at least three times;
- report mean, standard deviation and bootstrap confidence intervals;
- retain a natural-only test split without marked-delivery audit sheets.
