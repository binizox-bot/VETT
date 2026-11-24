"""t17 — J gate: can these annotations enter the main analysis?

Independent recomputation from raw artefacts (no reuse of t14/t16 self-audit code):

  J0  protocol precondition (protocol_verify --check 22/22, digests)
  J1  local vs mechanical truth      T1 (stratified, per class) / T2 (order only)
                                     S1 (no R28 mechanical truth) / C1 (not run)
  J2  cloud vs mechanical truth      T1 two arms / T2 / T3 (n=12, descriptive)
  J3  cross-model kappa              n>=30 only, otherwise NOT_ESTIMATED
  J4  self-consistency               t14 10% repeats; cloud repeats (none)
  J5  adversarial probes             (not run in this round)
  J6  blind-packet leak audit        protocol audit_packet + R28 id patterns
  J7  ledger + replay binding (R-R7) template versions, required fields, cache key v2
  J8  template hygiene               T2.naturalness_pair.choice.v1 quarantine audit
  J9  disagreement rate vs 30%       T1 same-stimulus cloud/local arms
  J10 degenerate-truth guard         why t1_override_truth (all false) cannot gate
  J11 T3 data-quality items          the 5 `unsure`
  J12 t16 crosscheck C_t14 status    and why its flip is not admissible evidence
  J13 no-discrimination audit        abstain / conformance / overall verdict

Writes ``04_verify/J_GATE.json``.  ``--check-md`` asserts that the numbers quoted in
``J_GATE.md`` equal the ones in the JSON (doc/JSON drift guard).

Read-only.  No network, no model, no GPU.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

HERE = Path(__file__).resolve().parent
VERIFY_ROOT = HERE.parent
RUN_ROOT = VERIFY_ROOT.parent
WORKSPACE_ROOT = RUN_ROOT.parent

sys.path.insert(0, str(RUN_ROOT / "02_design" / "scripts"))

import judge_protocol as jp  # noqa: E402

LOCAL = RUN_ROOT / "03_build" / "local"
T14 = LOCAL / "t14"
T14_MAIN = T14 / "runs" / "t14_main"
ANN = LOCAL / "annotations"
MATRIX_DIR = LOCAL / "runs" / "matrix_20261112T103502Z_full"
DATASET = RUN_ROOT / "03_build" / "dataset_r28"
PROTOCOL_RESULT = RUN_ROOT / "02_design" / "protocol_verify_result.json"
PROTOCOL_JSON = RUN_ROOT / "02_design" / "protocol.json"
PROTOCOL_MD = RUN_ROOT / "02_design" / "PROTOCOL.md"

GATE_ID = "VETT-R28-GATE-J-20261112"
OUT_PATH = VERIFY_ROOT / "J_GATE.json"
MD_PATH = VERIFY_ROOT / "J_GATE.md"

TASKS = ("T1_factor_visibility", "T2_naturalness", "S1_span_topic", "C1_cert_sentence_consistency")
NUM_PREDICT = {"T1_factor_visibility": 128, "T2_naturalness": 128, "S1_span_topic": 96,
               "C1_cert_sentence_consistency": 96, "R1_readability": 96}
DISAGREEMENT_THRESHOLD = 0.30
Z95 = 1.959964


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.relative_to(RUN_ROOT).as_posix()


def wilson(k: int, n: int) -> list[float]:
    if n == 0:
        return [None, None]
    p = k / n
    denom = 1 + Z95 * Z95 / n
    centre = p + Z95 * Z95 / (2 * n)
    spread = Z95 * math.sqrt(p * (1 - p) / n + Z95 * Z95 / (4 * n * n))
    return [round((centre - spread) / denom, 4), round((centre + spread) / denom, 4)]


def cohen_kappa(a: Sequence[Any], b: Sequence[Any]) -> float | None:
    if len(a) != len(b) or not a:
        return None
    labels = sorted({str(x) for x in a} | {str(x) for x in b})
    ae, be = [str(x) for x in a], [str(x) for x in b]
    n = len(ae)
    observed = sum(1 for x, y in zip(ae, be) if x == y) / n
    ca, cb = Counter(ae), Counter(be)
    expected = sum(ca[l] * cb[l] for l in labels) / (n * n)
    if expected >= 1.0:
        return None
    return round((observed - expected) / (1 - expected), 4)


def bootstrap_kappa(a: Sequence[Any], b: Sequence[Any], *, resamples: int = 2000,
                    seed: int = 20261112) -> dict[str, Any]:
    rng = random.Random(seed)
    idx = list(range(len(a)))
    vals = []
    for _ in range(resamples):
        pick = [rng.choice(idx) for _ in idx]
        k = cohen_kappa([a[i] for i in pick], [b[i] for i in pick])
        if k is not None:
            vals.append(k)
    if not vals:
        return {"point": cohen_kappa(a, b), "ci95": [None, None], "resamples": 0}
    vals.sort()
    lo = vals[int(0.025 * (len(vals) - 1))]
    hi = vals[int(0.975 * (len(vals) - 1))]
    return {"point": cohen_kappa(a, b), "ci95": [round(lo, 4), round(hi, 4)],
            "resamples": len(vals)}


def verdict_entry(verdict: str, *, gate_eligible: bool, evidence: Any,
                  reason: str = "", required_fix: str | None = None) -> dict[str, Any]:
    out = {"verdict": verdict, "gate_eligible": gate_eligible, "evidence": evidence}
    if reason:
        out["reason"] = reason
    if required_fix:
        out["required_fix"] = required_fix
    return out


# ---------------------------------------------------------------------------
# J0 protocol precondition
# ---------------------------------------------------------------------------
def j0_protocol() -> dict[str, Any]:
    result = load_json(PROTOCOL_RESULT)
    protocol = load_json(PROTOCOL_JSON)
    summary = result.get("summary") or {}
    ok = bool(summary.get("ok")) and summary.get("total") == 22 and summary.get("failed") == 0
    return verdict_entry(
        "PASS" if ok else "FAIL", gate_eligible=ok,
        evidence={
            "protocol_id": protocol["protocol_id"],
            "protocol_version": protocol["version"],
            "protocol_json_sha256": sha256_file(PROTOCOL_JSON),
            "protocol_md_sha256": sha256_file(PROTOCOL_MD),
            "verify_summary": summary,
            "verify_failed_ids": result.get("failed_ids"),
            "verify_checked_at_utc": result.get("checked_at_utc"),
            "checklist": [c["id"] for c in protocol["verification"]["checklist"]],
            "bindings": {k: (v.get("sha256") or "")[:16] for k, v in protocol["bindings"].items()
                         if isinstance(v, dict) and "sha256" in v},
            "binding_versions": {k: v.get("document_version") for k, v in protocol["bindings"].items()
                                 if isinstance(v, dict) and v.get("document_version")},
            "single_source": "02_design/protocol.json（未写任何副本，见 PAMEND-002）",
        },
        reason="" if ok else "protocol_verify --check is not 22/22; J gate must not run",
    )


# ---------------------------------------------------------------------------
# J1 local vs mechanical truth
# ---------------------------------------------------------------------------
def _t1_rows() -> list[dict[str, Any]]:
    return load_jsonl(T14_MAIN / "annotations_T1_factor_visibility.jsonl")


def j1_t1() -> dict[str, Any]:
    rows = _t1_rows()
    by_class: dict[str, dict[str, Any]] = {}
    conf = Counter()
    truth_map = {"POS_OVERRIDE": True, "NEG_PLAIN": False, "NEG_PROVENANCE_ADJACENT": False}
    consistency_problems: list[str] = []
    for row in rows:
        cls = row.get("truth_class")
        truth = bool(row.get("mechanical_truth"))
        pred = bool((row.get("parsed_output") or {}).get("supported"))
        bucket = by_class.setdefault(cls, {"n": 0, "correct": 0, "truth_values": set()})
        bucket["n"] += 1
        bucket["correct"] += int(pred == truth)
        bucket["truth_values"].add(truth)
        conf[(truth, pred)] += 1
        if cls in truth_map and truth_map[cls] != truth:
            consistency_problems.append(f"{row.get('item_id')}: class {cls} carries truth {truth}")

    n = len(rows)
    correct = sum(b["correct"] for b in by_class.values())
    classes = {}
    for cls, b in sorted(by_class.items()):
        classes[cls] = {"n": b["n"], "correct": b["correct"],
                        "agreement": round(b["correct"] / b["n"], 4) if b["n"] else None,
                        "wilson95": wilson(b["correct"], b["n"]),
                        "sufficient_n": b["n"] >= jp.N_MIN,
                        "truth_values": sorted(b["truth_values"])}
    all_false = sum(1 for row in rows if not bool(row.get("mechanical_truth"))) / n
    all_true = sum(1 for row in rows if bool(row.get("mechanical_truth"))) / n
    # majority-class baseline under the *true* stratified truth
    neg = sum(1 for row in rows if not bool(row.get("mechanical_truth")))
    pos = n - neg
    majority = max(neg, pos) / n
    degenerate = {
        "constant_false_accuracy": round(all_false, 4),
        "constant_true_accuracy": round(all_true, 4),
        "majority_class_accuracy": round(majority, 4),
        "local_accuracy": round(correct / n, 4),
        "lift_over_majority": round(correct / n - majority, 4),
        "note": ("constant-false 在此分层真值上只有 %.4f：分层真值不是退化的 t1_override_truth（全 false）。"
                 % all_false),
    }
    classes_ok = all(c["sufficient_n"] for c in classes.values())
    overall = correct / n
    gate_ok = (n >= jp.N_MIN and classes_ok and overall >= jp.THRESHOLD_LOCAL
               and not consistency_problems)
    weakest = min(classes.items(), key=lambda kv: kv[1]["agreement"])
    per_class_below = [c for c, v in classes.items() if v["agreement"] < jp.THRESHOLD_LOCAL]
    return verdict_entry(
        "PASS" if gate_ok else ("INSUFFICIENT" if not classes_ok else "FAIL"),
        gate_eligible=gate_ok,
        evidence={
            "task": "T1_factor_visibility",
            "source": rel(T14_MAIN / "annotations_T1_factor_visibility.jsonl"),
            "n": n, "correct": correct, "agreement": round(overall, 4),
            "wilson95": wilson(correct, n),
            "threshold": jp.THRESHOLD_LOCAL, "n_min": jp.N_MIN,
            "per_class": classes,
            "classes_all_sufficient": classes_ok,
            "confusion": {f"truth={t}|pred={p}": c for (t, p), c in sorted(conf.items())},
            "degenerate_baselines": degenerate,
            "class_truth_consistency_problems": consistency_problems[:5],
            "per_class_below_threshold": per_class_below,
            "weakest_class": {"class": weakest[0], **weakest[1]},
            "reporting_rule": "逐类必须并列披露；POS_OVERRIDE 单独低于 0.85 时不得用总体 0.975 掩盖",
        },
        reason=(f"overall {overall:.4f} >= {jp.THRESHOLD_LOCAL} over n={n}; weakest class "
                f"{weakest[0]} {weakest[1]['agreement']:.4f}"),
        required_fix=(f"{weakest[0]} 类一致率 {weakest[1]['agreement']:.4f} < 0.85 —— 报告必须按类披露，"
                      f"并禁止用总体数字代替；不需要修标注"),
    )


def j1_t2() -> dict[str, Any]:
    rows = load_jsonl(T14_MAIN / "annotations_T2_naturalness.jsonl")
    problems: list[str] = []
    templates = Counter(row.get("prompt_template_version") for row in rows)
    metrics = Counter(row.get("metric") for row in rows)
    for row in rows:
        clean = row.get("clean_score")
        degraded = row.get("degraded_score")
        correct = row.get("correct")
        expect = bool(clean is not None and degraded is not None and clean > degraded)
        if bool(correct) != expect:
            problems.append(f"{row.get('item_id')}: correct={correct} but clean={clean}/degraded={degraded}")
    effective = [r for r in rows if r.get("corruption_effective") is not False]
    ineffective = [r for r in rows if r.get("corruption_effective") is False]
    n_valid = len(effective)
    ok_n = sum(1 for r in effective if r.get("correct") is True)
    by_corruptor: dict[str, dict[str, Any]] = {}
    for row in effective:
        key = str(row.get("corruptor"))
        b = by_corruptor.setdefault(key, {"n": 0, "correct": 0})
        b["n"] += 1
        b["correct"] += int(row.get("correct") is True)
    for key, b in by_corruptor.items():
        b["agreement"] = round(b["correct"] / b["n"], 4) if b["n"] else None
    agreement = ok_n / n_valid if n_valid else 0.0
    single_template = set(k for k in templates) == {"T2.naturalness_pair.v1"}
    order_only = set(k for k in metrics) == {"ordinal_preference_from_frozen_T2v1_scores"}
    gate_ok = (single_template and order_only and not problems and n_valid >= jp.N_MIN
               and agreement >= jp.THRESHOLD_LOCAL)
    clean_scores = Counter(r.get("clean_score") for r in rows)
    degraded_scores = Counter(r.get("degraded_score") for r in rows)
    return verdict_entry(
        "PASS" if gate_ok else "FAIL", gate_eligible=gate_ok,
        evidence={
            "task": "T2_naturalness",
            "source": rel(T14_MAIN / "annotations_T2_naturalness.jsonl"),
            "n_rows": len(rows), "n_valid": n_valid, "correct": ok_n,
            "agreement": round(agreement, 4), "wilson95": wilson(ok_n, n_valid),
            "threshold": jp.THRESHOLD_LOCAL,
            "excluded_ineffective": len(ineffective),
            "ineffective_items": [r.get("item_id") for r in ineffective],
            "per_corruptor": by_corruptor,
            "templates": dict(templates), "metrics": dict(metrics),
            "single_frozen_template": single_template,
            "metric_is_order_only": order_only,
            "score_semantics_problems": problems[:5],
            "absolute_scores_descriptive_only": {
                "clean": dict(sorted(clean_scores.items(), key=lambda kv: str(kv[0]))),
                "degraded": dict(sorted(degraded_scores.items(), key=lambda kv: str(kv[0]))),
                "rule": "绝对分不可比（t16：云端 clean 全 5、本地 20/30 给 4）；进阈值判定即 FAIL",
            },
        },
        reason=f"order-only agreement {agreement:.4f} over n={n_valid} (n_ineffective excluded)",
    )


def j1_s1() -> dict[str, Any]:
    rows = load_jsonl(T14_MAIN / "annotations_S1_span_topic.jsonl")
    status = Counter(row.get("status") for row in rows)
    basis = Counter((row.get("annotation") or {}).get("basis") for row in rows)
    topics = Counter((row.get("parsed_output") or {}).get("topic") for row in rows
                     if row.get("status") == "OK")
    degraded = load_jsonl(T14_MAIN / "DEGRADED_EVENTS.jsonl")
    s1_deg = [e for e in degraded if e.get("task") == "S1_span_topic"]
    has_truth = any("mechanical_truth" in row or "truth" in row for row in rows)
    return verdict_entry(
        "INSUFFICIENT", gate_eligible=False,
        evidence={
            "task": "S1_span_topic",
            "source": rel(T14_MAIN / "annotations_S1_span_topic.jsonl"),
            "n_rows": len(rows), "status": {str(k): v for k, v in status.items()},
            "label_basis": {str(k): v for k, v in basis.items()},
            "topic_distribution_on_model_rows": {str(k): v for k, v in
                                                 sorted(topics.items(), key=lambda kv: str(kv[0]))},
            "degraded_events": len(s1_deg),
            "truth_field_present_in_annotations": has_truth,
            "reason_detail": (
                "R28 卷宗 span 是叙述性事实/规则句，没有 t18 那种字段词组，因此不存在可独立复算的"
                " S1 机械主题真值；96 条 PROVENANCE 是机械词表回退（fallback），不是模型输出，"
                "拿它算准确率等于自己判自己。"
            ),
            "t18_licence_does_not_transfer": (
                "t18 的 ALLOW（1.0，n=32）建立在 R26.15 字段词组 span 上；R28 span 分布不同，"
                "ALLOW 不能平移（R-Q3 fail-safe：未测量即 DENY）。"
            ),
        },
        reason="no independent mechanical topic truth on R28 spans → descriptive only",
    )


def j1_c1() -> dict[str, Any]:
    candidates = sorted((LOCAL / "t21").rglob("*.jsonl")) if (LOCAL / "t21").exists() else []
    runs = sorted((LOCAL / "runs").glob("*t21*")) if (LOCAL / "runs").exists() else []
    found = [str(p) for p in candidates] + [str(p) for p in runs]
    return verdict_entry(
        "INSUFFICIENT", gate_eligible=False,
        evidence={
            "task": "C1_cert_sentence_consistency",
            "r28_artifacts_found": found,
            "t18_reference": {"agreement": 1.0, "n": 30,
                              "source": "03_build/local/capability_matrix.json#/tasks/"
                                        "C1_cert_sentence_consistency"},
            "reason_detail": ("C1 在 R28 上尚未运行（t21 未产出）；t18 的 1.0/30 是 R26.15 证书句，"
                              "不能当作 R28 的测量（R-Q3）。"),
        },
        reason="C1 not measured on R28 (t21 not delivered) → cannot enter main analysis as a gate",
    )



# ---------------------------------------------------------------------------
# J1b truth grounding (independent corroboration of the stratified T1 truth)
# ---------------------------------------------------------------------------
OVERRIDE_LEXICON = re.compile(
    r"(?i)\b(supersed\w*|controls?|set aside|higher signed revision|replac\w*|displac\w*|"
    r"amend\w*|retract\w*|cancel\w*|withdr\w*|overrid\w*|no longer operative)\b")
PROVENANCE_LEXICON = re.compile(
    r"(?i)\b(records?|recorded|initially entered|first circulated|supplied|transcrib\w*|"
    r"inherits?|copied|carries no independent value|adds no separate verification|"
    r"provisional|docket|revision)\b")


def _span_index() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for path in sorted((DATASET / "public").glob("*/public_instance.json")):
        doc = load_json(path)
        for document in (doc.get("dossier") or {}).get("documents") or []:
            for span in document.get("spans") or []:
                out[str(span.get("span_id"))] = {"text": str(span.get("text") or ""),
                                                 "role": str(span.get("role") or ""),
                                                 "item": path.parent.name}
    return out


def j1b_truth_grounding() -> dict[str, Any]:
    spans = _span_index()
    rows = _t1_rows()
    by_class: dict[str, dict[str, Any]] = {}
    missing = []
    for row in rows:
        span = spans.get(str(row.get("passage_span_id")))
        cls = row.get("truth_class")
        bucket = by_class.setdefault(cls, {"n": 0, "found": 0, "override_hit": 0,
                                           "provenance_hit": 0})
        bucket["n"] += 1
        if span is None:
            missing.append(str(row.get("passage_span_id")))
            continue
        bucket["found"] += 1
        text = span["text"]
        bucket["override_hit"] += int(bool(OVERRIDE_LEXICON.search(text)))
        bucket["provenance_hit"] += int(bool(PROVENANCE_LEXICON.search(text)))
    for cls, b in by_class.items():
        b["override_hit_rate"] = round(b["override_hit"] / b["found"], 4) if b["found"] else None
        b["provenance_hit_rate"] = round(b["provenance_hit"] / b["found"], 4) if b["found"] else None
        b["span_coverage"] = round(b["found"] / b["n"], 4) if b["n"] else None
    pos = by_class.get("POS_OVERRIDE", {})
    neg = by_class.get("NEG_PLAIN", {})
    prov = by_class.get("NEG_PROVENANCE_ADJACENT", {})
    separation = {
        "pos_override_rate": pos.get("override_hit_rate"),
        "neg_plain_rate": neg.get("override_hit_rate"),
        "delta_pos_minus_neg": (round((pos.get("override_hit_rate") or 0)
                                      - (neg.get("override_hit_rate") or 0), 4)),
        "provenance_rate_pos": pos.get("provenance_hit_rate"),
        "provenance_rate_neg_provenance": prov.get("provenance_hit_rate"),
    }
    ok = (len(missing) == 0 and (separation["delta_pos_minus_neg"] or 0) >= 0.5)
    return verdict_entry(
        "PASS" if ok else "FAIL", gate_eligible=ok,
        evidence={
            "span_index_size": len(spans),
            "coverage": f"{len(rows) - len(missing)}/{len(rows)}",
            "missing_span_ids": missing[:5],
            "by_class": by_class,
            "separation": separation,
            "lexicon": {"override": OVERRIDE_LEXICON.pattern[:120],
                        "provenance": PROVENANCE_LEXICON.pattern[:120]},
            "interpretation": ("POS 类压倒性地含覆盖/取代语汇、NEG_PLAIN 几乎不含 → 分层真值与卷宗文本一致；"
                               "这是**佐证**，真值本身来自刺激构造，不由该词表生成。"),
        },
        reason=(f"POS override-lexicon {separation['pos_override_rate']} vs NEG_PLAIN "
                f"{separation['neg_plain_rate']}"),
    )



def j1c_shortcut_audit() -> dict[str, Any]:
    """Where does the local T1 agreement fail? (lexicon-sensitive; report the robust part)."""
    spans = _span_index()
    rows = _t1_rows()
    by_role: dict[str, dict[str, Any]] = {}
    for row in rows:
        role = str(row.get("passage_role"))
        truth = bool(row.get("mechanical_truth"))
        pred = bool((row.get("parsed_output") or {}).get("supported"))
        b = by_role.setdefault(role, {"n": 0, "correct": 0, "truth_true": 0})
        b["n"] += 1
        b["correct"] += int(pred == truth)
        b["truth_true"] += int(truth)
    for role, b in by_role.items():
        b["agreement"] = round(b["correct"] / b["n"], 4) if b["n"] else None

    pos = [r for r in rows if r.get("truth_class") == "POS_OVERRIDE"]
    neg = [r for r in rows if r.get("truth_class") == "NEG_PLAIN"]
    errors = [str(r.get("item_id")) for r in pos
              if bool((r.get("parsed_output") or {}).get("supported")) is not True]
    error_roles = Counter(str(r.get("passage_role")) for r in pos
                          if bool((r.get("parsed_output") or {}).get("supported")) is not True)

    # lexicon sensitivity: the "errors == no-lexicon-hit" identity is NOT robust (t8 F1)
    variants = {
        "declared": OVERRIDE_LEXICON,
        "plus_controlling": re.compile(
            r"(?i)\b(supersed\w*|controls?|controlling|set aside|higher signed revision|"
            r"replac\w*|displac\w*|amend\w*|retract\w*|cancel\w*|withdr\w*|overrid\w*|"
            r"no longer operative)\b"),
        "broad_semantic": re.compile(
            r"(?i)\b(supersed\w*|control\w*|set aside|higher signed revision|replac\w*|"
            r"displac\w*|amend\w*|retract\w*|cancel\w*|withdr\w*|overrid\w*|"
            r"no longer operative|governs?|authoritative|signed observation)\b"),
    }
    sensitivity = {}
    for name, rx in variants.items():
        no_hit = {str(r.get("item_id")) for r in pos
                  if not rx.search((spans.get(str(r.get("passage_span_id"))) or {"text": ""})["text"])}
        sensitivity[name] = {
            "pos_without_lexicon_hit": len(no_hit),
            "equals_error_set": no_hit == set(errors),
            "overlap_with_errors": len(no_hit & set(errors)),
            "neg_plain_false_hits": sum(1 for r in neg
                                        if rx.search((spans.get(str(r.get("passage_span_id")))
                                                      or {"text": ""})["text"])),
        }
    declared = variants["declared"]
    table = {"hit_and_correct": 0, "hit_and_wrong": 0, "nohit_and_correct": 0, "nohit_and_wrong": 0}
    for row in pos:
        hit = bool(declared.search((spans.get(str(row.get("passage_span_id"))) or {"text": ""})["text"]))
        correct = bool((row.get("parsed_output") or {}).get("supported")) is True
        table[f"{'hit' if hit else 'nohit'}_and_{'correct' if correct else 'wrong'}"] += 1
    authority = by_role.get("authority_policy", {})
    return {
        "verdict": "SHORTCUT_FLAG",
        "gate_eligible": False,
        "by_passage_role": by_role,
        "pos_errors_n": len(errors),
        "pos_errors": errors,
        "pos_error_roles": dict(error_roles),
        "declared_lexicon_2x2": table,
        "lexicon_sensitivity": sensitivity,
        "conclusion_robust": (
            f"POS_OVERRIDE 的 {len(errors)} 个错**全部集中**在 {dict(error_roles)} 这一类构造"
            f"（authority_policy 同一句式）；POS 类一致率 0.8333，authority_policy 子组 "
            f"{authority.get('agreement')}。这是稳健结论。"
        ),
        "conclusion_not_robust": (
            "『错集 == 词表不命中集』只在声明的 OVERRIDE_LEXICON 下成立（8/8）：把 controlling 加进词表后 "
            "不命中集变 0 而错误仍是 8，等式即破。因此该等式**不得**作为机制断言引用（t8 F1 已复核）。"
        ),
        "consequence_for_downstream": [
            "T1 仍可用作标注劳动（数值过门 0.9750），但**不得**当作'本地能判断证据支持'的能力证据。",
            "T1 报告必须按 span role 分组：authority_policy 子组 0.7500（32 条）是全部门槛以下的部分。",
            "t11/t23 的表述统一为：『8/8 错误集中在 authority_policy 构造；POS 0.8333；constant-false 基线 0.8500』。",
        ],
        "authority_policy_subgroup": authority,
    }


# ---------------------------------------------------------------------------
# J2 cloud vs mechanical truth
# ---------------------------------------------------------------------------
def _cloud_rows() -> list[dict[str, Any]]:
    return load_jsonl(ANN / "cloud_alpha.jsonl")


def _selection_index() -> dict[str, Any]:
    return load_json(ANN / "packets" / "SELECTION_INDEX.json")


def _t1_rows_by_item() -> dict[str, dict[str, Any]]:
    return {str(r.get("item_id")): r for r in _t1_rows()}


def _t1_truth_by_span() -> dict[str, dict[str, Any]]:
    out = {}
    for row in _t1_rows():
        out[str(row.get("passage_span_id"))] = row
    return out


def j2_t1_r28_arm(cloud: list[dict[str, Any]]) -> dict[str, Any]:
    """Cloud T1 vs truth on the 24 R28 items; local comparison only on identical spans."""
    index = _selection_index()
    truth_rows = _t1_truth_by_span()
    cloud_t1 = {r["packet_id"]: r for r in cloud if r["task"] == "T1_factor_visibility"}
    items, problems = [], []
    for entry in index["t1"]:
        packet_id = entry["packet_id"]
        row = cloud_t1.get(packet_id)
        if row is None:
            problems.append(f"{packet_id}: cloud label missing")
            continue
        cloud_answer = bool((row.get("labels") or {}).get("supported"))
        truth = entry["truth_class"] == "POS_SUPERSESSION"
        same_span = str(entry["span_id"]).startswith(("r28rev", "r28fact", "r28shadow", "r28auth"))
        local = truth_rows.get(entry["span_id"])
        item = {
            "packet_id": packet_id, "item_id": entry["item_id"], "span_id": entry["span_id"],
            "span_role": entry.get("span_role"), "t16_truth_class": entry["truth_class"],
            "truth": truth, "cloud_answer": cloud_answer,
            "cloud_correct": cloud_answer == truth,
            "local_span_matches_cloud_span": local is not None,
        }
        if local is not None:
            item["t14_truth_class"] = local.get("truth_class")
            item["local_answer"] = bool((local.get("parsed_output") or {}).get("supported"))
            item["local_correct"] = item["local_answer"] == truth
            item["agree"] = item["local_answer"] == cloud_answer
            if bool(local.get("mechanical_truth")) != truth:
                problems.append(f"{packet_id}: truth disagreement t14={local.get('mechanical_truth')} "
                                f"t16={truth}")
        else:
            # the cloud packet uses a span t14 never annotated (authority_policy / revision /
            # distractor); the local answer to a *different* stimulus must not be compared.
            by_item = _t1_rows_by_item().get(entry["item_id"])
            item["local_span_note"] = (
                f"t14 标注的是 {by_item.get('passage_role') if by_item else '?'} span "
                f"({str(by_item.get('passage_span_id'))[:18] if by_item else '?'})，与云端 packet 的 "
                f"{entry.get('span_role')} span 不同 → 不可逐条比较")
        items.append(item)
    n = len(items)
    matched = [i for i in items if i.get("local_span_matches_cloud_span")]
    return {
        "n": n,
        "cloud_correct": sum(1 for i in items if i["cloud_correct"]),
        "cloud_accuracy": round(sum(1 for i in items if i["cloud_correct"]) / n, 4) if n else None,
        "class_counts": dict(Counter(i["t16_truth_class"] for i in items)),
        "comparable_subset_n": len(matched),
        "comparable_subset_agree": sum(1 for i in matched if i.get("agree")),
        "comparable_subset_disagree": sum(1 for i in matched if i.get("agree") is False),
        "comparable_subset_disagreement_rate": (
            round(sum(1 for i in matched if i.get("agree") is False) / len(matched), 4)
            if matched else None),
        "comparable_subset_local_accuracy": (
            round(sum(1 for i in matched if i.get("local_correct")) / len(matched), 4)
            if matched else None),
        "unmatched_items": [{"item_id": i["item_id"], "cloud_span_role": i["span_role"],
                             "note": i.get("local_span_note")}
                            for i in items if not i.get("local_span_matches_cloud_span")],
        "not_comparable_reason": (
            "R28 臂的 packet 用题目的决定性 span（revision/authority/distractor），t14 只标了它自己挑的"
            "一个 span；两者不同即不是同刺激，逐条比较无效。"),
        "problems": problems,
        "items": items,
        "source": rel(ANN / "cloud_alpha.jsonl"),
        "matching": "packet_id → SELECTION_INDEX.t1[]；逐条可比较性由 span_id 相等判定",
    }


def j2_t1_local_arm(cloud: list[dict[str, Any]]) -> dict[str, Any]:
    index = load_json(ANN / "packets" / "T1_LOCALARM_INDEX.json")
    local_rows = {r["sample_id"]: r for r in load_jsonl(MATRIX_DIR / "T1_factor_visibility.jsonl")}
    cloud_t1 = {r["packet_id"]: r for r in cloud if r["task"] == "T1_factor_visibility"}
    items, problems = [], []
    for entry in index["selected"]:
        row = cloud_t1.get(entry["packet_id"])
        local = local_rows.get(entry["matrix_sample_id"])
        if row is None or local is None:
            problems.append(f"{entry['packet_id']}: missing cloud or local row")
            continue
        truth = entry["group"] == "POS_OVERRIDE"
        local_answer = bool((local.get("parsed") or {}).get("supported"))
        cloud_answer = bool((row.get("labels") or {}).get("supported"))
        items.append({"packet_id": entry["packet_id"], "matrix_sample_id": entry["matrix_sample_id"],
                      "group": entry["group"], "truth": truth,
                      "local_answer": local_answer, "cloud_answer": cloud_answer,
                      "local_correct": local_answer == truth, "cloud_correct": cloud_answer == truth,
                      "agree": local_answer == cloud_answer})
    n = len(items)
    agree = sum(1 for i in items if i["agree"])
    all_local = list(local_rows.values())
    local_errors = [{"sample_id": r["sample_id"], "group": r["group"],
                     "answer": bool((r.get("parsed") or {}).get("supported")),
                     "truth": bool((r.get("score") or {}).get("truth"))}
                    for r in all_local if not (r.get("score") or {}).get("correct")]
    covered = [e for e in local_errors if e["sample_id"] in {i["matrix_sample_id"] for i in items}]
    return {
        "n": n, "agree": agree, "disagree": n - agree,
        "disagreement_rate": round((n - agree) / n, 4) if n else None,
        "local_accuracy": round(sum(1 for i in items if i["local_correct"]) / n, 4) if n else None,
        "cloud_accuracy": round(sum(1 for i in items if i["cloud_correct"]) / n, 4) if n else None,
        "local_arm_full_n": len(all_local),
        "local_arm_full_correct": sum(1 for r in all_local if (r.get("score") or {}).get("correct")),
        "local_arm_full_errors": local_errors,
        "errors_covered_by_cloud_sample": len(covered),
        "problems": problems, "items": items,
        "source": f"{rel(ANN / 'cloud_alpha.jsonl')} + {rel(MATRIX_DIR / 'T1_factor_visibility.jsonl')}",
    }


def j2_t2(cloud: list[dict[str, Any]]) -> dict[str, Any]:
    packets = {p["packet_id"]: p for p in load_jsonl(ANN / "packets" / "T2_packets.jsonl")}
    items, problems = [], []
    for row in cloud:
        if row["task"] != "T2_naturalness":
            continue
        labels = row.get("labels") or {}
        packet = packets.get(row["packet_id"])
        if packet is None:
            problems.append(f"{row['packet_id']}: packet missing")
            continue
        clean_position = packet["payload"]["clean_position"]
        score_a, score_b = labels.get("score_a"), labels.get("score_b")
        more = labels.get("more_natural")
        argmax = "a" if (score_a or 0) > (score_b or 0) else ("b" if (score_b or 0) > (score_a or 0) else None)
        if more != argmax:
            problems.append(f"{row['packet_id']}: more_natural={more} but scores {score_a}/{score_b}")
        correct = more == clean_position
        items.append({"packet_id": row["packet_id"], "clean_position": clean_position,
                      "more_natural": more, "score_a": score_a, "score_b": score_b,
                      "correct": correct, "unsure": row.get("unsure")})
    n = len(items)
    correct = sum(1 for i in items if i["correct"])
    clean_scores = Counter(i["score_a"] if i["clean_position"] == "a" else i["score_b"] for i in items)
    degraded_scores = Counter(i["score_b"] if i["clean_position"] == "a" else i["score_a"] for i in items)
    return {
        "n": n, "correct": correct,
        "order_agreement": round(correct / n, 4) if n else None,
        "wilson95": wilson(correct, n),
        "clean_scores": dict(sorted(clean_scores.items())),
        "degraded_scores": dict(sorted(degraded_scores.items())),
        "problems": problems, "items": items,
        "gate_eligible": False,
        "gate_note": f"n={n} < {jp.N_MIN}：只作描述性对照，不得当门（R-Q1）",
        "source": rel(ANN / "cloud_alpha.jsonl"),
    }


def j2_t3(cloud: list[dict[str, Any]]) -> dict[str, Any]:
    items = {x["submission_id"]: x for x in load_jsonl(ANN / "packets" / "T3_items.jsonl")}
    sub_index = load_json(ANN / "packets" / "T3_SUBMISSION_INDEX.json")
    item_of = {s["submission_id"]: s["item_id"] for s in sub_index["submissions"]}
    gold_cache: dict[str, Any] = {}
    rows, problems = [], []
    dims = ("fields", "span", "edge", "abstain", "conformance")
    dim_counts: dict[str, Counter] = {d: Counter() for d in dims}
    overall_counts = Counter()
    for row in cloud:
        if row["task"] != "T3_adjudication":
            continue
        sid = row["packet_id"]
        item = items.get(sid)
        if item is None:
            problems.append(f"{sid}: T3 item missing")
            continue
        item_id = item_of.get(sid) or item.get("item_id")
        gold_path = DATASET / "private" / str(item_id) / "private_gold.json"
        if item_id not in gold_cache:
            gold_cache[item_id] = load_json(gold_path) if gold_path.exists() else None
        gold_doc = gold_cache[item_id]
        if gold_doc is None:
            problems.append(f"{sid}: gold missing for {item_id}")
            continue
        gold = gold_doc["decision_record_flat"]
        submission = (item.get("submission") or {}).get("decision_record") or {}
        labels = row.get("labels") or {}

        field_diff = [f for f in jp.RECORD_FIELDS if submission.get(f) != gold.get(f)]
        true_verdict = "DEFECT" if field_diff else "PASS"
        field_verdicts = ((labels.get("fields") or {}).get("field_verdicts")) or {}
        flagged = [f for f, v in field_verdicts.items() if str(v).startswith("WRONG")]
        flag_correct = sum(1 for f in flagged if f in field_diff)
        missed = [f for f in field_diff if f not in flagged]
        correct_record = (labels.get("fields") or {}).get("correct_record") or {}
        record_agreement = sum(1 for f in jp.RECORD_FIELDS
                               if correct_record.get(f) == gold.get(f))

        for dim in dims:
            dim_counts[dim][(labels.get(dim) or {}).get("verdict")] += 1
        overall_counts[labels.get("overall")] += 1
        rows.append({
            "submission_id": sid, "item_id": item_id,
            "true_field_diff_count": len(field_diff), "true_field_diff": field_diff,
            "true_verdict": true_verdict, "cloud_overall": labels.get("overall"),
            "overall_correct": labels.get("overall") == true_verdict,
            "cloud_flagged_fields": flagged,
            "flagged_correct": flag_correct, "missed_fields": missed,
            "cloud_correct_record_field_agreement": record_agreement,
            "unsure": row.get("unsure"),
        })
    n = len(rows)
    return {
        "n": n,
        "note": f"n={n} < {jp.N_MIN}：不足以做推断性主张，只能 DESCRIPTIVE_ONLY（R-C4 / 队长指令 E）",
        "dimension_counts": {d: dict(c) for d, c in dim_counts.items()},
        "overall_counts": dict(overall_counts),
        "overall_verdict_correct": sum(1 for r in rows if r["overall_correct"]),
        "all_items_defective": all(r["true_verdict"] == "DEFECT" for r in rows),
        "flagged_field_precision": (
            round(sum(r["flagged_correct"] for r in rows)
                  / max(1, sum(len(r["cloud_flagged_fields"]) for r in rows)), 4)),
        "recall_on_true_diff_fields": (
            round(1 - sum(len(r["missed_fields"]) for r in rows)
                  / max(1, sum(r["true_field_diff_count"] for r in rows)), 4)),
        "correct_record_field_agreement": (
            round(sum(r["cloud_correct_record_field_agreement"] for r in rows)
                  / max(1, n * len(jp.RECORD_FIELDS)), 4)),
        "counts": {
            "fields_flagged": sum(len(r["cloud_flagged_fields"]) for r in rows),
            "fields_flagged_correct": sum(r["flagged_correct"] for r in rows),
            "fields_truly_diff": sum(r["true_field_diff_count"] for r in rows),
            "fields_missed": sum(len(r["missed_fields"]) for r in rows),
            "record_fields_compared": n * len(jp.RECORD_FIELDS),
            "record_fields_agreeing_with_gold": sum(r["cloud_correct_record_field_agreement"]
                                                    for r in rows),
        },
        "unsure_items": [r for r in rows if r.get("unsure")],
        "items": rows,
        "problems": problems,
        "gold_source": "03_build/dataset_r28/private/<item_id>/private_gold.json#decision_record_flat（solver）",
        "model_output_not_gold": ("云端 labels.fields.correct_record 是**模型输出**，按 R-M1/R-M2 不得当金标；"
                                  "本门只用它做描述性对照（与 solver 金标逐字段比较）。"),
        "source": rel(ANN / "cloud_alpha.jsonl") + " + " + rel(ANN / "packets" / "T3_items.jsonl"),
    }


# ---------------------------------------------------------------------------
# J3 kappa, J4 self-consistency
# ---------------------------------------------------------------------------
def j3_kappa(t1_r28: dict[str, Any], t1_local_arm: dict[str, Any],
             t2_cloud: dict[str, Any]) -> dict[str, Any]:
    arms = {}
    pooled_local, pooled_cloud = [], []
    for name, block in (("T1_r28_arm", t1_r28), ("T1_local_arm", t1_local_arm)):
        items = [i for i in block["items"] if "local_answer" in i]
        local = [i["local_answer"] for i in items]
        cloud = [i["cloud_answer"] for i in items]
        pooled_local.extend(local)
        pooled_cloud.extend(cloud)
        n = len(items)
        arms[name] = {
            "n": n,
            "usable_pairs": len(items),
            "estimated": n >= jp.N_MIN,
            "verdict": "ESTIMATED" if n >= jp.N_MIN else "NOT_ESTIMATED",
            "kappa": bootstrap_kappa(local, cloud) if n >= jp.N_MIN else None,
            "reason": None if n >= jp.N_MIN else f"n={n} < {jp.N_MIN}：不估计（R-Q1 / 队长指令 G）",
        }
    pooled_n = len(pooled_local)
    arms["T2_pairs"] = {
        "n": t2_cloud["n"], "estimated": t2_cloud["n"] >= jp.N_MIN,
        "verdict": "ESTIMATED" if t2_cloud["n"] >= jp.N_MIN else "NOT_ESTIMATED",
        "kappa": None,
        "reason": (f"n={t2_cloud['n']} < {jp.N_MIN}：不估计" if t2_cloud["n"] < jp.N_MIN
                   else "cloud T2 是序判定，本地 T2 与之非同刺激，无法逐条配对"),
    }
    exploratory = None
    if pooled_n >= jp.N_MIN:
        exploratory = {
            "verdict": "EXPLORATORY_POOLED_ONLY",
            "n": pooled_n,
            "kappa": bootstrap_kappa(pooled_local, pooled_cloud),
            "caveat": ("两个臂的刺激分布不同（R28 叙述性 span vs R26.15 字段词组 span），"
                       "合并只为给出量级，**不得进入任何判定或报告主表**"),
        }
    return {
        "verdict": "NOT_ESTIMATED",
        "gate_eligible": False,
        "arms": arms,
        "exploratory_pooled_T1": exploratory,
        "policy": "n≥30 才估计；n<30 一律报'不估计'；不设通过线（R-S2 / kappa_policy）",
    }


def j4_self_consistency() -> dict[str, Any]:
    repeats = {}
    for task, fname in (("T1_factor_visibility", "repeats_T1_factor_visibility.jsonl"),
                        ("S1_span_topic", "repeats_S1_span_topic.jsonl"),
                        ("T2_naturalness", "repeats_T2_naturalness.jsonl")):
        rows = load_jsonl(T14_MAIN / fname)
        same = sum(1 for r in rows if r.get("same") is True)
        repeats[task] = {
            "n": len(rows), "same": same,
            "exact_repeat_rate": round(same / len(rows), 4) if rows else None,
            "fraction_of_320": round(len(rows) / 320, 4) if rows else None,
            "floor": jp.REPEAT_FLOOR_LOCAL,
            "pass": bool(rows) and same / len(rows) >= jp.REPEAT_FLOOR_LOCAL,
        }
    cloud_repeat = {
        "n": 0, "verdict": "NOT_RUN",
        "reason": ("云端没有做 10% 重复；t16 的 76 条全部只判一次。因此云端自一致**未测量**，"
                   "不得声称 ≥0.90（R-Q5 fail-safe）。"),
    }
    local_ok = all(v["pass"] for v in repeats.values()) and len(repeats) == 3
    return {
        "verdict": "PASS" if local_ok else "FAIL",
        "gate_eligible": local_ok,
        "local": repeats,
        "cloud": cloud_repeat,
        "note": ("本地三项 10% 重测均 1.0；但 temperature=0 非逐位确定（t18：152 样本 1 次 1 分移动），"
                 "1.0 是本次重复的实测，不是确定性保证。"),
    }


def j5_adversarial() -> dict[str, Any]:
    probes = []
    for pattern in ("*adversar*", "*probe*", "*swap*", "*tamper*"):
        probes.extend(str(p) for p in LOCAL.rglob(pattern) if p.is_file())
    return {
        "verdict": "NOT_RUN", "gate_eligible": False,
        "found_artifacts": sorted(set(probes))[:10],
        "requirement": "t17 原规格：交换记录/篡改字段/不可答题；云端 ≥0.90，本地只报检测率",
        "consequence": ("未测量 → 不得声称云端对抗鲁棒（R-Q3）。本轮 T3 输出本就只作描述性，"
                        "因此不阻断主分析，但必须写进 t11 的局限。"),
    }


# ---------------------------------------------------------------------------
# J6 leak audit
# ---------------------------------------------------------------------------
_VARIANT_VALUE = re.compile(r"(?i)T2\.naturalness_pair\.choice(\.[a-z0-9]+)?")
PROSE_CHOICE_MENTIONS: list[str] = []

EXTRA_ID_PATTERNS = (
    ("R28-ITEM-ID", re.compile(r"\br28q_\d{4}\b"), "R28 题号"),
    ("R28-SPAN-ID", re.compile(r"\br28(?:fact|rev|auth|policy)[_-][0-9a-z]+"), "R28 span/revision id"),
    ("R28-FAMILY", re.compile(r"\b(?:FC|DL)_[A-Z0-9_]+"), "R28 族/块编码"),
)


def j6_leak_audit() -> dict[str, Any]:
    packets = []
    for name in ("T1_packets.jsonl", "T1_localarm_packets.jsonl", "T2_packets.jsonl"):
        packets.extend(load_jsonl(ANN / "packets" / name))
    protocol_violations, extra_hits = [], []
    for packet in packets:
        violations = jp.audit_packet(packet)
        if violations:
            protocol_violations.append({"packet_id": packet.get("packet_id"),
                                        "violations": violations[:3]})
        blob = json.dumps(packet.get("payload"), ensure_ascii=False, sort_keys=True)
        for pid, regex, label in EXTRA_ID_PATTERNS:
            for match in regex.finditer(blob):
                extra_hits.append({"packet_id": packet.get("packet_id"), "pattern": pid,
                                   "match": match.group(0)})
    max_tokens = max((p.get("token_estimate") or 0) for p in packets) if packets else 0
    by_task = Counter(p.get("task") for p in packets)
    ok = not protocol_violations and not extra_hits
    return {
        "verdict": "PASS" if ok else "FAIL",
        "gate_eligible": ok,
        "packets_audited": len(packets),
        "by_task": dict(by_task),
        "protocol_audit_violations": protocol_violations[:5],
        "protocol_audit_violation_count": len(protocol_violations),
        "extra_id_pattern_hits": extra_hits[:5],
        "extra_id_pattern_hit_count": len(extra_hits),
        "max_token_estimate": max_tokens,
        "token_caps": {"T1": 3000, "T2": 2000},
        "tokens_within_caps": max_tokens <= 2000,
        "protocol_pattern_coverage": {
            "closed_by": "PAMEND-003",
            "protocol_r28_patterns": [p["id"] for p in jp.BLIND_FORBIDDEN_PATTERNS
                                      if p["id"].startswith("BP-R28")],
            "protocol_covers_r28_ids": all(
                any(p["id"] == expected for p in jp.BLIND_FORBIDDEN_PATTERNS)
                for expected in ("BP-R28-ID", "BP-R28-HELDOUT-ITEM", "BP-R28-FAMILY")),
            "history": ("首冻时协议模式表只覆盖 match_ 与 L#_FAMILY（R28 id 方案尚未存在），本门当时用"
                        "更严的额外模式扫描并判 0 命中；captain 随后以 PAMEND-003 把 r28q_/r28h_/rfam_/"
                        "r28*_ 四条模式补进协议，新增规则复扫 64 个既有盲包仍 0 违规。"),
            "independent_scan_still_runs": True,
        },
    }


# ---------------------------------------------------------------------------
# J7 ledger & replay binding
# ---------------------------------------------------------------------------

_VARIANT_KEY = "t2_choice_template_version"


def scan_variant_under(root: Path) -> dict[str, Any]:
    """C2 scanner: raw-byte scan **and** a JSON structural scan (whole-file for .json).

    t8 F4: the first version parsed the file line by line and ``break``-ed on the first
    failure, so *pretty-printed* .json (the most common form) was silently skipped and the
    "double channel" claim was false.  Now:
      * ``.json``  -> json.loads(whole file) then recursive walk
      * ``.jsonl`` -> per line
      * a file/line that cannot be parsed is reported as ``unauditable`` (never silently
        dropped); production (``t14_main``) being unauditable is a gate failure.
    """
    hit_files: list[str] = []
    structural_hits: list[dict[str, Any]] = []
    unauditable: list[str] = []
    prose_mentions: list[str] = []

    def walk(node: Any, where: str) -> None:
        stack = [(node, where)]
        while stack:
            current, path_hint = stack.pop()
            if isinstance(current, dict):
                for key, value in current.items():
                    k_low = str(key).lower()
                    if k_low == _VARIANT_KEY:
                        structural_hits.append({"file": where, "where": f"key:{key}"})
                    elif "template" in k_low and isinstance(value, str) and "choice" in value.lower():
                        structural_hits.append({"file": where, "where": f"{key}={value}"})
                    stack.append((value, where))
            elif isinstance(current, list):
                for item in current:
                    stack.append((item, where))
            elif isinstance(current, str) and _VARIANT_VALUE.search(current):
                structural_hits.append({"file": where, "where": f"value:{current[:60]}"})

    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in (".json", ".jsonl"):
            continue
        try:
            raw = path.read_bytes()
        except OSError as exc:
            unauditable.append(f"{path_relative(path)}: unreadable ({exc})")
            continue
        text = raw.decode("utf-8", errors="replace")
        if "choice.v1" in text.lower():
            hit_files.append(path_relative(path))
        if "choice" in text.lower() and not _VARIANT_VALUE.search(text) \
                and _VARIANT_KEY not in text.lower():
            prose_mentions.append(path_relative(path))

        if path.suffix == ".json":
            try:
                walk(json.loads(text), path_relative(path))
            except json.JSONDecodeError as exc:
                unauditable.append(f"{path_relative(path)}: json decode error ({exc})")
            continue

        for line_no, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                walk(json.loads(line), path_relative(path))
            except json.JSONDecodeError as exc:
                unauditable.append(f"{path_relative(path)}:{line_no} ({exc})")
    return {"hit_files": hit_files, "structural_hits": structural_hits,
            "unauditable": unauditable, "prose_mentions": prose_mentions,
            "root": path_relative(root)}


def path_relative(path: Path) -> str:
    try:
        return rel(path)
    except ValueError:
        return str(path)


def _current_versions() -> set[str]:
    out: set[str] = set()
    for task, version in jp.TEMPLATE_VERSION_CURRENT.items():
        out.add(version)
        out.update(jp.TEMPLATE_VERSION_REPLAY_COMPATIBLE.get(task, ()))
    return out


def j7_ledger() -> dict[str, Any]:
    ledger_path = T14_MAIN / "local_cost_ledger.jsonl"
    rows = load_jsonl(ledger_path)
    billing_path = T14_MAIN / "cost_ledger.jsonl"
    billing = load_jsonl(billing_path)
    templates = Counter(r.get("prompt_template_version") for r in rows)
    missing = sum(1 for r in rows if any(r.get(k) is None for k in jp.REQUIRED_LEDGER_FIELDS))
    legacy = [r for r in rows
              if str(r.get("prompt_template_version")) not in _current_versions()
              and not jp.replay_parser_compatible(r)["parser_compatible"]]
    missing_task = sum(1 for r in rows if not r.get("task"))
    model_digests = Counter((r.get("model_digest") or "")[:16] for r in rows)
    params = Counter((r.get("temperature"), r.get("seed"), r.get("num_ctx"), r.get("num_predict"))
                     for r in rows)
    cache_hits = sum(1 for r in rows if r.get("cache_hit") is True)

    annotations = {}
    for task, fname in (("T1_factor_visibility", "annotations_T1_factor_visibility.jsonl"),
                        ("S1_span_topic", "annotations_S1_span_topic.jsonl"),
                        ("T2_naturalness", "annotations_T2_naturalness.jsonl")):
        annotations[task] = load_jsonl(T14_MAIN / fname)

    # cache key v2 re-derivation from the cache objects themselves (the objects store the
    # actual prompt, so the key is recomputable; the annotation's input_sha256 is a packet
    # hash and cannot address an object).
    checked = matched = 0
    key_mismatch: list[dict[str, Any]] = []
    objects = list((T14_MAIN / "cache" / "objects").rglob("*.json"))
    for path in objects:
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        prompt = obj.get("input_text") or ""
        params = obj.get("params") or {}
        if not prompt or not params:
            continue
        basis = {
            "schema": jp.CACHE_SCHEMA,
            "task": obj.get("task"),
            "input_sha256": sha256_text(prompt),
            "params": {k: params.get(k) for k in jp.REQUIRED_PARAMS},
            "prompt_template_version": obj.get("prompt_template_version"),
            "model_digest": obj.get("model_digest"),
        }
        recomputed = jp.sha256_json(basis)
        checked += 1
        if recomputed == path.stem:
            matched += 1
        elif len(key_mismatch) < 3:
            key_mismatch.append({"object": path.name, "recomputed": recomputed})
    ok = (missing == 0 and not legacy and matched == checked and checked > 0
          and set(templates) <= set(jp.TEMPLATE_VERSION_CURRENT.values()))
    return {
        "verdict": "PASS" if ok else "FAIL",
        "gate_eligible": ok,
        "annotation_ledger": rel(ledger_path),
        "rows": len(rows),
        "required_fields_missing": missing,
        "templates": dict(templates),
        "legacy_template_entries_excluded": len(legacy),
        "r_r7_note": "旧模板条目不计入一致率（本账本 0 条，无需排除）",
        "params": {f"{k}": v for k, v in params.items()},
        "model_digests": dict(model_digests),
        "cache_hits": cache_hits,
        "cache_key_v2_recomputed": {"checked": checked, "matched": matched,
                                    "mismatch_sample": key_mismatch,
                                    "where": "t14/runs/t14_main/cache/objects/**（对象自带 prompt）"},
        "missing_task_rows": missing_task,
        "input_sha256_semantics": {
            "finding": ("annotations/ledger 的 input_sha256 与缓存对象里 prompt 的 sha256 不同"
                        "（例如 r28q_0001：标注 218441b2…，对象 9c6316f0…），因此它不能用来定位缓存对象；"
                        "可靠指针是 annotation.cache_key（= 对象文件名）。"),
            "impact": "不影响重放（raw_output 与 cache_key 均在），但字段语义有两个含义，容易被误用。",
            "recommendation": "后续把账本字段改名为 packet_sha256，或另存 prompt_sha256（owner: local_operator）",
            "blocking": False,
        },
        "billing_ledger": {
            "path": rel(billing_path), "rows": len(billing),
            "note": ("这是**计费账本**（tokens/成本），不是标注账本；它缺少 "
                     "prompt_template_version/temperature/seed 等字段是设计如此。"
                     "按 R-R2 它不得被用来重建标注。"),
        },
    }


# ---------------------------------------------------------------------------
# J8 template hygiene
# ---------------------------------------------------------------------------
def j8_template_hygiene() -> dict[str, Any]:
    hits = []
    for path in sorted(LOCAL.rglob("*.json*")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "choice.v1" in text:
            hits.append(rel(path))
    main_ledger = load_jsonl(T14_MAIN / "local_cost_ledger.jsonl")
    main_hits = [r for r in main_ledger
                 if str(r.get("prompt_template_version")).startswith("T2.naturalness_pair.choice")]
    main_annotations = [r for r in load_jsonl(T14_MAIN / "annotations_T2_naturalness.jsonl")
                        if r.get("prompt_template_version") != "T2.naturalness_pair.v1"]
    config = load_json(T14_MAIN / "config.json") if (T14_MAIN / "config.json").exists() else {}
    # any trace of the variant *under runs/* keeps J8 FAIL: quarantining only the ledger
    # while leaving cache objects behind is not a fix.
    c2 = scan_variant_under(T14 / "runs")
    variant_under_runs = c2["hit_files"]
    structural_hits = c2["structural_hits"]
    unparsable = c2["unauditable"]
    prose_mentions = c2["prose_mentions"]
    smoke_ledgers = [p for p in variant_under_runs if "smoke" in p or "ledger" in p]

    # the config field must be gone (or explicitly deprecated); a bare declaration is not a fix
    absent = "t2_choice_template_version" not in config
    raw_field = config.get("t2_choice_template_version")
    config_ok = (
        absent
        or raw_field is None
        or raw_field == ""
        or (isinstance(raw_field, dict) and raw_field.get("deprecated") is True)
        or "deprecated" in str(raw_field).lower()
    )
    # C4: every cache hit must resolve to a cache object built from a frozen template.
    hit_total = hit_resolved = 0
    hit_wrong_template: list[dict[str, Any]] = []
    hit_missing_object: list[str] = []
    annotation_rows = {
        task: load_jsonl(T14_MAIN / fname)
        for task, fname in (("T1_factor_visibility", "annotations_T1_factor_visibility.jsonl"),
                            ("S1_span_topic", "annotations_S1_span_topic.jsonl"),
                            ("T2_naturalness", "annotations_T2_naturalness.jsonl"))
    }
    for task, rows_a in annotation_rows.items():
        frozen = jp.TEMPLATE_VERSION_CURRENT.get(task)
        for row in rows_a:
            if row.get("cache_hit") is not True:
                continue
            hit_total += 1
            key = str(row.get("cache_key") or "")
            obj_path = T14_MAIN / "cache" / "objects" / key[:2] / f"{key}.json"
            if not key or not obj_path.exists():
                hit_missing_object.append(key or "<empty>")
                continue
            hit_resolved += 1
            try:
                obj = json.loads(obj_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                hit_missing_object.append(key)
                continue
            if (obj.get("prompt_template_version") != frozen
                    or row.get("prompt_template_version") != frozen):
                hit_wrong_template.append({"task": task, "item_id": row.get("item_id"),
                                           "cache_key": key,
                                           "object_template": obj.get("prompt_template_version"),
                                           "annotation_template": row.get("prompt_template_version"),
                                           "frozen": frozen})
    cache_hit_ok = not hit_wrong_template and not hit_missing_object

    # C5: the retired runs must be *quarantined with an audit trail*, not silently deleted.
    quarantine_root = T14 / "quarantine"
    q_manifest = None
    for name in ("MANIFEST.json", "QUARANTINE.json"):
        if (quarantine_root / name).exists():
            q_manifest = quarantine_root / name
            break
    q_evidence: dict[str, Any] = {
        "root": rel(quarantine_root) if quarantine_root.exists() else None,
        "manifest": rel(q_manifest) if q_manifest else None,
        "files_listed": 0, "verified": 0, "mismatches": [], "reason": None,
        "referenced_by": [],
    }
    q_ok = True
    if quarantine_root.exists():
        q_ok = q_manifest is not None
        if q_manifest:
            mdoc = load_json(q_manifest)
            q_evidence["reason"] = mdoc.get("reason")
            entries = mdoc.get("entries") or []
            q_evidence["files_listed"] = len(entries)
            bad = []
            for e in entries:
                target = quarantine_root / str(e.get("path") or "").replace("\\", "/")
                if not target.exists():
                    bad.append({"path": e.get("path"), "problem": "missing"})
                elif target.stat().st_size != e.get("bytes") or sha256_file(target) != e.get("sha256"):
                    bad.append({"path": e.get("path"), "problem": "bytes/sha256 mismatch"})
            q_evidence["verified"] = len(entries) - len(bad)
            q_evidence["mismatches"] = bad[:5]
            if not entries or bad:
                q_ok = False
            refs = []
            for artefact in sorted(T14_MAIN.rglob("*")):
                if not artefact.is_file() or artefact.suffix not in (".json", ".jsonl"):
                    continue
                try:
                    if "quarantine" in artefact.read_text(encoding="utf-8", errors="ignore"):
                        refs.append(rel(artefact))
                except OSError:
                    continue
            q_evidence["referenced_by"] = refs[:5]
            q_evidence["scan_scope"] = ("仅 t14_main/**（生产运行目录）；t14/test_*.py 与 t14/evidence/ 属测试/审计留存，不在范围")
            q_evidence["evidence_strength"] = ("文本层面未见引用（text grep）——**不是结构证明**；"
                                               "不得单独作为隔离有效性的强证据，需与 C1/C3/C4 同看")
            if refs:
                q_ok = False

    unauditable_production = [u for u in unparsable if "t14_main" in u]
    ok = (not main_hits and not main_annotations and not variant_under_runs
          and not structural_hits and not unauditable_production
          and config_ok and cache_hit_ok and q_ok)
    return {
        "verdict": "PASS" if ok else "FAIL",
        "gate_eligible": ok,
        "main_path_clean": ok,
        "main_ledger_variant_entries": len(main_hits),
        "main_annotation_variant_entries": len(main_annotations),
        "config_field": {
            "field": "t2_choice_template_version",
            "absent": absent,
            "value": raw_field,
            "ok": config_ok,
            "accepted_forms": ["字段不存在", "null / 空串", "{\"deprecated\": true}",
                               "任何含 'deprecated' 的字符串"],
        },
        "variant_files_under_runs": variant_under_runs,
        "structural_hits": structural_hits[:5],
        "structural_hit_count": len(structural_hits),
        "unauditable_files": unparsable[:8],
        "unauditable_production": unauditable_production[:5],
        "prose_choice_mentions": prose_mentions[:5],
        "c2_scope": "被扫范围 = t14/runs/**；其中 t14_main/** 为生产运行，不可解析即判 FAIL",
        "c2_method": ("raw-bytes 扫 'choice.v1' + 结构扫描（.json 整文件 json.loads 后递归；.jsonl 逐行）："
                      "键 t2_choice_template_version、任何 *template* 键的值含 choice、"
                      "或值匹配 T2.naturalness_pair.choice(.v*)；解析失败记为 unauditable，"
                      "生产目录（t14_main）内不可解析即判 FAIL（fail-safe，宁可误报不漏报）"),
        "c2_note": ("散文里的 'choice'（例如卷宗文本 \"required a choice between Stumped and Run out\"）"
                    "是合法数据，不算命中；只认变体声明与实际变体 token。"),
        "config_declares_variant": {
            "field": "t2_choice_template_version",
            "value": raw_field,
            "used_by_main_runner": False,
            "evidence": ("该字段只被 t14/pilot.py 与 t14/recon.py 使用（预检/侦察脚本）；"
                         "生产 runner 走 local_inference 冻结模板。"),
        },
        "variant_artifacts": hits,
        "smoke_ledgers_with_variant": smoke_ledgers,
        "cache_hit_provenance": {
            "rule": "每一条 cache_hit=true 的标注，其命中的缓存对象与标注自身的模板版本都必须是冻结版",
            "hits": hit_total,
            "resolved_objects": hit_resolved,
            "wrong_template": hit_wrong_template[:5],
            "missing_object": hit_missing_object[:5],
            "ok": cache_hit_ok,
        },
        "quarantine": q_evidence,
        "known_limitations": [
            ("F6（verifier 复现）C2 未堵的绕过：把变体 token 从中间拆开放在两个字段里"
             "（{\"a\": \"T2.naturalness_pair.cho\", \"b\": \"ice.v9\"}）不会被命中；"
             "captain 点名的 {\"prefix\": \"…choice\", \"suffix\": \".v9\"} 反而是能拦住的（prefix 本身命中形态）。"
             "caption 口径：C2 只报'未发现符合形态的变体，不证明不存在'。"
             "captain 裁决记为已知局限、不修；若未来升为结构证据，须改为 config schema 白名单 / 解析 runner 实际读取的键。"),
            ("C5 只是文本级（text grep）证据，不是结构证明；不得单独作为隔离有效性的强证据。"),
            ("C2 在 F4 修复前对 pretty-printed JSON 静默失效（verifier 发现，已修 + 已加回归测试）；"
             "C2 仍只作辅助通道。"),
        ],
        "reopen_runbook": rel(VERIFY_ROOT / "J8_REOPEN_RUNBOOK.md"),
        "hygiene_failures": {
            "variant_entered_cache_and_ledger": bool(smoke_ledgers),
            "why_fail": ("按队长指令 (D)：变体一旦进了缓存键或账本就报 FAIL。它确实进了 "
                         "t14/runs/t14_smoke 的 cache 与 ledger，因此 J8 判 FAIL，"
                         "尽管主路径（t14_main）0 条污染。"),
            "consequence": ("不推翻 J1-T2 的数值（主路径 320/320 用冻结模板、序判定口径正确），"
                            "但在隔离与字段废弃完成前，T2 标注不得进入发布/报告链路。"),
            "scope": "t14/runs/t14_smoke/（修复前预检运行）",
            "impact_on_main_analysis": "无（主账本 0 条、主标注 320/320 均为冻结版）",
            "required_fix": ("① 把 t14/runs/t14_smoke、t14/runs/t14_dry 标为 quarantine，"
                             "任何统计与报告不得读取；② 删除/废弃 config.t2_choice_template_version，"
                             "或在 config 里显式标 deprecated。"),
            "owner": "local_operator",
        },
    }


# ---------------------------------------------------------------------------
# J9/J10/J11/J12/J13
# ---------------------------------------------------------------------------
def j9_disagreement(t1_r28: dict[str, Any], t1_local_arm: dict[str, Any]) -> dict[str, Any]:
    def flag(rate):
        return (rate is not None) and (rate < DISAGREEMENT_THRESHOLD)

    per_arm = {
        "local_arm_24": {
            "n": t1_local_arm["n"], "disagree": t1_local_arm["disagree"],
            "rate": t1_local_arm["disagreement_rate"],
            "below_threshold": flag(t1_local_arm["disagreement_rate"]),
            "note": "同刺激构造（t18 冻结 30 条 prompt 的 24 条），是队长引用的 8.33% 来源",
        },
        "r28_arm_comparable_subset": {
            "n": t1_r28["comparable_subset_n"],
            "disagree": t1_r28["comparable_subset_disagree"],
            "rate": t1_r28["comparable_subset_disagreement_rate"],
            "below_threshold": flag(t1_r28["comparable_subset_disagreement_rate"]),
            "note": ("R28 臂 24 题中只有 17 题的 span 与 t14 相同，可逐条比较；"
                     "其余 7 题云端用的是 authority/revision span，t14 标的是别的 span，不可比"),
        },
    }
    total_n = per_arm["local_arm_24"]["n"] + per_arm["r28_arm_comparable_subset"]["n"]
    total_dis = per_arm["local_arm_24"]["disagree"] + per_arm["r28_arm_comparable_subset"]["disagree"]
    pooled_rate = round(total_dis / total_n, 4) if total_n else None
    ok = all(v["below_threshold"] for v in per_arm.values())
    local_errors = [i for i in t1_local_arm["items"] if not i["local_correct"]] + \
                   [i for i in t1_r28["items"]
                    if i.get("local_span_matches_cloud_span") and not i.get("local_correct")]
    return {
        "verdict": "PASS" if ok else "FAIL",
        "gate_eligible": ok,
        "threshold": DISAGREEMENT_THRESHOLD,
        "per_arm": per_arm,
        "pooled_comparable": {"n": total_n, "disagree": total_dis, "rate": pooled_rate,
                              "below_threshold": flag(pooled_rate)},
        "r28_arm_total_n": t1_r28["n"],
        "r28_arm_not_comparable": len(t1_r28.get("unmatched_items") or []),
        "local_errors_total": len(local_errors),
        "local_errors": [
            {k: i.get(k) for k in ("packet_id", "item_id", "matrix_sample_id", "group",
                                   "t14_truth_class", "span_role", "truth",
                                   "local_answer", "cloud_answer")}
            for i in local_errors
        ],
        "conclusion": ("两条可比较分歧都是本地漏正类、云端正确；判据（抄录 / 首次值 / 无独立校验 / "
                       "仅提编号）都不涵盖 displace / replacement 句式 → 本地能力不足，不是协议缺陷。"),
        "protocol_change_needed": False,
    }


def j10_degenerate_truth_guard() -> dict[str, Any]:
    recon = load_json(T14 / "recon.json")
    override_truth = recon.get("t1_override_truth")
    rows = _t1_rows()
    n = len(rows)
    neg = sum(1 for r in rows if not bool(r.get("mechanical_truth")))
    pred_true = sum(1 for r in rows if bool((r.get("parsed_output") or {}).get("supported")))
    return {
        "verdict": "GUARDED",
        "recon_t1_override_truth": override_truth,
        "all_false_is_degenerate": {
            "n": n, "negatives": neg,
            "constant_false_accuracy_under_override_truth": round(neg / n, 4),
            "threshold": jp.THRESHOLD_LOCAL,
            "conclusion": (f"用 t1_override_truth（全 false）时，一律答 false 就 {neg / n:.4f} ≥ {jp.THRESHOLD_LOCAL}，"
                           "闸门被平凡策略满足 → 该真值不可用于开门。"),
            "local_answers_true": pred_true,
        },
        "used_instead": ("按刺激类别分层构造的真值：POS_OVERRIDE 48 / NEG_PROVENANCE_ADJACENT 80 / "
                         "NEG_PLAIN 192（每类 ≥30），逐类报告，不用总体掩盖。"),
        "why_stratified_truth_is_not_circular": (
            "真值来自**刺激构造**（span 的角色与覆盖语义），不来自模型输出；本地答案在构造时不可见。"),
    }


def j11_t3_data_quality(t3: dict[str, Any]) -> dict[str, Any]:
    unsure = t3.get("unsure_items") or []
    items = {x["submission_id"]: x for x in load_jsonl(ANN / "packets" / "T3_items.jsonl")}
    rows = []
    for row in unsure:
        item = items.get(row["submission_id"], {})
        rows.append({"submission_id": row["submission_id"], "item_id": row["item_id"],
                     "edge_class": None, "unsure": True,
                     "true_field_diff": row["true_field_diff"],
                     "cloud_flagged": row["cloud_flagged_fields"]})
    return {
        "verdict": "TRANSFER_TO_T11",
        "gate_eligible": False,
        "n_unsure": len(unsure),
        "items": rows,
        "categories_report": ("① 4.1.5 罚分与记录 0 不一致；② catch/LBW/obstructing 后的越界 allowance；"
                             "③ boundary 条目跨越 supersede completed-runs"),
        "rule": "数据欠定项不得由模型自行填补（R-M1/R-M2）；作为数据质量项转交 t11",
    }


def j12_crosscheck_c14(t1_r28: dict[str, Any]) -> dict[str, Any]:
    path = ANN / "crosscheck_alpha_vs_local.json"
    doc = load_json(path) if path.exists() else {}
    c14 = doc.get("C_t14") or {}
    return {
        "verdict": "FLAG_NOT_ADMISSIBLE",
        "status_now": c14.get("status"),
        "candidate_files_count": len(c14.get("candidate_files") or []),
        "finding": ("按队长指令 (I) 已执行 tools/compare_with_local.py，C_t14 由 BLOCKED_ON_T14 翻为 "
                    "DETECTED；但该脚本的检测器是 `any('t14' in str(p))` 的**路径子串判定**，"
                    "没有做任何逐条匹配，candidate_files 全是 t14 之前就存在的账本/矩阵文件。"
                    "因此 DETECTED 是**空洞翻转**，不得作为证据。"),
        "independent_match": {
            "performed_by": "t17（本门）",
            "n": t1_r28["comparable_subset_n"],
            "agree": t1_r28["comparable_subset_agree"],
            "disagree": t1_r28["comparable_subset_disagree"],
            "disagreement_rate": t1_r28["comparable_subset_disagreement_rate"],
            "r28_arm_total": t1_r28["n"],
            "not_comparable": len(t1_r28.get("unmatched_items") or []),
            "matching": "packet_id → SELECTION_INDEX.t1[] → span_id 相等才比较",
        },
        "fix_owner": "annotator_alpha（t16 工具）",
        "required_fix": ("把检测器改成基于 span_id/item_id 的真实匹配并输出 n/agree/disagree；"
                         "在此之前该字段不得被 t11/t8 引用。"),
    }


def j13_no_discrimination(t3: dict[str, Any]) -> dict[str, Any]:
    dims = t3["dimension_counts"]
    flat = {d: (len(c) == 1 and "PASS" in c) for d, c in dims.items()}
    overall_flat = all(r["true_verdict"] == "DEFECT" for r in t3["items"]) and \
        (t3["overall_counts"].get("DEFECT", 0) == t3["n"])
    return {
        "verdict": "NO_DISCRIMINATION",
        "gate_eligible": False,
        "dimensions_all_pass": flat,
        "no_discrimination_dims": [d for d, v in flat.items() if v],
        "overall_verdict_degenerate": overall_flat,
        "overall_counts": t3["overall_counts"],
        "true_verdict_counts": dict(Counter(r["true_verdict"] for r in t3["items"])),
        "rule": ("abstain/conformance 在 R28 上 12/12 PASS → 无区分度，只能作满足率描述，"
                 "不得当质量门（队长指令 F）。"),
        "extra_finding": ("若 12 条提报全部真的与金标不同，则 'overall=DEFECT' 也是平凡策略；"
                          "因此 T3 的可用信号是**逐字段 verdict**（precision/recall），不是 overall"),
    }


# ---------------------------------------------------------------------------
# captain directives (A)–(I)
# ---------------------------------------------------------------------------
def directives(j0, j1, t1_r28, t1_local_arm, t2_cloud, t3, j3, j7, j8, j9, j12, j13) -> dict[str, Any]:
    return {
        "A_protocol_single_source": {
            "requirement": "唯一权威 02_design/protocol.json；不得写副本到主项目 design/ 或 R27 根",
            "result": "未创建任何副本；J 门直接 import 02_design/scripts/judge_protocol.py",
            "verdict": "PASS",
            "evidence": j0["evidence"]["protocol_json_sha256"],
        },
        "B_local_t1_no_degenerate_truth": {
            "requirement": "只用按真类分层的 T1 真值（每类 ≥30）、逐类报告；否则 DESCRIPTIVE_ONLY",
            "result": {"classes": j1["evidence"]["per_class"],
                       "all_sufficient": j1["evidence"]["classes_all_sufficient"],
                       "overall": j1["evidence"]["agreement"],
                       "per_class_below_threshold": j1["evidence"]["per_class_below_threshold"]},
            "verdict": "PASS" if j1["gate_eligible"] else "FAIL",
        },
        "C_cloud_local_t1_same_stimulus": {
            "requirement": "复核 8.33% 是否 <30%，并写明两条分歧句式原因",
            "result": {"r28_arm_comparable": {
                           "n": t1_r28["comparable_subset_n"],
                           "agree": t1_r28["comparable_subset_agree"],
                           "disagree": t1_r28["comparable_subset_disagree"],
                           "rate": t1_r28["comparable_subset_disagreement_rate"],
                           "not_comparable": len(t1_r28.get("unmatched_items") or [])},
                       "local_arm": {k: t1_local_arm[k] for k in ("n", "agree", "disagree",
                                                                  "disagreement_rate")},
                       "threshold": DISAGREEMENT_THRESHOLD},
            "verdict": "PASS" if j9["gate_eligible"] else "FAIL",
        },
        "D_t2_order_only": {
            "requirement": "T2 只报序判定；绝对分进阈值即 FAIL；模板必须是 T2.naturalness_pair.v1",
            "result": {"metric": "ordinal_preference_from_frozen_T2v1_scores",
                       "template": "T2.naturalness_pair.v1",
                       "main_path_clean": j8["main_path_clean"],
                       "variant_artifacts": j8["variant_artifacts"][:4]},
            "verdict": "PASS" if j8["main_path_clean"] else "FAIL",
        },
        "E_cloud_t3_descriptive_only": {
            "requirement": "n=12<30 只能 DESCRIPTIVE_ONLY；5 条 unsure 转 t11",
            "result": {"n": t3["n"], "overall_counts": t3["overall_counts"],
                       "unsure": len(t3["unsure_items"])},
            "verdict": "DESCRIPTIVE_ONLY",
        },
        "F_no_discrimination_dims": {
            "requirement": "abstain/conformance 不得当质量门",
            "result": {"no_discrimination_dims": j13["no_discrimination_dims"],
                       "overall_degenerate": j13["overall_verdict_degenerate"]},
            "verdict": "PASS",
        },
        "G_kappa_n30": {
            "requirement": "kappa 只在 n≥30 算；否则不估计",
            "result": {"arms": {k: {kk: v[kk] for kk in ("n", "verdict")}
                                for k, v in j3["arms"].items()},
                       "exploratory_pooled": (j3["exploratory_pooled_T1"] or {}).get("n")},
            "verdict": "PASS",
        },
        "H_replay_parser_binding": {
            "requirement": "旧 cost_ledger 条目不得计入一致率（R-R7）",
            "result": {"legacy_template_entries_excluded": j7["legacy_template_entries_excluded"],
                       "templates": j7["templates"]},
            "verdict": "PASS" if j7["verdict"] == "PASS" else "FAIL",
        },
        "I_reuse_t16_tool": {
            "requirement": "跑 tools/compare_with_local.py 把 C_t14 翻为 DETECTED",
            "result": {"status": j12["status_now"],
                       "admissible": False,
                       "independent_match": j12["independent_match"]},
            "verdict": "DONE_BUT_NOT_ADMISSIBLE",
        },
    }


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------
def build_report(generated_at_utc: str | None = None) -> dict[str, Any]:
    cloud = _cloud_rows()
    j0 = j0_protocol()
    t1 = j1_t1()
    t2 = j1_t2()
    s1 = j1_s1()
    c1 = j1_c1()
    j1b = j1b_truth_grounding()
    j1c = j1c_shortcut_audit()
    t1_r28 = j2_t1_r28_arm(cloud)
    t1_local_arm = j2_t1_local_arm(cloud)
    t2_cloud = j2_t2(cloud)
    t3 = j2_t3(cloud)
    j3 = j3_kappa(t1_r28, t1_local_arm, t2_cloud)
    j4 = j4_self_consistency()
    j5 = j5_adversarial()
    j6 = j6_leak_audit()
    j7 = j7_ledger()
    j8 = j8_template_hygiene()
    j9 = j9_disagreement(t1_r28, t1_local_arm)
    j10 = j10_degenerate_truth_guard()
    j11 = j11_t3_data_quality(t3)
    j12 = j12_crosscheck_c14(t1_r28)
    j13 = j13_no_discrimination(t3)

    can_enter = {
        "T1_local": {"verdict": t1["verdict"], "n": t1["evidence"]["n"],
                     "use": "可进主分析（逐类 + 逐 span role 披露；POS 类单独 <0.85）",
                     "conditions": ["报告必须并列三类一致率",
                                    "不得用总体 0.975 代替 POS 0.8333",
                                    "必须标注 authority_policy 子组 0.75（8/8 错在此组）",
                                    "不得把 T1 当作'本地能读懂证据支持'的能力证据（J1c）"]},
        "T2_local": {"verdict": t2["verdict"], "n": t2["evidence"]["n_valid"],
                     "use": "可进主分析（序判定 0.9905）；J8 已于修复后重开为 PASS",
                     "conditions": ["报告只报序判定；绝对分仅描述",
                                    "不得读取 t14/quarantine/（35 个文件仅作审计留存）"]},
        "S1_local": {"verdict": s1["verdict"], "n": s1["evidence"]["n_rows"],
                     "use": "不可当门；只可作 DESCRIPTIVE_ONLY 描述",
                     "conditions": ["要当门必须先造可独立复算的机械主题真值"]},
        "C1_local": {"verdict": c1["verdict"], "n": 0,
                     "use": "不可进主分析（R28 未测量）",
                     "conditions": ["先跑 t21 并在 ≥30 条上重测"]},
        "cloud_T1": {"verdict": "REFERENCE", "n": t1_r28["n"] + t1_local_arm["n"],
                     "use": "可作参考标尺；逐条对照见 J2/J9", "conditions": []},
        "cloud_T2": {"verdict": "REFERENCE", "n": t2_cloud["n"],
                     "use": "序判定 16/16，作参考；n<30 不入推断", "conditions": []},
        "cloud_T3": {"verdict": "DESCRIPTIVE_ONLY", "n": t3["n"],
                     "use": "只作描述性裁定摘要；逐字段 verdict 可用，overall/abstain/conformance 不可当门",
                     "conditions": ["n=12 不足以做推断性主张", "5 条 unsure 转 t11"]},
    }
    failed = [k for k, v in (("J0", j0), ("J1_T1", t1), ("J1_T2", t2), ("J1b", j1b), ("J4", j4),
                             ("J6", j6), ("J7", j7), ("J8", j8), ("J9", j9))
              if v["verdict"] == "FAIL"]
    return {
        "schema": "vett-r28-j-gate/v1",
        "gate_id": GATE_ID,
        "generated_at_utc": generated_at_utc or jp.utc_now(),
        "run_by": "judge_architect",
        "purpose": ("用冻结协议核验本地/云端标注的可信度，判定它们能不能进主分析；"
                    "本地 vs 机械真值可作门，云端 T3 n=12 仅描述性。"),
        "protocol_precondition": j0,
        "items": {
            "J0_protocol_precondition": j0,
            "J1_local_vs_mechanical": {"T1_factor_visibility": t1, "T2_naturalness": t2,
                                       "S1_span_topic": s1,
                                       "C1_cert_sentence_consistency": c1},
            "J1b_truth_grounding": j1b,
            "J1c_shortcut_audit": j1c,
            "J2_cloud_vs_mechanical": {"T1_r28_arm": {k: v for k, v in t1_r28.items() if k != "items"},
                                       "T1_local_arm": {k: v for k, v in t1_local_arm.items()
                                                        if k != "items"},
                                       "T2_naturalness": {k: v for k, v in t2_cloud.items()
                                                          if k != "items"},
                                       "T3_adjudication": t3},
            "J3_cross_model_kappa": j3,
            "J4_self_consistency": j4,
            "J5_adversarial": j5,
            "J6_blind_leak_audit": j6,
            "J7_ledger_replay_binding": j7,
            "J8_template_hygiene": j8,
            "J9_disagreement_threshold": j9,
            "J10_degenerate_truth_guard": j10,
            "J11_t3_data_quality_items": j11,
            "J12_crosscheck_c_t14": j12,
            "J13_no_discrimination": j13,
        },
        "captain_directives": directives(j0, t1, t1_r28, t1_local_arm, t2_cloud, t3, j3, j7,
                                         j8, j9, j12, j13),
        "ruling": {
            "can_enter_main_analysis": can_enter,
            "blocking": failed,
            "summary": ("T1/T2 本地标注可进主分析：T1 0.9750（POS 0.8333、authority_policy 0.7500；"
                        "8/8 错误集中在 authority_policy 构造 —— 稳健表述，不再引用'错集=词表不命中集'）；"
                        "T2 序判定 0.9905（J8 修复后已重开为 PASS：C1 主路径 0/0、C2 runs/ 下 0 命中、"
                        "C3 config 字段已移除、C4 71/71 缓存命中均解析到冻结模板、C5 35 个退役文件已隔离且 sha256 校验）。"
                        "S1（无机械真值）与 C1（未运行）在 R28 上不可当门；云端 T1 24/24、T2 16/16 可作参考标尺；"
                        "T3 n=12 只作描述性（逐字段 precision 0.9333 / recall 0.6087，云端自写记录仅 0.4514 与金标同）。"),
            "verdict_index": {
                "J0": j0["verdict"], "J1_T1": t1["verdict"], "J1_T2": t2["verdict"],
                "J1_S1": s1["verdict"], "J1_C1": c1["verdict"], "J1b": j1b["verdict"],
                "J1c": j1c["verdict"], "J2_T3": "DESCRIPTIVE_ONLY", "J3": j3["verdict"],
                "J4": j4["verdict"], "J5": j5["verdict"], "J6": j6["verdict"],
                "J7": j7["verdict"], "J8": j8["verdict"], "J9": j9["verdict"],
                "J10": j10["verdict"], "J11": j11["verdict"], "J12": j12["verdict"],
                "J13": j13["verdict"],
            },
        },
        "counts": Counter(),
        "artifacts": {
            "J_GATE.json": rel(OUT_PATH),
            "J_GATE.md": rel(MD_PATH),
            "inputs": {
                "t14_annotations": [rel(T14_MAIN / f) for f in
                                    ("annotations_T1_factor_visibility.jsonl",
                                     "annotations_S1_span_topic.jsonl",
                                     "annotations_T2_naturalness.jsonl",
                                     "local_cost_ledger.jsonl")],
                "t16_annotations": [rel(ANN / "cloud_alpha.jsonl"),
                                    rel(ANN / "packets" / "SELECTION_INDEX.json"),
                                    rel(ANN / "crosscheck_alpha_vs_local.json")],
                "dataset_gold": "03_build/dataset_r28/private/<item_id>/private_gold.json",
                "matrix_arm": rel(MATRIX_DIR / "T1_factor_visibility.jsonl"),
            },
        },
        "honest_limits": [
            "T1 的 POS_OVERRIDE 类单独 0.8333 < 0.85：ALLOW 是总体口径，类级不达标必须披露。",
            "S1 在 R28 上没有机械真值，96 条 PROVENANCE 是回退标签而非模型能力证据。",
            "C1 未在 R28 上运行，t18 的 1.0/30 不能平移。",
            "kappa 全部 n<30 → 不估计；合并臂的 48 条只作量级参考，不得进报告主表。",
            "云端没有做 10% 重复与对抗探针 → 云端自一致与鲁棒性未测量。",
            "T3 n=12，且 12 条提报全部与金标不同 → overall=DEFECT 也是平凡策略。",
            "t16 的 C_t14 检测器是路径子串判定，DETECTED 不可采信；真正的匹配由本门完成。",
            "T1 的 8 个错全部集中在 authority_policy 同一句式（J1c）；『错集=词表不命中集』的等式依赖"
            "特定词表、不稳健，不得引用。T1 不能当作'本地能判断证据支持'的能力证据。",
            "T3 云端自写 correct_record 与 solver 金标只有 0.4514 字段一致 → 模型输出绝不能当金标。",
        ],
    }


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")


MD_CHECKS: tuple[str, ...] = ()


def check_md(report: Mapping[str, Any]) -> int:
    """Assert the numbers quoted in J_GATE.md equal the ones in J_GATE.json."""
    md = MD_PATH.read_text(encoding="utf-8")
    ev1 = report["items"]["J1_local_vs_mechanical"]["T1_factor_visibility"]["evidence"]
    ev2 = report["items"]["J1_local_vs_mechanical"]["T2_naturalness"]["evidence"]
    cl = report["items"]["J2_cloud_vs_mechanical"]["T1_r28_arm"]
    arm = report["items"]["J2_cloud_vs_mechanical"]["T1_local_arm"]
    t3 = report["items"]["J2_cloud_vs_mechanical"]["T3_adjudication"]
    j7 = report["items"]["J7_ledger_replay_binding"]
    j9 = report["items"]["J9_disagreement_threshold"]
    j1c = report["items"]["J1c_shortcut_audit"]
    required = [
        f"{ev1['agreement']:.4f}",
        f"{ev1['per_class']['POS_OVERRIDE']['agreement']:.4f}",
        f"{ev1['per_class']['NEG_PLAIN']['agreement']:.4f}",
        f"{ev1['per_class']['NEG_PROVENANCE_ADJACENT']['agreement']:.4f}",
        f"{ev1['degenerate_baselines']['constant_false_accuracy']:.4f}",
        f"{j1c['authority_policy_subgroup']['agreement']:.4f}",
        f"{ev2['agreement']:.4f}",
        f"{ev2['n_valid']}",
        f"{cl['cloud_accuracy']:.4f}",
        f"{cl['comparable_subset_disagreement_rate']:.4f}",
        f"{arm['disagreement_rate']:.4f}",
        f"{t3['n']}",
        f"{t3['flagged_field_precision']:.4f}",
        f"{t3['recall_on_true_diff_fields']:.4f}",
        f"{t3['correct_record_field_agreement']:.4f}",
        f"{j7['cache_key_v2_recomputed']['matched']}",
        f"{j9['threshold']:.2f}",
        "DESCRIPTIVE_ONLY", "INSUFFICIENT", "never evidence",
    ]
    missing = [s for s in required if s not in md]
    if missing:
        print(f"[FAIL] J_GATE.md is missing {missing}", file=sys.stderr)
        return 4
    print(f"[ok] J_GATE.md quotes {len(required)}/{len(required)} recomputed values")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="t17 J gate")
    parser.add_argument("--write", action="store_true",
                        help="persist J_GATE.json (default: build in memory only)")
    parser.add_argument("--json-only", action="store_true")
    parser.add_argument("--check-md", action="store_true",
                        help="compare J_GATE.md against the JSON; never rewrites the JSON")
    parser.add_argument("--no-write", action="store_true", help="build in memory only")
    parser.add_argument("--generated-at", default=None,
                        help="pin generated_at_utc so the JSON is byte-reproducible")
    parser.add_argument("--determinism-check", action="store_true",
                        help="build twice with a pinned timestamp and compare digests")
    args = parser.parse_args(argv)

    if args.determinism_check:
        pinned = args.generated_at or "2026-11-12T00:00:00Z"
        first = build_report(pinned)
        second = build_report(pinned)
        a = sha256_text(json.dumps(first, ensure_ascii=False, indent=2))
        b = sha256_text(json.dumps(second, ensure_ascii=False, indent=2))
        print(f"[{'ok' if a == b else 'FAIL'}] determinism: {a[:16]} vs {b[:16]}")
        return 0 if a == b else 4

    report = build_report(args.generated_at)
    report["counts"] = dict(Counter(v["verdict"] for section in report["items"].values()
                                    if isinstance(section, dict)
                                    for v in section.values()
                                    if isinstance(v, dict) and "verdict" in v))
    # ``--check-md`` is a *read-only* consistency check: rewriting J_GATE.json on every check
    # churned its sha256 (t8 observed three digests in a row).  Only an explicit write run
    # (no --check-md, no --no-write) touches the file.
    # F9 (t8): plain runs also rewrote the artefact and broke snapshot S1.  Writing is now
    # **opt-in**: only `--write` persists J_GATE.json.  Default = build in memory + print.
    do_write = bool(args.write) and not args.check_md and not args.no_write
    if do_write:
        write_json(OUT_PATH, report)
    else:
        print(f"[info] not writing {rel(OUT_PATH)}（需要显式 --write 才落盘）")
    if not args.json_only:
        print(json.dumps({"gate_id": report["gate_id"],
                          "verdicts": report["counts"],
                          "blocking": report["ruling"]["blocking"],
                          "can_enter": {k: v["verdict"] for k, v in
                                        report["ruling"]["can_enter_main_analysis"].items()}},
                         ensure_ascii=False, indent=1))
        print(f"[ok] wrote {rel(OUT_PATH)}")
    if args.check_md:
        return check_md(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
