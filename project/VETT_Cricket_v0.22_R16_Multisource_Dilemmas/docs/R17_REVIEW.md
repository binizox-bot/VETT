# R17 Five-Axis Review

## Verdict

Approved for a six-match direction pilot. No critical finding remains. This is not approval
for a public benchmark claim until an external blind-model evaluation is performed.

## Correctness

- All direct targets resolve without a source ranking; derived targets reconcile from
  resolved operands.
- Every amendment, withdrawal, and copy edge has a literal hashed public witness.
- Eighty-four decisive-span deletions and 600 individual graph-edge ablations change the
  answer, create ambiguity, or invalidate the graph.
- Alternate score worlds preserve extras arithmetic and implied batting subtotals.
- Full R16+R17 test suite and independent disk audit pass.

## Readability and Simplicity

- R17 remains a standard-library-only package with separate model, resolver, generator,
  auditor, release, and CLI modules.
- The generator is intentionally linear: document roles and graph construction remain
  visible instead of being hidden behind a generic configuration framework.
- No dead compatibility layer or unused R17 implementation was found.

## Architecture

- R17 is additive and isolated from R16. The committed R16 release is byte-unchanged.
- Public, private, and audit artifacts remain separate; release output is never used as
  canonical truth.
- The main review finding was that semantic IDs (`doc_final`, `FIN`, `AM1`) exposed answer
  roles. These were replaced with per-match opaque IDs and enforced by mutation tests.

## Security and Integrity

- No network calls, credentials, external dependencies, or executable user content exist.
- Unknown graph references, duplicate IDs, cycles, missing witnesses, leakage, and altered
  file hashes fail closed.
- The manifest checks every non-manifest file by byte count and SHA-256. It is tamper-evident,
  not cryptographically signed against a separately trusted external anchor.

## Performance

- Work is bounded by six small instances. Exhaustive edge ablation is intentionally used;
  the full local suite completes in seconds.
- No unbounded network, database, or recursive data traversal exists; graph cycles are
  rejected before resolution.

## Known Boundaries

- Commentary is controlled semi-synthetic rather than observed live-feed text.
- Mechanical language checks cannot replace human naturalness review.
- Private semantic claim mapping is construction-time ground truth; the auditor verifies
  its public witnesses but does not perform open-ended natural-language extraction.
- No external language model has yet been tested blindly, so model failure is unproven.
