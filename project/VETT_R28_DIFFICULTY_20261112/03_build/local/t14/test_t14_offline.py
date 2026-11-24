"""Offline (no-GPU) validation of t14 report + acceptance logic.

Builds a synthetic set of 320 annotation rows with the expected class/score shapes,
plus a fake complete ledger, and asserts that ``check_acceptance`` passes and
``build_report`` renders.  Also validates the negative cases: constant T1 truth and
a T2 row whose preference is not derived from the scores must fail.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

T14_ROOT = Path(__file__).resolve().parent
LOCAL = T14_ROOT.parent
RUN_ROOT = LOCAL.parents[1]
for _p in (str(T14_ROOT), str(LOCAL), str(RUN_ROOT / "05_pipeline"),
           str(RUN_ROOT / "02_design" / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from local_inference import ledger  # noqa: E402

import t14_report  # noqa: E402
import t14_runner as R  # noqa: E402

RUN_ID = "t14_offline_test"
FAKE_SHA = "a" * 64


def fake_ledger(run_dir: Path, calls: int = 960) -> None:
    path = run_dir / "local_cost_ledger.jsonl"
    if path.exists():
        path.unlink()
    for index in range(calls):
        entry = ledger.build_entry(
            task="T1_factor_visibility", template_version="T1.factor_visibility.v1",
            prompt=f"fake prompt {index}", raw_output='{"supported": true}',
            parsed_output={"supported": True}, parsed_ok=True, wall_clock=0.1,
            call={"prompt_eval_count": 10, "eval_count": 2, "context_length": 8192,
                  "_num_predict": 128},
            service_info={"digest": "fake", "quantization_level": "Q4_K_M"})
        ledger.append_entry(entry, path=path)


def t1_rows() -> list[dict]:
    classes = (["POS_OVERRIDE"] * 64 + ["NEG_PROVENANCE_ADJACENT"] * 64
               + ["NEG_PLAIN"] * 192)
    rows = []
    for index, cls in enumerate(classes):
        truth = cls == "POS_OVERRIDE"
        visible = truth if index % 10 else (not truth)
        rows.append({
            "schema": "vett.r28.t14.annotation/v1", "task": R.T1_TASK,
            "item_id": f"off_{index:03d}", "item_handle": f"{index:016x}",
            "status": "OK", "source": "local_model",
            "truth_class": cls, "mechanical_truth": truth,
            "annotation": {"visible": visible},
            "raw_output": json.dumps({"supported": visible}),
            "parsed_output": {"supported": visible},
            "input_sha256": FAKE_SHA,
            "prompt_template_version": "T1.factor_visibility.v1",
            "cache_hit": False, "wall_clock": 0.1,
        })
    return rows


def s1_rows() -> list[dict]:
    rows = []
    for index in range(320):
        mechanical = index >= 224
        rows.append({
            "schema": "vett.r28.t14.annotation/v1", "task": R.S1_TASK,
            "item_id": f"off_{index:03d}", "item_handle": f"{index:016x}",
            "status": "MECHANICAL_FALLBACK" if mechanical else "OK",
            "source": "mechanical_provenance_lexicon" if mechanical else "local_model",
            "annotation": ({"topic": "PROVENANCE", "basis": "mechanical"}
                           if mechanical else {"topic": "RUNS", "basis": "local_model"}),
            "raw_output": None if mechanical else '{"topic":"RUNS"}',
            "parsed_output": {"topic": "PROVENANCE" if mechanical else "RUNS"},
            "input_sha256": FAKE_SHA,
            "prompt_template_version": None if mechanical else "S1.span_topic.v4",
            "cache_hit": False, "wall_clock": 0.0 if mechanical else 0.1,
        })
    return rows


def t2_rows(pairs: list[dict]) -> list[dict]:
    rows = []
    for index, pair in enumerate(pairs):
        clean_score, degraded_score = (4, 2) if index % 20 else (2, 4)  # 5% wrong
        if pair["clean_position"] == "a":
            score_a, score_b = clean_score, degraded_score
        else:
            score_a, score_b = degraded_score, clean_score
        preference = ("clean" if clean_score > degraded_score
                      else "degraded" if clean_score < degraded_score else "tie")
        rows.append({
            "schema": "vett.r28.t14.annotation/v1", "task": R.T2_TASK,
            "item_id": pair["item_id"], "item_handle": f"{index:016x}",
            "status": "OK", "source": "local_model",
            "clean_position": pair["clean_position"], "corruptor": pair["corruptor"],
            "annotation": {"score_a": score_a, "score_b": score_b},
            "raw_output": json.dumps({"score_a": score_a, "score_b": score_b}),
            "parsed_output": {"score_a": score_a, "score_b": score_b},
            "score_a": score_a, "score_b": score_b,
            "clean_score": clean_score, "degraded_score": degraded_score,
            "preference": preference, "correct": preference == "clean",
            "corruption_effective": True,
            "efficacy": {"syntax_break_delta": 1, "bigram_delta": 0.2,
                         "fre_delta": 0.0, "ineffective": False},
            "input_sha256": FAKE_SHA,
            "prompt_template_version": "T2.naturalness_pair.v1",
            "cache_hit": False, "wall_clock": 0.2,
        })
    return rows


def main() -> None:
    run_dir = T14_ROOT / "runs" / RUN_ID
    run_dir.mkdir(parents=True, exist_ok=True)
    config = {"schema": "test", "run_id": RUN_ID, "seed": R.SEED,
              "blind_salt": "offline-test-salt-0123456789abcdef"}
    (run_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")
    fake_ledger(run_dir)
    pairs = json.loads((T14_ROOT / "runs" / "t14_main" / "t2_pairs.json")
                       .read_text(encoding="utf-8"))["pairs"]
    t1 = t1_rows()
    s1 = s1_rows()
    t2 = t2_rows(pairs)
    calibration = {"n": 30, "correct": 30, "ties": 0, "agreement": 1.0}
    repeats = {
        R.T1_TASK: {"n": 32, "repeat": 32, "agreement": 1.0},
        R.S1_TASK: {"n": 22, "repeat": 22, "agreement": 1.0,
                    "preference_repeat_rate": None},
        R.T2_TASK: {"n": 32, "repeat": 32, "agreement": 1.0,
                    "preference_repeat_rate": 1.0},
    }
    runner = R.Runner(run_id=RUN_ID, execute=False, use_cache=True, limit=None)
    runner.build_index_sha_before = R.sha256_text(
        (R.DATASET / "build_index.json").read_text(encoding="utf-8"))
    acceptance = t14_report.check_acceptance(
        runner=runner, items=R.recon.load_dev_items(), t1_rows=t1, s1_rows=s1,
        t2_rows=t2, pairs=pairs, calibration=calibration, repeats=repeats)
    print("acceptance:", acceptance["n_passed"], "/", acceptance["n_checks"],
          "ok=", acceptance["ok"])
    for check in acceptance["checks"]:
        if not check["ok"]:
            print("FAIL", check)
    report = t14_report.build_report(
        runner=runner, items=R.recon.load_dev_items(), t1_rows=t1, s1_rows=s1,
        t2_rows=t2, t1_analysis=[], s1_analysis=[], pairs=pairs,
        calibration=calibration, repeats=repeats)
    assert "T1 因子可见性（冻结 T1v1，按真类分层）" in report
    assert "T2 相对自然度（冻结 T2.naturalness_pair.v1，序判定）" in report
    # Negative case: make T1 truth constant -> must fail the stratified check.
    bad_t1 = [dict(row, truth_class="NEG_PLAIN", mechanical_truth=False) for row in t1]
    bad = t14_report.check_acceptance(
        runner=runner, items=R.recon.load_dev_items(), t1_rows=bad_t1, s1_rows=s1,
        t2_rows=t2, pairs=pairs, calibration=calibration, repeats=repeats)
    stratified = next(c for c in bad["checks"] if c["id"] == "t1_stratified_truth_classes")
    assert not stratified["ok"], "constant T1 truth must fail"
    # Negative case: T2 preference not derived from scores -> must fail.
    bad_t2 = [dict(row, preference="degraded") for row in t2]
    bad2 = t14_report.check_acceptance(
        runner=runner, items=R.recon.load_dev_items(), t1_rows=t1, s1_rows=s1,
        t2_rows=bad_t2, pairs=pairs, calibration=calibration, repeats=repeats)
    score_check = next(c for c in bad2["checks"] if c["id"] == "t2_frozen_template_scores_present")
    assert not score_check["ok"], "non-ordinal T2 preference must fail"
    assert acceptance["ok"], acceptance["checks"]
    print("offline report/acceptance test: PASS")


if __name__ == "__main__":
    main()
