# R23.1 Text-Embedded Pilot Quality Report

## Scope

- 20 matches, 7,944 unchanged Track A table targets and 500 unchanged R22 probes.
- 100 hybrid cricket-law questions and 100 open grounded-reasoning questions.
- 180 embedded rule-evidence spans: 140 decisive and 40 misleading.

## Minimal-change controls

- R22 base documents contain 27,046 spans.
- Exactly 100 unreferenced routing-noise spans were replaced and 80 rule-evidence spans were inserted.
- The patch touches 0.67% of base spans and increases span count by 0.30%.
- Every patch is reversible. The reconstructed document bundle must equal the original R22 SHA-256 digest; table-target and R22-probe digests must also remain unchanged.

## Difficulty controls

Each level occurs exactly 20 times:

- L1: single explicit rule clue.
- L2: distributed complementary clues.
- L3: scoped case outcome and exclusions.
- L4: plausible conflict followed by authoritative correction.
- L5: case facts that still require ruleset application.

All 80 multi-span rule questions place their evidence in distinct documents. All 180 embedded span texts are unique at the full-string level. Eight deterministic surface frames are used with counts between 17 and 27, while the evidence role is not disclosed by the frame.

## Machine checks

- Instance audit: 20/20 PASS.
- Legacy R23 compatibility audit: PASS.
- Test-only oracle: 100% on answers, reasoning atoms, decisive spans, misleading spans and open evidence graphs.
- Full repository regression: 80 tests PASS.

## Remaining validity limits

This remains a structural pilot. It contains only 10 independent MCC law themes, each reused 10 times. Unique surface wording prevents exact-copy shortcuts but does not make repeated themes independent. Before a 220-match release, the rule bank should be expanded to at least 50–80 independently sourced rules/scenarios, and a held-out strong-model run should empirically verify the intended level gaps and overall accuracy target. The current `empirical_calibration` status is therefore `UNMEASURED`.
