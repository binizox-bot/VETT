"""Verify the frozen judge protocol against its authorities (V1–V22).

Design rules:

* Every check is a pure function of files on disk.  No network, no model, no GPU.
* A check that cannot be executed is **failed**, never skipped silently.
* ``--freeze`` writes ``protocol_freeze.json`` + ``PROTOCOL.sha256``; ``--check``
  recomputes the protocol from the routing card and re-runs all 22 checks.
  Editing any frozen artefact after the freeze makes ``--check`` fail.

Usage:
    python protocol_verify.py --freeze    # fingerprint the frozen artefacts
    python protocol_verify.py --check     # run V1–V22, write protocol_verify_result.json
    python protocol_verify.py --check --json-only

Exit codes: 0 = all PASS, 4 = at least one FAIL.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable, Mapping

HERE = Path(__file__).resolve().parent
DESIGN_ROOT = HERE.parent
RUN_ROOT = DESIGN_ROOT.parent
sys.path.insert(0, str(HERE))

import judge_protocol as jp  # noqa: E402
import build_protocol as bp  # noqa: E402

PROTOCOL_PATH = DESIGN_ROOT / "protocol.json"
PROTOCOL_MD_PATH = DESIGN_ROOT / "PROTOCOL.md"
VERIFY_RESULT_PATH = DESIGN_ROOT / "protocol_verify_result.json"
FREEZE_PATH = DESIGN_ROOT / "protocol_freeze.json"
SHA256_PATH = DESIGN_ROOT / "PROTOCOL.sha256"
SNAPSHOT_PATH = DESIGN_ROOT / "evidence" / "routing_evidence_snapshot.json"

FROZEN_ARTIFACTS = {
    "protocol_json": PROTOCOL_PATH,
    "protocol_md": PROTOCOL_MD_PATH,
    "routing_evidence_snapshot": SNAPSHOT_PATH,
    "judge_protocol_py": HERE / "judge_protocol.py",
    "build_protocol_py": HERE / "build_protocol.py",
    "protocol_verify_py": HERE / "protocol_verify.py",
    "tests": DESIGN_ROOT / "tests" / "test_judge_protocol.py",
}

RESULTS: list[dict[str, Any]] = []


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def record(check_id: str, description: str, ok: bool, evidence: Any,
           error: str | None = None) -> None:
    status = "passed" if ok else "failed"
    RESULTS.append({"id": check_id, "description": description, "status": status,
                    "evidence": evidence, "error": error})
    flag = "PASS" if ok else "FAIL"
    print(f"[{flag:4s}] {check_id}: {description}")


def guard(check_id: str, description: str, fn: Callable[[], tuple[bool, Any]]) -> None:
    """Run one check; an exception is a failure with the exception text as evidence."""
    try:
        ok, evidence = fn()
    except Exception as exc:  # noqa: BLE001 - a check that blows up is a failed check
        record(check_id, description, False, None, f"{type(exc).__name__}: {exc}")
        return
    record(check_id, description, ok, evidence)


def load_protocol() -> dict[str, Any]:
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))


def _allow(protocol: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {e["task"]: e for e in protocol["rulers"]["local"]["allow"]}


def _deny(protocol: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {e["task"]: e for e in protocol["rulers"]["local"]["deny"]}


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def check_v1(protocol: Mapping[str, Any]) -> tuple[bool, Any]:
    card = jp.load_routing_card()
    card_tasks = sorted(card["tasks"])
    proto_tasks = sorted(set(_allow(protocol)) | set(_deny(protocol)))
    counts = protocol["rulers"]["local"]["counts"]
    ok = card_tasks == proto_tasks and counts["total"] == len(card_tasks) == 13
    return ok, {"card_tasks": card_tasks, "protocol_tasks": proto_tasks,
                "counts": counts, "equal": card_tasks == proto_tasks}


def check_v2(protocol: Mapping[str, Any]) -> tuple[bool, Any]:
    card = jp.load_routing_card()
    matrix = jp.load_capability_matrix()
    card_allow = sorted(t for t, e in card["tasks"].items() if e["verdict"] == "ALLOW")
    card_deny = sorted(t for t, e in card["tasks"].items() if e["verdict"] != "ALLOW")
    proto_allow = sorted(_allow(protocol))
    proto_deny = sorted(_deny(protocol))
    matrix_allow = sorted(t for t, e in matrix["tasks"].items() if e.get("verdict") == "ALLOW")
    ok = (card_allow == proto_allow == matrix_allow and len(proto_allow) == 4
          and card_deny == proto_deny and len(proto_deny) == 9)
    return ok, {"allow": proto_allow, "deny": proto_deny,
                "matrix_allow": matrix_allow, "allow_count": len(proto_allow),
                "deny_count": len(proto_deny)}


def check_v3(protocol: Mapping[str, Any]) -> tuple[bool, Any]:
    card = jp.load_routing_card()
    matrix = jp.load_capability_matrix()
    pinned = {"T1_factor_visibility": 0.9333, "T2_naturalness": 1.0,
              "S1_span_topic": 1.0, "C1_cert_sentence_consistency": 1.0}
    problems: list[str] = []
    detail = {}
    for task, entry in _allow(protocol).items():
        card_m = card["tasks"][task].get("measured") or {}
        mx = matrix["tasks"][task]
        measured = entry["measured"]
        agreement = measured["agreement"]
        n = measured["n"]
        detail[task] = {"agreement": agreement, "n": n, "threshold": measured["threshold"],
                        "card_agreement": card_m.get("agreement"),
                        "matrix_agreement": mx.get("agreement")}
        if agreement != card_m.get("agreement") or agreement != mx.get("agreement"):
            problems.append(f"{task}: agreement {agreement} != card {card_m.get('agreement')} "
                            f"/ matrix {mx.get('agreement')}")
        if n != card_m.get("n") or n != mx.get("n_scored"):
            problems.append(f"{task}: n {n} != card {card_m.get('n')} / matrix {mx.get('n_scored')}")
        if measured["threshold"] != jp.THRESHOLD_LOCAL:
            problems.append(f"{task}: threshold {measured['threshold']} != {jp.THRESHOLD_LOCAL}")
        if not (isinstance(agreement, (int, float)) and agreement >= jp.THRESHOLD_LOCAL):
            problems.append(f"{task}: agreement {agreement} below gate")
        if not (isinstance(n, int) and n >= jp.N_MIN):
            problems.append(f"{task}: n {n} < {jp.N_MIN}")
        if round(float(agreement), 4) != pinned[task]:
            problems.append(f"{task}: agreement {agreement} != prompt-claimed {pinned[task]}")
        if entry["verdict"] != card["tasks"][task]["verdict"] != "ALLOW":
            problems.append(f"{task}: verdict mismatch")
    return not problems, {"tasks": detail, "problems": problems}


def check_v4(protocol: Mapping[str, Any]) -> tuple[bool, Any]:
    card = jp.load_routing_card()
    problems: list[str] = []
    detail = {}
    for task, entry in _deny(protocol).items():
        card_entry = card["tasks"][task]
        detail[task] = {"reason_code": entry["reason_code"],
                        "card_reason_code": card_entry.get("reason_code"),
                        "evidence_status": entry["evidence_status"]}
        if entry["verdict"] != "DENY" or card_entry["verdict"] != "DENY":
            problems.append(f"{task}: not DENY in protocol or card")
        if entry["reason_code"] != card_entry.get("reason_code"):
            problems.append(f"{task}: reason_code {entry['reason_code']} != "
                            f"{card_entry.get('reason_code')}")
        if (entry["deny_reason"] or "") != (card_entry.get("deny_reason") or ""):
            problems.append(f"{task}: deny_reason text differs from the card")
        if (entry["measured_evidence"] or {}) != (card_entry.get("measured_evidence") or {}):
            problems.append(f"{task}: measured_evidence differs from the card")
        if not (entry["deny_reason"] or "").strip():
            problems.append(f"{task}: empty deny_reason")
    return not problems, {"tasks": detail, "problems": problems}


def check_v5(protocol: Mapping[str, Any]) -> tuple[bool, Any]:
    problems: list[str] = []
    measured, policy = [], []
    for task, entry in _deny(protocol).items():
        cls = entry["rationale_class"]
        evidence_status = entry["evidence_status"]
        has_numbers = bool(bp._numeric_values(entry["measured_evidence"])) or \
            bool(entry["measured_evidence"]) or \
            bool(bp._numeric_values(entry.get("measured_evidence_supplement") or {})) or \
            bool(bp._numeric_values(entry.get("measured") or {}))
        if cls == "MEASURED":
            measured.append(task)
            if evidence_status != "MEASURED" or not has_numbers:
                problems.append(f"{task}: MEASURED class without numeric evidence")
        elif cls == "POLICY":
            policy.append(task)
            if evidence_status != "POLICY_NO_MEASUREMENT" or has_numbers:
                problems.append(f"{task}: POLICY class carries fabricated evidence")
        else:
            problems.append(f"{task}: unknown rationale_class {cls}")
    ok = (not problems and len(measured) == 7
          and sorted(policy) == sorted(jp.POLICY_DENY_TASKS) == ["D5_contract_or_code_design",
                                                                 "D8_T3_adjudication"])
    return ok, {"measured": sorted(measured), "policy": sorted(policy),
                "policy_expected": list(jp.POLICY_DENY_TASKS), "problems": problems}


def check_v6(protocol: Mapping[str, Any]) -> tuple[bool, Any]:
    matrix = jp.load_capability_matrix()
    entry = _deny(protocol)["R1_readability"]
    extra = matrix["tasks"]["R1_readability"].get("extra") or {}
    supplement = entry.get("measured_evidence_supplement") or {}
    problems: list[str] = []
    if entry["measured"]["agreement"] != 0.6667:
        problems.append(f"agreement {entry['measured']['agreement']} != 0.6667")
    if entry["measured"]["n"] != 30:
        problems.append(f"n {entry['measured']['n']} != 30")
    if extra.get("spearman_rho") != -0.1672:
        problems.append(f"rho {extra.get('spearman_rho')} != -0.1672")
    if extra.get("discrimination_ok") is not False:
        problems.append("discrimination_ok is not False")
    if entry["fallback_used"] != "flesch_reading_ease_band":
        problems.append(f"fallback {entry['fallback_used']} != flesch_reading_ease_band")
    if "discrimination_ok" not in (entry["deny_reason"] or ""):
        problems.append("deny_reason does not cite discrimination_ok")
    if supplement.get("agreement") != 0.6667:
        problems.append("supplement does not carry the matrix agreement")
    return not problems, {"agreement": entry["measured"]["agreement"],
                          "n": entry["measured"]["n"],
                          "spearman_rho": extra.get("spearman_rho"),
                          "discrimination_ok": extra.get("discrimination_ok"),
                          "fallback_used": entry["fallback_used"],
                          "problems": problems}


def check_v7(protocol: Mapping[str, Any]) -> tuple[bool, Any]:
    card = jp.load_routing_card()
    hard = card.get("hard_limits") or {}
    proto_hard = protocol["rulers"]["local"]["hard_limits"]
    behaviour = proto_hard.get("over_limit_behaviour") or ""
    ok = (hard.get("max_input_tokens") == jp.HARD_INPUT_CAP_TOKENS
          and proto_hard.get("max_input_tokens") == jp.HARD_INPUT_CAP_TOKENS
          and "never truncate" in behaviour
          and proto_hard.get("temperature") == 0.0
          and proto_hard.get("seed") == 20261112)
    return ok, {"card_max_input_tokens": hard.get("max_input_tokens"),
                "protocol_max_input_tokens": proto_hard.get("max_input_tokens"),
                "over_limit_behaviour": behaviour,
                "temperature": proto_hard.get("temperature"),
                "seed": proto_hard.get("seed")}


def check_v8() -> tuple[bool, Any]:
    params = {"temperature": 0.0, "seed": 20261112, "num_ctx": 8192, "num_predict": 128}
    base = jp.cache_key("T1_factor_visibility", "PASSAGE", params, "T1.factor_visibility.v1",
                        jp.MODEL_DIGEST)
    repeat = jp.cache_key("T1_factor_visibility", "PASSAGE", dict(params),
                          "T1.factor_visibility.v1", jp.MODEL_DIGEST)
    variants = {
        "input": jp.cache_key("T1_factor_visibility", "PASSAGE ", params,
                              "T1.factor_visibility.v1", jp.MODEL_DIGEST),
        "temperature": jp.cache_key("T1_factor_visibility", "PASSAGE",
                                    {**params, "temperature": 0.1},
                                    "T1.factor_visibility.v1", jp.MODEL_DIGEST),
        "seed": jp.cache_key("T1_factor_visibility", "PASSAGE", {**params, "seed": 1},
                             "T1.factor_visibility.v1", jp.MODEL_DIGEST),
        "num_ctx": jp.cache_key("T1_factor_visibility", "PASSAGE", {**params, "num_ctx": 4096},
                                "T1.factor_visibility.v1", jp.MODEL_DIGEST),
        "num_predict": jp.cache_key("T1_factor_visibility", "PASSAGE",
                                    {**params, "num_predict": 96},
                                    "T1.factor_visibility.v1", jp.MODEL_DIGEST),
        "template": jp.cache_key("T1_factor_visibility", "PASSAGE", params,
                                 "T1.factor_visibility.v2", jp.MODEL_DIGEST),
        "model_digest": jp.cache_key("T1_factor_visibility", "PASSAGE", params,
                                     "T1.factor_visibility.v1", "0" * 64),
    }
    problems = [name for name, key in variants.items() if key == base]
    if repeat != base:
        problems.append("not deterministic for identical inputs")
    missing_param_raises = False
    try:
        jp.cache_key("T1_factor_visibility", "PASSAGE", {"temperature": 0.0},
                     "T1.factor_visibility.v1", jp.MODEL_DIGEST)
    except jp.ProtocolError:
        missing_param_raises = True
    if not missing_param_raises:
        problems.append("missing params did not raise")
    return not problems, {"base": base, "variants": variants, "problems": problems,
                          "deterministic": repeat == base}


def check_v9() -> tuple[bool, Any]:
    params = {"temperature": 0.0, "seed": 20261112, "num_ctx": 8192, "num_predict": 128}
    v2 = jp.cache_key("T1_factor_visibility", "PROMPT", params, "T1.factor_visibility.v1",
                      jp.MODEL_DIGEST)
    v1 = jp.legacy_cache_key_v1("T1_factor_visibility", "PROMPT", "T1.factor_visibility.v1")
    v1_repeat = jp.legacy_cache_key_v1("T1_factor_visibility", "PROMPT", "T1.factor_visibility.v1")
    digest_sensitive = v2 != jp.cache_key("T1_factor_visibility", "PROMPT", params,
                                          "T1.factor_visibility.v1", "f" * 64)
    formula = "|".join(["vett-local-cache/v1", "T1.factor_visibility.v1", jp.MODEL_TAG,
                        str(jp.TEMPERATURE), str(jp.SEED), str(jp.HARD_INPUT_CAP_TOKENS),
                        "256", "PROMPT"])
    formula_key = jp.sha256_text(formula)
    ok = (v2 != v1 and v1 == v1_repeat and digest_sensitive and formula_key == v1)
    return ok, {"v2": v2, "v1": v1, "v1_recount": v1_repeat, "v1_formula_reproduced": formula_key == v1,
                "digest_sensitive": digest_sensitive, "v2_differs_from_v1": v2 != v1}


def check_v10() -> tuple[bool, Any]:
    """Replay = recompute from raw_output, verified on the real 457-entry ledger.

    Replay must be pinned to the parser version of the entry (R-R7): the ledger holds
    25 entries from the retired S1 v1/v2 templates whose PROVENANCE topic no longer
    parses.  Those may only be reported as legacy; every entry at a current template
    version must replay identically.
    """
    problems: list[str] = []
    semantics = jp.REPLAY_SEMANTICS
    if semantics["regenerates_model_output"] is not False or semantics["may_call_model"] is not False:
        problems.append("replay semantics allow regeneration")
    damaged = {"task": "T1_factor_visibility", "input_sha256": "x" * 64,
               "prompt_template_version": "v1", "temperature": 0.0, "seed": 1,
               "model_tag": jp.MODEL_TAG, "parsed_output": {}, "wall_clock": 0.1}
    try:
        jp.replay_score(damaged, lambda raw: ({}, False, "no raw"))
        problems.append("missing raw_output did not raise ReplayUnavailable")
    except jp.ReplayUnavailable:
        pass

    sys.path.insert(0, str(jp.LOCAL_ROOT))
    from local_inference import tasks  # noqa: PLC0415 - local, stdlib-only module
    entries = []
    with open(jp.COST_LEDGER_PATH, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    missing_fields = sum(1 for e in entries
                         if not all(field in e for field in jp.REQUIRED_LEDGER_FIELDS))

    in_scope_matches = 0
    in_scope_mismatches = []
    legacy = []
    for entry in entries:
        spec = tasks.TASK_SPECS.get(entry.get("task"))
        compat = jp.replay_parser_compatible(entry)
        if spec is None:
            in_scope_mismatches.append({"task": entry.get("task"), "problem": "unknown task"})
            continue
        payload = jp.replay_score(entry, spec.parse)
        if compat["parser_compatible"]:
            if payload["parsed_matches_ledger"]:
                in_scope_matches += 1
            else:
                in_scope_mismatches.append({
                    "task": entry["task"], "template": entry.get("prompt_template_version"),
                    "replayed": payload["replayed_parsed"], "stored": entry.get("parsed_output")})
        else:
            legacy.append({"task": entry["task"],
                           "template": entry.get("prompt_template_version"),
                           "replay_agrees": payload["parsed_matches_ledger"],
                           "note": compat["legacy_note"]})

    declared = {(t, v) for t, versions in jp.TEMPLATE_VERSION_PARSER_INCOMPATIBLE.items()
                for v in versions}
    undeclared = [row for row in legacy if (row["task"], row["template"]) not in declared]
    if missing_fields:
        problems.append(f"{missing_fields} ledger entries miss required fields")
    if in_scope_mismatches:
        problems.append(f"{len(in_scope_mismatches)} current-version replays disagree with the ledger")
    if undeclared:
        problems.append(f"{len(undeclared)} legacy-version mismatches are not declared in "
                        f"TEMPLATE_VERSION_PARSER_INCOMPATIBLE")
    if not declared:
        problems.append("no legacy parser policy declared")
    return not problems, {
        "entries": len(entries),
        "current_version_entries": in_scope_matches + len(in_scope_mismatches),
        "current_version_replay_matches": in_scope_matches,
        "current_version_mismatches": in_scope_mismatches[:3],
        "legacy_entries": len(legacy),
        "legacy_by_template": {k: sum(1 for r in legacy if r["template"] == k)
                               for k in sorted({r["template"] for r in legacy})},
        "legacy_policy": {t: sorted(v) for t, v in jp.TEMPLATE_VERSION_PARSER_INCOMPATIBLE.items()},
        "missing_field_entries": missing_fields,
        "regenerates_model_output": semantics["regenerates_model_output"],
        "problems": problems,
    }


def _ok_record() -> dict[str, Any]:
    return {f: 0 for f in jp.RECORD_FIELDS}


def check_v11() -> tuple[bool, Any]:
    salt = "s" * 32
    clean_items = {
        "T1_factor_visibility": {"passage": "The docket records four runs off the bat."},
        "T2_naturalness": {"natural_text": "Four runs were scored.", "degraded_text":
                           "Four runs were were scored.", "clean_position": "a"},
        "S1_span_topic": {"span_text": "Four runs were scored off the bat."},
        "C1_cert_sentence_consistency": {"sentence": "The batter scored four runs.",
                                         "record": _ok_record()},
    }
    problems: list[str] = []
    built = {}
    for task, item in clean_items.items():
        payload = dict(item)
        payload["instance_id"] = "match_0003"
        payload["scenario_family"] = "L3_NB_LBW"
        payload["level"] = 3
        payload["difficulty_vector"] = {"x": 1}
        payload["private_gold"] = {"answer": "hidden"}
        try:
            packet = jp.build_blind_packet(payload, task, salt)
        except jp.BlindPacketViolation as exc:
            problems.append(f"{task}: clean item rejected: {exc}")
            continue
        built[task] = packet
        if jp.audit_packet(packet):
            problems.append(f"{task}: built packet fails its own audit")
        serialised = jp.canonical_json(packet["payload"])
        for needle in ("match_0003", "L3_NB_LBW", "private_gold", "difficulty_vector",
                       "scenario_family"):
            if needle in serialised:
                problems.append(f"{task}: leaked {needle!r} into the packet")

    attacks = {
        "match_id_in_text": ({"passage": "as in match_0021 the batter scored four"},
                             "T1_factor_visibility"),
        "family_in_text": ({"passage": "family L5_RUNOUT_LATER_BOUNDARY says four"},
                          "T1_factor_visibility"),
        "level_in_text": ({"passage": "level L3 dossier"}, "T1_factor_visibility"),
        "difficulty_word": ({"passage": "this passage is harder by design, dose 2"},
                            "T1_factor_visibility"),
        "winpath": ({"span_text": "see C:\\VETT\\dataset\\x.json"}, "S1_span_topic"),
        "inner_file": ({"span_text": "from private_gold.json row 4"}, "S1_span_topic"),
        "r28_item_id": ({"passage": "see item r28q_0001 for this row"}, "T1_factor_visibility"),
        "r28_heldout_id": ({"passage": "held-out twin r28h_0005 says otherwise"},
                           "T1_factor_visibility"),
        "r28_family_id": ({"passage": "family rfam_83faedd9516b governs this row"},
                          "T1_factor_visibility"),
        "r28_span_id": ({"span_text": "span r28fact_446afd688a87582ab949 supports it"},
                        "S1_span_topic"),
        "r28_rule_id": ({"span_text": "rule r28rule_e2e38c24dc261b9ef56b applies"},
                        "S1_span_topic"),
        "r28_bind_id": ({"span_text": "binding r28bind_abc123 covers it"}, "S1_span_topic"),
        "r28_masked_id": ({"span_text": "masked cell r28masked_aa11"}, "S1_span_topic"),
        "r28_revpolicy_id": ({"span_text": "policy r28revpolicy_ff00 chooses 18:25"},
                             "S1_span_topic"),
        "r28_conflict_id": ({"span_text": "conflict r28conflict_9debe0b6fb7e7f71ed8d"},
                            "S1_span_topic"),
        "record_extra_field": ({"sentence": "x", "record": {**_ok_record(), "gold": 1}},
                               "C1_cert_sentence_consistency"),
        "record_missing_field": ({"sentence": "x", "record": {"batter_runs": 1}},
                                 "C1_cert_sentence_consistency"),
        "bad_position": ({"natural_text": "a", "degraded_text": "b", "clean_position": "c"},
                         "T2_naturalness"),
        "missing_field": ({"passage": None}, "T1_factor_visibility"),
    }
    for name, (item, task) in attacks.items():
        payload = dict(item)
        payload["instance_id"] = "match_0009"
        try:
            jp.build_blind_packet(payload, task, salt)
        except (jp.BlindPacketViolation, TypeError, ValueError):
            continue
        problems.append(f"attack {name} was NOT blocked")
    # unknown task and short salt must be refused
    for label, kwargs in (("unknown_task", {"task": "D1_12_field_record_derivation",
                                            "salt": salt}),
                          ("short_salt", {"task": "T1_factor_visibility", "salt": "short"})):
        item = {"passage": "x", "instance_id": "i1"}
        try:
            jp.build_blind_packet(item, kwargs["task"], kwargs["salt"])
        except jp.BlindPacketViolation:
            continue
        problems.append(f"{label} was NOT blocked")
    return not problems, {"built": sorted(built), "attacks": len(attacks),
                          "problems": problems}


def check_v12() -> tuple[bool, Any]:
    salt = "t" * 32
    problems: list[str] = []
    record = {"batter_runs": "4", "bowler_runs": 0, "counts_in_over": "1",
              "delivery_status": "LEGAL", "dismissal": "NONE", "ledger.BATTER": 4.0,
              "ledger.BYE": 0, "ledger.LEG_BYE": 0, "ledger.NO_BALL_EXTRA": 0,
              "ledger.PENALTY": 0, "ledger.WIDE_EXTRA": 0, "total_runs": "4"}
    packet = jp.build_blind_packet({"sentence": "x", "record": record,
                                   "instance_id": "i2"},
                                  "C1_cert_sentence_consistency", salt)
    canonical = packet["payload"]["record"]
    if list(canonical) != sorted(jp.RECORD_FIELDS):
        problems.append("record keys are not canonically sorted")
    if canonical["batter_runs"] != 4 or canonical["ledger.BATTER"] != 4:
        problems.append("numeric strings/floats were not narrowed to int")
    if packet["contains_answer"] is not True:
        problems.append("C1 contains_answer is not True")
    for task, item in (("T1_factor_visibility", {"passage": "x"}),
                       ("S1_span_topic", {"span_text": "x"}),
                       ("T2_naturalness", {"natural_text": "a", "degraded_text": "b",
                                           "clean_position": "b"})):
        pkt = jp.build_blind_packet({**item, "instance_id": "i3"}, task, salt)
        if pkt["contains_answer"] is not False:
            problems.append(f"{task}: contains_answer must be False")
        if any(field.startswith("ledger.") for field in pkt["payload"]):
            problems.append(f"{task}: payload leaked record fields")
    # handle stability & salt sensitivity
    a = jp.build_blind_packet({"passage": "x", "instance_id": "i4"}, "T1_factor_visibility", salt)
    b = jp.build_blind_packet({"passage": "x", "instance_id": "i4"}, "T1_factor_visibility", salt)
    c = jp.build_blind_packet({"passage": "x", "instance_id": "i4"}, "T1_factor_visibility", "u" * 32)
    if a["item_handle"] != b["item_handle"]:
        problems.append("handle is not stable within a run")
    if a["item_handle"] == c["item_handle"]:
        problems.append("handle does not depend on the salt")
    return not problems, {"canonical_record": canonical, "handle": a["item_handle"],
                          "salt_sensitive": a["item_handle"] != c["item_handle"],
                          "problems": problems}


def check_v13() -> tuple[bool, Any]:
    cases = {
        "n_below_30": jp.gate_capability(task="X", ruler="local", n=29, agreement=1.0),
        "unmeasured": jp.gate_capability(task="X", ruler="local", n=None, agreement=None),
        "below_threshold": jp.gate_capability(task="X", ruler="local", n=30, agreement=0.849),
        "at_threshold": jp.gate_capability(task="X", ruler="local", n=30, agreement=0.85),
        "matrix_deny": jp.gate_capability(task="X", ruler="local", n=30, agreement=0.99,
                                          matrix_verdict="DENY"),
        "cloud_t3_n12": jp.gate_capability(task="T3_adjudication", ruler="cloud", n=12,
                                           agreement=0.99),
        "cloud_n30": jp.gate_capability(task="T3_adjudication", ruler="cloud", n=30,
                                        agreement=0.91),
        "cloud_below": jp.gate_capability(task="T3_adjudication", ruler="cloud", n=30,
                                          agreement=0.89),
        "local_repeat_low": jp.gate_capability(task="T2_naturalness", ruler="local", n=30,
                                               agreement=0.95, repeat_pairs=10,
                                               repeat_agreement=0.5),
    }
    expect = {"n_below_30": "DENY", "unmeasured": "DENY", "below_threshold": "DENY",
              "at_threshold": "ALLOW", "matrix_deny": "DENY", "cloud_t3_n12": "DENY",
              "cloud_n30": "ALLOW", "cloud_below": "DENY", "local_repeat_low": "DENY"}
    problems = [f"{name}: {cases[name]['verdict']} != {expect[name]}"
                for name in expect if cases[name]["verdict"] != expect[name]]
    if cases["cloud_t3_n12"].get("label") != "DESCRIPTIVE_ONLY":
        problems.append("cloud n=12 is not labelled DESCRIPTIVE_ONLY")
    return not problems, {name: {"verdict": cases[name]["verdict"],
                                 "reason_code": cases[name]["reason_code"]}
                          for name in cases} | {"problems": problems}


def check_v14() -> tuple[bool, Any]:
    problems: list[str] = []
    cases = {}
    for task, cap in (("T1_factor_visibility", 3000), ("T2_naturalness", 2000),
                      ("S1_span_topic", 1000), ("C1_cert_sentence_consistency", 2000)):
        route = jp.assert_local_allowed(task, tokens=cap)
        cases[task] = {"cap": cap, "accepted_at_cap": route["verdict"]}
        for label, tokens in (("over_task_cap", cap + 1), ("over_hard_cap", 8193)):
            try:
                jp.assert_local_allowed(task, tokens=tokens)
                problems.append(f"{task}: {label} ({tokens}) was accepted")
            except jp.InputCapExceeded:
                cases[task][label] = "InputCapExceeded"
            except jp.ProtocolError as exc:
                problems.append(f"{task}: {label} raised {type(exc).__name__} instead")
        if cap > jp.HARD_INPUT_CAP_TOKENS:
            problems.append(f"{task}: task cap {cap} exceeds the hard ceiling")
    # a prompt-shaped oversize input must also be refused (estimator path)
    big = "x" * (3 * (jp.HARD_INPUT_CAP_TOKENS + 5))
    try:
        jp.assert_local_allowed("T1_factor_visibility", prompt=big)
        problems.append("oversize prompt was accepted")
    except jp.InputCapExceeded:
        cases["prompt_path"] = "InputCapExceeded"
    # DENY tasks must raise, and the exception type must match the reason class:
    # every static DENY raises TaskDenied except R1, which raises the more specific
    # CapabilityBelowThreshold (its DENY comes from a measurement, not a role rule).
    expected_exc = {"R1_readability": jp.CapabilityBelowThreshold}
    for task in jp.denied_local_tasks():
        want = expected_exc.get(task, jp.TaskDenied)
        try:
            jp.assert_local_allowed(task, tokens=10)
            problems.append(f"{task}: DENY task was accepted")
        except want:
            cases[f"deny:{task}"] = want.__name__
        except jp.ProtocolError as exc:
            problems.append(f"{task}: raised {type(exc).__name__}, expected {want.__name__}")
    return not problems, {"cases": cases, "problems": problems}


def _baseline_block(overrides: Mapping[str, Any] | None = None) -> dict[str, Any]:
    block = {
        "informative_field_accuracy": 0.45,
        "record_exact": 0.10,
        "n_items": 320, "n_families": 320, "n_distinct_records": 320,
        "baselines": {
            "constant_prior": {"reference_rate": 0.5288888888888889, "same_set_rate": 0.55,
                               "status": "MEASURED"},
            "question_text_tfidf_logreg": {"reference_rate": 0.5422222222222223,
                                           "same_set_rate": 0.501, "status": "MEASURED"},
            "anchor_mode": {"reference_rate": 0.7333333333333333, "same_set_rate": 0.72,
                            "status": "MEASURED"},
            "anchor_record_exact": {"reference_rate": 0.32, "same_set_rate": 0.30,
                                    "status": "MEASURED"},
        },
    }
    if overrides:
        block = {**block, **overrides}
    return block


def check_v15() -> tuple[bool, Any]:
    problems: list[str] = []
    cases: dict[str, str] = {}
    good = jp.require_baseline_trio(_baseline_block())
    cases["complete"] = good["status"]
    if good["status"] != "PASS":
        problems.append(f"complete report returned {good['status']}")

    missing = _baseline_block({"baselines": {
        "constant_prior": {"reference_rate": 0.5288888888888889, "same_set_rate": 0.55},
        "anchor_mode": {"reference_rate": 0.7333333333333333, "same_set_rate": 0.72},
        "anchor_record_exact": {"reference_rate": 0.32, "same_set_rate": 0.30}}})
    try:
        jp.require_baseline_trio(missing)
        problems.append("missing question-text baseline was accepted")
    except jp.BaselineTrioMissing:
        cases["missing_one"] = "rejected"

    single = _baseline_block({"baselines": {
        "constant_prior": {"reference_rate": 0.5288888888888889, "same_set_rate": 0.55},
        "anchor_record_exact": {"reference_rate": 0.32, "same_set_rate": 0.30}}})
    try:
        jp.require_baseline_trio(single)
        problems.append("single-baseline report was accepted")
    except jp.BaselineTrioMissing:
        cases["single_baseline"] = "rejected"

    no_exact = _baseline_block({"baselines": {
        "constant_prior": {"reference_rate": 0.5288888888888889, "same_set_rate": 0.55},
        "question_text_tfidf_logreg": {"reference_rate": 0.5422222222222223,
                                       "same_set_rate": 0.501},
        "anchor_mode": {"reference_rate": 0.7333333333333333, "same_set_rate": 0.72}}})
    try:
        jp.require_baseline_trio(no_exact)
        problems.append("report without record-exact baseline was accepted")
    except jp.BaselineTrioMissing:
        cases["missing_exact"] = "rejected"

    failing = jp.require_baseline_trio(_baseline_block({"informative_field_accuracy": 0.74}))
    cases["above_anchor"] = failing["status"]
    if failing["status"] != "FAIL":
        problems.append(f"report above anchor returned {failing['status']}")

    untested_block = _baseline_block()
    untested_block["baselines"] = dict(untested_block["baselines"])
    untested_block["baselines"]["anchor_mode"] = {"reference_rate": 0.7333333333333333,
                                                 "same_set_rate": None,
                                                 "status": "UNTESTED"}
    untested = jp.require_baseline_trio(untested_block)
    cases["untested_baseline"] = untested["status"]
    if untested["status"] != "UNTESTED":
        problems.append(f"unmeasured same-set baseline returned {untested['status']}")
    return not problems, {"cases": cases, "problems": problems,
                          "thresholds": {b["id"]: b["display"] for b in jp.BASELINE_TRIO}
                          | {jp.RECORD_EXACT_BASELINE["id"]: jp.RECORD_EXACT_BASELINE["display"]}}


def check_v16() -> tuple[bool, Any]:
    baselines = jp.load_json(jp.BASELINES_PATH)["baselines"]
    pairs = {
        "constant_prior": ("constant_75_to_25", 0.5288888888888889, "field_accuracy_informative"),
        "question_text_tfidf_logreg": ("tfidf_logreg_question_text_75_to_25",
                                       0.5422222222222223, "field_accuracy_informative"),
        "anchor_mode": ("anchor_classifier_75_to_25", 0.7333333333333333,
                        "field_accuracy_informative"),
    }
    problems: list[str] = []
    detail = {}
    for entry in jp.BASELINE_TRIO:
        block, expected, path = pairs[entry["id"]]
        observed = baselines[block][path]["rate"]
        detail[entry["id"]] = {"expected": expected, "observed": observed,
                               "source": entry["source"]}
        if observed != expected or entry["reference_rate"] != expected:
            problems.append(f"{entry['id']}: {observed} != {expected}")
    exact = baselines["anchor_classifier_75_to_25"]["record_exact"]["rate"]
    detail[jp.RECORD_EXACT_BASELINE["id"]] = {"expected": 0.32, "observed": exact}
    if exact != 0.32 or jp.RECORD_EXACT_BASELINE["reference_rate"] != 0.32:
        problems.append(f"record exact {exact} != 0.32")
    return not problems, {"baselines": detail, "problems": problems}


def check_v17() -> tuple[bool, Any]:
    problems: list[str] = []
    cases: dict[str, Any] = {}
    good = jp.check_effective_n({"n_items": 320, "n_families": 320,
                                 "n_distinct_records": 320, "independent_units": 320,
                                 "pairing": "item", "bootstrap_unit": "family"},
                                comparison="r28")
    cases["r28_valid"] = good["ok"]
    if not good["ok"]:
        problems.append(f"valid R28 block flagged: {good['violations']}")

    def violations_of(block, comparison):
        return [v["code"] for v in jp.check_effective_n(block, comparison=comparison)["violations"]]

    cases["field_pseudo_n"] = violations_of(
        {"n_items": 320, "n_families": 320, "n_distinct_records": 320,
         "independent_units": 2880, "pairing": "item"}, "r28")
    cases["twin_as_independent"] = violations_of(
        {"n_items": 320, "n_families": 320, "n_distinct_records": 320,
         "independent_units": 640, "pairing": "item"}, "r28")
    cases["r2615_not_clustered"] = violations_of(
        {"n_items": 100, "n_families": 100, "n_distinct_records": 16,
         "bootstrap_unit": "item"}, "r26_15")
    cases["cross_not_exploratory"] = violations_of(
        {"n_items": 320, "n_families": 320, "n_distinct_records": 320}, "cross")
    cases["cross_family_split"] = violations_of(
        {"n_items": 320, "n_families": 320, "n_distinct_records": 320,
         "split_has_cross_family": True}, "r28")
    cases["missing_fields"] = violations_of({"n_items": 320}, "r28")

    expect = {
        "field_pseudo_n": "EN5",
        "twin_as_independent": "EN5",
        "r2615_not_clustered": "EN1",
        "cross_not_exploratory": "EN6",
        "cross_family_split": "EN4",
        "missing_fields": "EN2",
    }
    for name, code in expect.items():
        if code not in cases[name]:
            problems.append(f"{name}: expected {code}, got {cases[name]}")
    if "EN3" not in cases["r2615_not_clustered"]:
        problems.append("R26.15 comparison with item-level bootstrap did not raise EN3")
    return not problems, {"cases": cases, "problems": problems}


def check_v18() -> tuple[bool, Any]:
    problems: list[str] = []
    event = jp.make_degraded(task="R1_readability", reason_code="CAPABILITY_BELOW_THRESHOLD",
                             reason="agreement 0.6667 on n=30", fallback_used="flesch_reading_ease_band",
                             affected_items=["R1-1"], scope="local", source="t17")
    problems.extend(jp.validate_degraded(event))
    missing_required = [f for f in ("task", "reason_code", "fallback_used", "affected_items")
                        if f not in event]
    if missing_required:
        problems.append(f"event misses {missing_required}")
    for bad in ({"reason_code": "MADE_UP_CODE"}, {"affected_items": []},
                {"fallback_used": ""}, {"task": ""}, {"scope": "nowhere"}):
        try:
            jp.make_degraded(**{"task": "T1_factor_visibility",
                                "reason_code": "TASK_DENIED", "fallback_used": "x",
                                "affected_items": ["a"], **bad})
            problems.append(f"bad event {bad} was accepted")
        except ValueError:
            continue
    broken = dict(event)
    broken.pop("affected_items")
    if not jp.validate_degraded(broken):
        problems.append("validate_degraded accepted an event without affected_items")
    return not problems, {"event_fields": sorted(event), "reason_codes": len(jp.JUDGE_REASON_CODES),
                          "required": list(jp.DEGRADED_REQUIRED_FIELDS), "problems": problems}


def check_v19() -> tuple[bool, Any]:
    path = jp.SELFTEST_DEGRADED_PATH
    events = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    problems: list[str] = []
    normalised = []
    for event in events:
        try:
            upgraded = jp.normalize_degraded(event)
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{event.get('reason_code')}: {type(exc).__name__}: {exc}")
            continue
        problems.extend(jp.validate_degraded(upgraded))
        normalised.append({"task": upgraded["task"], "reason_code": upgraded["reason_code"],
                           "fallback_used": upgraded["fallback_used"],
                           "affected_items": upgraded["affected_items"]})
    # protocol.json's published example must validate too
    protocol = load_protocol()
    problems.extend(jp.validate_degraded(protocol["degraded"]["example"]))
    return not problems, {"source": path.relative_to(RUN_ROOT).as_posix(),
                          "events": len(events), "normalised": normalised,
                          "problems": problems[:6]}


def check_v20() -> tuple[bool, Any]:
    problems: list[str] = []
    cases: dict[str, str] = {}
    ok_t3 = jp.assert_cloud_allowed("T3_adjudication", 12)
    cases["T3_12"] = ok_t3["verdict"]
    ok_t1 = jp.assert_cloud_allowed("T1_cross_check", 24, used_calls=0)
    cases["T1_24"] = ok_t1["verdict"]
    ok_t2 = jp.assert_cloud_allowed("T2_cross_check", 16)
    cases["T2_16"] = ok_t2["verdict"]
    for label, kind, n, used in (("T3_13", "T3_adjudication", 13, 0),
                                 ("T1_25", "T1_cross_check", 25, 0),
                                 ("total_over_80", "T1_cross_check", 24, 70)):
        try:
            jp.assert_cloud_allowed(kind, n, used_calls=used)
            problems.append(f"{label} was accepted")
        except jp.CloudBudgetExceeded:
            cases[label] = "rejected"
    for label, kind in (("unknown_kind", "T1_full_run"), ("zero_calls", "T1_cross_check")):
        try:
            jp.assert_cloud_allowed(kind, 0 if label == "zero_calls" else 1)
            problems.append(f"{label} was accepted")
        except jp.ProtocolError:
            cases[label] = "rejected"
    for provider in ("openai", "https://api.example.com", "anthropic-claude"):
        try:
            jp.assert_cloud_allowed("T3_adjudication", 1, provider=provider)
            problems.append(f"provider {provider} was accepted")
        except jp.PaidProviderForbidden:
            cases[f"provider:{provider}"] = "rejected"
    workload = jp.workload_split()
    if workload["cloud"]["calls_total"] > jp.CLOUD_TOTAL_CALL_CAP:
        problems.append("planned cloud calls exceed the 80 cap")
    return not problems, {"cases": cases, "planned_calls": workload["cloud"]["calls_total"],
                          "cap": jp.CLOUD_TOTAL_CAP if hasattr(jp, "CLOUD_TOTAL_CAP")
                          else jp.CLOUD_TOTAL_CALL_CAP,
                          "local_calls": workload["local"]["calls_total"], "problems": problems}


def check_v21() -> tuple[bool, Any]:
    import re
    protocol = load_protocol()
    md = PROTOCOL_MD_PATH.read_text(encoding="utf-8")
    md_ids = set(re.findall(r"R-[A-Z]+\d+", md))
    json_ids = {r["id"] for r in protocol["rules"]}
    code_ids = set(jp.RULE_IDS)
    problems: list[str] = []
    if not (md_ids == json_ids == code_ids):
        problems.append(f"id sets differ: md-only={sorted(md_ids - json_ids)} "
                        f"json-only={sorted(json_ids - md_ids)} "
                        f"code-only={sorted(code_ids - json_ids)}")
    if protocol["protocol_id"] not in md:
        problems.append("PROTOCOL.md does not state the protocol id")
    for entry in protocol["verification"]["checklist"]:
        if entry["id"] not in md:
            problems.append(f"checklist item {entry['id']} missing from PROTOCOL.md")
    # the doc must carry the measured numbers it claims to be based on (doc/data drift guard)
    required_strings = ("0.9333", "0.6667", "0.1672", "52.89%", "54.22%", "73.33%",
                        "32%", "8192", "n ≥ 30", "affected_items", "fallback_used",
                        "model_digest", "343afde4")
    missing_strings = [s for s in required_strings if s not in md]
    if missing_strings:
        problems.append(f"PROTOCOL.md is missing measured strings {missing_strings}")
    amendments = DESIGN_ROOT / "protocol_amendments.jsonl"
    if not amendments.exists():
        problems.append("protocol_amendments.jsonl is missing")
    else:
        for line_no, line in enumerate(amendments.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                problems.append(f"protocol_amendments.jsonl line {line_no} is not JSON: {exc}")
    return not problems, {"md_rules": len(md_ids), "json_rules": len(json_ids),
                          "code_rules": len(code_ids),
                          "required_strings": len(required_strings),
                          "missing_strings": missing_strings,
                          "amendments_log": str(amendments.name), "problems": problems}


def check_v22() -> tuple[bool, Any]:
    protocol = load_protocol()
    problems: list[str] = []
    detail: dict[str, Any] = {}
    for name, expected in protocol["bindings"].items():
        if name == "r26_15_dataset":
            continue
        path = jp.WORKSPACE_ROOT / expected["path"]
        actual = sha256_file(path) if path.exists() else None
        detail[name] = {"expected": expected["sha256"], "actual": actual}
        if expected["sha256"] is None or actual != expected["sha256"]:
            problems.append(f"binding {name} changed: {actual} != {expected['sha256']}")

    # protocol.json must still equal a fresh build from the live authorities
    rebuilt = bp.build(protocol["frozen_at_utc"])
    if json.dumps(rebuilt, ensure_ascii=False, sort_keys=True) != \
            json.dumps(protocol, ensure_ascii=False, sort_keys=True):
        problems.append("protocol.json differs from a rebuild (hand-edited or stale)")
    detail["rebuild_equal"] = not any("rebuild" in p for p in problems)

    # freeze digests (when frozen) must match the current bytes
    if FREEZE_PATH.exists():
        freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
        for name, expected in (freeze.get("artifacts") or {}).items():
            path = jp.WORKSPACE_ROOT / expected["path"]
            actual = sha256_file(path) if path.exists() else None
            detail[f"freeze:{name}"] = {"expected": expected["sha256"], "actual": actual}
            if actual != expected["sha256"]:
                problems.append(f"frozen artefact {name} changed after the freeze")

    # R26.15 must be byte-identical to the t1 freeze
    r26 = jp.r26_15_tree_aggregate()
    detail["r26_15"] = r26
    if r26["file_count"] != jp.R26_15_EXPECTED_FILES:
        problems.append(f"R26.15 file_count {r26['file_count']} != {jp.R26_15_EXPECTED_FILES}")
    if r26["total_bytes"] != jp.R26_15_EXPECTED_BYTES:
        problems.append(f"R26.15 total_bytes {r26['total_bytes']} != {jp.R26_15_EXPECTED_BYTES}")
    if r26["aggregate_sha256"] != jp.R26_15_EXPECTED_AGGREGATE:
        problems.append(f"R26.15 aggregate {r26['aggregate_sha256']} != "
                        f"{jp.R26_15_EXPECTED_AGGREGATE}")
    return not problems, {**detail, "problems": problems}


CHECKS: tuple[tuple[str, str, Callable[..., tuple[bool, Any]], bool], ...] = (
    ("V1", "protocol 任务集合 == routing_card 任务集合（13）", check_v1, True),
    ("V2", "ALLOW 恰四项且与矩阵 verdict 一致", check_v2, True),
    ("V3", "ALLOW 的 agreement/n/threshold 与 card+matrix 逐值相等且过门", check_v3, True),
    ("V4", "DENY 的 reason_code/deny_reason/evidence 与 card 逐值相等", check_v4, True),
    ("V5", "DENY 依据分级：7 MEASURED 有数 / 2 POLICY 不造数", check_v5, True),
    ("V6", "R1 证据完整（0.6667 / n=30 / ρ=-0.1672 / discrimination_ok=false / FRE）", check_v6, True),
    ("V7", "硬上限 8192 与 card 一致且 never truncate", check_v7, True),
    ("V8", "缓存键确定性与四维敏感性", check_v8, False),
    ("V9", "v2 键含 model_digest 且 ≠ v1 键", check_v9, False),
    ("V10", "真实账本 raw_output 重放解析 100% 一致且不重生成", check_v10, False),
    ("V11", "盲包白名单执行：干净通过 / 注入阻断", check_v11, False),
    ("V12", "C1 contains_answer=true；记录 canonical 化", check_v12, False),
    ("V13", "n<30 / 未测 / 低于阈值 → DENY", check_v13, False),
    ("V14", "超任务上限与超 8192 硬顶均抛出、不截断", check_v14, False),
    ("V15", "三基线缺失（含单基线）拒绝；完整报告 PASS/FAIL/UNTESTED", check_v15, False),
    ("V16", "三基线参考值与 BASELINES.json 逐值相等", check_v16, False),
    ("V17", "有效 n：320/320/320 通过；字段级/640/跨族/R26.15 违规", check_v17, False),
    ("V18", "DEGRADED 必填四字段 + 封闭原因码", check_v18, False),
    ("V19", "t18 真实事件可无损归一化", check_v19, False),
    ("V20", "云端 24/16/12 与总 80 上限；外部 provider 拒绝", check_v20, False),
    ("V21", "PROTOCOL.md 与 protocol.json 的 rule id 集合完全一致", check_v21, False),
    ("V22", "绑定摘要未变 + 重建一致 + R26.15 聚合 == 343afde4…51bd", check_v22, False),
)


# ---------------------------------------------------------------------------
# freeze / run
# ---------------------------------------------------------------------------
def freeze() -> int:
    artifacts = {}
    for name, path in FROZEN_ARTIFACTS.items():
        if not path.exists():
            print(f"[FAIL] cannot freeze missing artefact {name}: {path}", file=sys.stderr)
            return 4
        artifacts[name] = {"path": path.relative_to(jp.WORKSPACE_ROOT).as_posix(),
                           "bytes": path.stat().st_size,
                           "sha256": sha256_file(path)}
    protocol = load_protocol()
    freeze_obj = {
        "schema_version": "vett-judge-protocol-freeze/v1",
        "protocol_id": protocol["protocol_id"],
        "version": protocol["version"],
        "frozen_at_utc": jp.utc_now(),
        "protocol_frozen_at_utc": protocol["frozen_at_utc"],
        "artifacts": artifacts,
        "digests": {
            "rules": jp.sha256_json(protocol["rules"]),
            "allow_tasks": jp.sha256_json(protocol["rulers"]["local"]["allow"]),
            "deny_tasks": jp.sha256_json(protocol["rulers"]["local"]["deny"]),
            "blind_packet": jp.sha256_json(protocol["blind_packet"]),
            "cache_and_replay": jp.sha256_json(protocol["cache_and_replay"]),
            "confidence_floor": jp.sha256_json(protocol["confidence_floor"]),
            "baselines": jp.sha256_json(protocol["baselines"]),
            "effective_n": jp.sha256_json(protocol["effective_n"]),
            "degraded": jp.sha256_json(protocol["degraded"]),
            "cloud_ruler": jp.sha256_json(protocol["rulers"]["cloud"]),
        },
        "bindings": protocol["bindings"],
        "verification": {"checklist": [c["id"] for c in jp.VERIFICATION_CHECKLIST],
                         "count": len(jp.VERIFICATION_CHECKLIST)},
        "statement": (
            "冻结后本协议的任何字节改动都会被 protocol_verify.py --check 的 V22 检出："
            "改动者必须显式重新冻结并在 protocol_amendments 登记。"
        ),
    }
    FREEZE_PATH.write_text(json.dumps(freeze_obj, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
    lines = ["# VETT-R28 judge protocol — frozen artefacts (sha256)",
             f"# protocol_id {protocol['protocol_id']}  version {protocol['version']}",
             f"# frozen_at_utc {freeze_obj['frozen_at_utc']}"]
    for name, entry in artifacts.items():
        lines.append(f"{entry['sha256']}  {entry['path']}")
    SHA256_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"[ok] wrote {FREEZE_PATH.relative_to(RUN_ROOT).as_posix()}")
    print(f"[ok] wrote {SHA256_PATH.relative_to(RUN_ROOT).as_posix()}")
    for name, entry in artifacts.items():
        print(f"     {entry['sha256'][:16]}  {name}")
    return 0


def run_checks() -> int:
    RESULTS.clear()
    protocol = load_protocol()
    for check_id, description, fn, takes_protocol in CHECKS:
        if takes_protocol:
            guard(check_id, description, lambda fn=fn: fn(protocol))
        else:
            guard(check_id, description, fn)
    failed = [r for r in RESULTS if r["status"] != "passed"]
    result = {
        "schema_version": "vett-judge-protocol-verify/v1",
        "protocol_id": protocol["protocol_id"],
        "version": protocol["version"],
        "checked_at_utc": jp.utc_now(),
        "protocol_json_sha256": sha256_file(PROTOCOL_PATH),
        "protocol_md_sha256": sha256_file(PROTOCOL_MD_PATH),
        "checks": RESULTS,
        "summary": {"total": len(RESULTS), "passed": len(RESULTS) - len(failed),
                    "failed": len(failed), "ok": not failed},
        "failed_ids": [r["id"] for r in failed],
    }
    VERIFY_RESULT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8", newline="\n")
    print(f"\n[{'ok' if not failed else 'FAIL'}] {len(RESULTS) - len(failed)}/{len(RESULTS)} checks "
          f"passed; wrote {VERIFY_RESULT_PATH.relative_to(RUN_ROOT).as_posix()}")
    if failed:
        for item in failed:
            print(f"  - {item['id']}: {item.get('error') or json.dumps(item['evidence'], ensure_ascii=False)[:300]}")
        return 4
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="verify the frozen judge protocol")
    parser.add_argument("--freeze", action="store_true", help="write protocol_freeze.json + PROTOCOL.sha256")
    parser.add_argument("--check", action="store_true", help="run V1–V22")
    parser.add_argument("--json-only", action="store_true", help="suppress per-check stdout")
    args = parser.parse_args(argv)

    if not (args.freeze or args.check):
        parser.print_help()
        return 0
    if args.freeze:
        code = freeze()
        if code != 0:
            return code
    if args.check:
        return run_checks()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
