# T³ versus strict Map&Make on natural pilot v0.3

Date: 2026-07-23

## Same-instance result

| Method | Correct fields | Field accuracy | Field error | Blank rate | Table EM |
| --- | ---: | ---: | ---: | ---: | ---: |
| Strict Map&Make-process self-test | 71 / 109 | 65.14% | 34.86% | 34.86% | 0 |
| T³ code-integration self-test | 109 / 109 | 100% | 0% | 0% | 1 |

Both methods received the same case, output schema, gold file and deterministic
field scorer.

## T³ execution

The implementation follows the official three-stage structure:

1. **Text-to-Tuple**
   - 72 event tuples;
   - 24 reconciliation tuples.
2. **Information Integration**
   - generated numerical consolidation logic;
   - constructed a 24 × 24 coefficient matrix;
   - verified matrix rank 24;
   - solved all 24 clip readings;
   - maximum reconciliation residual: 0.
3. **Tuple-to-Table**
   - projected integrated events into summary, batting, bowling,
     fall-of-wickets and partnership tables.

The integration stage did not read `pilot_v03_gold.json`.

## Why T³ passed

The pilot's hard component is a globally coupled numerical reconciliation
system. Strict proposition-by-proposition Map&Make filling had no explicit
global constraint state and left 38 dependent cells blank.

T³ explicitly permits code generation in its default information-integration
stage. Once text was converted into accurate tuples, the dense equations became
a standard numerical consolidation problem. The resulting integrated event
tuples were sufficient to populate every downstream table.

## Important limitation

This is a fixed-current-model process self-test, not the authors' exact API
configuration. The Text-to-Tuple stage was serialized by model-generated
parsing code because the pilot language follows controlled templates. This
gives T³ a near-perfect tuple-extraction setting.

Consequently, the result demonstrates:

- the current v0.3 instance challenges strict Map&Make;
- it does **not** challenge T³ when tuple extraction is clean and generated
  integration code can execute.

It does not establish a general 0% T³ error rate on free-form natural
commentary.

## Dataset implication

To challenge both methods, future samples must move uncertainty before or
across tuple extraction:

- multiple sentences referring to the same event without stable delivery keys;
- duplicated and stale feeds that look like new events;
- corrections that retract or change earlier tuples;
- entity aliases and mistaken batter/bowler attribution;
- one correction changing event identity, not only a numeric value;
- scope conflicts between target match, archive ticker and neighboring match;
- non-monotonic corrections that require deletion or tuple replacement;
- constraints whose variables depend on resolving event coreference first.

This creates a two-level problem:

1. recover the correct versioned event graph;
2. solve the numerical constraints over that graph.

T³'s generated integration code cannot recover information that was omitted,
duplicated or assigned to the wrong event during Text-to-Tuple extraction.

## Method source

The method structure follows the official
[T³ paper](https://aclanthology.org/2024.emnlp-main.523/), which defines
Text-to-Tuple, Information Integration and Tuple-to-Table stages and uses code
generation as the default integration approach.
