# R15 iteration history

## Provenance gate

The 220-match source archive contains `commentary.txt`, `scorecard.md`, `evidence_chain.md`, and `meta.json`, but no observed delivery JSON. The available R6 ledger builder and ledger payload both explicitly identify delivery order as constrained synthetic data. R15 therefore branched into a synthetic mechanism-stress track instead of presenting the ledger as natural evidence.

## R15-A1: unused root `match_0034`

- Static feasibility label: strict event reversible.
- Canonical scale: 489 cells and 94 source events.
- Result: no ledger or progress certificate after a 120-second compute budget.
- Disposition: `FAIL_SOLVER_TIMEBOUND`.

The run was interrupted rather than allowed to consume an unbounded budget. No partial output was promoted.

## R15-A2: unused root `match_0186`

- Static feasibility label: strict event reversible.
- Canonical scale: 407 cells and 77 source events.
- Result: no ledger or progress certificate after a 60-second compute budget.
- Disposition: `FAIL_SOLVER_TIMEBOUND`.

This second failure showed that smaller canonical scale did not guarantee acceptable solver latency. R15 reused the previously validated `match_0031` ledger strictly for mechanism testing; the root is not counted as independent.

## R15-B1: conservation-equivalent pairs with positional bias

- 68 scored cells.
- 34 paired decisions.
- All 34 pair sums conserved.
- Gold registry positions: A=22, B=12.
- Best fixed registry shortcut: 12/34 component errors (35.29%).
- Disposition: `FAIL_AUTHORITY_POSITION_BIAS`.

The authority schedule was replaced by a deterministic hash ranking with exact 17/17 balance.

## R15-B2: balanced but topologically homogeneous

- Gold registry positions: A=17, B=17.
- Fixed A and fixed B: both 50% component error.
- Ledger validation: 356/356 checks.
- Remaining defect: all 34 chains used the same embedded-letter verification rule.
- Disposition: `FAIL_CHAIN_TOPOLOGY_FINGERPRINT`.

Although the evidence spans were distinct, a single extraction routine could solve every component after discovering the repeated rule.

## R15-C: four authority topologies

R15-C mixes four deterministic but semantically different chain types:

- `embedded_mark`: 9 components;
- `folio_side`: 9 components;
- `withdrawal_inverse`: 8 components;
- `seal_colour`: 8 components.

Final results:

- 68/68 gold cells reconstructed by the custody oracle;
- 68/68 decoy cells differ from gold;
- 34/34 pairwise conservation checks pass;
- 8/8 complete innings-field totals match the ledger in both worlds;
- A/B authority positions are 17/17;
- release validation passes all 15 checks;
- scorer self-test passes blank, perfect, mutation, and hallucination cases.

R15-C is the released synthetic mechanism pilot. It remains blocked from natural-evidence claims and from model-performance claims until separate audits are run.
