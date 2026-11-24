# Model-assisted generation protocol

Models assist with discourse planning, verbalization, inverse extraction and
adversarial review. They never choose canonical values.

## Pass 1: discourse planner

Input:

- canonical events selected by the private recipe;
- source roles and arrival order;
- required operators;
- forbidden construction phrases.

Output:

- document plan;
- event-to-document assignment;
- revision and source precedence plan;
- no surface prose.

## Pass 2: verbalizer

Input:

- approved plan;
- immutable fact records;
- target style.

Output:

- English documents;
- fact-to-character-span map.

The verbalizer must preserve every number, entity, innings, source status and
revision relation. It may not add cricket facts.

## Pass 3: inverse extractor

The inverse extractor sees only generated documents. It returns claims with:

```json
{
  "entity": "",
  "attribute": "",
  "value": "",
  "innings": "",
  "source": "",
  "version": 1,
  "status": "valid",
  "evidence_quote": ""
}
```

Generated text fails if the inverse claims cannot reconstruct the intended
ledger or if multiple values remain valid.

## Pass 4: adversarial critic

The critic searches for:

- ambiguity;
- unsupported gold cells;
- unintended answer leakage;
- template fingerprints;
- inconsistent source authority;
- revision wording that permits multiple final states;
- grammatical or cricket-usage errors;
- facts added during paraphrase.

## Required independence

The same prompt response cannot serve as both verbalizer output and final
verification. Prefer a different model family for inverse extraction when
available. When only one family is available, use independent contexts and
different role prompts, then require symbolic and human verification.

## Forbidden shortcuts

- exposing table coordinates such as `Batting[1].R`;
- mentioning `source game`, `scorecard fingerprint`, `synthetic sample` or
  construction recipes in model input text;
- generating prose directly from hidden gold tables without recording a
  fact-to-span map;
- using T³, Map&Make or Direct-CoT outputs to decide gold values;
- modifying a frozen test version after observing baseline outputs.

## Current candidate status

The deterministic renderer establishes evidence completeness and exact spans.
Its prose is a draft. Model-assisted naturalization and human verification are
required before public release.
