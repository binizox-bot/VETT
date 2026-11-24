# Cricket Text-to-Table Dataset Card

## Dataset Goal
A text-to-table reasoning benchmark where models reconstruct cricket scorecards from natural commentary. Difficulty comes from distributed operands (D2), implicit cricket rules (D3), and noise filtering — not from missing evidence.

## Input Files
- `match_XXXX/scorecard.md` — Canonical scorecard (ground truth, read-only)
- `match_XXXX/evidence_chain.md` — Original L1/L2/L3 evidence chain design (read-only)
- `match_XXXX/commentary.txt` — Original commentary (read-only)

## Output Files
- `output/upgraded/match_XXXX/candidate_traps.json` — Structured Core(7)+Hard(5) trap design
- `output/upgraded/match_XXXX/trap_design.md` — Rendered trap design
- `output/upgraded/match_XXXX/evidence_contract.json` — Required evidence specification
- `output/upgraded/match_XXXX/commentary_build_plan.md` — Trap-to-text placement map
- `output/upgraded/match_XXXX/candidate_commentary.txt` — Generated commentary (data-complete)
- `output/upgraded/match_XXXX/final_verification.json` — Verification result

## Generation Pipeline
1. `scripts/generate_trap_designs.py` — Scorecard → candidate_traps.json + trap_design.md
2. `scripts/gen_contract.py` — candidate_traps.json → evidence_contract.json
3. `scripts/gen_candidate.py` — evidence_contract.json → candidate_commentary.txt
4. `scripts/verify_candidate.py` — evidence_contract.json vs candidate_commentary.txt → final_verification.json (+ auto-repair)

## Validation Pipeline
- `scripts/audit_traps.py` — 8-check audit on trap designs against scorecards
- `scripts/final_audit_sample.py` — Core/Hard recoverability + naturalness + table-dump check
- `scripts/batch_verify_all.py` — Full batch verification with auto-repair

## Trap Design Summary
- **218 matches** (2 excluded: 0004 multi-day, 0066 single-innings)
- **Core**: 7 traps per match (D2: extras, batting+extras, FOW, bowler sum, margin, extras Inn2; D3: POM cross-innings)
- **Hard**: 5 traps per match (D3: bowling charged ×2; D2: max partnership, partnership gap, noise filter)
- **Total**: 2,616 validated traps. Zero rejected/invalid.

## Build Plan Summary
- 218 build plans mapping each trap to specific text placement
- Diagnostic downgrade: Trap 12 (noise filtering) consistently marked [DIAGNOSTIC]
- Numeric whitelist: complete for all 218 matches

## Final Commentary Generation Summary
- Pipeline: evidence_contract → gen_candidate → verify → auto-repair → PASS
- **218/218 approved** (100%)
- **0 repairs needed** (0%)
- **0 unsupported numbers**
- Sample audit (10 matches): Core 60% fully recoverable, TableDump risk LOW (10/10), Naturalness OK (10/10)
- Note: Hard trap recoverability (0/10) reflects auto-generated text prioritizing Core evidence. Hard traps require manual polish for full coverage.

## Excluded Match Policy
- match_0004: Multi-day innings victory — non-standard 3-innings format
- match_0066: Single-innings Match Abandoned — 1 innings structure
- Policy: Excluded matches are documented, not silently dropped

## Known Limitations
1. Candidate commentaries are data-dense (~550 chars) — prioritize Core evidence over narrative richness
2. Hard trap operands (max partnership, partnership gap) not fully recoverable in auto-generated text
3. FOW chains in scorecards occasionally incomplete (74/220 Inn2 missing 10th FOW entry)
4. D/L matches use official margin, not simple subtraction — correctly handled
5. No human evaluation of naturalness beyond automated checks

## Recommended Use
- Benchmarking text-to-table reasoning models on Core trap recovery
- Evaluating cricket rule inference (bowling charged, D/L margin)
- Cross-innings POM synthesis
- Noise filtering capability assessment

## Not Recommended Use
- Evaluating narrative quality (candidate texts are data-dense, not literary)
- Hard trap recovery without manual polish
- Multi-day or single-innings formats (excluded from pipeline)
