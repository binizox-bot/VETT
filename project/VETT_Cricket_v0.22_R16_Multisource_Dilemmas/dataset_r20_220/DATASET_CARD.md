# Dataset Card: VETT-Cricket-v0.27-R20-220-full-table

R20 is a 220-match long-context text-to-full-table benchmark. It contains
91555 directly scored cells grounded in repaired canonical roots.
Source-conflicted cells remain preserved in the repair release but are not targets.

Use only each `public_instance.json` as model input. Never expose `private_gold.json`,
`private_evidence.json`, or `audit/` to a solver. Report 217 independent matches and the
three exact duplicates separately as consistency controls.

Primary metrics are micro cell exact match, macro match cell accuracy, row exact match,
table exact match, and match exact match. Report results by revision depth. The intended
strong-model direct-cell accuracy is about 75%; that value is pending blind calibration.
