import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


VERSION = "n2-oldvalue-visibility-audit-v1-20261123"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ANALYSIS = ROOT / "VETT_INTEGRATED_20261113" / "analysis"
WF = ANALYSIS / "vett_autonomous_20261117"
BATCHES = WF / "batches"
RUNS = WF / "runs"
SAMPLES_PATH = ANALYSIS / "attribution_followup" / "samples.json"

sys.path.insert(0, str(WF))
import vettlib as V  # noqa: E402


FULL_Q4_BATCH = "B243"
WINDOW_BATCH = "B246"
RANK_BATCHES = ["B228", "B229", "B230", "B231", "B232", "B233", "B234", "B235"]
MODELS = ["qwen2.5:7b-instruct-q4_K_M", "llama3.1:8b", "gemma2:9b"]

MANUAL_VISIBILITY = {
    "match_0003": {
        "critical_competitors": "Caleb Price 1/30 | Gavin Turner 1/35",
        "visible_evidence": "Caleb Price bowled Drake; Gavin Turner removed Cross",
        "missing_evidence": "Caleb 30 and Gavin 35 runs conceded are not stated",
        "top2_membership_resolvable": True,
        "top2_order_resolvable": True,
        "third_identity_resolvable": False,
        "third_reason": "Caleb and Gavin both have one wicket; their runs tiebreak is hidden",
    },
    "match_0008": {
        "critical_competitors": "Evan Reed 2/27 | Luke Barrett 2/30",
        "visible_evidence": "Evan Reed cut off Owen Carter and removed Dylan Price; Luke is A in record+notice",
        "missing_evidence": "Evan Reed's 27 runs conceded is not stated",
        "top2_membership_resolvable": False,
        "top2_order_resolvable": False,
        "third_identity_resolvable": False,
        "third_reason": "Evan and Luke both finish with two wickets; hidden 27 vs 30 decides second/third",
    },
    "match_0010": {
        "critical_competitors": "Luke Barrett 2/38 | Ryan Foster 2/48",
        "visible_evidence": "Luke removed Daniel Cross and Zane Foster; text calls them two key breaks; Ryan is A in record+notice",
        "missing_evidence": "Luke Barrett's 38 runs conceded is not stated",
        "top2_membership_resolvable": False,
        "top2_order_resolvable": False,
        "third_identity_resolvable": False,
        "third_reason": "Luke and Ryan both finish with two wickets; hidden 38 vs 48 decides second/third",
    },
    "match_0012": {
        "critical_competitors": "Liam Frost 2/46 | Noah Grant 2/53",
        "visible_evidence": "Liam got Nolan Reed and removed Adrian Stone; Noah removed Connor and is mentioned again only in summary",
        "missing_evidence": "Noah's exact wicket total and both competitors' runs conceded are not directly stated",
        "top2_membership_resolvable": True,
        "top2_order_resolvable": True,
        "third_identity_resolvable": False,
        "third_reason": "Liam and Noah both have two wickets; their runs tiebreak is hidden",
    },
    "match_0015": {
        "critical_competitors": "Mason Hart 2/58",
        "visible_evidence": "Mason supplied the breakthrough twice, dismissing Aiden and Ethan",
        "missing_evidence": "Mason Hart's 58 runs conceded is not stated",
        "top2_membership_resolvable": True,
        "top2_order_resolvable": True,
        "third_identity_resolvable": True,
        "third_reason": "Mason's two wickets are uniquely below the two three-wicket leaders",
    },
    "match_0017": {
        "critical_competitors": "Mason Gray 2/23",
        "visible_evidence": "Mason removed Adrian Clarke and later Zach Foster",
        "missing_evidence": "Mason Gray's 23 runs conceded is not stated",
        "top2_membership_resolvable": True,
        "top2_order_resolvable": True,
        "third_identity_resolvable": True,
        "third_reason": "Mason's two wickets are uniquely below the two four-wicket leaders",
    },
    "match_0026": {
        "critical_competitors": "Lucas Barrett 1/12",
        "visible_evidence": "Lucas Barrett bowled Caleb Stone and is described as the first incision",
        "missing_evidence": "Lucas Barrett's 12 runs conceded is not stated",
        "top2_membership_resolvable": True,
        "top2_order_resolvable": True,
        "third_identity_resolvable": True,
        "third_reason": "Lucas's one wicket is uniquely below the four- and three-wicket leaders",
    },
    "match_0030": {
        "critical_competitors": "Caleb Hart 2/10 | Connor Blake 2/11",
        "visible_evidence": "Caleb bowled Isaac and removed Tyler; Daniel is explicitly caught off Connor",
        "missing_evidence": "Connor's exact wicket total and both competitors' runs conceded are not directly stated",
        "top2_membership_resolvable": True,
        "top2_order_resolvable": True,
        "third_identity_resolvable": False,
        "third_reason": "Caleb and Connor both have two wickets; their runs tiebreak is hidden",
    },
}


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha256_text(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def load_batch(batch_id):
    manifest_path = BATCHES / f"{batch_id}.json"
    run_path = RUNS / f"{batch_id}.jsonl"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    runs = [json.loads(line) for line in run_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return manifest, runs, manifest_path, run_path


def write_csv(path, rows, fieldnames=None):
    rows = list(rows)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with Path(path).open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def normalize_scalar(value):
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    try:
        return int(str(value).strip())
    except Exception:
        return value


def normalized_key(value):
    return re.sub(r"[^a-z0-9]+", "", str(value).casefold())


def raw_mapping(run):
    parsed = run.get("parsed")
    if isinstance(parsed, dict):
        return parsed
    raw = run.get("raw_output") or ""
    fenced = re.fullmatch(r"\s*```(?:json)?\s*(\{.*\})\s*```\s*", raw, re.I | re.S)
    candidate = fenced.group(1) if fenced else raw
    try:
        parsed = json.loads(candidate)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def extract_output(run, fields):
    parsed = raw_mapping(run)
    values = {}
    key_status = {}
    strict_values = {}
    for field in fields:
        strict_values[field] = normalize_scalar(parsed.get(field))
        if field in parsed:
            values[field] = strict_values[field]
            key_status[field] = "exact"
            continue
        matches = [(key, value) for key, value in parsed.items() if normalized_key(key) == normalized_key(field)]
        if len(matches) == 1:
            values[field] = normalize_scalar(matches[0][1])
            key_status[field] = f"identity_alias:{matches[0][0]}"
        elif len(matches) > 1:
            values[field] = None
            key_status[field] = "conflict"
        else:
            values[field] = None
            key_status[field] = "missing"
    return values, strict_values, key_status


def pair_class(a_pred, b_pred, a_old, b_old, a_new, b_new):
    if a_pred == a_old and b_pred == b_old:
        return "old_pair"
    if a_pred == a_new and b_pred == b_new:
        return "new_pair"
    if a_pred == a_old and b_pred == b_new:
        return "A_old_B_new"
    if a_pred == a_new and b_pred == b_old:
        return "A_new_B_old"
    return "other_or_missing"


def commentary_from_prompt(prompt):
    match = re.search(r"\n\nCommentary:\n(.*)\n\nJSON:\s*$", prompt, re.S)
    if not match:
        raise RuntimeError("unable to extract commentary")
    return match.group(1)


def before_record(commentary):
    marker = "Pre-revision record:"
    return commentary.split(marker, 1)[0].strip() if marker in commentary else commentary


def context_for_name(text, name, radius=260):
    low = text.casefold()
    needle = name.casefold()
    positions = []
    start = 0
    while True:
        idx = low.find(needle, start)
        if idx < 0:
            break
        positions.append(idx)
        start = idx + len(needle)
    excerpts = []
    for idx in positions[:4]:
        left = max(0, idx - radius)
        right = min(len(text), idx + len(name) + radius)
        excerpt = re.sub(r"\s+", " ", text[left:right]).strip()
        excerpts.append(excerpt)
    return " || ".join(excerpts)


def exact_figure_visible(text, name, wickets, runs):
    escaped = re.escape(name)
    patterns = [
        rf"{escaped}.{{0,120}}?\b{wickets}\s+wickets?\s+for\s+{runs}\b",
        rf"{escaped}.{{0,120}}?\b{wickets}\s+for\s+{runs}\b",
    ]
    return any(re.search(pattern, text, re.I | re.S) for pattern in patterns)


def direct_wickets_visible(text, name, wickets):
    escaped = re.escape(name)
    patterns = [
        rf"{escaped}.{{0,120}}?\b{wickets}\s+wickets?\b",
        rf"{escaped}.{{0,120}}?\b{wickets}\s+for\s+\d+\b",
    ]
    return any(re.search(pattern, text, re.I | re.S) for pattern in patterns)


samples = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))[:8]
sample_by_match = {sample["match"]: sample for sample in samples}

source_paths = [SAMPLES_PATH]
manifests = {}
runs_by_batch = {}
for batch_id in [FULL_Q4_BATCH, WINDOW_BATCH] + RANK_BATCHES:
    manifest, runs, manifest_path, run_path = load_batch(batch_id)
    manifests[batch_id] = manifest
    runs_by_batch[batch_id] = {row["task_key"]: row for row in runs}
    source_paths.extend([manifest_path, run_path])
for sample in samples:
    source_paths.append(
        ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches" / sample["match"] / "scorecard.md"
    )

full_tasks = [task for task in manifests[FULL_Q4_BATCH]["tasks"] if task["cond"] == "q4_old"]
window_tasks = [
    task
    for task in manifests[WINDOW_BATCH]["tasks"]
    if task["cond"] == "q4_old" and "formally reassigned" in task["prompt"]
]
assert len(full_tasks) == 24, len(full_tasks)
assert len(window_tasks) == 24, len(window_tasks)

full_by_key = {(task["match"], task["model"]): task for task in full_tasks}
window_by_key = {(task["match"], task["model"]): task for task in window_tasks}
assert set(full_by_key) == set(window_by_key)

rank_tasks = []
for batch_id in RANK_BATCHES:
    for task in manifests[batch_id]["tasks"]:
        if str(task["cond"]).startswith("N2_"):
            rank_tasks.append(task | {"batch_id": batch_id})
assert len(rank_tasks) == 24, len(rank_tasks)
rank_by_match = {}
for match in sample_by_match:
    tasks = [task for task in rank_tasks if task["match"] == match]
    assert len(tasks) == 3
    assert len({task["text_sha"] for task in tasks}) == 1
    assert len({task["prompt_sha"] for task in tasks}) == 1
    rank_by_match[match] = tasks[0]


paired_rows = []
for key in sorted(full_by_key):
    match, model = key
    sample = sample_by_match[match]
    full_task = full_by_key[key]
    window_task = window_by_key[key]
    full_run = runs_by_batch[FULL_Q4_BATCH][full_task["task_key"]]
    window_run = runs_by_batch[WINDOW_BATCH][window_task["task_key"]]
    a_field = f'{sample["A"]}_wickets'
    b_field = f'{sample["B"]}_wickets'
    assert full_task["fields"] == [a_field, b_field]
    assert window_task["fields"] == [a_field, b_field]
    a_old = sample["Aw"]
    b_old = sample["Bw"]
    a_new = sample["fields"][a_field]
    b_new = sample["fields"][b_field]
    assert full_task["gold"] == {a_field: a_old, b_field: b_old}
    assert window_task["gold"] == {a_field: a_old, b_field: b_old}
    full_pred, full_strict_pred, full_key_status = extract_output(full_run, [a_field, b_field])
    window_pred, window_strict_pred, window_key_status = extract_output(window_run, [a_field, b_field])
    full_commentary = commentary_from_prompt(full_task["prompt"])
    window_commentary = commentary_from_prompt(window_task["prompt"])
    full_narrative = before_record(full_commentary)
    window_narrative = before_record(window_commentary)
    rank_task = rank_by_match[match]
    expected_record = (
        f'Pre-revision record: {sample["A"]} {a_old} wickets for {sample["Ar"]} runs; '
        f'{sample["B"]} {b_old} wickets for {sample["Br"]} runs; '
        f'the innings total was {sample["total"]} wickets.'
    )
    expected_notice = (
        f'Match review: the dismissal of {sample["batter"]} is formally reassigned '
        f'from {sample["A"]} to {sample["B"]}.'
    )
    assert expected_record in full_commentary and expected_record in window_commentary
    assert expected_notice in full_commentary and expected_notice in window_commentary
    assert full_task["text_sha"] == rank_task["text_sha"]
    assert full_task["model_digest"] == window_task["model_digest"]
    assert full_task["decode_json"] == window_task["decode_json"]
    assert full_task["input_version"] == window_task["input_version"]
    assert full_task["prompt_version"] == window_task["prompt_version"]
    assert window_narrative in full_narrative
    paired_rows.append(
        {
            "audit_version": VERSION,
            "match": match,
            "innings": sample["innings"],
            "event_batter": sample["batter"],
            "model": model,
            "question_timepoint": "pre_revision_before_notice_update",
            "question_text": "Give the pre-revision wicket counts of the two bowlers named in the record.",
            "bowler_A": sample["A"],
            "bowler_B": sample["B"],
            "A_old_wickets": a_old,
            "B_old_wickets": b_old,
            "A_old_runs": sample["Ar"],
            "B_old_runs": sample["Br"],
            "A_new_wickets": a_new,
            "B_new_wickets": b_new,
            "A_new_runs": sample["Ar"],
            "B_new_runs": sample["Br"],
            "innings_total_wickets": sample["total"],
            "full_task_key": full_task["task_key"],
            "full_text_sha256": full_task["text_sha"],
            "full_prompt_sha256": full_task["prompt_sha"],
            "full_raw_output_sha256": sha256_text(full_run.get("raw_output", "")),
            "full_raw_output": full_run.get("raw_output", ""),
            "full_A_strict_pred": full_strict_pred[a_field],
            "full_B_strict_pred": full_strict_pred[b_field],
            "full_A_pred": full_pred[a_field],
            "full_B_pred": full_pred[b_field],
            "full_A_key_status": full_key_status[a_field],
            "full_B_key_status": full_key_status[b_field],
            "full_pair_class": pair_class(full_pred[a_field], full_pred[b_field], a_old, b_old, a_new, b_new),
            "full_A_old_correct": full_pred[a_field] == a_old,
            "full_B_old_correct": full_pred[b_field] == b_old,
            "full_pair_old_correct": full_pred[a_field] == a_old and full_pred[b_field] == b_old,
            "window_task_key": window_task["task_key"],
            "window_text_sha256": window_task["text_sha"],
            "window_prompt_sha256": window_task["prompt_sha"],
            "window_raw_output_sha256": sha256_text(window_run.get("raw_output", "")),
            "window_raw_output": window_run.get("raw_output", ""),
            "window_A_strict_pred": window_strict_pred[a_field],
            "window_B_strict_pred": window_strict_pred[b_field],
            "window_A_pred": window_pred[a_field],
            "window_B_pred": window_pred[b_field],
            "window_A_key_status": window_key_status[a_field],
            "window_B_key_status": window_key_status[b_field],
            "window_pair_class": pair_class(window_pred[a_field], window_pred[b_field], a_old, b_old, a_new, b_new),
            "window_A_old_correct": window_pred[a_field] == a_old,
            "window_B_old_correct": window_pred[b_field] == b_old,
            "window_pair_old_correct": window_pred[a_field] == a_old and window_pred[b_field] == b_old,
            "full_to_window": (
                ("correct" if full_pred[a_field] == a_old and full_pred[b_field] == b_old else "wrong")
                + "_to_"
                + ("correct" if window_pred[a_field] == a_old and window_pred[b_field] == b_old else "wrong")
            ),
            "record_excerpt": expected_record,
            "notice_excerpt": expected_notice,
            "full_record_offset": full_task["prompt"].index(expected_record),
            "full_notice_offset": full_task["prompt"].index(expected_notice),
            "window_record_offset": window_task["prompt"].index(expected_record),
            "window_notice_offset": window_task["prompt"].index(expected_notice),
            "ranking_fulltable_batch": rank_task["batch_id"],
            "ranking_same_commentary_as_full_q4": full_task["text_sha"] == rank_task["text_sha"],
            "same_model_digest": full_task["model_digest"] == window_task["model_digest"],
            "same_decode_settings": full_task["decode_json"] == window_task["decode_json"],
            "same_input_and_prompt_version": (
                full_task["input_version"] == window_task["input_version"]
                and full_task["prompt_version"] == window_task["prompt_version"]
            ),
            "full_narrative_chars": len(full_narrative),
            "window_narrative_chars": len(window_narrative),
            "window_narrative_is_literal_substring_of_full": window_narrative in full_narrative,
        }
    )


visibility_detail = []
visibility_events = []
for sample in samples:
    match = sample["match"]
    innings_num = int(str(sample["innings"]).replace("inn", ""))
    rank_task = rank_by_match[match]
    commentary = commentary_from_prompt(rank_task["prompt"])
    narrative = before_record(commentary)
    source_bowlers = V.load_bundle(match)["md"].innings[innings_num - 1].bowlers
    ranked = []
    for source_index, bowler in enumerate(source_bowlers):
        post_wickets = bowler.wickets
        if bowler.name == sample["A"]:
            post_wickets -= 1
        if bowler.name == sample["B"]:
            post_wickets += 1
        ranked.append(
            {
                "name": bowler.name,
                "old_wickets": bowler.wickets,
                "runs": bowler.runs_conceded,
                "post_wickets": post_wickets,
                "source_index": source_index,
            }
        )
    ranked.sort(key=lambda row: (-row["post_wickets"], row["runs"], row["source_index"]))
    second = ranked[1]
    for rank, bowler in enumerate(ranked, 1):
        is_a = bowler["name"] == sample["A"]
        is_b = bowler["name"] == sample["B"]
        record_notice_derived = is_a or is_b
        exact_source_figure = exact_figure_visible(narrative, bowler["name"], bowler["old_wickets"], bowler["runs"])
        direct_wickets = direct_wickets_visible(narrative, bowler["name"], bowler["old_wickets"])
        if record_notice_derived:
            post_pair_visibility = "record_plus_notice"
        elif exact_source_figure:
            post_pair_visibility = "explicit_old_pair_unchanged"
        else:
            post_pair_visibility = "not_explicit"
        visibility_detail.append(
            {
                "audit_version": VERSION,
                "match": match,
                "innings": sample["innings"],
                "ranking_batch": rank_task["batch_id"],
                "ranking_text_sha256": rank_task["text_sha"],
                "bowler": bowler["name"],
                "source_order": bowler["source_index"],
                "old_wickets": bowler["old_wickets"],
                "post_notice_wickets": bowler["post_wickets"],
                "runs": bowler["runs"],
                "post_notice_rank_stable_source_order": rank,
                "role": "top2" if rank <= 2 else ("third" if rank == 3 else "other_competitor"),
                "ties_second_on_wickets": bowler["post_wickets"] == second["post_wickets"],
                "is_notice_A_or_B": record_notice_derived,
                "name_visible_in_narrative": bowler["name"].casefold() in narrative.casefold(),
                "name_occurrences_in_narrative": narrative.casefold().count(bowler["name"].casefold()),
                "exact_old_figure_explicit_in_narrative": exact_source_figure,
                "old_wicket_total_directly_explicit_in_narrative": direct_wickets,
                "post_pair_visibility": post_pair_visibility,
                "name_contexts": context_for_name(narrative, bowler["name"]),
            }
        )
    top3 = ranked[:3]
    top3_detail = [row for row in visibility_detail if row["match"] == match and row["post_notice_rank_stable_source_order"] <= 3]
    top2_pairs_known = all(row["post_pair_visibility"] != "not_explicit" for row in top3_detail[:2])
    third = top3_detail[2]
    third_need_runs = third["post_notice_wickets"] == top3_detail[1]["post_notice_wickets"]
    third_evidence_known = (
        third["post_pair_visibility"] != "not_explicit"
        if third_need_runs
        else (
            third["post_pair_visibility"] != "not_explicit"
            or third["old_wicket_total_directly_explicit_in_narrative"]
        )
    )
    all_non_top2_wickets_direct = all(
        row["post_pair_visibility"] != "not_explicit" or row["old_wicket_total_directly_explicit_in_narrative"]
        for row in visibility_detail
        if row["match"] == match and row["post_notice_rank_stable_source_order"] > 2
    )
    manifest_rows = []
    for i in (1, 2):
        prefix = f"inn{innings_num}.bowl{i}"
        manifest_rows.append(
            f'{rank_task["gold"].get(prefix + "_name")} '
            f'{rank_task["gold"].get(prefix + "_wickets")}/{rank_task["gold"].get(prefix + "_runs")}'
        )
    visibility_events.append(
        {
            "audit_version": VERSION,
            "match": match,
            "innings": sample["innings"],
            "event_batter": sample["batter"],
            "ranking_batch": rank_task["batch_id"],
            "ranking_text_sha256": rank_task["text_sha"],
            "same_commentary_as_full_q4": rank_task["text_sha"] == full_by_key[(match, MODELS[0])]["text_sha"],
            "semantic_post_top1": f'{top3[0]["name"]} {top3[0]["post_wickets"]}/{top3[0]["runs"]}',
            "semantic_post_top2": f'{top3[1]["name"]} {top3[1]["post_wickets"]}/{top3[1]["runs"]}',
            "semantic_post_third": f'{top3[2]["name"]} {top3[2]["post_wickets"]}/{top3[2]["runs"]}',
            "frozen_manifest_rows": " | ".join(manifest_rows),
            "manifest_matches_semantic_top2": set(manifest_rows)
            == {f'{top3[0]["name"]} {top3[0]["post_wickets"]}/{top3[0]["runs"]}', f'{top3[1]["name"]} {top3[1]["post_wickets"]}/{top3[1]["runs"]}'},
            "top2_exact_pairs_model_visible": top2_pairs_known,
            "third_ties_second_on_wickets": third_need_runs,
            "third_required_evidence_model_visible": third_evidence_known,
            "all_other_competitor_wicket_totals_direct": all_non_top2_wickets_direct,
            "ranking_fully_resolvable_from_explicit_figures": top2_pairs_known and third_evidence_known and all_non_top2_wickets_direct,
            "critical_competitors": MANUAL_VISIBILITY[match]["critical_competitors"],
            "visible_evidence": MANUAL_VISIBILITY[match]["visible_evidence"],
            "missing_evidence": MANUAL_VISIBILITY[match]["missing_evidence"],
            "manual_top2_membership_resolvable": MANUAL_VISIBILITY[match]["top2_membership_resolvable"],
            "manual_top2_order_resolvable": MANUAL_VISIBILITY[match]["top2_order_resolvable"],
            "manual_third_identity_resolvable": MANUAL_VISIBILITY[match]["third_identity_resolvable"],
            "manual_third_reason": MANUAL_VISIBILITY[match]["third_reason"],
            "complete_top3_numeric_rows_explicit": False,
            "visibility_note": "manual disposition distinguishes derivable wicket events from directly stated wickets/runs pairs",
        }
    )


pair_summary = []
for mode in ("full", "window"):
    class_field = f"{mode}_pair_class"
    correct_field = f"{mode}_pair_old_correct"
    counts = Counter(row[class_field] for row in paired_rows)
    pair_summary.append(
        {
            "input_mode": mode,
            "old_pair_correct": sum(row[correct_field] for row in paired_rows),
            "total": len(paired_rows),
            "old_pair": counts["old_pair"],
            "new_pair": counts["new_pair"],
            "A_old_B_new": counts["A_old_B_new"],
            "A_new_B_old": counts["A_new_B_old"],
            "other_or_missing": counts["other_or_missing"],
        }
    )

model_summary = []
for model in MODELS:
    rows = [row for row in paired_rows if row["model"] == model]
    model_summary.append(
        {
            "model": model,
            "events": len(rows),
            "full_old_pair_correct": sum(row["full_pair_old_correct"] for row in rows),
            "window_old_pair_correct": sum(row["window_pair_old_correct"] for row in rows),
            "wrong_to_correct": sum(row["full_to_window"] == "wrong_to_correct" for row in rows),
            "correct_to_wrong": sum(row["full_to_window"] == "correct_to_wrong" for row in rows),
            "both_wrong": sum(row["full_to_window"] == "wrong_to_wrong" for row in rows),
            "both_correct": sum(row["full_to_window"] == "correct_to_correct" for row in rows),
        }
    )


write_csv(HERE / "N2_Q4_FULL_WINDOW_AUDIT.csv", paired_rows)
write_csv(HERE / "N2_RANKING_VISIBILITY_DETAIL.csv", visibility_detail)
write_csv(HERE / "N2_RANKING_VISIBILITY_EVENTS.csv", visibility_events)
write_csv(HERE / "N2_Q4_SUMMARY.csv", pair_summary)
write_csv(HERE / "N2_Q4_MODEL_SUMMARY.csv", model_summary)

source_inventory = []
source_hashes = {}
for path in source_paths:
    digest = sha256_file(path)
    source_hashes[str(path)] = digest
    source_inventory.append(
        {
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": digest,
            "read_only": True,
        }
    )
write_csv(HERE / "SOURCE_INVENTORY.csv", source_inventory)
source_hash_path = HERE / "SOURCE_HASHES.json"
source_hash_payload = {"audit_version": VERSION, "files": source_hashes}
if source_hash_path.exists():
    previous = json.loads(source_hash_path.read_text(encoding="utf-8"))
    if previous != source_hash_payload:
        raise RuntimeError("source hashes changed after this audit version was created")
source_hash_path.write_text(json.dumps(source_hash_payload, ensure_ascii=False, indent=2), encoding="utf-8")

payload = {
    "audit_version": VERSION,
    "paired_rows": len(paired_rows),
    "full_old_pair_correct": sum(row["full_pair_old_correct"] for row in paired_rows),
    "window_old_pair_correct": sum(row["window_pair_old_correct"] for row in paired_rows),
    "transitions": dict(Counter(row["full_to_window"] for row in paired_rows)),
    "full_pair_classes": dict(Counter(row["full_pair_class"] for row in paired_rows)),
    "window_pair_classes": dict(Counter(row["window_pair_class"] for row in paired_rows)),
    "ranking_events": len(visibility_events),
    "ranking_fully_resolvable_from_explicit_figures": sum(
        row["ranking_fully_resolvable_from_explicit_figures"] for row in visibility_events
    ),
    "ranking_top2_resolvable_from_visible_text": sum(
        row["manual_top2_membership_resolvable"] and row["manual_top2_order_resolvable"]
        for row in visibility_events
    ),
    "ranking_third_identity_resolvable_from_visible_text": sum(
        row["manual_third_identity_resolvable"] for row in visibility_events
    ),
    "complete_top3_numeric_rows_explicit": sum(
        row["complete_top3_numeric_rows_explicit"] for row in visibility_events
    ),
    "full_rows_with_identity_key_alias": sum(
        row["full_A_key_status"] != "exact" or row["full_B_key_status"] != "exact" for row in paired_rows
    ),
    "window_rows_with_identity_key_alias": sum(
        row["window_A_key_status"] != "exact" or row["window_B_key_status"] != "exact" for row in paired_rows
    ),
}
(HERE / "summary.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def model_short(model):
    if model.startswith("qwen"):
        return "Qwen"
    if model.startswith("llama"):
        return "Llama"
    return "Gemma"


def pair_text(a, b):
    return f"{a if a is not None else '∅'},{b if b is not None else '∅'}"


report = []
report.append("# N2 全文旧值回答与排名可见性审计")
report.append("")
report.append(f"版本：`{VERSION}`。源 manifest、原始 JSONL 和记分表均只读。")
report.append("")
report.append("## 结论")
report.append("")
report.append("- 题目要求的是通知前旧值。每个 prompt 都直接写出 `Pre-revision record`，但紧接着又写 `Update both bowlers' figures`。因此金标时点明确，模型输入本身却同时包含面向新值的末尾指令。")
report.append("- 24 条全文旧值回答为 0/24 全对：20 条直接给出新数对，2 条为 A 旧/B 新，2 条为 A 新/B 旧。没有空白数值；其中 2 条使用下划线姓名键，内容可按人物唯一恢复。")
report.append("- 配对窗口为 10/24 全对。Gemma 8/8，Qwen 2/8，Llama 0/8；全文到窗口有 10 条错→对、14 条仍错，没有对→错。")
report.append("- 全文 q4 与整表 N2 在 8 场的 `text_sha` 全部一致。排名可见性可以在同一实际正文上审，不是仅按比赛编号推断。")
report.append("- 严格要求正文直接给出 top-3 的姓名、wickets、runs 时，8 场均不完整。两场甚至无法从可见文本唯一决定 top-2：`match_0008` 缺 Evan Reed 的 27 runs，`match_0010` 缺 Luke Barrett 的 38 runs；两人都与另一候选同 wickets。")
report.append("- 若允许逐句数 dismissal，6/8 场的 top-2 可以推导；第三名身份只有 3/8 可唯一确定。所有 8 场都缺至少一名非通知竞争者的完整 wickets/runs 数对。")
report.append("")
report.append("## 24 条全文与窗口逐条对照")
report.append("")
report.append("数对顺序均为 A,B；`old` 是评分目标，`new` 是执行通知后的值。原始 JSON 字符串、键名状态、哈希和偏移见逐行 CSV。")
report.append("")
report.append("| 比赛 | 模型 | A / B | old | new | 全文原答 | 类型 | 窗口原答 | 类型 |")
report.append("|---|---|---|---:|---:|---:|---|---:|---|")
for row in sorted(paired_rows, key=lambda item: (item["match"], MODELS.index(item["model"]))):
    report.append(
        f'| {row["match"]} | {model_short(row["model"])} | {row["bowler_A"]} / {row["bowler_B"]} '
        f'| {row["A_old_wickets"]},{row["B_old_wickets"]} | {row["A_new_wickets"]},{row["B_new_wickets"]} '
        f'| {pair_text(row["full_A_pred"], row["full_B_pred"])} | {row["full_pair_class"]} '
        f'| {pair_text(row["window_A_pred"], row["window_B_pred"])} | {row["window_pair_class"]} |'
    )
report.append("")
report.append("两条窗口 `other_or_missing` 均非无法解析：`match_0012` Llama 为 3,4，`match_0017` Llama 为 4,2。`match_0015` 和 `match_0030` 的 Llama 用下划线连接姓名；本审计保留严格键状态，同时按唯一人物身份恢复数值。")
report.append("")
report.append("## 排名所需第三名和竞争者")
report.append("")
report.append("| 比赛 | 通知后 top-2 | 源表第三名 | 关键竞争者 | 正文可见证据 | 缺失数据 | top-2 可定 | 第三名可定 |")
report.append("|---|---|---|---|---|---|---|---|")
for row in visibility_events:
    top2 = f'{row["semantic_post_top1"]} / {row["semantic_post_top2"]}'
    competitors = row["critical_competitors"].replace(" | ", " / ")
    report.append(
        f'| {row["match"]} | {top2} | {row["semantic_post_third"]} | {competitors} '
        f'| {row["visible_evidence"]} | {row["missing_evidence"]} '
        f'| {"是" if row["manual_top2_membership_resolvable"] and row["manual_top2_order_resolvable"] else "否"} '
        f'| {"是" if row["manual_third_identity_resolvable"] else "否"} |'
    )
report.append("")
report.append("这里的“可定”允许跨句累计明确归属的 wickets；它不等于完整数值行已写在正文。严格的完整数值证据仍为 0/8。源表排序采用 wickets 降序、runs 升序；同 wickets 时缺少 runs 就不能用隐藏的源行序代替。")
report.append("")
report.append("## 可复查文件")
report.append("")
report.append("- `N2_Q4_FULL_WINDOW_AUDIT.csv`：24 条配对逐行证据，含 prompt/text/raw 哈希、旧新值、原始回答、恢复键状态和原句偏移。")
report.append("- `N2_RANKING_VISIBILITY_EVENTS.csv`：8 场排名结论。")
report.append("- `N2_RANKING_VISIBILITY_DETAIL.csv`：所有源表投手逐人数据及模型可见上下文。")
report.append("- `SOURCE_INVENTORY.csv`：只读输入文件的 SHA-256。")
(HERE / "N2_OLDVALUE_AND_RANKING_REVIEW.md").write_text("\n".join(report) + "\n", encoding="utf-8")

deliverables = [
    "N2_OLDVALUE_AND_RANKING_REVIEW.md",
    "N2_Q4_FULL_WINDOW_AUDIT.csv",
    "N2_Q4_SUMMARY.csv",
    "N2_Q4_MODEL_SUMMARY.csv",
    "N2_RANKING_VISIBILITY_EVENTS.csv",
    "N2_RANKING_VISIBILITY_DETAIL.csv",
    "SOURCE_INVENTORY.csv",
    "SOURCE_HASHES.json",
    "summary.json",
]
version_manifest = {
    "audit_version": VERSION,
    "source_files_mutated": False,
    "deliverables": {
        name: {"bytes": (HERE / name).stat().st_size, "sha256": sha256_file(HERE / name)}
        for name in deliverables
    },
}
(HERE / "VERSION_MANIFEST.json").write_text(
    json.dumps(version_manifest, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps(payload, ensure_ascii=False, indent=2))
