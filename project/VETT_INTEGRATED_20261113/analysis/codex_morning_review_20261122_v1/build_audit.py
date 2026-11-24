import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WF = ROOT / "VETT_INTEGRATED_20261113" / "analysis" / "vett_autonomous_20261117"
NIGHT = ROOT / "VETT_INTEGRATED_20261113" / "analysis" / "vett_night_20261121"
SAMPLES = ROOT / "VETT_INTEGRATED_20261113" / "analysis" / "attribution_followup" / "samples.json"
BATCHES = WF / "batches"
RUNS = WF / "runs"

sys.path.insert(0, str(WF))
import vettlib as V  # noqa: E402


CORE_BATCHES = ["B213", "B221", "B222", "B223", "B224", "B225", "B226", "B227"]
FULL_BATCHES = ["B228", "B229", "B230", "B231", "B232", "B233", "B234", "B235"]
N0_BATCH = "B247"
ALL_BATCHES = CORE_BATCHES + FULL_BATCHES + [N0_BATCH]
ARMS = ("N0", "N1", "N2")


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_name(value):
    if value is None:
        return None
    s = str(value).strip()
    while re.search(r"\s*\([^)]*\)\s*$", s):
        s = re.sub(r"\s*\([^)]*\)\s*$", "", s).strip()
    return re.sub(r"\s+", " ", s).casefold()


def to_int(value):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    s = str(value).strip()
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    return None


def parse_visible(raw):
    """Parse exact JSON first, then recover visibly emitted key/value pairs from malformed JSON."""
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict) and isinstance(obj.get("fields"), dict):
            return obj["fields"], "strict_json"
        if isinstance(obj, dict):
            return obj, "strict_json"
    except Exception:
        pass
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw or "", re.I | re.S)
    if fenced:
        try:
            obj = json.loads(fenced.group(1))
            if isinstance(obj, dict) and isinstance(obj.get("fields"), dict):
                return obj["fields"], "fenced_json"
            if isinstance(obj, dict):
                return obj, "fenced_json"
        except Exception:
            pass
    out = {}
    pattern = re.compile(
        r'"([^"\\]+)"\s*:\s*(?:"([^"\\]*)"|(-?\d+(?:\.\d+)?)|(true|false|null))',
        re.I,
    )
    for m in pattern.finditer(raw or ""):
        key, text_value, number, literal = m.groups()
        if text_value is not None:
            value = text_value
        elif number is not None:
            value = float(number) if "." in number else int(number)
        elif literal and literal.lower() == "true":
            value = True
        elif literal and literal.lower() == "false":
            value = False
        else:
            value = None
        out[key] = value
    return out, ("salvaged_malformed_json" if out else "unrecoverable")


def load_manifest(batch_id):
    path = BATCHES / f"{batch_id}.json"
    return json.loads(path.read_text(encoding="utf-8")), path


def load_run(batch_id):
    path = RUNS / f"{batch_id}.jsonl"
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows, path


manifests = {}
manifest_tasks = {}
run_rows = {}
source_files = []
for batch_id in ALL_BATCHES:
    manifest, manifest_path = load_manifest(batch_id)
    rows, run_path = load_run(batch_id)
    manifests[batch_id] = manifest
    source_files.extend([manifest_path, run_path])
    for task in manifest["tasks"]:
        manifest_tasks[task["task_key"]] = task | {"batch_id": batch_id}
    for row in rows:
        run_rows[row["task_key"]] = row


assert len([t for t in manifest_tasks.values() if t["field_scope"] == "night_core"]) == 144
assert len([t for t in manifest_tasks.values() if t["field_scope"] == "night_fulltable"]) == 72
assert len(run_rows) == 216


def task_for(match, model, cond, scope):
    found = [
        t
        for t in manifest_tasks.values()
        if t["match"] == match and t["model"] == model and t["cond"] == cond and t["field_scope"] == scope
    ]
    assert len(found) == 1, (match, model, cond, scope, len(found))
    task = found[0]
    return task, run_rows[task["task_key"]]


def expected_pair(sample, arm):
    if arm == "N2":
        return {
            sample["A"]: (sample["Aw"] - 1, sample["Ar"]),
            sample["B"]: (sample["Bw"] + 1, sample["Br"]),
        }
    return {
        sample["A"]: (sample["Aw"], sample["Ar"]),
        sample["B"]: (sample["Bw"], sample["Br"]),
    }


def semantic_ranking(sample, arm):
    innings = int(str(sample["innings"]).replace("inn", ""))
    bowlers = V.load_bundle(sample["match"])["md"].innings[innings - 1].bowlers
    rows = []
    for source_index, b in enumerate(bowlers):
        wickets = b.wickets
        if arm == "N2" and b.name == sample["A"]:
            wickets -= 1
        if arm == "N2" and b.name == sample["B"]:
            wickets += 1
        rows.append(
            {
                "name": b.name,
                "wickets": wickets,
                "runs": b.runs_conceded,
                "source_index": source_index,
            }
        )
    ranked = sorted(rows, key=lambda x: (x["wickets"], -x["runs"]), reverse=True)
    cutoff_tie = len(ranked) > 2 and (ranked[1]["wickets"], ranked[1]["runs"]) == (
        ranked[2]["wickets"],
        ranked[2]["runs"],
    )
    return ranked[:2], cutoff_tie, ranked


def short_values(parsed, sample):
    return {
        sample["A"]: (
            to_int(parsed.get(f"{sample['A']}_wickets")),
            to_int(parsed.get(f"{sample['A']}_runs")),
        ),
        sample["B"]: (
            to_int(parsed.get(f"{sample['B']}_wickets")),
            to_int(parsed.get(f"{sample['B']}_runs")),
        ),
        "total": to_int(parsed.get("innings_total_wickets")),
    }


def full_rows(parsed, innings):
    out = []
    for rank in (1, 2):
        prefix = f"inn{innings}.bowl{rank}"
        out.append(
            {
                "rank": rank,
                "name": parsed.get(prefix + "_name"),
                "wickets": to_int(parsed.get(prefix + "_wickets")),
                "runs": to_int(parsed.get(prefix + "_runs")),
            }
        )
    return out


def identity_lookup(rows, player):
    target = normalize_name(player)
    matches = [r for r in rows if normalize_name(r["name"]) == target]
    return matches[0] if len(matches) == 1 else None


def pair_is_correct(values, sample, arm):
    expected = expected_pair(sample, arm)
    return all(values[player] == expected[player] for player in (sample["A"], sample["B"])) and values["total"] == sample["total"]


def pair_wickets_total_is_correct(values, sample, arm):
    expected = expected_pair(sample, arm)
    return all(values[player][0] == expected[player][0] for player in (sample["A"], sample["B"])) and values["total"] == sample["total"]


def full_identity_is_correct(rows, total, sample, arm):
    expected = expected_pair(sample, arm)
    for player in (sample["A"], sample["B"]):
        row = identity_lookup(rows, player)
        if row is None or (row["wickets"], row["runs"]) != expected[player]:
            return False
    return total == sample["total"]


def full_identity_wickets_total_is_correct(rows, total, sample, arm):
    expected = expected_pair(sample, arm)
    for player in (sample["A"], sample["B"]):
        row = identity_lookup(rows, player)
        if row is None or row["wickets"] != expected[player][0]:
            return False
    return total == sample["total"]


def full_positional_wickets_total_is_correct(rows, total, sample, arm):
    expected = expected_pair(sample, arm)
    return (
        rows[0]["wickets"] == expected[sample["A"]][0]
        and rows[1]["wickets"] == expected[sample["B"]][0]
        and total == sample["total"]
    )


def full_fixed_is_correct(parsed, gold, innings):
    keys = [f"inn{innings}.total_wickets"]
    for rank in (1, 2):
        keys.extend(
            [
                f"inn{innings}.bowl{rank}_name",
                f"inn{innings}.bowl{rank}_wickets",
                f"inn{innings}.bowl{rank}_runs",
            ]
        )
    for key in keys:
        pred = parsed.get(key)
        target = gold.get(key)
        if key.endswith("_name"):
            if normalize_name(pred) != normalize_name(target):
                return False
        elif to_int(pred) != to_int(target):
            return False
    return True


def semantic_gold(sample, arm):
    innings = int(str(sample["innings"]).replace("inn", ""))
    top2, tie, ranked = semantic_ranking(sample, arm)
    gold = {f"inn{innings}.total_wickets": sample["total"]}
    for rank, row in enumerate(top2, 1):
        gold[f"inn{innings}.bowl{rank}_name"] = row["name"]
        gold[f"inn{innings}.bowl{rank}_wickets"] = row["wickets"]
        gold[f"inn{innings}.bowl{rank}_runs"] = row["runs"]
    return gold, tie, ranked


def fmt_pair(values, sample):
    a = values[sample["A"]]
    b = values[sample["B"]]
    return f"{sample['A']}={a[0]}/{a[1]}; {sample['B']}={b[0]}/{b[1]}; total={values['total']}"


def fmt_rows(rows, total):
    return "; ".join(f"r{r['rank']}={r['name']} {r['wickets']}/{r['runs']}" for r in rows) + f"; total={total}"


def bool_text(value):
    if value is None:
        return ""
    return "true" if value else "false"


samples = json.loads(SAMPLES.read_text(encoding="utf-8"))[:8]
models = sorted({t["model"] for t in manifest_tasks.values() if t["field_scope"] == "night_core"})
records = []
detail = []

for sample in samples:
    innings = int(str(sample["innings"]).replace("inn", ""))
    for model in models:
        row = {
            "match": sample["match"],
            "innings": innings,
            "event": sample["batter"],
            "model": model,
            "A": sample["A"],
            "B": sample["B"],
            "old_A": f"{sample['Aw']}/{sample['Ar']}",
            "old_B": f"{sample['Bw']}/{sample['Br']}",
            "new_A": f"{sample['Aw'] - 1}/{sample['Ar']}",
            "new_B": f"{sample['Bw'] + 1}/{sample['Br']}",
            "team_total_wickets": sample["total"],
        }
        for arm in ARMS:
            short_task, short_run = task_for(sample["match"], model, f"{arm}_F", "night_core")
            win_task, win_run = task_for(sample["match"], model, f"{arm}_W", "night_core")
            full_task, full_run = task_for(sample["match"], model, f"{arm}_F_fulltable", "night_fulltable")

            short_parsed, short_parse = parse_visible(short_run.get("raw_output", ""))
            win_parsed, win_parse = parse_visible(win_run.get("raw_output", ""))
            full_parsed, full_parse = parse_visible(full_run.get("raw_output", ""))
            s_values = short_values(short_parsed, sample)
            w_values = short_values(win_parsed, sample)
            f_rows = full_rows(full_parsed, innings)
            f_total = to_int(full_parsed.get(f"inn{innings}.total_wickets"))
            s_ok = pair_is_correct(s_values, sample, arm)
            w_ok = pair_is_correct(w_values, sample, arm)
            f_identity_ok = full_identity_is_correct(f_rows, f_total, sample, arm)
            s_wt_ok = pair_wickets_total_is_correct(s_values, sample, arm)
            f_identity_wt_ok = full_identity_wickets_total_is_correct(f_rows, f_total, sample, arm)
            f_positional_wt_ok = full_positional_wickets_total_is_correct(f_rows, f_total, sample, arm)
            f_manifest_ok = full_fixed_is_correct(full_parsed, full_task["gold"], innings)
            sem_gold, cutoff_tie, ranked = semantic_gold(sample, arm)
            f_semantic_ok = full_fixed_is_correct(full_parsed, sem_gold, innings)

            top_names = [normalize_name(sem_gold[f"inn{innings}.bowl{rank}_name"]) for rank in (1, 2)]
            pair_in_top2 = all(normalize_name(p) in top_names for p in (sample["A"], sample["B"]))
            same_text = short_task["text_sha"] == full_task["text_sha"] == short_run["text_sha256"] == full_run["text_sha256"]
            if not same_text:
                comparable = False
                not_comparable_reason = "different_text_sha"
            elif cutoff_tie:
                comparable = False
                not_comparable_reason = "post_notice_top2_cutoff_tie"
            elif not pair_in_top2:
                comparable = False
                not_comparable_reason = "target_not_in_post_notice_top2"
            else:
                comparable = True
                not_comparable_reason = ""

            if comparable:
                if s_ok and f_identity_ok:
                    category = "both_correct"
                elif s_ok and not f_identity_ok:
                    category = "short_correct_full_wrong"
                elif not s_ok and f_identity_ok:
                    category = "short_wrong_full_correct"
                else:
                    category = "both_wrong"
            else:
                category = "not_comparable"

            if comparable:
                if s_wt_ok and f_identity_wt_ok:
                    category_wt = "both_correct"
                elif s_wt_ok and not f_identity_wt_ok:
                    category_wt = "short_correct_full_wrong"
                elif not s_wt_ok and f_identity_wt_ok:
                    category_wt = "short_wrong_full_correct"
                else:
                    category_wt = "both_wrong"
            else:
                category_wt = "not_comparable"

            # Reproduce the published DSH table's mixed contract: all five short fields,
            # but only fixed-position wickets + total on the full table.
            if s_ok and f_positional_wt_ok:
                dsh_like_category = "both_correct"
            elif s_ok and not f_positional_wt_ok:
                dsh_like_category = "short_correct_full_wrong"
            elif not s_ok and f_positional_wt_ok:
                dsh_like_category = "short_wrong_full_correct"
            else:
                dsh_like_category = "both_wrong"

            target_rows_present = all(identity_lookup(f_rows, p) is not None for p in (sample["A"], sample["B"]))
            if not comparable:
                cause = not_comparable_reason
            elif f_identity_ok and not f_semantic_ok:
                cause = "row_order_or_ranking_only"
            elif f_identity_ok and not full_run.get("parse_ok"):
                cause = "answer_correct_but_dsh_parser_failed"
            elif f_identity_ok and full_parse == "fenced_json":
                cause = "answer_correct_fenced_json"
            elif not target_rows_present:
                cause = "missing_target_row"
            elif not f_identity_ok:
                cause = "observable_value_error"
            else:
                cause = "none"

            expected_new = expected_pair(sample, "N2")
            full_new_both = True
            for player in (sample["A"], sample["B"]):
                found = identity_lookup(f_rows, player)
                full_new_both = full_new_both and found is not None and (found["wickets"], found["runs"]) == expected_new[player]
            short_new_both = all(s_values[p] == expected_new[p] for p in (sample["A"], sample["B"]))

            embedded_cells = full_run.get("score", {}).get("cells", {})
            relevant_keys = [f"inn{innings}.total_wickets"]
            for rank in (1, 2):
                relevant_keys.extend(
                    [
                        f"inn{innings}.bowl{rank}_name",
                        f"inn{innings}.bowl{rank}_wickets",
                        f"inn{innings}.bowl{rank}_runs",
                    ]
                )
            dsh_embedded_target_ok = all(embedded_cells.get(k, {}).get("ok") is True for k in relevant_keys)
            stale_embedded_gold = any(
                k in embedded_cells
                and (
                    normalize_name(embedded_cells[k].get("gold")) != normalize_name(full_task["gold"].get(k))
                    if k.endswith("_name")
                    else to_int(embedded_cells[k].get("gold")) != to_int(full_task["gold"].get(k))
                )
                for k in relevant_keys
            )

            pref = arm.lower() + "_"
            row[pref + "text_sha"] = short_task["text_sha"]
            row[pref + "same_text"] = bool_text(same_text)
            row[pref + "post_notice_top2"] = " | ".join(
                f"{sem_gold[f'inn{innings}.bowl{rank}_name']} {sem_gold[f'inn{innings}.bowl{rank}_wickets']}/{sem_gold[f'inn{innings}.bowl{rank}_runs']}"
                for rank in (1, 2)
            )
            row[pref + "pair_in_top2"] = bool_text(pair_in_top2)
            row[pref + "cutoff_tie"] = bool_text(cutoff_tie)
            row[pref + "comparable"] = bool_text(comparable)
            row[pref + "not_comparable_reason"] = not_comparable_reason
            row[pref + "short_task_key"] = short_task["task_key"]
            row[pref + "full_task_key"] = full_task["task_key"]
            row[pref + "short_parse"] = short_parse
            row[pref + "full_parse"] = full_parse
            row[pref + "dsh_short_parse_ok"] = bool_text(short_run.get("parse_ok"))
            row[pref + "dsh_full_parse_ok"] = bool_text(full_run.get("parse_ok"))
            row[pref + "short_values"] = fmt_pair(s_values, sample)
            row[pref + "window_values"] = fmt_pair(w_values, sample)
            row[pref + "full_rows"] = fmt_rows(f_rows, f_total)
            row[pref + "short_correct"] = bool_text(s_ok)
            row[pref + "window_correct"] = bool_text(w_ok)
            row[pref + "full_identity_correct"] = bool_text(f_identity_ok)
            row[pref + "full_manifest_fixed_correct"] = bool_text(f_manifest_ok)
            row[pref + "full_semantic_rank_correct"] = bool_text(f_semantic_ok)
            row[pref + "pair_category"] = category
            row[pref + "short_wickets_total_correct"] = bool_text(s_wt_ok)
            row[pref + "full_identity_wickets_total_correct"] = bool_text(f_identity_wt_ok)
            row[pref + "full_positional_wickets_total_correct"] = bool_text(f_positional_wt_ok)
            row[pref + "identity_wickets_total_category"] = category_wt
            row[pref + "dsh_like_positional_category"] = dsh_like_category
            row[pref + "observed_cause"] = cause
            row[pref + "short_total_held"] = bool_text(s_values["total"] == sample["total"])
            row[pref + "full_total_held"] = bool_text(f_total == sample["total"])
            row[pref + "short_both_on_new_values"] = bool_text(short_new_both)
            row[pref + "full_both_on_new_values"] = bool_text(full_new_both)
            row[pref + "dsh_embedded_target_correct"] = bool_text(dsh_embedded_target_ok)
            row[pref + "dsh_embedded_stale_gold"] = bool_text(stale_embedded_gold)
            row[pref + "manifest_vs_semantic_rank_conflict"] = bool_text(
                not all(
                    (normalize_name(full_task["gold"].get(k)) == normalize_name(sem_gold.get(k)))
                    if k.endswith("_name")
                    else (to_int(full_task["gold"].get(k)) == to_int(sem_gold.get(k)))
                    for k in relevant_keys
                )
            )

            detail.append(
                {
                    "match": sample["match"],
                    "innings": innings,
                    "event": sample["batter"],
                    "model": model,
                    "arm": arm,
                    "comparable": comparable,
                    "not_comparable_reason": not_comparable_reason,
                    "category": category,
                    "category_wickets_total": category_wt,
                    "dsh_like_positional_category": dsh_like_category,
                    "short_correct": s_ok,
                    "window_correct": w_ok,
                    "full_identity_correct": f_identity_ok,
                    "short_wickets_total_correct": s_wt_ok,
                    "full_identity_wickets_total_correct": f_identity_wt_ok,
                    "full_positional_wickets_total_correct": f_positional_wt_ok,
                    "full_manifest_fixed_correct": f_manifest_ok,
                    "full_semantic_rank_correct": f_semantic_ok,
                    "short_parse": short_parse,
                    "full_parse": full_parse,
                    "dsh_full_parse_ok": full_run.get("parse_ok"),
                    "short_raw": short_run.get("raw_output", ""),
                    "full_raw": full_run.get("raw_output", ""),
                    "short_values": s_values,
                    "full_rows": f_rows,
                    "full_total": f_total,
                    "short_task": short_task,
                    "full_task": full_task,
                    "stale_embedded_gold": stale_embedded_gold,
                    "dsh_embedded_target_correct": dsh_embedded_target_ok,
                    "observed_cause": cause,
                }
            )
        records.append(row)


assert len(records) == 24

csv_path = HERE / "CODEX_MORNING_REVIEW_ROWS.csv"
with csv_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
    writer.writeheader()
    writer.writerows(records)


summary = {}
for arm in ARMS:
    summary[arm] = {}
    for model in models:
        items = [d for d in detail if d["arm"] == arm and d["model"] == model]
        comp = [d for d in items if d["comparable"]]
        counts = Counter(d["category"] for d in comp)
        summary[arm][model] = {
            "actual_denominator": len(comp),
            "independent_matches": len({d["match"] for d in comp}),
            "both_correct": counts["both_correct"],
            "short_correct_full_wrong": counts["short_correct_full_wrong"],
            "short_wrong_full_correct": counts["short_wrong_full_correct"],
            "both_wrong": counts["both_wrong"],
            "excluded": len(items) - len(comp),
            "excluded_reasons": dict(Counter(d["not_comparable_reason"] for d in items if not d["comparable"])),
        }

summary_wickets_total = {}
dsh_like_positional = {}
for arm in ARMS:
    summary_wickets_total[arm] = {}
    dsh_like_positional[arm] = {}
    for model in models:
        items = [d for d in detail if d["arm"] == arm and d["model"] == model]
        comp = [d for d in items if d["comparable"]]
        wt_counts = Counter(d["category_wickets_total"] for d in comp)
        pos_counts = Counter(d["dsh_like_positional_category"] for d in items)
        summary_wickets_total[arm][model] = {
            "actual_denominator": len(comp),
            "both_correct": wt_counts["both_correct"],
            "short_correct_full_wrong": wt_counts["short_correct_full_wrong"],
            "short_wrong_full_correct": wt_counts["short_wrong_full_correct"],
            "both_wrong": wt_counts["both_wrong"],
        }
        dsh_like_positional[arm][model] = {
            "denominator": len(items),
            "both_correct": pos_counts["both_correct"],
            "short_correct_full_wrong": pos_counts["short_correct_full_wrong"],
            "short_wrong_full_correct": pos_counts["short_wrong_full_correct"],
            "both_wrong": pos_counts["both_wrong"],
        }

overall = {}
for arm in ARMS:
    items = [d for d in detail if d["arm"] == arm and d["comparable"]]
    overall[arm] = {
        "denominator": len(items),
        "independent_matches": len({d["match"] for d in items}),
        "categories": dict(Counter(d["category"] for d in items)),
    }

window_summary = {}
pairing_checks = []
for arm in ARMS:
    window_summary[arm] = {}
    for model in models:
        items = [d for d in detail if d["arm"] == arm and d["model"] == model]
        window_summary[arm][model] = {
            "correct": sum(1 for d in items if d["window_correct"]),
            "denominator": len(items),
        }
for sample in samples:
    for model in models:
        for arm in ARMS:
            short_task, short_run = task_for(sample["match"], model, f"{arm}_F", "night_core")
            full_task, full_run = task_for(sample["match"], model, f"{arm}_F_fulltable", "night_fulltable")
            short_decode = json.loads(short_task["decode_json"])
            full_decode = json.loads(full_task["decode_json"])
            short_without_budget = {k: v for k, v in short_decode.items() if k != "num_predict"}
            full_without_budget = {k: v for k, v in full_decode.items() if k != "num_predict"}
            pairing_checks.append(
                {
                    "match": sample["match"],
                    "model": model,
                    "arm": arm,
                    "same_text_sha": short_task["text_sha"] == full_task["text_sha"],
                    "same_model_digest": short_task["model_digest"] == full_task["model_digest"],
                    "same_versions": all(
                        short_task[k] == full_task[k]
                        for k in ("input_version", "prompt_version", "replicate_id")
                    ),
                    "same_decode_except_budget": short_without_budget == full_without_budget,
                    "short_num_predict": short_decode.get("num_predict"),
                    "full_num_predict": full_decode.get("num_predict"),
                }
            )
assert all(
    p["same_text_sha"] and p["same_model_digest"] and p["same_versions"] and p["same_decode_except_budget"]
    for p in pairing_checks
)

rank_conflicts = []
for sample in samples:
    for arm in ARMS:
        sem_gold, cutoff_tie, ranked = semantic_gold(sample, arm)
        model = models[0]
        full_task, _ = task_for(sample["match"], model, f"{arm}_F_fulltable", "night_fulltable")
        innings = int(str(sample["innings"]).replace("inn", ""))
        keys = []
        for rank in (1, 2):
            keys.extend([f"inn{innings}.bowl{rank}_name", f"inn{innings}.bowl{rank}_wickets", f"inn{innings}.bowl{rank}_runs"])
        different = any(
            (normalize_name(full_task["gold"].get(k)) != normalize_name(sem_gold.get(k)))
            if k.endswith("_name")
            else (to_int(full_task["gold"].get(k)) != to_int(sem_gold.get(k)))
            for k in keys
        )
        if different:
            rank_conflicts.append(
                {
                    "match": sample["match"],
                    "arm": arm,
                    "manifest_rows": [
                        {
                            "rank": r,
                            "name": full_task["gold"].get(f"inn{innings}.bowl{r}_name"),
                            "wickets": full_task["gold"].get(f"inn{innings}.bowl{r}_wickets"),
                            "runs": full_task["gold"].get(f"inn{innings}.bowl{r}_runs"),
                        }
                        for r in (1, 2)
                    ],
                    "semantic_rows": [
                        {
                            "rank": r,
                            "name": sem_gold.get(f"inn{innings}.bowl{r}_name"),
                            "wickets": sem_gold.get(f"inn{innings}.bowl{r}_wickets"),
                            "runs": sem_gold.get(f"inn{innings}.bowl{r}_runs"),
                        }
                        for r in (1, 2)
                    ],
                }
            )


def find_detail(match, model, arm):
    found = [d for d in detail if d["match"] == match and d["model"] == model and d["arm"] == arm]
    assert len(found) == 1
    return found[0]


support = {
    "generated_from": "sealed batch manifests and run JSONL only; no Ollama and no SQLite",
    "counts": {"core_tasks": 144, "fulltable_tasks": 72, "events": 8, "main_rows": 24},
    "models": models,
    "summary_by_arm_model": summary,
    "summary_wickets_total_identity": summary_wickets_total,
    "dsh_like_positional_wickets_total": dsh_like_positional,
    "overall": overall,
    "window_summary": window_summary,
    "pairing_audit": {
        "pairs": len(pairing_checks),
        "all_same_text_sha": all(p["same_text_sha"] for p in pairing_checks),
        "all_same_model_digest": all(p["same_model_digest"] for p in pairing_checks),
        "all_same_versions": all(p["same_versions"] for p in pairing_checks),
        "all_same_decode_except_budget": all(p["same_decode_except_budget"] for p in pairing_checks),
        "short_num_predict_values": sorted({p["short_num_predict"] for p in pairing_checks}),
        "full_num_predict_values": sorted({p["full_num_predict"] for p in pairing_checks}),
    },
    "rank_conflicts": rank_conflicts,
    "parse_status_counts": dict(Counter(d["full_parse"] for d in detail)),
    "dsh_parse_disagreements": [
        {
            "match": d["match"],
            "model": d["model"],
            "arm": d["arm"],
            "independent_parse": d["full_parse"],
            "dsh_parse_ok": d["dsh_full_parse_ok"],
            "independent_identity_correct": d["full_identity_correct"],
            "cause": d["observed_cause"],
        }
        for d in detail
        if d["full_parse"] != "unrecoverable" and not d["dsh_full_parse_ok"]
    ],
    "deep_failure": find_detail("match_0003", "qwen2.5:7b-instruct-q4_K_M", "N1"),
    "deep_success": find_detail("match_0003", "llama3.1:8b", "N1"),
    "source_files": [
        {"path": str(p), "sha256": sha256_file(p), "bytes": p.stat().st_size} for p in source_files
    ],
    "output_csv": {"path": str(csv_path), "sha256": sha256_file(csv_path), "rows": len(records)},
}

support_path = HERE / "audit_support.json"
support_path.write_text(json.dumps(support, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"csv": str(csv_path), "support": str(support_path), "summary": summary, "overall": overall}, ensure_ascii=False, indent=2))
