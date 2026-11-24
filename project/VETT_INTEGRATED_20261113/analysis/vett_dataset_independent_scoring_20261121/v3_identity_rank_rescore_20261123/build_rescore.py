import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


VERSION = "score-v3-identity-rank-recovery-20261123"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ANALYSIS = ROOT / "VETT_INTEGRATED_20261113" / "analysis"
WF = ANALYSIS / "vett_autonomous_20261117"
BATCHES = WF / "batches"
RUNS = WF / "runs"
SAMPLES_PATH = ANALYSIS / "attribution_followup" / "samples.json"

sys.path.insert(0, str(WF))
import vettlib as V  # noqa: E402


FULL_BATCHES = ["B228", "B229", "B230", "B231", "B232", "B233", "B234", "B235", "B247"]
DIAG_BATCHES = ["B243", "B244", "B245", "B246"]
MODELS = ["qwen2.5:7b-instruct-q4_K_M", "llama3.1:8b", "gemma2:9b"]
ARMS = ("N0", "N1", "N2")


class Pairs(list):
    """Marker type used to retain duplicate JSON object keys."""


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_name(value):
    if value is None:
        return None
    s = str(value).strip()
    while re.search(r"\s*\([^)]*\)\s*$", s):
        s = re.sub(r"\s*\([^)]*\)\s*$", "", s).strip()
    return re.sub(r"\s+", " ", s).casefold()


def int_value(value):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    try:
        return int(str(value).strip().replace(",", ""))
    except Exception:
        return None


def canonical_scalar(value):
    if value is None:
        return ("null", None)
    if isinstance(value, bool):
        return ("bool", value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return ("number", float(value))
    return ("string", re.sub(r"\s+", " ", str(value).strip()).casefold())


def decode_json_string(token):
    try:
        return json.loads('"' + token + '"')
    except Exception:
        return token.replace('\\"', '"').replace("\\\\", "\\")


SCALAR_PAIR_RE = re.compile(
    r'"(?P<key>(?:\\.|[^"\\])*)"\s*:\s*'
    r'(?P<value>"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|true|false|null)',
    re.I,
)


def parse_scalar_token(token):
    if token.startswith('"'):
        return decode_json_string(token[1:-1])
    low = token.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low == "null":
        return None
    try:
        return float(token) if any(c in token for c in ".eE") else int(token)
    except Exception:
        return token


def collect_pairs(obj, out):
    if isinstance(obj, Pairs):
        for key, value in obj:
            if isinstance(value, Pairs):
                collect_pairs(value, out)
            elif isinstance(value, list):
                for item in value:
                    collect_pairs(item, out)
            else:
                out.append((str(key), value))
    elif isinstance(obj, list):
        for item in obj:
            collect_pairs(item, out)


def pairs_duplicates(obj):
    duplicates = []
    if isinstance(obj, Pairs):
        counts = Counter(str(k) for k, _ in obj)
        duplicates.extend(k for k, n in counts.items() if n > 1)
        for _, value in obj:
            duplicates.extend(pairs_duplicates(value))
    elif isinstance(obj, list):
        for item in obj:
            duplicates.extend(pairs_duplicates(item))
    return duplicates


def strict_fields_from_root(root):
    if not isinstance(root, Pairs):
        return None, "root_not_object"
    root_keys = [str(k) for k, _ in root]
    if root_keys != ["fields"]:
        return None, "root_must_contain_only_fields"
    fields_obj = root[0][1]
    if not isinstance(fields_obj, Pairs):
        return None, "fields_not_object"
    keys = [str(k) for k, _ in fields_obj]
    if len(keys) != len(set(keys)):
        return None, "duplicate_key"
    values = {}
    for key, value in fields_obj:
        if isinstance(value, (Pairs, list)):
            return None, "nonscalar_field"
        values[str(key)] = value
    return values, "pass"


def recover_raw(raw):
    raw = raw or ""
    strict_root = None
    strict_reason = "invalid_json"
    try:
        strict_root = json.loads(raw, object_pairs_hook=Pairs)
        strict_values, strict_reason = strict_fields_from_root(strict_root)
    except Exception:
        strict_values = None
    strict_pass = strict_values is not None

    source = "strict_json" if strict_root is not None else None
    pairs = []
    if strict_root is not None:
        collect_pairs(strict_root, pairs)
    else:
        fenced = re.fullmatch(r"\s*```(?:json)?\s*(\{.*\})\s*```\s*", raw, re.I | re.S)
        if fenced:
            try:
                fenced_root = json.loads(fenced.group(1), object_pairs_hook=Pairs)
                collect_pairs(fenced_root, pairs)
                source = "fenced_json"
            except Exception:
                pass
        if not pairs:
            for match in SCALAR_PAIR_RE.finditer(raw):
                pairs.append((decode_json_string(match.group("key")), parse_scalar_token(match.group("value"))))
            if pairs:
                source = "token_recovery"

    grouped = defaultdict(list)
    for key, value in pairs:
        if key == "fields" and isinstance(value, (Pairs, list)):
            continue
        grouped[key].append(value)

    fields = {}
    for key, values in grouped.items():
        canon = {canonical_scalar(v) for v in values}
        if len(canon) > 1:
            fields[key] = {
                "status": "conflict",
                "value": None,
                "occurrences": len(values),
                "values": values,
            }
        else:
            fields[key] = {
                "status": "unique" if len(values) == 1 else "duplicate_same",
                "value": values[0],
                "occurrences": len(values),
                "values": values,
            }
    return {
        "strict_format_pass": strict_pass,
        "strict_reason": strict_reason,
        "recovery_source": source or "unrecoverable",
        "fields": fields,
        "duplicate_keys_anywhere": sorted(set(pairs_duplicates(strict_root))) if strict_root is not None else [],
        "recovered_field_count": len(fields),
        "conflict_fields": sorted(k for k, v in fields.items() if v["status"] == "conflict"),
        "duplicate_same_fields": sorted(k for k, v in fields.items() if v["status"] == "duplicate_same"),
    }


def recovered_value(recovery, key):
    field = recovery["fields"].get(key)
    if field is None:
        return "missing", None
    return field["status"], field["value"]


def compare_value(gold, pred):
    if pred is None:
        return False
    if isinstance(gold, (int, float)) and not isinstance(gold, bool):
        return int_value(pred) == int(gold)
    return str(pred).strip().strip('"').casefold() == str(gold).strip().casefold()


def score_recovered_fields(gold, fields, recovery):
    cells = {}
    correct = wrong = missing = undetermined = 0
    for key in fields:
        target = gold.get(key)
        status, pred = recovered_value(recovery, key)
        if status == "conflict":
            result = "undetermined"
            undetermined += 1
        elif status == "missing":
            result = "missing"
            missing += 1
        elif compare_value(target, pred):
            result = "correct"
            correct += 1
        else:
            result = "wrong"
            wrong += 1
        cells[key] = {"gold": target, "pred": pred, "field_status": status, "result": result}
    return {
        "correct": correct,
        "wrong": wrong,
        "missing": missing,
        "undetermined": undetermined,
        "total": len(fields),
        "task_correct": correct == len(fields),
        "cells": cells,
    }


def arm_from_cond(cond):
    return cond.split("_")[0]


def semantic_ranking(sample, arm):
    innings = int(str(sample["innings"]).replace("inn", ""))
    bowlers = V.load_bundle(sample["match"])["md"].innings[innings - 1].bowlers
    rows = []
    for source_index, bowler in enumerate(bowlers):
        wickets = bowler.wickets
        if arm == "N2" and bowler.name == sample["A"]:
            wickets -= 1
        if arm == "N2" and bowler.name == sample["B"]:
            wickets += 1
        rows.append(
            {
                "name": bowler.name,
                "wickets": wickets,
                "runs": bowler.runs_conceded,
                "source_index": source_index,
            }
        )
    ranked = sorted(rows, key=lambda x: (x["wickets"], -x["runs"]), reverse=True)
    cutoff_tie = len(ranked) > 2 and (ranked[1]["wickets"], ranked[1]["runs"]) == (
        ranked[2]["wickets"],
        ranked[2]["runs"],
    )
    top_order_tie = (ranked[0]["wickets"], ranked[0]["runs"]) == (
        ranked[1]["wickets"],
        ranked[1]["runs"],
    )
    return ranked[:2], cutoff_tie, top_order_tie, ranked


def manifest_rows(task, innings):
    rows = []
    for rank in (1, 2):
        prefix = f"inn{innings}.bowl{rank}"
        rows.append(
            {
                "name": task["gold"].get(prefix + "_name"),
                "wickets": task["gold"].get(prefix + "_wickets"),
                "runs": task["gold"].get(prefix + "_runs"),
            }
        )
    return rows


def output_rows(recovery, innings):
    rows = []
    for rank in (1, 2):
        prefix = f"inn{innings}.bowl{rank}"
        name_status, name = recovered_value(recovery, prefix + "_name")
        wickets_status, wickets = recovered_value(recovery, prefix + "_wickets")
        runs_status, runs = recovered_value(recovery, prefix + "_runs")
        rows.append(
            {
                "rank": rank,
                "name_status": name_status,
                "name": name,
                "wickets_status": wickets_status,
                "wickets": int_value(wickets),
                "runs_status": runs_status,
                "runs": int_value(runs),
            }
        )
    return rows


def identity_score(recovery, sample, arm):
    innings = int(str(sample["innings"]).replace("inn", ""))
    expected, cutoff_tie, top_order_tie, ranked = semantic_ranking(sample, arm)
    observed = output_rows(recovery, innings)
    known_names = [normalize_name(r["name"]) for r in observed if r["name_status"] in ("unique", "duplicate_same")]

    expected_by_name = {normalize_name(r["name"]): r for r in ranked}
    valid_member_sets = []
    selected_expected = expected
    if cutoff_tie:
        cutoff_key = (ranked[1]["wickets"], ranked[1]["runs"])
        locked = [r for r in ranked if (r["wickets"], r["runs"]) != cutoff_key][:1]
        tied = [r for r in ranked if (r["wickets"], r["runs"]) == cutoff_key]
        slots = 2 - len(locked)
        for choice in combinations(tied, slots):
            members = locked + list(choice)
            valid_member_sets.append({normalize_name(r["name"]) for r in members})

    if len(known_names) != 2:
        member_set_status = "undetermined_output_identity"
    elif len(set(known_names)) != 2:
        member_set_status = "undetermined_duplicate_identity"
    elif cutoff_tie:
        observed_set = set(known_names)
        if observed_set in valid_member_sets:
            member_set_status = "correct_tie_accepted"
            selected_expected = [expected_by_name[name] for name in known_names]
        else:
            member_set_status = "wrong"
    else:
        expected_set = {normalize_name(r["name"]) for r in expected}
        member_set_status = "correct" if set(known_names) == expected_set else "wrong"

    if len(known_names) != 2 or len(set(known_names)) != 2:
        row_order_status = "undetermined_output_identity"
    elif member_set_status not in ("correct", "correct_tie_accepted"):
        row_order_status = "wrong_member_set"
    else:
        selected_ranked = sorted(selected_expected, key=lambda x: (x["wickets"], -x["runs"]), reverse=True)
        selected_top_tie = (selected_ranked[0]["wickets"], selected_ranked[0]["runs"]) == (
            selected_ranked[1]["wickets"], selected_ranked[1]["runs"]
        )
        if selected_top_tie:
            row_order_status = "undetermined_tie"
        else:
            expected_order = [normalize_name(r["name"]) for r in selected_ranked]
            row_order_status = "correct" if known_names == expected_order else "wrong"

    value_cells = []
    definite_wrong = False
    has_undetermined = False
    if cutoff_tie and member_set_status not in ("correct_tie_accepted",):
        value_status = "wrong_member_set" if member_set_status == "wrong" else "undetermined_output_identity"
    else:
        for target in selected_expected:
            matches = [r for r in observed if normalize_name(r["name"]) == normalize_name(target["name"])]
            if len(matches) > 1:
                has_undetermined = True
                value_cells.append({"player": target["name"], "field": "identity", "result": "undetermined_duplicate_identity"})
                continue
            if not matches:
                definite_wrong = True
                value_cells.append({"player": target["name"], "field": "identity", "result": "missing_member"})
                continue
            row = matches[0]
            for field in ("wickets", "runs"):
                source_status = row[field + "_status"]
                pred = row[field]
                if source_status == "conflict":
                    has_undetermined = True
                    result = "undetermined_conflict"
                elif source_status == "missing":
                    definite_wrong = True
                    result = "missing_field"
                elif pred == target[field]:
                    result = "correct"
                else:
                    definite_wrong = True
                    result = "wrong"
                value_cells.append(
                    {
                        "player": target["name"],
                        "field": field,
                        "gold": target[field],
                        "pred": pred,
                        "source_status": source_status,
                        "result": result,
                    }
                )
        if definite_wrong and has_undetermined:
            value_status = "wrong_and_undetermined"
        elif definite_wrong:
            value_status = "wrong"
        elif has_undetermined:
            value_status = "undetermined"
        else:
            value_status = "correct"

    total_key = f"inn{innings}.total_wickets"
    total_source_status, total_pred_raw = recovered_value(recovery, total_key)
    total_pred = int_value(total_pred_raw)
    if total_source_status == "conflict":
        total_status = "undetermined_conflict"
    elif total_source_status == "missing":
        total_status = "missing"
    else:
        total_status = "correct" if total_pred == sample["total"] else "wrong"

    identity_task_correct = (
        member_set_status in ("correct", "correct_tie_accepted")
        and value_status == "correct"
        and total_status == "correct"
    )
    ordered_task_correct = identity_task_correct and row_order_status == "correct"
    return {
        "expected_rows": expected,
        "ranked_top3": ranked[:3],
        "cutoff_tie": cutoff_tie,
        "top_order_tie": top_order_tie,
        "valid_member_sets": [sorted(s) for s in valid_member_sets],
        "observed_rows": observed,
        "member_set_status": member_set_status,
        "row_order_status": row_order_status,
        "identity_value_status": value_status,
        "identity_value_cells": value_cells,
        "total_status": total_status,
        "total_pred": total_pred,
        "identity_task_correct": identity_task_correct,
        "ordered_task_correct": ordered_task_correct,
    }


def fmt_rows(rows):
    return " | ".join(f"{r.get('name')} {r.get('wickets')}/{r.get('runs')}" for r in rows)


def write_csv(path, rows, fieldnames=None):
    rows = list(rows)
    if not rows:
        raise RuntimeError(f"refusing to write empty CSV: {path}")
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_batch(batch_id):
    manifest_path = BATCHES / f"{batch_id}.json"
    run_path = RUNS / f"{batch_id}.jsonl"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    runs = [json.loads(line) for line in run_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return manifest, runs, manifest_path, run_path


samples = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))[:8]
sample_by_match = {s["match"]: s for s in samples}

manifest_tasks = {}
run_rows = {}
source_paths = [SAMPLES_PATH]
for batch_id in FULL_BATCHES + DIAG_BATCHES:
    manifest, runs, manifest_path, run_path = load_batch(batch_id)
    source_paths.extend([manifest_path, run_path])
    for task in manifest["tasks"]:
        manifest_tasks[task["task_key"]] = task | {"batch_id": batch_id}
    for row in runs:
        run_rows[row["task_key"]] = row
for sample in samples:
    scorecard = ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches" / sample["match"] / "scorecard.md"
    source_paths.append(scorecard)

source_hashes = {str(p): sha256_file(p) for p in source_paths}
existing_hash_path = HERE / "SOURCE_HASHES.json"
if existing_hash_path.exists():
    old_hashes = json.loads(existing_hash_path.read_text(encoding="utf-8"))["files"]
    if old_hashes != source_hashes:
        raise RuntimeError("source file hashes changed since this scoring version was created")


full_tasks = [t for t in manifest_tasks.values() if t.get("field_scope") == "night_fulltable"]
assert len(full_tasks) == 72, len(full_tasks)
assert all(t["task_key"] in run_rows for t in full_tasks)

rescored = []
n1_diff = []
malformed = []
for task in sorted(full_tasks, key=lambda x: (x["match"], x["model"], x["cond"])):
    run = run_rows[task["task_key"]]
    sample = sample_by_match[task["match"]]
    arm = arm_from_cond(task["cond"])
    innings = int(task["innings"])
    recovery = recover_raw(run.get("raw_output", ""))
    fixed_score = score_recovered_fields(task["gold"], task["fields"], recovery)
    semantic = identity_score(recovery, sample, arm)
    current_rows = manifest_rows(task, innings)
    expected_rows = semantic["expected_rows"]
    rank_conflict = (
        [(normalize_name(r["name"]), r["wickets"], r["runs"]) for r in current_rows]
        != [(normalize_name(r["name"]), r["wickets"], r["runs"]) for r in expected_rows]
    )
    old_score = run.get("score") or {}
    row = {
        "scoring_version": VERSION,
        "batch_id": task["batch_id"],
        "task_key": task["task_key"],
        "match": task["match"],
        "innings": innings,
        "event": sample["batter"],
        "model": task["model"],
        "arm": arm,
        "cond": task["cond"],
        "text_sha256": task["text_sha"],
        "raw_output_sha256": sha256_text(run.get("raw_output", "")),
        "old_parse_ok": bool(run.get("parse_ok")),
        "old_embedded_correct": old_score.get("correct"),
        "old_embedded_total": old_score.get("total"),
        "old_embedded_task_correct": old_score.get("task_correct"),
        "strict_format_pass": recovery["strict_format_pass"],
        "strict_reason": recovery["strict_reason"],
        "recovery_source": recovery["recovery_source"],
        "recovered_field_count": recovery["recovered_field_count"],
        "duplicate_same_fields": ";".join(recovery["duplicate_same_fields"]),
        "conflict_fields": ";".join(recovery["conflict_fields"]),
        "new_fixed_correct": fixed_score["correct"],
        "new_fixed_wrong": fixed_score["wrong"],
        "new_fixed_missing": fixed_score["missing"],
        "new_fixed_undetermined": fixed_score["undetermined"],
        "new_fixed_total": fixed_score["total"],
        "new_fixed_task_correct": fixed_score["task_correct"],
        "new_minus_old_correct": fixed_score["correct"] - int(old_score.get("correct") or 0),
        "manifest_rows": fmt_rows(current_rows),
        "semantic_rows": fmt_rows(expected_rows),
        "rank_conflict": rank_conflict,
        "cutoff_tie": semantic["cutoff_tie"],
        "top_order_tie": semantic["top_order_tie"],
        "observed_rows": fmt_rows(semantic["observed_rows"]),
        "member_set_status": semantic["member_set_status"],
        "row_order_status": semantic["row_order_status"],
        "identity_value_status": semantic["identity_value_status"],
        "total_status": semantic["total_status"],
        "identity_task_correct": semantic["identity_task_correct"],
        "ordered_task_correct": semantic["ordered_task_correct"],
    }
    rescored.append(row)

    if arm == "N1":
        old_cells = old_score.get("cells") or {}
        changed = []
        for key in task["fields"]:
            old_gold = (old_cells.get(key) or {}).get("gold")
            new_gold = task["gold"].get(key)
            if old_gold != new_gold:
                changed.append(
                    {
                        "field": key,
                        "old_gold": old_gold,
                        "new_gold": new_gold,
                        "pred": (fixed_score["cells"].get(key) or {}).get("pred"),
                        "old_ok": (old_cells.get(key) or {}).get("ok"),
                        "new_result": (fixed_score["cells"].get(key) or {}).get("result"),
                    }
                )
        n1_row = dict(row)
        n1_row["changed_gold_fields"] = ";".join(x["field"] for x in changed)
        n1_row["changed_gold_detail"] = json.dumps(changed, ensure_ascii=False, separators=(",", ":"))
        n1_diff.append(n1_row)

    if not recovery["strict_format_pass"] and recovery["recovery_source"] == "token_recovery":
        malformed.append(
            {
                "batch_id": task["batch_id"],
                "task_key": task["task_key"],
                "match": task["match"],
                "innings": innings,
                "model": task["model"],
                "arm": arm,
                "raw_output_sha256": row["raw_output_sha256"],
                "strict_format_score": 0,
                "strict_reason": recovery["strict_reason"],
                "recovery_source": recovery["recovery_source"],
                "recovered_field_count": recovery["recovered_field_count"],
                "duplicate_same_fields": row["duplicate_same_fields"],
                "conflict_fields": row["conflict_fields"],
                "recoverable_correct": fixed_score["correct"],
                "recoverable_wrong": fixed_score["wrong"],
                "recoverable_missing": fixed_score["missing"],
                "recoverable_undetermined": fixed_score["undetermined"],
                "member_set_status": semantic["member_set_status"],
                "row_order_status": semantic["row_order_status"],
                "identity_value_status": semantic["identity_value_status"],
                "total_status": semantic["total_status"],
            }
        )

assert len(n1_diff) == 24, len(n1_diff)
assert len(malformed) == 16, len(malformed)


rank_revision = []
for sample in samples:
    task = next(t for t in full_tasks if t["match"] == sample["match"] and arm_from_cond(t["cond"]) == "N2")
    innings = int(task["innings"])
    current_rows = manifest_rows(task, innings)
    expected, cutoff_tie, top_order_tie, ranked = semantic_ranking(sample, "N2")
    current_names = [normalize_name(r["name"]) for r in current_rows]
    expected_names = [normalize_name(r["name"]) for r in expected]
    if current_names == expected_names and [r["wickets"] for r in current_rows] == [r["wickets"] for r in expected]:
        continue
    membership_changed = set(current_names) != set(expected_names)
    action = "revise_member_set_and_order" if membership_changed else "revise_order_only"
    rank_revision.append(
        {
            "scoring_version": VERSION,
            "match": sample["match"],
            "innings": innings,
            "event": sample["batter"],
            "action": action,
            "membership_changed": membership_changed,
            "order_changed": current_names != expected_names,
            "current_manifest_rows": fmt_rows(current_rows),
            "revised_semantic_rows": fmt_rows(expected),
            "post_notice_rank3": fmt_rows(ranked[:3]),
            "cutoff_tie": cutoff_tie,
            "top_order_tie": top_order_tie,
            "note": "原投手退出 top-2" if membership_changed else "成员相同，按 wickets 降序、runs 升序重排",
        }
    )
assert len(rank_revision) == 5, len(rank_revision)


def notice_for_diag(batch_id, prompt):
    if batch_id == "B243":
        return "N2"
    if batch_id == "B244":
        return "N0"
    if batch_id == "B245":
        return "N1"
    if "No review notice is provided" in prompt:
        return "N0"
    if "is maintained" in prompt or "No change to either bowler" in prompt:
        return "N1"
    if "formally reassigned" in prompt:
        return "N2"
    raise RuntimeError("unable to classify diagnostic notice")


diag_rows = []
for batch_id in DIAG_BATCHES:
    tasks = [t for t in manifest_tasks.values() if t.get("batch_id") == batch_id]
    for task in tasks:
        if task["cond"] not in ("q1_batter", "q4_old"):
            continue
        run = run_rows[task["task_key"]]
        recovery = recover_raw(run.get("raw_output", ""))
        score = score_recovered_fields(task["gold"], task["fields"], recovery)
        notice = notice_for_diag(batch_id, task["prompt"])
        mode = "window" if batch_id == "B246" else "full"
        diag_rows.append(
            {
                "batch_id": batch_id,
                "task_key": task["task_key"],
                "match": task["match"],
                "innings": task["innings"],
                "model": task["model"],
                "input_mode": mode,
                "notice": notice,
                "question": task["cond"],
                "strict_format_pass": recovery["strict_format_pass"],
                "recovery_source": recovery["recovery_source"],
                "old_task_correct": bool((run.get("score") or {}).get("task_correct")),
                "new_content_correct": score["task_correct"],
                "new_correct_cells": score["correct"],
                "new_total_cells": score["total"],
                "undetermined_cells": score["undetermined"],
            }
        )

assert len(diag_rows) == 288, len(diag_rows)
diag_distribution = []
for mode in ("full", "window"):
    for notice in ARMS:
        for question in ("q1_batter", "q4_old"):
            rows = [r for r in diag_rows if r["input_mode"] == mode and r["notice"] == notice and r["question"] == question]
            assert len(rows) == 24, (mode, notice, question, len(rows))
            out = {
                "input_mode": mode,
                "notice": notice,
                "question": question,
                "correct": sum(r["new_content_correct"] for r in rows),
                "total": len(rows),
                "undetermined": sum(r["undetermined_cells"] > 0 for r in rows),
            }
            for model in MODELS:
                model_rows = [r for r in rows if r["model"] == model]
                out[model.split(":")[0] + "_correct"] = sum(r["new_content_correct"] for r in model_rows)
                out[model.split(":")[0] + "_total"] = len(model_rows)
            diag_distribution.append(out)

controls = {}
for mode in ("full", "window"):
    for question in ("q1_batter", "q4_old"):
        rows = [r for r in diag_rows if r["input_mode"] == mode and r["question"] == question]
        controls[(mode, question)] = (sum(r["new_content_correct"] for r in rows), len(rows))
assert controls[("full", "q1_batter")] == (11, 72), controls
assert controls[("full", "q4_old")] == (44, 72), controls
assert controls[("window", "q1_batter")] == (36, 72), controls
assert controls[("window", "q4_old")] == (56, 72), controls


def row_for(match, model, arm):
    found = [r for r in rescored if r["match"] == match and r["model"] == model and r["arm"] == arm]
    assert len(found) == 1
    return found[0]


regression_cases = []
wrong_person = row_for("match_0003", "qwen2.5:7b-instruct-q4_K_M", "N1")
regression_cases.append(
    {
        "case_id": "R1_match_0003_wrong_person",
        "kind": "wrong_person_not_numeric_transfer",
        "task_key": wrong_person["task_key"],
        "expected": {"member_set_status": "wrong", "observed_contains": "Mason Cooper", "observed_omits": "Connor Reed"},
        "actual": {"member_set_status": wrong_person["member_set_status"], "observed_rows": wrong_person["observed_rows"]},
        "pass": wrong_person["member_set_status"] == "wrong" and "Mason Cooper" in wrong_person["observed_rows"] and "Connor Reed" not in wrong_person["observed_rows"],
    }
)
for index, match in enumerate(("match_0008", "match_0010"), 2):
    revision = next(r for r in rank_revision if r["match"] == match)
    regression_cases.append(
        {
            "case_id": f"R{index}_{match}_ranking_exit",
            "kind": "post_notice_target_exits_top2",
            "expected": {"action": "revise_member_set_and_order", "membership_changed": True},
            "actual": revision,
            "pass": revision["action"] == "revise_member_set_and_order" and revision["membership_changed"],
        }
    )
tie_sample = sample_by_match["match_0010"]
tie_fixture = recover_raw(
    '{"fields":{'
    '"inn2.bowl1_name":"Ryan Foster","inn2.bowl1_wickets":3,"inn2.bowl1_runs":48,'
    '"inn2.bowl2_name":"Luke Barrett","inn2.bowl2_wickets":2,"inn2.bowl2_runs":38,'
    '"inn2.total_wickets":10}}'
)
tie_semantic = identity_score(tie_fixture, tie_sample, "N1")
regression_cases.append(
    {
        "case_id": "R4_match_0010_exact_cutoff_tie",
        "kind": "exact_cutoff_tie_accepts_alternate_member_without_source_order_tiebreak",
        "fixture": "Ryan Foster 3/48 | Luke Barrett 2/38",
        "expected": {
            "cutoff_tie": True,
            "member_set_status": "correct_tie_accepted",
            "row_order_status": "correct",
            "identity_value_status": "correct",
        },
        "actual": {
            "cutoff_tie": tie_semantic["cutoff_tie"],
            "valid_member_sets": tie_semantic["valid_member_sets"],
            "member_set_status": tie_semantic["member_set_status"],
            "row_order_status": tie_semantic["row_order_status"],
            "identity_value_status": tie_semantic["identity_value_status"],
        },
        "pass": (
            tie_semantic["cutoff_tie"]
            and tie_semantic["member_set_status"] == "correct_tie_accepted"
            and tie_semantic["row_order_status"] == "correct"
            and tie_semantic["identity_value_status"] == "correct"
        ),
    }
)
assert all(case["pass"] for case in regression_cases)


parser_tests = [
    ("valid", '{"fields":{"a":1}}', True, "strict_json", 1, []),
    ("fenced", '```json\n{"fields":{"a":1}}\n```', False, "fenced_json", 1, []),
    ("malformed_recover", '{"fields":{"a":1"}}', False, "token_recovery", 1, []),
    ("duplicate_same", '{"fields":{"a":1,"a":1}}', False, "strict_json", 1, []),
    ("duplicate_conflict", '{"fields":{"a":1,"a":2}}', False, "strict_json", 1, ["a"]),
]
parser_results = []
for name, raw, strict_pass, source, field_count, conflicts in parser_tests:
    parsed = recover_raw(raw)
    passed = (
        parsed["strict_format_pass"] == strict_pass
        and parsed["recovery_source"] == source
        and parsed["recovered_field_count"] == field_count
        and parsed["conflict_fields"] == conflicts
    )
    parser_results.append({"name": name, "pass": passed, "actual": parsed})
assert all(x["pass"] for x in parser_results)


write_csv(HERE / "fulltable_rescore_rows.csv", rescored)
write_csv(HERE / "n1_old_to_new_diff.csv", n1_diff)
write_csv(HERE / "n2_rank_revision.csv", rank_revision)
write_csv(HERE / "malformed_json_rescore.csv", malformed)
write_csv(HERE / "minimal_diag_q1_q4_rows.csv", diag_rows)
write_csv(HERE / "minimal_diag_q1_q4_distribution.csv", diag_distribution)

source_inventory = []
for path in source_paths:
    if path == SAMPLES_PATH:
        role = "attribution_samples"
        source_id = "samples"
    elif path.parent == BATCHES:
        role = "frozen_manifest"
        source_id = path.stem
    elif path.parent == RUNS:
        role = "sealed_raw_jsonl_with_old_scores"
        source_id = path.stem
    else:
        role = "source_scorecard"
        source_id = path.parent.name
    source_inventory.append(
        {
            "source_id": source_id,
            "role": role,
            "path": str(path),
            "sha256": source_hashes[str(path)],
            "bytes": path.stat().st_size,
            "read_only_in_this_version": True,
        }
    )
write_csv(HERE / "SOURCE_INVENTORY.csv", source_inventory)

with (HERE / "rescored_lines.jsonl").open("w", encoding="utf-8", newline="\n") as f:
    for row in rescored:
        f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

(HERE / "regression_cases.json").write_text(json.dumps(regression_cases, ensure_ascii=False, indent=2), encoding="utf-8")
(HERE / "parser_regression_tests.json").write_text(json.dumps(parser_results, ensure_ascii=False, indent=2), encoding="utf-8")

source_hash_payload = {"scoring_version": VERSION, "files": source_hashes}
existing_hash_path.write_text(json.dumps(source_hash_payload, ensure_ascii=False, indent=2), encoding="utf-8")

summary = {
    "scoring_version": VERSION,
    "source_files_preserved": True,
    "fulltable_rows": len(rescored),
    "n1_stale_rows_rescored": len(n1_diff),
    "n1_old_cells_correct": sum(int(r["old_embedded_correct"] or 0) for r in n1_diff),
    "n1_new_cells_correct": sum(r["new_fixed_correct"] for r in n1_diff),
    "n1_cell_delta": sum(r["new_minus_old_correct"] for r in n1_diff),
    "n2_rank_revisions": len(rank_revision),
    "n2_membership_revisions": sum(r["membership_changed"] for r in rank_revision),
    "n2_order_only_revisions": sum(not r["membership_changed"] for r in rank_revision),
    "malformed_json_rows": len(malformed),
    "malformed_strict_pass": sum(r["strict_format_score"] for r in malformed),
    "malformed_recoverable_identity_correct": sum(r["identity_value_status"] == "correct" for r in malformed),
    "malformed_recoverable_fixed_task_correct": sum(r["recoverable_correct"] == 43 for r in malformed),
    "diag_controls": {f"{k[0]}_{k[1]}": {"correct": v[0], "total": v[1]} for k, v in controls.items()},
    "regression_cases_passed": sum(c["pass"] for c in regression_cases),
    "parser_tests_passed": sum(c["pass"] for c in parser_results),
}
(HERE / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

workbook_payload = {
    "summary": summary,
    "n1_diff": n1_diff,
    "n2_rank": rank_revision,
    "malformed": malformed,
    "diag_distribution": diag_distribution,
    "regression": regression_cases,
    "source_inventory": source_inventory,
}
(HERE / "workbook_data.json").write_text(
    json.dumps(workbook_payload, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps(summary, ensure_ascii=False, indent=2))
