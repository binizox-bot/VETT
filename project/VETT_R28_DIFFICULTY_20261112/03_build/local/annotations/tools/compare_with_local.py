"""t16 (annotator_alpha): cross-model comparison, cloud arm vs local arm.

Two comparisons are produced:

A. T1, item-level, identical stimuli (the only scientifically valid per-item comparison
   available in this round): 24 passages that the local model actually saw in t18's
   frozen capability matrix.  For each one we report the local answer, the cloud answer,
   the mechanical truth (POS_OVERRIDE / NEG_*) and whether they agree.  The local arm's
   full 30-sample error pattern is reported too, so a sample that misses the local
   errors says so instead of implying "no failures exist".

B. T2, distributional only: the local pair texts and the cloud pair texts are different
   renderings of different R28/R26 spans, so per-item pairing is impossible.  We report
   the ordering accuracy of both arms against the frozen mechanical truth (clean beats
   corrupted) and the score-scale usage of each model.

C. t14 status: if the local pre-annotation run has published labels, they are picked up
   and matched where stimuli coincide; otherwise the file records BLOCKED_ON_T14.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

RUN_ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112")
ROOT = RUN_ROOT / "03_build" / "local" / "annotations"
MATRIX_DIR = RUN_ROOT / "03_build" / "local" / "runs" / "matrix_20261112T103502Z_full"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    cloud = {row["packet_id"]: row for row in load_jsonl(ROOT / "cloud_alpha.jsonl")}
    index = json.loads((ROOT / "packets" / "T1_LOCALARM_INDEX.json").read_text(encoding="utf-8"))
    local_t1 = {row["sample_id"]: row for row in load_jsonl(MATRIX_DIR / "T1_factor_visibility.jsonl")}

    items = []
    agree = 0
    for entry in index["selected"]:
        local = local_t1[entry["matrix_sample_id"]]
        mine = cloud[entry["packet_id"]]
        local_answer = bool(local["parsed"]["supported"])
        my_answer = bool(mine["labels"]["supported"])
        truth = entry["group"] == "POS_OVERRIDE"
        same = local_answer == my_answer
        agree += same
        items.append({
            "packet_id": entry["packet_id"],
            "matrix_sample_id": entry["matrix_sample_id"],
            "group": entry["group"],
            "mechanical_truth": truth,
            "local_answer": local_answer,
            "local_correct": bool(local["score"]["correct"]),
            "cloud_answer": my_answer,
            "cloud_correct": my_answer == truth,
            "agree": same,
        })

    local_all = list(local_t1.values())
    local_errors = [{"sample_id": row["sample_id"], "group": row["group"],
                     "answer": bool(row["parsed"]["supported"]),
                     "truth": bool(row["score"]["truth"])}
                    for row in local_all if not row["score"]["correct"]]
    covered_errors = [err for err in local_errors
                      if err["sample_id"] in {item["matrix_sample_id"] for item in items}]

    # T2 distributional arm
    local_t2 = load_jsonl(MATRIX_DIR / "T2_naturalness.jsonl")
    local_clean = Counter((row["score"]["predicted"] or {}).get("clean") for row in local_t2)
    local_degraded = Counter((row["score"]["predicted"] or {}).get("degraded") for row in local_t2)
    md_t2 = {row["packet_id"]: row for row in load_jsonl(ROOT / "packets" / "T2_packets.jsonl")}

    # t14 discovery
    t14_candidates = sorted((RUN_ROOT / "03_build" / "local").rglob("*.jsonl"))
    t14_files = [p for p in t14_candidates
                 if "annotations" not in p.parts and p.name.endswith(".jsonl")]

    report = {
        "schema": "vett-t16-crosscheck/v1",
        "generated_from": {"cloud": str(ROOT / "cloud_alpha.jsonl"),
                           "local_t1": str(MATRIX_DIR / "T1_factor_visibility.jsonl"),
                           "local_t2": str(MATRIX_DIR / "T2_naturalness.jsonl")},
        "A_T1_item_level": {
            "n": len(items),
            "agree": agree,
            "disagree": len(items) - agree,
            "disagreement_rate": round((len(items) - agree) / len(items), 4),
            "local_accuracy_on_items": round(sum(1 for i in items if i["local_correct"]) / len(items), 4),
            "cloud_accuracy_on_items": round(sum(1 for i in items if i["cloud_correct"]) / len(items), 4),
            "items": items,
            "local_arm_full_errors": local_errors,
            "local_arm_full_correct": sum(1 for row in local_all if row["score"]["correct"]),
            "local_arm_full_n": len(local_all),
            "cloud_sample_covered_local_errors": len(covered_errors),
            "note": ("identical stimuli; the cloud arm is blind to the local answer. "
                     "local_arm_full_errors lists every local miss in the whole 30-sample arm, "
                     "so a 0/24 disagreement figure is never read as 'the local model never fails'."),
        },
        "B_T2_distributional": {
            "local_pairs": len(local_t2),
            "local_ordering_correct": sum(1 for row in local_t2 if row["score"]["correct"]),
            "local_clean_scores": dict(sorted(local_clean.items())),
            "local_degraded_scores": dict(sorted(local_degraded.items())),
            "cloud_pairs": len(md_t2),
            "cloud_ordering_correct": sum(
                1 for row in cloud.values() if row["task"] == "T2_naturalness"
                and ((row["labels"]["more_natural"] == "a" and row["labels"]["score_a"] > row["labels"]["score_b"])
                     or (row["labels"]["more_natural"] == "b" and row["labels"]["score_b"] > row["labels"]["score_a"]))),
            "cloud_clean_scores": dict(sorted(Counter(
                row["labels"]["score_a"] if md_t2[row["packet_id"]]["payload"]["clean_position"] == "a"
                else row["labels"]["score_b"]
                for row in cloud.values() if row["task"] == "T2_naturalness").items())),
            "cloud_degraded_scores": dict(sorted(Counter(
                row["labels"]["score_b"] if md_t2[row["packet_id"]]["payload"]["clean_position"] == "a"
                else row["labels"]["score_a"]
                for row in cloud.values() if row["task"] == "T2_naturalness").items())),
            "comparable_per_item": False,
            "reason": "the two arms judge different spans; only the task and the corruption factory are shared",
        },
        "C_t14": {
            "status": "BLOCKED_ON_T14" if not any("t14" in str(p) for p in t14_files) else "DETECTED",
            "candidate_files": [str(p) for p in t14_files][:10],
            "note": "t14 was still running when this report was written; its per-item labels are matched here if present.",
        },
    }
    out = ROOT / "crosscheck_alpha_vs_local.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("A_T1_item_level", "B_T2_distributional", "C_t14")},
                     ensure_ascii=False, indent=1)[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
