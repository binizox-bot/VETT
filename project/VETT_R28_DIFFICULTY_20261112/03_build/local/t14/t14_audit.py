"""t14 no-GPU audit: blind packets, T2 determinism, T1 stratified truth, route caps.

Run (no model calls, no GPU)::

    python t14_audit.py

Writes only under ``03_build/local/t14/evidence``.
"""
from __future__ import annotations

import collections
import hashlib
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

import judge_protocol as jp  # noqa: E402
from local_inference import corpus, service, tasks  # noqa: E402

import recon  # noqa: E402
import t14_runner as runner_mod  # noqa: E402

RUN_ID = "t14_main"
EVIDENCE = T14_ROOT / "evidence"
RUN_DIR = T14_ROOT / "runs" / RUN_ID
DATASET = runner_mod.DATASET


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(name: str, obj) -> Path:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE / name
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                    encoding="utf-8", newline="\n")
    return path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    config = load_json(RUN_DIR / "config.json")
    salt = str(config["blind_salt"])
    items = recon.load_dev_items()
    pairs = load_json(RUN_DIR / "t2_pairs.json")["pairs"]
    t1_analysis = load_json(RUN_DIR / "t1_analysis.json")["rows"]
    pairs_by_id = {p["item_id"]: p for p in pairs}

    # ---------------- blind packet audit ----------------
    packet_records = []
    packet_violations = []
    task_counts = collections.Counter()
    token_max = collections.Counter()
    route_problems = []
    for item in items:
        item_id = item["item_id"]
        handle = jp.make_item_handle(salt, item_id)
        bundle = recon.item_bundle(item)
        # T1
        selection = runner_mod.select_t1_passage(bundle, item)
        tv = str(jp.local_route_at_judge_time(runner_mod.T1_TASK)["template_version"])
        packet = jp.build_blind_packet({"passage": selection["passage"]},
                                       runner_mod.T1_TASK, salt, source_id=item_id,
                                       template_version=tv)
        violations = jp.audit_packet(packet)
        packet_records.append({"item_handle": handle, "task": runner_mod.T1_TASK,
                               "packet_id": packet["packet_id"],
                               "violations": len(violations)})
        task_counts["T1_packets"] += 1
        packet_violations.extend({"item_handle": handle, "task": runner_mod.T1_TASK,
                                  "violations": violations} for _ in [0] if violations)
        prompt = tasks.build_prompt(runner_mod.T1_TASK, packet["payload"])
        token_max["T1"] = max(token_max["T1"], service.estimate_tokens(prompt))
        try:
            jp.assert_local_allowed(runner_mod.T1_TASK, prompt=prompt)
        except Exception as exc:  # noqa: BLE001
            route_problems.append({"item_id": item_id, "task": runner_mod.T1_TASK,
                                   "error": f"{type(exc).__name__}: {exc}"})
        # S1
        s1 = runner_mod.select_s1_span(bundle)
        if corpus.PROVENANCE_SIGNAL_RE.search(s1["text"]):
            task_counts["S1_mechanical"] += 1
        else:
            tv = str(jp.local_route_at_judge_time(runner_mod.S1_TASK)["template_version"])
            packet = jp.build_blind_packet({"span_text": s1["text"]}, runner_mod.S1_TASK,
                                           salt, source_id=item_id, template_version=tv)
            violations = jp.audit_packet(packet)
            packet_records.append({"item_handle": handle, "task": runner_mod.S1_TASK,
                                   "packet_id": packet["packet_id"],
                                   "violations": len(violations)})
            task_counts["S1_packets"] += 1
            packet_violations.extend({"item_handle": handle, "task": runner_mod.S1_TASK,
                                      "violations": violations} for _ in [0] if violations)
            prompt = tasks.build_prompt(runner_mod.S1_TASK, packet["payload"])
            token_max["S1"] = max(token_max["S1"], service.estimate_tokens(prompt))
            try:
                jp.assert_local_allowed(runner_mod.S1_TASK, prompt=prompt)
            except Exception as exc:  # noqa: BLE001
                route_problems.append({"item_id": item_id, "task": runner_mod.S1_TASK,
                                       "error": f"{type(exc).__name__}: {exc}"})
        # T2
        pair = pairs_by_id[item_id]
        payload = {"natural_text": pair["natural_text"],
                   "degraded_text": pair["degraded_text"],
                   "clean_position": pair["clean_position"]}
        tv = str(jp.local_route_at_judge_time(runner_mod.T2_TASK)["template_version"])
        packet = jp.build_blind_packet(payload, runner_mod.T2_TASK, salt,
                                       source_id=item_id, template_version=tv)
        violations = jp.audit_packet(packet)
        packet_records.append({"item_handle": handle, "task": runner_mod.T2_TASK,
                               "packet_id": packet["packet_id"],
                               "violations": len(violations)})
        task_counts["T2_packets"] += 1
        packet_violations.extend({"item_handle": handle, "task": runner_mod.T2_TASK,
                                  "violations": violations} for _ in [0] if violations)
        prompt = tasks.build_prompt(runner_mod.T2_TASK, packet["payload"])
        token_max["T2"] = max(token_max["T2"], service.estimate_tokens(prompt))
        try:
            jp.assert_local_allowed(runner_mod.T2_TASK, prompt=prompt)
        except Exception as exc:  # noqa: BLE001
            route_problems.append({"item_id": item_id, "task": runner_mod.T2_TASK,
                                   "error": f"{type(exc).__name__}: {exc}"})

    packet_ids_digest = sha256_text("\n".join(
        sorted(r["packet_id"] for r in packet_records)))
    blind_audit = {
        "schema": "vett-r28-t14-blind-audit/v1",
        "generated_at": jp.utc_now(),
        "run_id": RUN_ID,
        "items": len(items),
        "tasks": dict(sorted(task_counts.items())),
        "packets_audited": len(packet_records),
        "violations": len(packet_violations),
        "violation_records": packet_violations[:20],
        "packet_ids_digest": packet_ids_digest,
        "token_max": dict(sorted(token_max.items())),
        "token_caps": {"T1": 3000, "S1": 1000, "T2": 2000},
        "route_problems": route_problems[:20],
        "salts_included": False,
        "command": "python t14_audit.py",
        "note": ("Every payload was built with judge_protocol.build_blind_packet "
                 "(the same audit runs inside it); jp.audit_packet was re-run explicitly. "
                 "Packet ids are reproducible from the private run salt; the salt is not "
                 "written outside runs/<run_id>/config.json."),
    }
    write_json("BLIND_PACKET_AUDIT.json", blind_audit)

    # ---------------- T2 determinism / replay ----------------
    replay_records = []
    replay_problems = []
    kind_counts = collections.Counter()
    positions = collections.Counter()
    word_min, word_max = 10**9, 0
    for pair in pairs:
        first = corpus.corrupt_text(pair["natural_text"], pair["corruptor"])
        second = corpus.corrupt_text(pair["natural_text"], pair["corruptor"])
        replay_equal = first == pair["degraded_text"]
        deterministic_equal = first == second
        sha_equal = sha256_text(first) == pair.get("degraded_sha256")
        words = len(pair["natural_text"].split())
        word_min = min(word_min, words)
        word_max = max(word_max, words)
        kind_counts[pair["corruptor"]] += 1
        positions[pair["clean_position"]] += 1
        record = {"item_id": pair["item_id"], "corruptor": pair["corruptor"],
                  "natural_sha256": pair["natural_sha256"],
                  "degraded_sha256": pair["degraded_sha256"],
                  "replay_equal": replay_equal,
                  "deterministic_equal": deterministic_equal,
                  "sha_equal": sha_equal,
                  "clean_position": pair["clean_position"]}
        replay_records.append(record)
        if not (replay_equal and deterministic_equal and sha_equal):
            replay_problems.append(record)
    determinism = {
        "schema": "vett-r28-t14-t2-determinism/v1",
        "generated_at": jp.utc_now(),
        "run_id": RUN_ID,
        "pairs": len(pairs),
        "all_replayable": all(r["replay_equal"] for r in replay_records),
        "all_deterministic_twice": all(r["deterministic_equal"] for r in replay_records),
        "all_sha_match": all(r["sha_equal"] for r in replay_records),
        "problems": replay_problems[:20],
        "corruptor_counts": dict(sorted(kind_counts.items())),
        "position_counts": dict(sorted(positions.items())),
        "position_balanced": positions.get("a") == 160 and positions.get("b") == 160,
        "natural_words_min": word_min,
        "natural_words_max": word_max,
        "command": "python t14_audit.py",
    }
    write_json("T2_DETERMINISM_AUDIT.json", determinism)

    # ---------------- T1 stratified truth ----------------
    class_counts = collections.Counter(str(r["truth_class"]) for r in t1_analysis)
    by_mech = collections.Counter((str(r["mechanism"]), str(r["truth_class"]))
                                  for r in t1_analysis)
    t18_pos = sum(1 for r in t1_analysis
                  if r["truth_class"] == "POS_OVERRIDE" and r["override_t18"])
    examples = collections.defaultdict(list)
    for row in t1_analysis:
        if len(examples[row["truth_class"]]) < 4:
            bundle = recon.item_bundle({i["item_id"]: i for i in items}[row["item_id"]])
            span = bundle["span_map"].get(row["span_id"], {})
            examples[row["truth_class"]].append({
                "item_id": row["item_id"], "mechanism": row["mechanism"],
                "dose": row["dose"], "selection_source": row["selection_source"],
                "span_id": row["span_id"], "role": row["role"],
                "text_head": (span.get("text") or "")[:220]})
    stratified = {
        "schema": "vett-r28-t14-t1-stratified-truth/v1",
        "generated_at": jp.utc_now(),
        "run_id": RUN_ID,
        "classes": dict(sorted(class_counts.items())),
        "required_min_per_class": 30,
        "all_classes_sufficient": all(class_counts.get(c, 0) >= 30 for c in
                                      ("POS_OVERRIDE", "NEG_PROVENANCE_ADJACENT", "NEG_PLAIN")),
        "class_x_mechanism": {f"{m}|{c}": n for (m, c), n in sorted(by_mech.items())},
        "t18_strict_override_hits_pos": t18_pos,
        "pos_override_n": class_counts.get("POS_OVERRIDE", 0),
        "examples": dict(examples),
        "construction": {
            "POS_OVERRIDE": "D2 dose>=2: revision_version with t18 override word "
                            "(else revision_policy); D3 dose>0: authority_policy",
            "NEG_PROVENANCE_ADJACENT": "D2 dose=1 temporal review lock; "
                                       "D1 dose>0 alias locator/bridge; D4 dose>0 distractor",
            "NEG_PLAIN": "fact span with no override / authority / provenance marker",
        },
        "command": "python t14_audit.py",
    }
    write_json("T1_STRATIFIED_TRUTH.json", stratified)

    summary = {
        "run_id": RUN_ID,
        "blind_packets": {"audited": len(packet_records),
                          "violations": len(packet_violations),
                          "tasks": dict(sorted(task_counts.items())),
                          "token_max": dict(sorted(token_max.items()))},
        "t2_determinism": {k: determinism[k] for k in
                           ("pairs", "all_replayable", "all_deterministic_twice",
                            "all_sha_match", "position_balanced", "corruptor_counts")},
        "t1_stratified": {"classes": dict(sorted(class_counts.items())),
                          "all_classes_sufficient": stratified["all_classes_sufficient"]},
        "route_problems": len(route_problems),
    }
    write_json("AUDIT_SUMMARY.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    if packet_violations or route_problems or replay_problems or not stratified["all_classes_sufficient"]:
        raise SystemExit(4)


if __name__ == "__main__":
    main()
