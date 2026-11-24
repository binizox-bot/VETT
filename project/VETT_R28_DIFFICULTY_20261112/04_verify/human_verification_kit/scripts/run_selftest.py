"""End-to-end self-test for the R28 human-verification readiness kit.

The self-test is the acceptance evidence for t24.  It runs the full pipeline on a
synthetic R28-shaped build (there is no R28 data yet) with two scripted annotators:

    design manifest -> stratified sample -> build binding -> public/gold bundles
    -> blind DERIVED -> gold-revealed VERIFY -> export validation -> Cohen's kappa
    -> disagreement list -> adjudication -> H1/H2/H3 gates
    -> qualification pass and fail paths -> pre-annotation (DEGRADED) -> baseline check

It also re-computes kappa independently of ``scripts/agreement.py`` and fails if the
two disagree; it re-hashes the R26.15 baseline instead of trusting t1's receipt; and
it syntax-checks the HTML tool's inline JavaScript with Node.

Everything is written under ``out/selftest``.  No network, no paid API, no write
outside the kit directory, no change to R26.15.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import time
import traceback
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import build_bundle  # noqa: E402
import make_design  # noqa: E402

KIT = common.kit_root()
OUT = os.path.join(KIT, "out", "selftest")
SCRIPTS = os.path.join(KIT, "scripts")
FIXTURES = os.path.join(KIT, "fixtures")
TOOL = os.path.join(KIT, "tool", "annotate.html")
SEED = 20261112
EXPECTED_AGREEMENT = {"value": 0.98, "scope": 0.98, "rule_version": 0.99, "proof": 0.98}
EXPECTED_QUALIFICATION = {"value": 1.0, "scope": 1.0, "rule_version": 1.0, "proof": 1.0}
R26_AGGREGATE = "343afde4c91d7785f42296074ecea685d5d466260674ab5a8c3bc37323d851bd"


class StepFailure(RuntimeError):
    pass


def py() -> str:
    return sys.executable


def run(args: list[str], timeout: int = 600, env_extra: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    if env_extra:
        env.update(env_extra)
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, env=env)


def require(condition: bool, message: str, details: Any | None = None) -> None:
    if not condition:
        raise StepFailure(message + ("" if details is None else " | " + common.canonical_json(details)[:1200]))


def script(name: str) -> str:
    return os.path.join(SCRIPTS, name)


def clean_dir(path: str) -> None:
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def strip_time(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: strip_time(item) for key, item in value.items() if not any(token in key for token in ("generated_at", "locked_at", "verified_at", "bound_at", "sealed_at", "created_at"))}
    if isinstance(value, list):
        return [strip_time(item) for item in value]
    return value


def independent_kappa(pairs: list[tuple[str, str]], categories: list[str]) -> float | None:
    """Independent re-implementation used to cross-check scripts/common.py."""
    n = len(pairs)
    index = {category: i for i, category in enumerate(categories)}
    matrix = [[0 for _ in categories] for _ in categories]
    for a, b in pairs:
        matrix[index[a]][index[b]] += 1
    observed = sum(matrix[i][i] for i in range(len(categories))) / n
    row_sums = [sum(row) / n for row in matrix]
    col_sums = [sum(matrix[i][j] for i in range(len(categories))) / n for j in range(len(categories))]
    expected = sum(row_sums[i] * col_sums[i] for i in range(len(categories)))
    if abs(1 - expected) < 1e-15:
        return None
    return (observed - expected) / (1 - expected)


def load_verify_pairs(path: str) -> dict[str, list[tuple[str, str]]]:
    rows = common.load_jsonl(path)
    pairs: dict[str, list[tuple[str, str]]] = {dimension: [] for dimension in common.DIMENSIONS}
    for row in rows:
        if row.get("kind") != common.KIND_VERIFY:
            raise StepFailure(f"{path}: not a VERIFY file")
        for dimension in common.DIMENSIONS:
            pairs[dimension].append(row["labels"][dimension]["verdict"])
    return pairs


def html_static_check() -> dict[str, Any]:
    require(os.path.isfile(TOOL), "tool/annotate.html missing")
    text = open(TOOL, "r", encoding="utf-8").read()
    forbidden = ["http://", "https://", "fetch(", "XMLHttpRequest", "<script src", "<link rel=", "WebSocket", "navigator.sendBeacon"]
    hits = [token for token in forbidden if token in text]
    require(not hits, "HTML tool contains network/external-resource constructs", hits)
    for marker in ["bundle-file", "gold-file", "derive-form", "verify-form", "adj-form", "export-derived", "export-verify", "export-adjudication", "record-fields", "proof-spans"]:
        require(f'id="{marker}"' in text, f"HTML tool missing marker id={marker}")
    start = text.rfind("<script>")
    end = text.rfind("</script>")
    require(start >= 0 and end > start, "HTML tool has no inline script block")
    inline = text[start + len("<script>") : end]
    js_path = os.path.join(OUT, "annotate_inline.js")
    common.write_text(js_path, inline)
    node = shutil.which("node")
    if node:
        result = run([node, "--check", js_path], timeout=120)
        require(result.returncode == 0, "node --check failed for inline JavaScript", result.stderr[-1500:])
        node_status = "PASS"
    else:
        node_status = "SKIPPED_NODE_ABSENT"
    return {"forbidden_tokens_hits": hits, "markers": "present", "node_syntax_check": node_status}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the R28 human-verification kit self-test")
    parser.add_argument("--out", default=OUT)
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args(argv)
    out = os.path.abspath(args.out)
    clean_dir(out)
    started_at = common.utc_now()
    steps: list[dict[str, Any]] = []

    def step(name: str, fn):
        begin = time.time()
        try:
            evidence = fn()
            steps.append({"name": name, "status": "PASS", "seconds": round(time.time() - begin, 2), "evidence": evidence})
            print(f"[PASS] {name} ({round(time.time() - begin, 2)}s)")
            return evidence
        except Exception as exc:  # noqa: BLE001 - report, never hide
            message = f"{type(exc).__name__}: {exc}"
            steps.append(
                {
                    "name": name,
                    "status": "FAIL",
                    "seconds": round(time.time() - begin, 2),
                    "error": message,
                    "traceback": traceback.format_exc()[-2500:],
                }
            )
            print(f"[FAIL] {name}: {message}")
            raise

    try:
        # ---------------------------------------------------------------- assets
        def assets() -> dict[str, Any]:
            required = [
                "ANNOTATION_PROTOCOL.md",
                "SAMPLING_PLAN.md",
                "README.md",
                "E_PHASE_HANDOFF.md",
                "sample_ids.json",
                "design_manifest_n320.json",
                "design_manifest_n160_legacy.json",
                "sample_ids_n160_legacy.json",
                "schema/bundle.schema.json",
                "schema/annotation.schema.json",
                "schema/adjudication.schema.json",
                "schema/build_index.schema.json",
                "scripts/common.py",
                "scripts/make_design.py",
                "scripts/build_bundle.py",
                "scripts/annotate_cli.py",
                "scripts/validate_export.py",
                "scripts/seal_export.py",
                "scripts/agreement.py",
                "scripts/qualification.py",
                "scripts/adjudicate.py",
                "scripts/preannotate.py",
                "scripts/make_synthetic.py",
                "scripts/check_baseline.py",
                "tool/annotate.html",
                "fixtures/synthetic_build_v320.json",
                "fixtures/synthetic_build_index.json",
                "preannotation/PREANNOTATION_POLICY.md",
            ]
            missing = [rel for rel in required if not os.path.isfile(os.path.join(KIT, rel))]
            require(not missing, "kit assets missing", missing)
            html = html_static_check()
            return {"required_files": len(required), "html": html}

        step("env_and_assets", assets)

        # ---------------------------------------------------------------- real-R28 schema adapter
        def r28_schema_adapter() -> dict[str, Any]:
            # Representative of the real t5 build: public uses dossier.documents,
            # spans only; gold keeps proof inside certificate and stores evidence
            # span ids as bare strings.
            legal_example = {
                "batter_runs": 11,
                "bowler_runs": 11,
                "counts_in_over": True,
                "delivery_status": "LEGAL",
                "dismissal": "NONE",
                "ledger.BATTER": 11,
                "ledger.BYE": 0,
                "ledger.LEG_BYE": 0,
                "ledger.NO_BALL_EXTRA": 0,
                "ledger.PENALTY": 5,
                "ledger.WIDE_EXTRA": 0,
                "total_runs": 16,
            }
            legal_no_count = dict(legal_example)
            legal_no_count.update({"batter_runs": 4, "ledger.BATTER": 4, "ledger.PENALTY": 10, "total_runs": 14})
            for record in (legal_example, legal_no_count):
                result = common.check_record_consistency(record)
                require(result["ok"], "contract checker rejected a valid real-R28-shaped record", result)
            bad_wide = dict(legal_example)
            bad_wide.update({"delivery_status": "WIDE", "ledger.BYE": 1})
            require(not common.check_record_consistency(bad_wide)["ok"], "checker missed WIDE+BYE")
            bad_dead = dict(legal_example)
            bad_dead.update({"delivery_status": "DEAD_REBALL", "dismissal": "NONE", "ledger.PENALTY": 1})
            require(not common.check_record_consistency(bad_dead)["ok"], "checker missed DEAD_REBALL ledger")
            bad_both = dict(legal_example)
            bad_both.update({"ledger.BYE": 1, "ledger.LEG_BYE": 1})
            require(not common.check_record_consistency(bad_both)["ok"], "checker missed BYE+LEG_BYE")

            def public_payload(item_id: str) -> dict[str, Any]:
                return {
                    "question_id": item_id,
                    "question": f"Resolve review token {item_id}.",
                    "ruleset": {"ruleset_id": "R28-CRICKET-LAWS-2026", "title": "2026 Laws of Cricket", "effective_date": "2026-01-01"},
                    "dossier": {
                        "documents": [
                            {"document_id": "doc_cover", "title": "Review cover sheet", "spans": [{"role": "scope", "span_id": "r28scope_1", "text": "This dossier covers one delivery."}]},
                            {"document_id": "doc_obs", "title": "Signed observation sheet", "spans": [{"role": "fact", "span_id": "r28fact_1", "text": "The fielding side appealed."}]},
                        ]
                    },
                }

            def gold_payload(item_id: str, block: str, cell: str) -> dict[str, Any]:
                return {
                    "question_id": item_id,
                    "block": block,
                    "cell": cell,
                    "doses": {"D1": 1, "D2": 0, "D3": 0, "D4": 0} if block == "dose_ladder" else {"D1": 0, "D2": 1, "D3": 0, "D4": 0},
                    "decision_record_flat": legal_example,
                    "solver_facts": {"appeal_made": True},
                    "certificate": {
                        "minimum_evidence_spans": ["r28fact_1", "r28scope_1"],
                        "rule_path": [{"rule_key": "LEGAL_COUNT", "span_id": "r28rule_1"}],
                        "revision_chain": None,
                        "authority_decision": None,
                        "why_not_distractor": [],
                    },
                    "layer": {"status": "LEGAL", "dismissal": "NONE"},
                    "scenario_family": "rfam_probe",
                }

            public_raw, _ = build_bundle.normalise_public("q1", public_payload("q1"))
            require(public_raw["question_text"].startswith("Resolve review token q1"), "adapter lost question text")
            require(public_raw["ruleset"]["title"] == "2026 Laws of Cricket", "adapter lost ruleset")
            require(len(public_raw["documents"]) == 2 and public_raw["documents"][1]["genre"] == "Signed observation sheet", "adapter lost dossier documents/title")
            require(public_raw["documents"][0]["spans"][0]["span_id"] == "r28scope_1", "adapter lost spans")
            gold_raw, warnings = build_bundle.normalise_gold("q1", gold_payload("q1", "factor_core", "0000"))
            require(gold_raw["decision_record_flat"] == legal_example, "adapter changed the record")
            require(len(gold_raw["proof"]["minimum_evidence_spans"]) == 2, "adapter lost certificate proof spans")
            require(gold_raw["proof"]["minimum_evidence_spans"][0]["span_id"] == "r28fact_1", "adapter proof ids wrong")
            require(any("revision_chain" in message for message in warnings), "optional certificate fields should be reported as warnings")
            index_entry = make_design._normalise_index_item({"item_id": "q1", "block": "dose_ladder", "cell": "D1-1"})
            require(index_entry["mechanism"] == "D1" and index_entry["dose"] == 1 and index_entry["stratum_id"] == "DL:D1=1", "adapter cannot parse real dose-ladder cell D1-1")
            # mini on-disk build in the real layout: published/<id>/{public_instance,private_gold}.json
            mini = os.path.join(out, "r28_schema_mini")
            for item_id, block, cell in (("q1", "factor_core", "0000"), ("q2", "dose_ladder", "D1-1")):
                item_dir = os.path.join(mini, "published", item_id)
                os.makedirs(item_dir, exist_ok=True)
                common.write_json(os.path.join(item_dir, "public_instance.json"), public_payload(item_id))
                common.write_json(os.path.join(item_dir, "private_gold.json"), gold_payload(item_id, block, cell))
            scanned = make_design.scan_build_index(mini, expected_n=2)
            require(len(scanned["items"]) == 2, "scanner missed items")
            require(scanned["items"][1]["mechanism"] == "D1" and scanned["items"][1]["dose"] == 1, "scanner lost dose-ladder metadata")
            mini_index = os.path.join(out, "r28_schema_mini_index.json")
            common.write_json(mini_index, scanned)
            build = build_bundle.load_build(None, mini, mini_index)
            mini_bundle = os.path.join(out, "r28_schema_mini_bundle")
            receipt = build_bundle.build_bundles(build, None, mini_bundle, strict=True)
            require(receipt["n_items"] == 2 and receipt["leak_screen"]["verdict"] == "PASS", "real-layout bundle failed")
            return {
                "checker_accepts_real_records": True,
                "public_dossier_adapter": "PASS",
                "certificate_proof_adapter": "PASS",
                "dose_ladder_cell_parser": "D1-1 -> D1/1",
                "mini_build_bundle": receipt["n_items"],
            }

        step("real_r28_schema_adapter", r28_schema_adapter)

        # ---------------------------------------------------------------- design
        def design() -> dict[str, Any]:
            design_dir = os.path.join(out, "design")
            os.makedirs(design_dir, exist_ok=True)
            manifest_path = os.path.join(design_dir, "manifest_n320.json")
            result = run([py(), script("make_design.py"), "manifest", "--n", "320", "--out", manifest_path])
            require(result.returncode == 0, "make_design manifest failed", result.stderr[-1500:])
            generated = common.load_json(manifest_path)
            canonical = common.load_json(os.path.join(KIT, "design_manifest_n320.json"))
            require(generated["slots"] == canonical["slots"], "generated design slots differ from canonical")
            require(generated["strata"] == canonical["strata"], "generated design strata differ from canonical")
            require(generated["counts"] == canonical["counts"], "generated design counts differ")
            sample_path = os.path.join(design_dir, "sample.json")
            result = run([py(), script("make_design.py"), "sample", "--manifest", manifest_path, "--out", sample_path])
            require(result.returncode == 0, "make_design sample failed", result.stderr[-1500:])
            sample = common.load_json(sample_path)
            canonical_sample = common.load_json(os.path.join(KIT, "sample_ids.json"))
            require(sample["slots"] == canonical_sample["slots"], "regenerated sample slots differ from canonical")
            require(sample["strata"] == canonical_sample["strata"], "regenerated sample strata differ")
            # determinism under shuffled input order
            shuffled = json.loads(json.dumps(canonical))
            shuffled["slots"] = list(reversed(shuffled["slots"]))
            shuffled["strata"] = list(reversed(shuffled["strata"]))
            second = make_design.make_sample(shuffled, seed=SEED)
            require([slot["slot_id"] for slot in second["slots"]] == [slot["slot_id"] for slot in canonical_sample["slots"]], "sample depends on input order")
            validation = run([py(), script("make_design.py"), "validate", "--sample", os.path.join(KIT, "sample_ids.json"), "--manifest", os.path.join(KIT, "design_manifest_n320.json")])
            require(validation.returncode == 0, "sample_ids.json failed validation", validation.stdout)
            allocation = {stratum["block"]: 0 for stratum in canonical_sample["strata"]}
            for stratum in canonical_sample["strata"]:
                allocation[stratum["block"]] += stratum["sample_n"]
            require(allocation == {"factor_core": 40, "dose_ladder": 60}, "sample allocation changed", allocation)
            return {
                "n_published": generated["counts"]["n_published"],
                "n_slots": len(generated["slots"]),
                "n_sample": len(canonical_sample["slots"]),
                "strata": len(canonical_sample["strata"]),
                "allocation": allocation,
                "sample_sha256": common.sha256_file(os.path.join(KIT, "sample_ids.json")),
            }

        step("design_manifest_and_sample", design)

        # ---------------------------------------------------------------- synthetic build
        def synthetic() -> dict[str, Any]:
            build_out = os.path.join(out, "synthetic_build_v320.json")
            index_out = os.path.join(out, "synthetic_build_index.json")
            result = run(
                [
                    py(),
                    script("make_synthetic.py"),
                    "build",
                    "--design-manifest",
                    os.path.join(KIT, "design_manifest_n320.json"),
                    "--out-build",
                    build_out,
                    "--out-index",
                    index_out,
                ]
            )
            require(result.returncode == 0, "synthetic build failed", result.stderr[-1500:])
            rebuilt = common.load_json(build_out)
            fixture = common.load_json(os.path.join(FIXTURES, "synthetic_build_v320.json"))
            require(common.canonical_json(rebuilt) == common.canonical_json(fixture), "synthetic build is not deterministic")
            require(len(rebuilt["items"]) == 320 and len(rebuilt["build_index"]) == 320, "synthetic build wrong size")
            return {"sha256": common.sha256_file(build_out), "n_items": len(rebuilt["items"]), "deterministic": True}

        step("synthetic_build_determinism", synthetic)

        # ---------------------------------------------------------------- binding
        def binding() -> dict[str, Any]:
            bound_path = os.path.join(out, "sample_ids_bound.json")
            receipt_path = os.path.join(out, "BINDING_RECEIPT.json")
            result = run(
                [
                    py(),
                    script("make_design.py"),
                    "resolve",
                    "--index",
                    os.path.join(KIT, "fixtures", "synthetic_build_index.json"),
                    "--sample",
                    os.path.join(KIT, "sample_ids.json"),
                    "--out",
                    bound_path,
                    "--receipt",
                    receipt_path,
                    "--strict",
                ]
            )
            require(result.returncode == 0, "sample binding failed", result.stderr[-1500:])
            bound = common.load_json(bound_path)
            receipt = common.load_json(receipt_path)
            require(bound["status"] == "BOUND", "bound sample status wrong")
            require(len(bound["item_ids"]) == 100 and len(set(bound["item_ids"])) == 100, "bound sample ids not 100 unique")
            require(len(bound["strata"]) == 28, "bound sample lost strata")
            require(receipt["coverage"]["dead_ball"] == 1, "certainty inclusion missed the DEAD_REBALL item", receipt["coverage"])
            # re-run and compare selection (timestamps are the only allowed difference)
            bound2 = os.path.join(out, "sample_ids_bound_2.json")
            receipt2 = os.path.join(out, "BINDING_RECEIPT_2.json")
            result = run(
                [
                    py(),
                    script("make_design.py"),
                    "resolve",
                    "--index",
                    os.path.join(KIT, "fixtures", "synthetic_build_index.json"),
                    "--sample",
                    os.path.join(KIT, "sample_ids.json"),
                    "--out",
                    bound2,
                    "--receipt",
                    receipt2,
                    "--strict",
                ]
            )
            require(result.returncode == 0, "second binding failed")
            require(strip_time(common.load_json(bound_path)) == strip_time(common.load_json(bound2)), "binding is not deterministic")
            return {
                "n_bound": len(bound["item_ids"]),
                "dead_ball": receipt["coverage"]["dead_ball"],
                "legal_dismissals": receipt["coverage"]["legal_dismissals"],
                "bound_sha256": common.sha256_file(bound_path),
            }

        step("sample_to_build_binding", binding)

        # ---------------------------------------------------------------- bundles
        def bundles() -> dict[str, Any]:
            bundle_dir = os.path.join(out, "bundle")
            result = run(
                [
                    py(),
                    script("build_bundle.py"),
                    "--build-file",
                    os.path.join(FIXTURES, "synthetic_build_v320.json"),
                    "--sample",
                    os.path.join(out, "sample_ids_bound.json"),
                    "--out-dir",
                    bundle_dir,
                ]
            )
            require(result.returncode == 0, "bundle build failed", result.stderr[-1500:])
            receipt = common.load_json(os.path.join(bundle_dir, "BUNDLE_RECEIPT.json"))
            require(receipt["n_items"] == 100, "bundle item count wrong")
            require(receipt["leak_screen"]["verdict"] == "PASS", "public bundle leak screen failed", receipt["leak_screen"])
            require(receipt["files"]["bundle_public.json"]["sha256"] != receipt["files"]["bundle_gold.json"]["sha256"], "public and gold bundles are identical")
            public = common.load_json(os.path.join(bundle_dir, "bundle_public.json"))
            gold = common.load_json(os.path.join(bundle_dir, "bundle_gold.json"))
            require(public["kind"] == "PUBLIC" and gold["kind"] == "GOLD", "bundle kinds wrong")
            forbidden = {"gold", "decision_record_flat", "solver_facts", "level", "dose", "family", "stratum"}
            def keys(node: Any) -> set[str]:
                found: set[str] = set()
                if isinstance(node, dict):
                    for key, value in node.items():
                        found.add(str(key).lower())
                        found.update(keys(value))
                elif isinstance(node, list):
                    for value in node:
                        found.update(keys(value))
                return found
            require(not (keys(public) & forbidden), "public bundle contains answer-bearing keys", sorted(keys(public) & forbidden))
            for gold_item in gold["items"]:
                require(len(gold_item["gold"]["proof"]["minimum_evidence_spans"]) >= 1, "gold proof empty")
            return {
                "n_items": receipt["n_items"],
                "public_sha256": receipt["files"]["bundle_public.json"]["sha256"],
                "gold_sha256": receipt["files"]["bundle_gold.json"]["sha256"],
                "leak_screen": receipt["leak_screen"]["verdict"],
            }

        step("bundle_build_and_hidden_gold", bundles)

        # ---------------------------------------------------------------- answers + qualification set
        def answers() -> dict[str, Any]:
            answer_dir = os.path.join(out, "answers")
            result = run(
                [
                    py(),
                    script("make_synthetic.py"),
                    "answers",
                    "--build",
                    os.path.join(FIXTURES, "synthetic_build_v320.json"),
                    "--bound-sample",
                    os.path.join(out, "sample_ids_bound.json"),
                    "--out-dir",
                    answer_dir,
                ]
            )
            require(result.returncode == 0, "synthetic answers failed", result.stderr[-1500:])
            for annotator in ("a", "b"):
                rows = common.load_jsonl(os.path.join(answer_dir, f"synthetic_answers_{annotator}.jsonl"))
                require(len(rows) == 100, f"answer script {annotator} not 100 rows")
            adjudications = common.load_jsonl(os.path.join(answer_dir, "synthetic_adjudications.jsonl"))
            require(len(adjudications) == 7, "expected 7 planned adjudications")
            qualification_dir = os.path.join(out, "qualification")
            result = run(
                [
                    py(),
                    script("make_synthetic.py"),
                    "qualification",
                    "--build",
                    os.path.join(FIXTURES, "synthetic_build_v320.json"),
                    "--bound-sample",
                    os.path.join(out, "sample_ids_bound.json"),
                    "--out-dir",
                    qualification_dir,
                ]
            )
            require(result.returncode == 0, "qualification fixture failed", result.stderr[-1500:])
            qualification = common.load_json(os.path.join(qualification_dir, "qualification_ids.json"))
            require(len(qualification["item_ids"]) == 20, "qualification set must be 20 items")
            return {"n_answers": 100, "n_adjudications": len(adjudications), "n_qualification": len(qualification["item_ids"])}

        step("synthetic_answer_scripts", answers)

        # ---------------------------------------------------------------- CLI two-phase annotation
        def annotate() -> dict[str, Any]:
            bundle_dir = os.path.join(out, "bundle")
            answer_dir = os.path.join(out, "answers")
            for annotator in ("a", "b"):
                derived = os.path.join(out, f"ann_{annotator}_derived.jsonl")
                verify = os.path.join(out, f"ann_{annotator}_verify.jsonl")
                result = run(
                    [
                        py(),
                        script("annotate_cli.py"),
                        "derive",
                        "--annotator-id",
                        annotator.upper(),
                        "--bundle",
                        os.path.join(bundle_dir, "bundle_public.json"),
                        "--out",
                        derived,
                        "--script",
                        os.path.join(answer_dir, f"synthetic_answers_{annotator}.jsonl"),
                    ]
                )
                require(result.returncode == 0, f"derive {annotator} failed", result.stderr[-1500:])
                result = run(
                    [
                        py(),
                        script("annotate_cli.py"),
                        "verify",
                        "--annotator-id",
                        annotator.upper(),
                        "--bundle",
                        os.path.join(bundle_dir, "bundle_public.json"),
                        "--gold-bundle",
                        os.path.join(bundle_dir, "bundle_gold.json"),
                        "--derived",
                        derived,
                        "--out",
                        verify,
                        "--script",
                        os.path.join(answer_dir, f"synthetic_answers_{annotator}.jsonl"),
                    ]
                )
                require(result.returncode == 0, f"verify {annotator} failed", result.stderr[-1500:])
                for kind, path, extra in (
                    (common.KIND_DERIVED, derived, ["--public-bundle", os.path.join(bundle_dir, "bundle_public.json")]),
                    (
                        common.KIND_VERIFY,
                        verify,
                        [
                            "--public-bundle",
                            os.path.join(bundle_dir, "bundle_public.json"),
                            "--gold-bundle",
                            os.path.join(bundle_dir, "bundle_gold.json"),
                            "--derived",
                            derived,
                        ],
                    ),
                ):
                    validation_path = os.path.join(out, f"validate_{annotator}_{kind.lower()}.json")
                    result = run(
                        [
                            py(),
                            script("validate_export.py"),
                            "--kind",
                            kind,
                            "--file",
                            path,
                            *extra,
                            "--sample",
                            os.path.join(out, "sample_ids_bound.json"),
                            "--out",
                            validation_path,
                        ]
                    )
                    require(result.returncode == 0, f"validation {annotator}/{kind} failed", result.stdout + result.stderr[-1200:])
            return {"n_derived_per_annotator": 100, "n_verify_per_annotator": 100}

        step("cli_blind_derive_and_verify", annotate)

        # ---------------------------------------------------------------- browser export seal path
        def seal() -> dict[str, Any]:
            bundle_dir = os.path.join(out, "bundle")
            answer_dir = os.path.join(out, "answers")
            browser_dir = os.path.join(out, "browser_export")
            os.makedirs(browser_dir, exist_ok=True)
            # simulate a browser export: integrity fields absent
            derived_rows = common.load_jsonl(os.path.join(out, "ann_a_derived.jsonl"))
            for row in derived_rows:
                row["derived_sha256"] = None
                row["public_bundle_sha256"] = None
            browser_derived = os.path.join(browser_dir, "annotations_derived_A.jsonl")
            common.write_jsonl(browser_derived, derived_rows)
            sealed_derived = os.path.join(browser_dir, "sealed_derived_A.jsonl")
            result = run(
                [
                    py(), script("seal_export.py"), "--kind", common.KIND_DERIVED,
                    "--file", browser_derived, "--out", sealed_derived,
                    "--public-bundle", os.path.join(bundle_dir, "bundle_public.json"),
                    "--receipt", os.path.join(browser_dir, "seal_derived_A.json"),
                ]
            )
            require(result.returncode == 0, "seal DERIVED failed", result.stdout + result.stderr[-1200:])
            polished = common.load_jsonl(sealed_derived)
            require(all(row.get("derived_sha256") for row in polished), "sealed DERIVED lacks hashes")
            require(all(row.get("public_bundle_sha256") for row in polished), "sealed DERIVED lacks public bundle hash")
            require([row["derived"] for row in polished] == [row["derived"] for row in derived_rows], "seal changed derived values")
            validation = run(
                [
                    py(), script("validate_export.py"), "--kind", common.KIND_DERIVED, "--file", sealed_derived,
                    "--public-bundle", os.path.join(bundle_dir, "bundle_public.json"),
                    "--sample", os.path.join(out, "sample_ids_bound.json"),
                ]
            )
            require(validation.returncode == 0, "sealed DERIVED failed validation", validation.stdout)
            # VERIFY export: derived link + gold record hash filled by the seal step
            verify_rows = common.load_jsonl(os.path.join(out, "ann_a_verify.jsonl"))
            for row in verify_rows:
                row["derived_sha256"] = None
                row["gold_record_sha256"] = None
                row["gold_bundle_sha256"] = None
                row["public_bundle_sha256"] = None
            browser_verify = os.path.join(browser_dir, "annotations_verify_A.jsonl")
            common.write_jsonl(browser_verify, verify_rows)
            sealed_verify = os.path.join(browser_dir, "sealed_verify_A.jsonl")
            result = run(
                [
                    py(), script("seal_export.py"), "--kind", common.KIND_VERIFY,
                    "--file", browser_verify, "--out", sealed_verify,
                    "--public-bundle", os.path.join(bundle_dir, "bundle_public.json"),
                    "--gold-bundle", os.path.join(bundle_dir, "bundle_gold.json"),
                    "--derived", sealed_derived,
                    "--receipt", os.path.join(browser_dir, "seal_verify_A.json"),
                ]
            )
            require(result.returncode == 0, "seal VERIFY failed", result.stdout + result.stderr[-1200:])
            polished_verify = common.load_jsonl(sealed_verify)
            require(all(row.get("derived_sha256") and row.get("gold_record_sha256") for row in polished_verify), "sealed VERIFY lacks link hashes")
            require([row["labels"] for row in polished_verify] == [row["labels"] for row in verify_rows], "seal changed VERIFY labels")
            validation = run(
                [
                    py(), script("validate_export.py"), "--kind", common.KIND_VERIFY, "--file", sealed_verify,
                    "--public-bundle", os.path.join(bundle_dir, "bundle_public.json"),
                    "--gold-bundle", os.path.join(bundle_dir, "bundle_gold.json"),
                    "--derived", sealed_derived,
                    "--sample", os.path.join(out, "sample_ids_bound.json"),
                ]
            )
            require(validation.returncode == 0, "sealed VERIFY failed validation", validation.stdout)
            # ADJUDICATION seal path
            sealed_adj = os.path.join(browser_dir, "sealed_adjudications.jsonl")
            result = run(
                [
                    py(), script("seal_export.py"), "--kind", common.KIND_ADJUDICATION,
                    "--file", os.path.join(answer_dir, "synthetic_adjudications.jsonl"),
                    "--out", sealed_adj,
                ]
            )
            require(result.returncode == 0, "seal ADJUDICATION failed", result.stdout + result.stderr[-1200:])
            # negative path: sealing a DERIVED file as VERIFY must fail
            result = run(
                [
                    py(), script("seal_export.py"), "--kind", common.KIND_VERIFY,
                    "--file", browser_derived, "--out", os.path.join(browser_dir, "bad.jsonl"),
                    "--gold-bundle", os.path.join(bundle_dir, "bundle_gold.json"),
                    "--derived", sealed_derived,
                ]
            )
            require(result.returncode == 4, "seal kind mismatch must exit 4")
            return {"derived": "sealed", "verify": "sealed", "adjudication": "sealed", "kind_mismatch": "rejected"}

        step("browser_export_seal_and_validate", seal)

        # ---------------------------------------------------------------- agreement + independent kappa
        def agreement() -> dict[str, Any]:
            result = run(
                [
                    py(),
                    script("agreement.py"),
                    "--a",
                    os.path.join(out, "ann_a_verify.jsonl"),
                    "--b",
                    os.path.join(out, "ann_b_verify.jsonl"),
                    "--derived-a",
                    os.path.join(out, "ann_a_derived.jsonl"),
                    "--derived-b",
                    os.path.join(out, "ann_b_derived.jsonl"),
                    "--sample",
                    os.path.join(out, "sample_ids_bound.json"),
                    "--out-dir",
                    os.path.join(out, "agreement"),
                ]
            )
            require(result.returncode == 0, "agreement failed", result.stderr[-1500:])
            report = common.load_json(os.path.join(out, "agreement", "agreement_report.json"))
            require(report["h1_agreement_gate_pass"] is True, "H1 agreement gate failed in clean synthetic run")
            for dimension, expected in EXPECTED_AGREEMENT.items():
                actual = report["dimensions"][dimension]["agreement_rate"]
                require(abs(actual - expected) < 1e-9, f"{dimension} agreement {actual} != expected {expected}")
            require(report["n_disagreements"] == 9, "expected 9 disagreements (7 dimension + 2 field)", report["n_disagreements"])
            # independent kappa recomputation from raw annotations
            a_rows = common.load_jsonl(os.path.join(out, "ann_a_verify.jsonl"))
            b_rows = common.load_jsonl(os.path.join(out, "ann_b_verify.jsonl"))
            b_by_id = {row["item_id"]: row for row in b_rows}
            for dimension in common.DIMENSIONS:
                pairs = []
                for row in a_rows:
                    pairs.append((row["labels"][dimension]["verdict"], b_by_id[row["item_id"]]["labels"][dimension]["verdict"]))
                independent = independent_kappa(pairs, list(common.DIM_LABELS[dimension]))
                reported = report["dimensions"][dimension]["cohen_kappa"]
                if independent is None:
                    require(reported is None, f"{dimension}: report has kappa but independent is undefined")
                else:
                    require(reported is not None and abs(reported - independent) < 1e-6, f"{dimension}: kappa mismatch", {"reported": reported, "independent": independent})
            requires = [
                report["dimensions"][dimension]["bootstrap_kappa"]["n_defined"] >= 0
                for dimension in common.DIMENSIONS
            ]
            require(all(requires), "bootstrap CI did not run")
            return {
                "agreement": {dimension: report["dimensions"][dimension]["agreement_rate"] for dimension in common.DIMENSIONS},
                "kappa": {dimension: report["dimensions"][dimension]["cohen_kappa"] for dimension in common.DIMENSIONS},
                "n_disagreements": report["n_disagreements"],
                "independent_kappa_check": "PASS",
            }

        step("agreement_kappa_and_disagreements", agreement)

        # ---------------------------------------------------------------- qualification pass/fail
        def qualification() -> dict[str, Any]:
            qualification_dir = os.path.join(out, "qualification")
            bundle_dir = os.path.join(qualification_dir, "qualification_bundle")
            ids = os.path.join(qualification_dir, "qualification_ids.json")
            results: dict[str, Any] = {}
            for annotator in ("a", "b"):
                derived = os.path.join(qualification_dir, f"qual_ann_{annotator}_derived.jsonl")
                verify = os.path.join(qualification_dir, f"qual_ann_{annotator}_verify.jsonl")
                result = run(
                    [
                        py(),
                        script("annotate_cli.py"),
                        "derive",
                        "--annotator-id",
                        annotator.upper(),
                        "--bundle",
                        os.path.join(bundle_dir, "bundle_public.json"),
                        "--out",
                        derived,
                        "--script",
                        os.path.join(qualification_dir, f"synthetic_qualification_{annotator}.jsonl"),
                    ]
                )
                require(result.returncode == 0, f"qualification derive {annotator} failed", result.stderr[-1200:])
                result = run(
                    [
                        py(),
                        script("annotate_cli.py"),
                        "verify",
                        "--annotator-id",
                        annotator.upper(),
                        "--bundle",
                        os.path.join(bundle_dir, "bundle_public.json"),
                        "--gold-bundle",
                        os.path.join(bundle_dir, "bundle_gold.json"),
                        "--derived",
                        derived,
                        "--out",
                        verify,
                        "--script",
                        os.path.join(qualification_dir, f"synthetic_qualification_{annotator}.jsonl"),
                        "--feedback",
                    ]
                )
                require(result.returncode == 0, f"qualification verify {annotator} failed", result.stderr[-1200:])
                out_path = os.path.join(qualification_dir, f"qualification_{annotator}.json")
                result = run(
                    [
                        py(),
                        script("qualification.py"),
                        "--derived",
                        derived,
                        "--verify",
                        verify,
                        "--gold-bundle",
                        os.path.join(bundle_dir, "bundle_gold.json"),
                        "--annotator-id",
                        annotator.upper(),
                        "--items",
                        ids,
                        "--out",
                        out_path,
                    ]
                )
                require(result.returncode == 0, f"qualification gate failed for {annotator}", result.stdout + result.stderr[-1200:])
                payload = common.load_json(out_path)
                require(payload["pass"] is True, f"qualification {annotator} did not pass")
                for dimension, expected in EXPECTED_QUALIFICATION.items():
                    require(abs(payload["dimensions"][dimension]["confirmation_accuracy"] - expected) < 1e-9, "qualification accuracy changed")
                results[annotator] = {"pass": True, "critical_errors": payload["critical_errors_total"]}
            # negative path: one critical error must fail the gate
            negative_path = os.path.join(qualification_dir, "negative_b_verify.jsonl")
            rows = common.load_jsonl(os.path.join(qualification_dir, "qual_ann_b_verify.jsonl"))
            rows[0]["labels"]["value"]["fields"]["batter_runs"] = "MISMATCH"
            rows[0]["labels"]["value"]["verdict"] = "MISMATCH"
            common.write_jsonl(negative_path, rows)
            negative_out = os.path.join(qualification_dir, "negative_b_result.json")
            result = run(
                [
                    py(),
                    script("qualification.py"),
                    "--derived",
                    os.path.join(qualification_dir, "qual_ann_b_derived.jsonl"),
                    "--verify",
                    negative_path,
                    "--gold-bundle",
                    os.path.join(bundle_dir, "bundle_gold.json"),
                    "--annotator-id",
                    "B",
                    "--items",
                    ids,
                    "--out",
                    negative_out,
                ]
            )
            require(result.returncode == 4, "qualification negative path must exit 4")
            negative = common.load_json(negative_out)
            require(negative["pass"] is False and negative["critical_errors_total"] >= 1, "qualification negative path did not fail on a critical error")
            results["negative_path"] = {"pass": False, "critical_errors": negative["critical_errors_total"]}
            return results

        step("qualification_gate_pass_and_fail", qualification)

        # ---------------------------------------------------------------- adjudication clean + defect
        def adjudication() -> dict[str, Any]:
            qualification_dir = os.path.join(out, "qualification")
            bundle_dir = os.path.join(out, "bundle")
            clean_dir = os.path.join(out, "adjudication_clean")
            result = run(
                [
                    py(),
                    script("adjudicate.py"),
                    "--a",
                    os.path.join(out, "ann_a_verify.jsonl"),
                    "--b",
                    os.path.join(out, "ann_b_verify.jsonl"),
                    "--gold-bundle",
                    os.path.join(bundle_dir, "bundle_gold.json"),
                    "--out-dir",
                    clean_dir,
                    "--adjudications",
                    os.path.join(out, "answers", "synthetic_adjudications.jsonl"),
                    "--sample",
                    os.path.join(out, "sample_ids_bound.json"),
                    "--derived-a",
                    os.path.join(out, "ann_a_derived.jsonl"),
                    "--derived-b",
                    os.path.join(out, "ann_b_derived.jsonl"),
                    "--qual-a-derived",
                    os.path.join(qualification_dir, "qual_ann_a_derived.jsonl"),
                    "--qual-a-verify",
                    os.path.join(qualification_dir, "qual_ann_a_verify.jsonl"),
                    "--qual-b-derived",
                    os.path.join(qualification_dir, "qual_ann_b_derived.jsonl"),
                    "--qual-b-verify",
                    os.path.join(qualification_dir, "qual_ann_b_verify.jsonl"),
                    "--qual-gold",
                    os.path.join(qualification_dir, "qualification_bundle", "bundle_gold.json"),
                    "--qual-items",
                    os.path.join(qualification_dir, "qualification_ids.json"),
                ]
            )
            require(result.returncode == 0, "clean adjudication should exit 0 (PASS)", result.stdout + result.stderr[-1500:])
            clean = common.load_json(os.path.join(clean_dir, "HUMAN_VERIFICATION_REPORT.json"))
            require(clean["status"] == "PASS", "clean adjudication status != PASS")
            require(all(gate["pass"] for gate in clean["gates"].values()), "clean adjudication gates not all pass", clean["gates"])
            require(clean["counts"]["n_verified"] == 100, "clean adjudication did not verify 100 items")
            require(clean["counts"]["n_gold_defect"] == 0, "clean adjudication found a gold defect")
            require(clean["human_gold_produced"] is False and clean["gold_authoritative_source"] == "deterministic_solver", "gold boundary statement missing")
            # defect path: both annotators agree the gold value is wrong (simulated gold defect)
            defect_dir = os.path.join(out, "adjudication_defect")
            os.makedirs(defect_dir, exist_ok=True)
            first_item = common.load_json(os.path.join(out, "sample_ids_bound.json"))["item_ids"][0]
            for annotator in ("a", "b"):
                rows = common.load_jsonl(os.path.join(out, f"ann_{annotator}_verify.jsonl"))
                for row in rows:
                    if row["item_id"] == first_item:
                        row["labels"]["value"]["fields"]["batter_runs"] = "MISMATCH"
                        row["labels"]["value"]["verdict"] = "MISMATCH"
                common.write_jsonl(os.path.join(defect_dir, f"ann_{annotator}_verify.jsonl"), rows)
            adjudications = common.load_jsonl(os.path.join(out, "answers", "synthetic_adjudications.jsonl"))
            adjudications = [row for row in adjudications if not (row["item_id"] == first_item and row["dimension"] == "value")]
            adjudications.append(
                {
                    "schema": f"{common.SCHEMA_PREFIX}.adjudication.v1",
                    "kind": common.KIND_ADJUDICATION,
                    "kit_version": common.KIT_VERSION,
                    "adjudicator_id": "C",
                    "item_id": first_item,
                    "dimension": "value",
                    "field": None,
                    "final_label": "MISMATCH",
                    "attribution": "GOLD_DEFECT",
                    "rationale": "simulated defect: both annotators independently found the gold record wrong",
                }
            )
            defect_adj_path = os.path.join(defect_dir, "adjudications.jsonl")
            common.write_jsonl(defect_adj_path, adjudications)
            result = run(
                [
                    py(),
                    script("adjudicate.py"),
                    "--a",
                    os.path.join(defect_dir, "ann_a_verify.jsonl"),
                    "--b",
                    os.path.join(defect_dir, "ann_b_verify.jsonl"),
                    "--gold-bundle",
                    os.path.join(bundle_dir, "bundle_gold.json"),
                    "--out-dir",
                    defect_dir,
                    "--adjudications",
                    defect_adj_path,
                    "--sample",
                    os.path.join(out, "sample_ids_bound.json"),
                    "--derived-a",
                    os.path.join(out, "ann_a_derived.jsonl"),
                    "--derived-b",
                    os.path.join(out, "ann_b_derived.jsonl"),
                    "--qual-a-derived",
                    os.path.join(qualification_dir, "qual_ann_a_derived.jsonl"),
                    "--qual-a-verify",
                    os.path.join(qualification_dir, "qual_ann_a_verify.jsonl"),
                    "--qual-b-derived",
                    os.path.join(qualification_dir, "qual_ann_b_derived.jsonl"),
                    "--qual-b-verify",
                    os.path.join(qualification_dir, "qual_ann_b_verify.jsonl"),
                    "--qual-gold",
                    os.path.join(qualification_dir, "qualification_bundle", "bundle_gold.json"),
                    "--qual-items",
                    os.path.join(qualification_dir, "qualification_ids.json"),
                ]
            )
            require(result.returncode == 4, "defect adjudication must exit 4 (FAIL)")
            defect = common.load_json(os.path.join(defect_dir, "HUMAN_VERIFICATION_REPORT.json"))
            require(defect["status"] == "FAIL", "defect adjudication status != FAIL")
            require(defect["gates"]["H2_zero_gold_defects"]["pass"] is False, "H2 did not fail on a simulated gold defect")
            require(defect["counts"]["n_gold_defect"] >= 1, "defect count did not increase")
            require(defect["gold_quarantine_required"] is True, "gold quarantine flag not set")
            require(os.path.isfile(os.path.join(defect_dir, "gold_defects.jsonl")), "gold_defects.jsonl missing")
            return {
                "clean_status": clean["status"],
                "clean_verified": clean["counts"]["n_verified"],
                "defect_status": defect["status"],
                "defect_items": defect["counts"]["n_gold_defect"],
                "gold_boundary": "NO HUMAN GOLD PRODUCED",
            }

        step("adjudication_clean_and_defect_paths", adjudication)

        # ---------------------------------------------------------------- pre-annotation
        def preannotation() -> dict[str, Any]:
            pre_dir = os.path.join(out, "preannotation")
            result = run(
                [
                    py(),
                    script("preannotate.py"),
                    "--bundle",
                    os.path.join(out, "bundle", "bundle_public.json"),
                    "--out-dir",
                    pre_dir,
                    "--adapter",
                    "stub",
                    "--max-spans-per-item",
                    "8",
                ]
            )
            require(result.returncode == 0, "preannotation stub failed", result.stderr[-1500:])
            rows = common.load_jsonl(os.path.join(pre_dir, "preannotations.jsonl"))
            require(len(rows) > 0, "preannotation produced no rows")
            for row in rows:
                require(row["not_gold"] is True and row["usable_as_gold"] is False, "preannotation must never be gold")
                require(row["provenance"]["status"] == "DEGRADED", "stub adapter must be DEGRADED")
                candidate = row.get("candidate") or {}
                require(not (set(candidate) & set(common.RECORD_FIELDS)), "preannotation must not emit record values")
            coverage = common.load_json(os.path.join(pre_dir, "PREANNOTATION_COVERAGE.json"))
            require(coverage["usable_as_gold"] is False, "coverage report claims gold")
            require(coverage["degraded_reason_counts"].get("RULE_BASELINE_ONLY", 0) == len(rows), "degraded coverage accounting wrong")
            # local-adapter failure path must downgrade, not crash
            local_dir = os.path.join(out, "preannotation", "does_not_exist")
            result = run(
                [
                    py(),
                    script("preannotate.py"),
                    "--bundle",
                    os.path.join(out, "bundle", "bundle_public.json"),
                    "--out-dir",
                    os.path.join(out, "preannotation_local_missing"),
                    "--adapter",
                    "local",
                    "--local-dir",
                    local_dir,
                    "--max-spans-per-item",
                    "2",
                ]
            )
            require(result.returncode == 0, "local-adapter failure path must degrade, not fail", result.stderr[-1500:])
            local_report = common.load_json(os.path.join(out, "preannotation_local_missing", "PREANNOTATION_COVERAGE.json"))
            require(local_report["coverage"]["S1_span_topic"]["degraded"] == local_report["coverage"]["S1_span_topic"]["attempted"], "missing local runtime must be 100% DEGRADED")
            # fake local service: prove the OK code path without calling any model
            fake_root = os.path.join(out, "fake_local")
            fake_pkg = os.path.join(fake_root, "local_inference")
            os.makedirs(fake_pkg, exist_ok=True)
            common.write_text(os.path.join(fake_pkg, "__init__.py"), "")
            common.write_text(
                os.path.join(fake_pkg, "api.py"),
                "def annotate(task_id, sample, caller='t24'):\n"
                "    text = (sample.get('span_text') or sample.get('passage') or '').lower()\n"
                "    topic = 'RUNS' if 'run' in text else 'BOWLING'\n"
                "    return {'status': 'OK', 'annotation': {'topic': topic, 'supported': True}, 'degraded': None,\n"
                "            'ledger_entry': {'model_tag': 'fake-local-for-selftest',\n"
                "                            'prompt_template_version': 'S1.span_topic.v4',\n"
                "                            'input_sha256': '0' * 64}}\n",
            )
            result = run(
                [
                    py(), script("preannotate.py"),
                    "--bundle", os.path.join(out, "bundle", "bundle_public.json"),
                    "--out-dir", os.path.join(out, "preannotation_fake_local"),
                    "--adapter", "local", "--local-dir", fake_root, "--max-spans-per-item", "3",
                ]
            )
            require(result.returncode == 0, "fake local adapter failed", result.stderr[-1500:])
            fake_rows = common.load_jsonl(os.path.join(out, "preannotation_fake_local", "preannotations.jsonl"))
            require(any(row["provenance"]["status"] == "OK" for row in fake_rows), "fake local adapter produced no OK rows")
            require(all(row["usable_as_gold"] is False and row["not_gold"] is True for row in fake_rows), "fake local rows claimed gold")
            require(all(row["provenance"]["adapter"] == "local_inference" for row in fake_rows), "fake local adapter not recorded")
            require(all(not (set((row.get("candidate") or {})) & set(common.RECORD_FIELDS)) for row in fake_rows), "fake local rows leaked record fields")
            return {"n_rows": len(rows), "status": "ALL_DEGRADED", "local_missing": "DEGRADED", "fake_local_ok_rows": sum(1 for row in fake_rows if row["provenance"]["status"] == "OK")}

        step("preannotation_degraded_only", preannotation)

        # ---------------------------------------------------------------- baseline
        def baseline() -> dict[str, Any]:
            out_path = os.path.join(out, "BASELINE_CHECK.json")
            result = run([py(), script("check_baseline.py"), "--out", out_path], timeout=600)
            require(result.returncode == 0, "baseline/freeze check failed", result.stdout + result.stderr[-1500:])
            payload = common.load_json(out_path)
            require(payload["protected_paths"]["totals"]["files"] == 338, "protected file count changed")
            require(payload["protected_paths"]["totals"]["aggregate_sha256"] == "66e108d8efbe91c6e2d91b973f5cbac3929518386384d8a8bafa26a97b2a0433", "protected aggregate changed")
            r26_group = next(group for group in payload["protected_paths"]["groups"] if group["id"] == "r26_15_candidate")
            require(r26_group["aggregate_sha256"] == R26_AGGREGATE, "R26.15 aggregate changed")
            require(payload["freeze_binding"]["ok"] is True, "contract/prereg freeze binding failed")
            return {
                "protected_files": payload["protected_paths"]["totals"]["files"],
                "protected_bytes": payload["protected_paths"]["totals"]["bytes"],
                "r26_15_aggregate": r26_group["aggregate_sha256"],
                "freeze_binding": "PASS",
            }

        step("r26_15_and_freeze_integrity", baseline)

    except StepFailure:
        pass

    selftest_result = {
        "schema": f"{common.SCHEMA_PREFIX}.selftest_result.v1",
        "kit_version": common.KIT_VERSION,
        "started_at_utc": started_at,
        "finished_at_utc": common.utc_now(),
        "python": sys.version,
        "out_dir": out,
        "steps": steps,
        "n_pass": sum(1 for item in steps if item["status"] == "PASS"),
        "n_fail": sum(1 for item in steps if item["status"] == "FAIL"),
        "ok": all(item["status"] == "PASS" for item in steps) and len(steps) == 14,
        "scope": "synthetic R28-shaped build only; no R28 data exists; no human annotation was performed",
        "no_network": True,
        "no_paid_api": True,
        "human_gold_produced": False,
    }
    result_path = os.path.join(out, "SELFTEST_RESULT.json")
    common.write_json(result_path, selftest_result)
    # status + manifest
    status = build_status(selftest_result)
    common.write_json(os.path.join(KIT, "STATUS.json"), status)
    manifest = build_manifest()
    common.write_json(os.path.join(KIT, "KIT_MANIFEST.json"), manifest)
    print(common.canonical_json({"ok": selftest_result["ok"], "n_pass": selftest_result["n_pass"], "n_fail": selftest_result["n_fail"], "result": result_path, "manifest_files": manifest["file_count"]}))
    return 0 if selftest_result["ok"] else 4


def build_status(selftest_result: dict[str, Any]) -> dict[str, Any]:
    build_index_found = []
    run_root = common.run_root()
    if os.path.isdir(run_root):
        for dirpath, dirnames, filenames in os.walk(run_root):
            dirnames[:] = [name for name in dirnames if name not in ("__pycache__", "local", "04_verify", "05_release")]
            for name in filenames:
                if name.lower() in ("build_index.json",):
                    build_index_found.append(os.path.join(dirpath, name))
    blockers = [
        "HUMAN_DOUBLE_ANNOTATION_NOT_EXECUTED: t24 prepares the kit; it never produces human gold",
        "R28_BUILD_NOT_PRESENT: a build_index.json with per-item block/cell or mechanism/dose was not found under the R28 run root",
        "SAMPLE_ITEM_IDS_UNBOUND: sample_ids.json is a 100-slot design sample; run make_design.py resolve after the build exists",
        "PREANNOTATION_DEGRADED_ONLY: no local-model call was made in this kit; the pack is DEGRADED by design until R28 data exists",
        "PAPER_BLOCKER: until adjudicate.py reports PASS on real data, the paper must list 'gold not verified by independent human double annotation' as a blocking limitation",
    ]
    return {
        "schema": f"{common.SCHEMA_PREFIX}.status.v1",
        "kit_version": common.KIT_VERSION,
        "generated_at_utc": common.utc_now(),
        "ready_for_handoff": bool(selftest_result["ok"]),
        "ready_to_annotate": False,
        "ready_to_annotate_reason": "requires the frozen R28 build, a published build_index.json, bound sample item ids, and 20-item qualification passes",
        "selftest": {"ok": selftest_result["ok"], "n_pass": selftest_result["n_pass"], "n_fail": selftest_result["n_fail"], "result": "out/selftest/SELFTEST_RESULT.json"},
        "components": {
            "annotation_protocol": "present",
            "sampling_plan_and_sample_ids": "present (100 slots; provisional until build binding)",
            "annotation_tool": "present (single-file offline HTML + CLI)",
            "agreement_statistics": "present (Cohen's kappa + per-dimension agreement + disagreements)",
            "adjudication_and_gates": "present (H1/H2/H3; no human gold produced)",
            "preannotation_pack": "present (hints only; DEGRADED by design without R28 data)",
            "baseline_integrity": "present (R26.15 re-hashed from bytes in selftest)",
        },
        "blockers": blockers,
        "paper_blocker": True,
        "human_gold_produced": False,
        "gold_authoritative_source": "deterministic_solver",
        "build_index_candidates_found": build_index_found,
        "next_actions": [
            "After t6 publishes the candidate build: export build_index.json (block/cell for factor core; mechanism/dose for dose ladder).",
            "If the build only ships published/<id>/private_gold.json with block/cell/doses, derive the index first: python scripts/make_design.py index --build-dir <candidate> --out build_index.json",
            "Run: python scripts/make_design.py resolve --index <build_index.json> --sample sample_ids.json --out sample_ids_bound.json --receipt BINDING_RECEIPT.json --strict",
            "Run: python scripts/build_bundle.py --build-dir <candidate> --sample sample_ids_bound.json --out-dir out/annotation_bundle",
            "Run: python scripts/preannotate.py --bundle out/annotation_bundle/bundle_public.json --out-dir out/preannotation --adapter local",
            "Run qualification for A and B (20 synthetic calibration items) before the 100-item sample.",
            "Execute two independent blind DERIVED passes and two gold-revealed VERIFY passes; seal exports; run agreement.py then adjudicate.py.",
            "If adjudicate.py does not return PASS: quarantine the gold, repair, re-verify; do not publish a 'human-verified gold' claim.",
        ],
    }


def build_manifest() -> dict[str, Any]:
    rows = []
    for dirpath, dirnames, filenames in os.walk(KIT):
        dirnames[:] = sorted(name for name in dirnames if name not in ("__pycache__", "out"))
        for name in sorted(filenames):
            if name in ("KIT_MANIFEST.json",) or name.endswith(".pyc"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, KIT).replace("\\", "/")
            rows.append({"path": rel, "bytes": os.path.getsize(path), "sha256": common.sha256_file(path)})
    rows.sort(key=lambda row: row["path"])
    text = "".join(f"{row['sha256']}  {row['path']}\n" for row in rows)
    return {
        "schema": f"{common.SCHEMA_PREFIX}.kit_manifest.v1",
        "kit_version": common.KIT_VERSION,
        "generated_at_utc": common.utc_now(),
        "file_count": len(rows),
        "total_bytes": sum(row["bytes"] for row in rows),
        "aggregate_recipe": "vett-tree-aggregate-v1: sorted '<sha256>  <path>\\n' lines, trailing LF",
        "aggregate_sha256": common.sha256_text(text),
        "files": rows,
    }


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except common.KitError as exc:
        common.eprint(f"ERROR {exc}")
        raise SystemExit(4)
