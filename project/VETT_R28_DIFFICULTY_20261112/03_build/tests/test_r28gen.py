#!/usr/bin/env python3
"""Unit tests for the R28 generator (task t5).

Run directly (``python 03_build/tests/test_r28gen.py``) or via unittest.  The tests
pin the properties the contract cares about: solver equivalence, real revision
chains, authority conflicts that adjudicate to identical facts, near-miss
distractors, twin rendering, quota exactness, HA18 cap, determinism and the
PRESENTATION_ONLY classification that answers the t3 finding.
"""

from __future__ import annotations

import sys
import unittest

sys.dont_write_bytecode = True

import pathlib

BUILD = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))

from r28gen.assignment import (  # noqa: E402
    assign,
    cell_doses,
    dose_cells,
    factor_cells,
    strategy_summary,
    validate_assignment,
)
from r28gen.build import build_instance, instance_summary, render_arm  # noqa: E402
from r28gen.canonical import canon, sha256_text  # noqa: E402
from r28gen.certificates import analyse_instance, reconstruct_facts  # noqa: E402
from r28gen.config import load  # noqa: E402
from r28gen.constants import DOSE_IDS, LEDGER_FIELDS, RECORD_FIELDS  # noqa: E402
from r28gen.derivation import (  # noqa: E402
    NECESSARY,
    PRESENTATION_ONLY,
    analyse_derivation,
    pipeline_equivalence,
    run_pipeline,
)
from r28gen.doses import (  # noqa: E402
    build_alias_hops,
    build_authority,
    build_distractors,
    build_revisions,
    resolve_bindings,
    resolve_revisions,
)
from r28gen.record_space import (  # noqa: E402
    enumerate_combined,
    enumerate_layers,
    layer_key,
    reachable_summary,
    required_candidates,
)
from r28gen.render import build_identity, question_text, scan_public_text  # noqa: E402
from r28gen.reports import quota_report  # noqa: E402
from r28gen.solver_bridge import (  # noqa: E402
    PINNED_SOLVER_SHA256,
    solve_flat,
    solver_provenance,
)

CONFIG = load()
PROV = solver_provenance()
CANONICAL = enumerate_layers("canonical")
COMBINED = enumerate_combined()
PINNED = {row["record_sha256"]: row for row in required_candidates()}
ASSIGNMENT = assign(CONFIG, COMBINED, PINNED)
SUMMARY = strategy_summary(CONFIG, ASSIGNMENT)


def _first_candidate(layer):
    return COMBINED[layer][0]


def _facts_with(**overrides):
    base = {
        "contact": "BAT",
        "completed_runs": 0,
        "boundary_mode": "NONE",
        "boundary_allowance": 0,
        "crossed_at_throw": False,
        "award_run_in_progress": False,
        "penalty_runs_batting": 0,
        "wilful_deception": False,
        "forced_not_count": False,
        "dismissal_candidate": "NONE",
        "appeal_made": True,
        "appeal_in_time": True,
        "wicket_fair": True,
    }
    base.update(overrides)
    return base


class ConfigTests(unittest.TestCase):
    def test_config_is_internally_consistent(self):
        self.assertEqual(CONFIG.validate(), [])
        self.assertEqual(CONFIG.n_published % 40, 0)

    def test_quota_sums_match_blocks(self):
        self.assertEqual(CONFIG.quota_total, CONFIG.n_published)
        self.assertEqual(sum(layer.n_factor_core for layer in CONFIG.quota_layers), CONFIG.factor_n)
        self.assertEqual(sum(layer.n_dose_ladder for layer in CONFIG.quota_layers), CONFIG.dose_n)

    def test_solver_is_pinned(self):
        self.assertTrue(PROV["matches_pinned"])
        self.assertEqual(PROV["sha256"], PINNED_SOLVER_SHA256)


class RecordSpaceTests(unittest.TestCase):
    def test_canonical_space_reproduces_contract_lower_bound(self):
        summary = reachable_summary(CANONICAL)
        self.assertEqual(summary["distinct_records"], 761)
        self.assertEqual(summary["strata"], 67)
        self.assertEqual(summary["constant_fields_in_reachable_space"], [])

    def test_every_quota_layer_is_reachable(self):
        for layer in CONFIG.quota_layers:
            self.assertGreaterEqual(len(COMBINED.get(layer.key, [])), layer.quota,
                                    msg=f"layer {layer.key}")

    def test_records_are_distinct_within_layers(self):
        for bucket in COMBINED.values():
            self.assertEqual(len({cand.record_sha256 for cand in bucket}), len(bucket))

    def test_required_combinations_are_distinct(self):
        rows = required_candidates()
        self.assertEqual(len(rows), 5)
        self.assertEqual(len({row["record_sha256"] for row in rows}), 5)

    def test_layer_mask_order(self):
        flat = {"ledger.BYE": 1, "ledger.LEG_BYE": 0, "ledger.PENALTY": 5}
        self.assertEqual(layer_key({**flat, "delivery_status": "LEGAL", "dismissal": "NONE"})[2],
                         "101")


class DerivationTests(unittest.TestCase):
    def test_pipeline_matches_frozen_solver(self):
        fact_sets = [dict(cand.facts) for bucket in CANONICAL.values() for cand in bucket]
        result = pipeline_equivalence(fact_sets)
        self.assertEqual(result["mismatches"], 0, msg=str(result["first_mismatches"])[:800])
        self.assertEqual(result["checked"], 761)

    def test_necessary_operator_is_detected(self):
        facts = _facts_with(dismissal_candidate="BOWLED", wicket_broken_by_delivery=True)
        analysis = analyse_derivation(facts)
        self.assertIn("BOWLED_TEST", analysis.necessary)
        self.assertGreaterEqual(analysis.derivation_depth_verified, 2)

    def test_failed_test_is_load_bearing(self):
        facts = _facts_with(
            no_ball_called=True,
            dismissal_candidate="BOWLED",
            wicket_broken_by_delivery=True,
        )
        analysis = analyse_derivation(facts)
        row = next(item for item in analysis.operators if item["operator_id"] == "BOWLED_TEST")
        self.assertEqual(row["verdict"], NECESSARY)
        self.assertEqual(row["ablation"]["outcome"], "RECORD_CHANGED")
        self.assertIn("dismissal", row["ablation"]["changed_fields"])

    def test_redundant_gate_is_presentation_only(self):
        facts = _facts_with(
            dismissal_candidate="RUN_OUT",
            out_of_ground=True,
            appeal_made=False,
            wicket_fair=False,
        )
        analysis = analyse_derivation(facts)
        verdicts = {
            row["operator_id"]: row["verdict"] for row in analysis.operators
        }
        # the appeal gate blocks first, so the fair-wicket gate is never evaluated;
        # ablating the appeal gate still yields NONE through the second gate, so the
        # first gate alone is redundant for this instance
        self.assertEqual(verdicts["GATE_APPEAL"], PRESENTATION_ONLY)
        self.assertEqual(verdicts["GATE_FAIR_WICKET"], "NOT_ON_PATH")

    def test_fair_wicket_gate_alone_is_necessary(self):
        facts = _facts_with(dismissal_candidate="RUN_OUT", wicket_fair=False)
        analysis = analyse_derivation(facts)
        verdicts = {row["operator_id"]: row["verdict"] for row in analysis.operators}
        self.assertEqual(verdicts["GATE_FAIR_WICKET"], NECESSARY)

    def test_single_blocking_gate_is_necessary(self):
        facts = _facts_with(dismissal_candidate="RUN_OUT", appeal_made=False)
        analysis = analyse_derivation(facts)
        verdicts = {row["operator_id"]: row["verdict"] for row in analysis.operators}
        self.assertEqual(verdicts["GATE_APPEAL"], NECESSARY)

    def test_movement_is_presentation_only_after_completed_dismissal(self):
        facts = _facts_with(
            dismissal_candidate="BOWLED",
            wicket_broken_by_delivery=True,
            completed_runs=3,
            boundary_mode="OVERTHROW",
            boundary_allowance=4,
            awarded=False,
        )
        analysis = analyse_derivation(facts)
        verdicts = {row["operator_id"]: row["verdict"] for row in analysis.operators}
        self.assertEqual(verdicts["MOVEMENT_COMPOSE"], PRESENTATION_ONLY)
        self.assertEqual(verdicts["RUN_CREDIT_ROUTE"], PRESENTATION_ONLY)

    def test_rule_text_does_not_imply_depth(self):
        facts = _facts_with(
            dismissal_candidate="BOWLED",
            wicket_broken_by_delivery=True,
            completed_runs=2,
            boundary_mode="NORMAL",
            boundary_allowance=4,
        )
        analysis = analyse_derivation(facts)
        self.assertIn("BOUNDARY_NORMAL", analysis.rule_keys)
        self.assertNotIn("BOUNDARY_NORMAL", analysis.necessary_rule_keys)


class DoseRenderTests(unittest.TestCase):
    def setUp(self):
        self.candidate = _first_candidate(("LEGAL", "NONE", "100"))
        self.facts = dict(self.candidate.facts)
        self.flat = dict(self.candidate.flat)
        self.analysis, self.pivot = analyse_instance(self.facts, CONFIG.fact_grid)
        self.identity = build_identity("r28q_9999", d1_level=2, seed=CONFIG.seed)
        self.qid = "r28q_9999"

    # -- D1 ---------------------------------------------------------------
    def test_binding_chain_resolves(self):
        artifacts = build_alias_hops(self.qid, dose=2, identity=self.identity,
                                     facts_sha256="0" * 64, seed=CONFIG.seed)
        self.assertEqual(len(artifacts.spans), 2)
        self.assertTrue(artifacts.witness["resolvable"])
        self.assertEqual(artifacts.witness["resolved_terminal"], self.identity.terminal)
        resolution = resolve_bindings(self.identity.head, artifacts.evidence["bindings"])
        self.assertEqual(resolution["terminal"], self.identity.terminal)

    def test_dose_zero_has_no_binding(self):
        identity = build_identity(self.qid, d1_level=0, seed=CONFIG.seed)
        artifacts = build_alias_hops(self.qid, dose=0, identity=identity,
                                     facts_sha256="0" * 64, seed=CONFIG.seed)
        self.assertEqual(artifacts.spans, [])
        self.assertEqual(artifacts.witness["verdict"], "DOSE_ZERO")

    # -- D2 ---------------------------------------------------------------
    def test_revision_policy_selection(self):
        versions = [
            {"version_id": "VER-A", "cell": "completed_runs", "revision_no": 2,
             "effective_at": "18:09", "value": 9, "cites": None},
            {"version_id": "VER-B", "cell": "completed_runs", "revision_no": 9,
             "effective_at": "18:22", "value": 3, "cites": None},
            {"version_id": "VER-C", "cell": "completed_runs", "revision_no": 4,
             "effective_at": "18:29", "value": 7, "cites": None},
        ]
        self.assertEqual(resolve_revisions(versions, "HIGHEST_REVISION")["chosen"],
                         {"completed_runs": 3})
        # LAST_PRE_LOCK keeps the 18:22 entry: the 18:29 one is after the lock
        self.assertEqual(resolve_revisions(versions, "LAST_PRE_LOCK")["chosen"],
                         {"completed_runs": 3})
        versions[0] = {**versions[0], "effective_at": "18:24"}
        self.assertEqual(resolve_revisions(versions, "LAST_PRE_LOCK")["chosen"],
                         {"completed_runs": 9})

    def test_join_orders_the_replay(self):
        versions = [
            {"version_id": "VER-A1", "cell": "completed_runs", "revision_no": 2,
             "effective_at": "18:09", "value": 9, "cites": None},
            {"version_id": "VER-A2", "cell": "completed_runs", "revision_no": 9,
             "effective_at": "18:22", "value": 3, "cites": None},
            {"version_id": "VER-B1", "cell": "penalty_runs_batting", "revision_no": 7,
             "effective_at": "18:31", "value": 5, "cites": "VER-A2"},
        ]
        replay = resolve_revisions(versions, "HIGHEST_REVISION")
        self.assertEqual(replay["order"], ["completed_runs", "penalty_runs_batting"])
        self.assertEqual(replay["chosen"],
                         {"completed_runs": 3, "penalty_runs_batting": 5})

    def test_dose_two_has_three_versions_across_two_cells(self):
        artifacts = build_revisions(self.qid, dose=2, facts=self.facts, flat=self.flat,
                                    pivot_scan=self.pivot, identity=self.identity,
                                    facts_sha256=sha256_text(canon(self.facts)),
                                    seed=CONFIG.seed)
        witness = artifacts.witness
        self.assertEqual(witness["version_count"], 3)
        self.assertEqual(len(witness["cells_revised"]), 2)
        self.assertEqual(len(witness["joins"]), 1)
        self.assertEqual(witness["replays"], 2)
        self.assertTrue(witness["recovered_equals_gold"])

    def test_dose_one_has_two_versions_single_cell(self):
        artifacts = build_revisions(self.qid, dose=1, facts=self.facts, flat=self.flat,
                                    pivot_scan=self.pivot, identity=self.identity,
                                    facts_sha256=sha256_text(canon(self.facts)),
                                    seed=CONFIG.seed)
        self.assertEqual(artifacts.witness["version_count"], 2)
        self.assertEqual(artifacts.witness["replays"], 1)
        self.assertTrue(artifacts.witness["recovered_equals_gold"])

    # -- D3 ---------------------------------------------------------------
    def test_authority_dose_shapes(self):
        dose_one = build_authority(self.qid, dose=1, facts=self.facts, flat=self.flat,
                                   pivot_scan=self.pivot, identity=self.identity,
                                   facts_sha256=sha256_text(canon(self.facts)),
                                   seed=CONFIG.seed)
        self.assertEqual(dose_one.witness["conflict_count"], 1)
        self.assertEqual(dose_one.witness["source_count"], 2)
        self.assertEqual(dose_one.witness["masked_cells"], [])
        self.assertTrue(dose_one.witness["resolved_equals_gold"])
        dose_two = build_authority(self.qid, dose=2, facts=self.facts, flat=self.flat,
                                   pivot_scan=self.pivot, identity=self.identity,
                                   facts_sha256=sha256_text(canon(self.facts)),
                                   seed=CONFIG.seed)
        self.assertEqual(dose_two.witness["conflict_count"], 2)
        self.assertEqual(dose_two.witness["source_count"], 3)
        self.assertEqual(len(dose_two.witness["masked_cells"]), 1)
        self.assertTrue(dose_two.witness["resolved_equals_gold"])
        self.assertEqual(dose_two.witness["resolved_facts_sha256"],
                         sha256_text(canon(self.facts)))

    # -- D4 ---------------------------------------------------------------
    def test_near_miss_differs_in_one_fact(self):
        artifacts = build_distractors(self.qid, dose=2, facts=self.facts, flat=self.flat,
                                      pivot_scan=self.pivot, identity=self.identity,
                                      facts_sha256=sha256_text(canon(self.facts)),
                                      seed=CONFIG.seed)
        distractors = artifacts.witness["distractors"]
        self.assertEqual(len(distractors), 2)
        self.assertEqual(sum(1 for item in distractors if item["near_miss"]), 1)
        near = next(item for item in distractors if item["near_miss"])
        self.assertEqual(near["differing_fact_count"], 1)
        self.assertTrue(near["distractor_record_differs_in"])
        self.assertTrue(all(item["distractor_record_differs_in"] for item in distractors))

    def test_dose_zero_renders_nothing(self):
        for builder, kwargs in (
            (build_revisions, {}),
            (build_authority, {}),
            (build_distractors, {}),
        ):
            artifacts = builder(self.qid, dose=0, facts=self.facts, flat=self.flat,
                                pivot_scan=self.pivot, identity=self.identity,
                                facts_sha256=sha256_text(canon(self.facts)),
                                seed=CONFIG.seed, **kwargs)
            self.assertEqual(artifacts.spans, [])


class BuildTests(unittest.TestCase):
    def _plan(self, block="factor_core", cell="1111"):
        return next(plan for plan in ASSIGNMENT.published
                    if plan.block == block and plan.cell == cell)

    def test_twin_rendering_identity(self):
        plan = self._plan()
        instance = build_instance(CONFIG, plan, PROV)
        twin = instance.checks["twin"]
        self.assertTrue(twin["facts_byte_identical"])
        self.assertTrue(twin["record_byte_identical"])
        self.assertTrue(twin["question_text_identical"])
        self.assertTrue(twin["output_schema_identical"])
        self.assertGreaterEqual(twin["published_tokens"], twin["control_tokens"])
        self.assertNotEqual(canon(instance.public_published["dossier"]),
                            canon(instance.public_control["dossier"]))

    def test_replay_both_arms(self):
        plan = self._plan()
        instance = build_instance(CONFIG, plan, PROV)
        self.assertTrue(instance.checks["replay_published"]["ok"],
                        msg=str(instance.checks["replay_published"]))
        self.assertTrue(instance.checks["replay_control"]["ok"],
                        msg=str(instance.checks["replay_control"]))

    def test_minimum_evidence_is_present_and_necessary(self):
        plan = self._plan()
        instance = build_instance(CONFIG, plan, PROV)
        certificate = instance.certificate_published
        self.assertTrue(certificate["minimum_evidence_spans"])
        present = instance.published.span_ids
        self.assertEqual(sorted(set(certificate["minimum_evidence_spans"]) - present), [])
        # removing a controlling fact span breaks the reconstruction
        evidence = instance.published.evidence
        dropped = next(iter(evidence["fact_spans"]))
        present_without = set(present) - {dropped}
        reconstruction = reconstruct_facts(present_without, evidence)
        self.assertNotEqual(canon(reconstruction["facts"]),
                            canon(instance.gold["solver_facts"]))
        self.assertIn(dropped, reconstruction["missing"])

    def test_prompt_budget_and_leak_scan(self):
        plan = self._plan(block="dose_ladder", cell="D4-2")
        instance = build_instance(CONFIG, plan, PROV)
        self.assertTrue(instance.checks["prompt_budget"]["within_budget"])
        self.assertEqual(instance.checks["leak_scan"]["published"], [])
        self.assertEqual(instance.checks["leak_scan"]["control"], [])

    def test_determinism_of_one_instance(self):
        plan = self._plan(block="dose_ladder", cell="D2-2")
        first = build_instance(CONFIG, plan, PROV)
        second = build_instance(CONFIG, plan, PROV)
        self.assertEqual(first.certificate_published, second.certificate_published)
        self.assertEqual(canon(first.public_published), canon(second.public_published))
        self.assertEqual(canon(first.gold), canon(second.gold))

    def test_question_text_has_no_dose_words(self):
        plan = self._plan()
        identity = build_identity(plan.question_id, d1_level=0, seed=CONFIG.seed)
        text = question_text(identity)
        self.assertEqual(scan_public_text([], text), [])

    def test_summary_fields(self):
        plan = self._plan()
        summary = instance_summary(build_instance(CONFIG, plan, PROV))
        self.assertIn("derivation_depth_verified", summary["derivation"])
        self.assertEqual(summary["family"], plan.family)
        self.assertTrue(summary["certificate_ok_published"])


class AssignmentTests(unittest.TestCase):
    def test_assignment_is_exact(self):
        self.assertEqual(validate_assignment(CONFIG, ASSIGNMENT), [])

    def test_distribution_matches_contract(self):
        self.assertEqual(SUMMARY["by_status"],
                         {"DEAD_REBALL": 1, "LEGAL": 166, "NO_BALL": 100, "WIDE": 53})
        self.assertEqual(SUMMARY["by_dismissal"]["NONE"], 124)
        self.assertEqual(SUMMARY["by_dismissal"]["RUN_OUT"], 86)
        self.assertEqual(SUMMARY["by_ledger_mask"],
                         {"000": 73, "001": 73, "010": 40, "011": 38, "100": 54, "101": 42})

    def test_ledger_coverage(self):
        self.assertGreaterEqual(SUMMARY["ledger_nonzero_records"]["ledger.BYE"], 80)
        self.assertGreaterEqual(SUMMARY["ledger_nonzero_records"]["ledger.LEG_BYE"], 64)
        self.assertGreaterEqual(SUMMARY["ledger_nonzero_records"]["ledger.PENALTY"], 120)

    def test_legal_dismissal_cap(self):
        self.assertLessEqual(SUMMARY["legal_dismissal_total"], 11)
        self.assertEqual(SUMMARY["by_status"]["DEAD_REBALL"], 1)

    def test_cells_are_full_and_diverse(self):
        self.assertEqual(len(factor_cells(CONFIG.factor_cells)), 16)
        self.assertEqual(len(dose_cells()), 12)
        for key, row in ASSIGNMENT.cells.items():
            self.assertEqual(row["n"], row["capacity"], msg=key)
            self.assertGreaterEqual(row["status_diversity"], 2, msg=key)
            self.assertGreaterEqual(row["dismissal_diversity"], 2, msg=key)

    def test_factor_cells_are_full_factorial(self):
        for cell in factor_cells(CONFIG.factor_cells):
            doses = cell_doses("factor_core", cell)
            self.assertEqual(len(doses), 4)
            self.assertTrue(all(level in (0, 1) for level in doses.values()))
        for cell in dose_cells():
            doses = cell_doses("dose_ladder", cell)
            self.assertLessEqual(sum(1 for level in doses.values() if level > 0), 1)

    def test_held_out_is_distinct(self):
        published = {plan.candidate.record_sha256 for plan in ASSIGNMENT.published}
        held = {plan.candidate.record_sha256 for plan in ASSIGNMENT.held_out}
        self.assertEqual(len(held), 40)
        self.assertFalse(published & held)


class QuotaReportTests(unittest.TestCase):
    def test_quota_report_has_no_shortfall(self):
        report = quota_report(
            CONFIG,
            canonical_layers=CANONICAL,
            extended_layers=COMBINED,
            combined_layers=COMBINED,
            required_rows=required_candidates(),
            assignment=ASSIGNMENT,
        )
        self.assertTrue(report["no_shortfall"])
        self.assertTrue(report["safety_margin_ok"])
        self.assertEqual(report["contract_cap_cross_check"]["mismatches"], [])
        self.assertTrue(report["ha18_legal_dismissal_cap"]["within_cap"])
        self.assertEqual(len(report["rows"]), 67)
        for row in report["rows"]:
            self.assertTrue(row["reaches_quota"], msg=row["status"])
            self.assertTrue(row["selected_equals_quota"], msg=row["status"])


class SolverEquivalencePropertyTests(unittest.TestCase):
    def test_stumped_after_no_ball_matches_solver(self):
        facts = _facts_with(
            no_ball_called=True,
            dismissal_candidate="STUMPED_OR_RUN_OUT",
            out_of_ground=True,
            keeper_only=True,
            attempting_run=False,
        )
        _, flat, _ = solve_flat(facts)
        result = run_pipeline(facts)
        self.assertTrue(result.resolved)
        self.assertEqual(canon(result.flat), canon(flat))
        self.assertEqual(flat["dismissal"], "NONE")

    def test_every_record_field_is_frozen(self):
        self.assertEqual(len(RECORD_FIELDS), 12)
        self.assertEqual(set(LEDGER_FIELDS), {"ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY"})

    def test_dose_ids_are_the_four_contract_mechanisms(self):
        self.assertEqual(DOSE_IDS, ("D1", "D2", "D3", "D4"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
