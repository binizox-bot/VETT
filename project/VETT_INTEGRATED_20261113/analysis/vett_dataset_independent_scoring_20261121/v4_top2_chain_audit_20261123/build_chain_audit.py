from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
ANALYSIS = ROOT / "VETT_INTEGRATED_20261113" / "analysis"
WF = ANALYSIS / "vett_autonomous_20261117"
BATCHES = WF / "batches"
RUNS = WF / "runs"
V3 = ANALYSIS / "vett_dataset_independent_scoring_20261121" / "v3_identity_rank_rescore_20261123"
PREV = ANALYSIS / "vett_dataset_independent_scoring_20261121" / "n2_prompt_rank_patches_20261123_v1"
SAMPLES_PATH = ANALYSIS / "attribution_followup" / "samples.json"
DIFFS_PATH = ANALYSIS / "vett_top2_20261123" / "NEUTRAL_DIFFS.json"

VERSION = "score-v4-top2-chain-20261123"
MODELS = ["qwen2.5:7b-instruct-q4_K_M", "llama3.1:8b", "gemma2:9b"]
MODEL_SHORT = {
    "qwen2.5:7b-instruct-q4_K_M": "Qwen",
    "llama3.1:8b": "Llama",
    "gemma2:9b": "Gemma",
}
ARMS = ["N0", "N1", "N2"]
FULL_BATCHES = ["B247", "B228", "B229", "B230", "B231", "B232", "B233", "B234", "B235"]
CHAIN_BATCHES = ["B254", "B255", "B248", "B253"] + FULL_BATCHES


class Pairs(list):
    pass


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def norm_name(value) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    while re.search(r"\s*\([^)]*\)\s*$", s):
        s = re.sub(r"\s*\([^)]*\)\s*$", "", s).strip()
    return re.sub(r"\s+", " ", s).casefold()


def int_value(value):
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    try:
        return int(str(value).strip().replace(",", ""))
    except Exception:
        return None


def canonical(value):
    if value is None:
        return ("null", None)
    if isinstance(value, bool):
        return ("bool", value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return ("number", float(value))
    return ("string", re.sub(r"\s+", " ", str(value).strip()).casefold())


SCALAR_RE = re.compile(
    r'"(?P<key>(?:\\.|[^"\\])*)"\s*:\s*'
    r'(?P<value>"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|true|false|null)',
    re.I,
)


def parse_scalar(token: str):
    if token.startswith('"'):
        try:
            return json.loads(token)
        except Exception:
            return token[1:-1]
    low = token.casefold()
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


def collect_scalar_pairs(obj, out: list[tuple[str, object]]) -> None:
    if isinstance(obj, Pairs):
        for key, value in obj:
            if isinstance(value, (Pairs, list)):
                collect_scalar_pairs(value, out)
            else:
                out.append((str(key), value))
    elif isinstance(obj, list):
        for value in obj:
            collect_scalar_pairs(value, out)


def recover_scalar_fields(raw: str) -> dict:
    raw = raw or ""
    root = None
    try:
        root = json.loads(raw, object_pairs_hook=Pairs)
    except Exception:
        fenced = re.fullmatch(r"\s*```(?:json)?\s*(\{.*\})\s*```\s*", raw, re.I | re.S)
        if fenced:
            try:
                root = json.loads(fenced.group(1), object_pairs_hook=Pairs)
            except Exception:
                root = None
    pairs: list[tuple[str, object]] = []
    source = "json" if root is not None else "token_recovery"
    if root is not None:
        collect_scalar_pairs(root, pairs)
    else:
        for m in SCALAR_RE.finditer(raw):
            try:
                key = json.loads('"' + m.group("key") + '"')
            except Exception:
                key = m.group("key")
            pairs.append((key, parse_scalar(m.group("value"))))
    grouped: dict[str, list] = defaultdict(list)
    order: list[str] = []
    for key, value in pairs:
        if key not in grouped:
            order.append(key)
        grouped[key].append(value)
    fields = {}
    for key in order:
        values = grouped[key]
        variants = {canonical(v) for v in values}
        fields[key] = {
            "status": "conflict" if len(variants) > 1 else ("duplicate_same" if len(values) > 1 else "unique"),
            "value": None if len(variants) > 1 else values[0],
            "values": values,
        }
    return {"root": root, "source": source if fields else "unrecoverable", "fields": fields, "order": order}


def strict_flat(recovery: dict, expected_fields: list[str]) -> tuple[bool, str]:
    root = recovery["root"]
    if not isinstance(root, Pairs):
        return False, "invalid_json_or_root"
    keys = [str(k) for k, _ in root]
    if len(keys) != len(set(keys)):
        return False, "duplicate_key"
    if set(keys) != set(expected_fields) or len(keys) != len(expected_fields):
        return False, "wrong_key_set"
    if any(isinstance(v, (Pairs, list)) for _, v in root):
        return False, "nonscalar_value"
    return True, "pass"


def field_value(recovery: dict, key: str):
    x = recovery["fields"].get(key)
    if x is None:
        return "missing", None
    return x["status"], x["value"]


def score_fields(task: dict, raw: str) -> dict:
    recovery = recover_scalar_fields(raw)
    strict, strict_reason = strict_flat(recovery, task["fields"])
    cells = {}
    counts = Counter()
    for key in task["fields"]:
        status, pred = field_value(recovery, key)
        gold = task["gold"].get(key)
        if status == "conflict":
            result = "undetermined"
        elif status == "missing":
            result = "missing"
        elif isinstance(gold, (int, float)) and not isinstance(gold, bool):
            result = "correct" if int_value(pred) == int(gold) else "wrong"
        else:
            result = "correct" if str(pred).strip().casefold() == str(gold).strip().casefold() else "wrong"
        counts[result] += 1
        cells[key] = {"gold": gold, "pred": pred, "source_status": status, "result": result}
    return {
        "strict_format_pass": strict,
        "strict_reason": strict_reason,
        "recovery_source": recovery["source"],
        "recovered_field_count": len(recovery["fields"]),
        "counts": counts,
        "cells": cells,
        "recovery": recovery,
    }


def recover_bowlers(raw: str) -> dict:
    raw = raw or ""
    root_pairs = None
    root_std = None
    try:
        root_pairs = json.loads(raw, object_pairs_hook=Pairs)
        root_std = json.loads(raw)
    except Exception:
        fenced = re.fullmatch(r"\s*```(?:json)?\s*(\{.*\})\s*```\s*", raw, re.I | re.S)
        if fenced:
            try:
                root_pairs = json.loads(fenced.group(1), object_pairs_hook=Pairs)
                root_std = json.loads(fenced.group(1))
            except Exception:
                pass
    strict = False
    strict_reason = "invalid_json"
    values = None
    source = "unrecoverable"
    if isinstance(root_pairs, Pairs):
        keys = [str(k) for k, _ in root_pairs]
        if keys == ["bowlers"] and isinstance(root_std.get("bowlers"), list) and len(root_std["bowlers"]) == 2 and all(isinstance(x, str) for x in root_std["bowlers"]):
            strict = True
            strict_reason = "pass"
        else:
            strict_reason = "wrong_schema"
        candidate = root_std.get("bowlers") if isinstance(root_std, dict) else None
        if isinstance(candidate, list) and len(candidate) >= 2:
            values = [str(candidate[0]), str(candidate[1])]
            source = "json"
    if values is None:
        m = re.search(r'"bowlers"\s*:\s*(\[[^\]]*\])', raw, re.I | re.S)
        if m:
            try:
                candidate = json.loads(m.group(1))
                if isinstance(candidate, list) and len(candidate) >= 2:
                    values = [str(candidate[0]), str(candidate[1])]
                    source = "token_recovery"
            except Exception:
                pass
    return {"strict_format_pass": strict, "strict_reason": strict_reason, "recovery_source": source, "bowlers": values}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    if not rows:
        raise AssertionError(f"empty output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]), extrasaction="raise")
        w.writeheader()
        w.writerows(rows)


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_rank_names(text: str) -> list[str]:
    rows = []
    for part in text.split(" | "):
        m = re.match(r"^(.*?)\s+(?:-?\d+|None)/(?:-?\d+|None)$", part.strip())
        if not m:
            raise AssertionError(f"cannot parse rank row: {part}")
        rows.append(m.group(1))
    return rows


def bool_csv(value) -> bool:
    return str(value).casefold() == "true"


samples = {x["match"]: x for x in read_json(SAMPLES_PATH)[:8]}
matches = list(samples)

manifests: dict[str, dict] = {}
runs: dict[str, list[dict]] = {}
tasks_by_key: dict[str, dict] = {}
runs_by_key: dict[str, dict] = {}
source_paths: list[Path] = [SAMPLES_PATH, V3 / "SCORING_CONTRACT.md", V3 / "fulltable_rescore_rows.csv", DIFFS_PATH]
for batch in sorted(set(CHAIN_BATCHES + ["B256"])):
    mp = BATCHES / f"{batch}.json"
    rp = RUNS / f"{batch}.jsonl"
    manifests[batch] = read_json(mp)
    runs[batch] = read_jsonl(rp)
    source_paths += [mp, rp]
    for task in manifests[batch]["tasks"]:
        tasks_by_key[task["task_key"]] = task | {"batch_id": batch}
    for run in runs[batch]:
        runs_by_key[run["task_key"]] = run

with (V3 / "fulltable_rescore_rows.csv").open(encoding="utf-8-sig", newline="") as f:
    full_v3_rows = list(csv.DictReader(f))
assert len(full_v3_rows) == 72
full_v3 = {(r["match"], r["model"], r["arm"]): r for r in full_v3_rows}


# Model-visible answerability. N0/N1 are not assumed answerable merely because A/B are named.
answerable_roots = {
    "N0": {"match_0008", "match_0017", "match_0026"},
    "N1": {"match_0008", "match_0017", "match_0026"},
    "N2": {"match_0003", "match_0012", "match_0015", "match_0017", "match_0026", "match_0030"},
}
answer_reasons = {
    ("match_0003", "N0"): "Evan Clarke is first on 4; Connor Reed, Caleb Price and Gavin Turner each have 1. Competitor runs are absent, so row 2 is not unique.",
    ("match_0003", "N1"): "The maintain notice leaves the same 1-wicket cutoff tie; competitor runs remain absent.",
    ("match_0003", "N2"): "After reassignment Evan Clarke has 3 and Connor Reed 2; every other visible wicket-taker has at most 1.",
    ("match_0008", "N0"): "Luke Barrett and Ryan Frost each have 3; visible runs 30 and 37 order the unique top two above Evan Reed on 2.",
    ("match_0008", "N1"): "Maintain leaves the same uniquely identified and ordered 3-wicket pair.",
    ("match_0008", "N2"): "Ryan Frost has 4; Evan Reed and Luke Barrett each have 2. Evan Reed's runs are absent, so rows 2/3 are unresolved.",
    ("match_0010", "N0"): "Ryan Foster has 3; Evan Turner and Luke Barrett each have 2. Luke Barrett's runs are absent, so row 2 is not unique.",
    ("match_0010", "N1"): "Maintain leaves the same 2-wicket cutoff tie; Luke Barrett's runs remain absent.",
    ("match_0010", "N2"): "Evan Turner has 3; Luke Barrett and Ryan Foster each have 2. Luke Barrett's runs are absent, so rows 2/3 are unresolved.",
    ("match_0012", "N0"): "Caleb Brooks has 4; Lucas Vale, Liam Frost and Noah Grant each have 2. Competitor runs are absent.",
    ("match_0012", "N1"): "Maintain leaves the same three-way 2-wicket cutoff group without competitor runs.",
    ("match_0012", "N2"): "Lucas Vale and Caleb Brooks each have 3; their visible runs 44 and 56 uniquely determine both rows.",
    ("match_0015", "N0"): "Noah Grant has 4; Caleb Rourke and Mason Hart each have 2. Mason Hart's runs are absent.",
    ("match_0015", "N1"): "Maintain leaves the same 2-wicket cutoff tie without Mason Hart's runs.",
    ("match_0015", "N2"): "Caleb Rourke and Noah Grant each have 3; visible runs 41 and 62 uniquely order them above Mason Hart on 2.",
    ("match_0017", "N0"): "Miles Carter has 5 and Liam Brooks 3; the next visible competitor has 2.",
    ("match_0017", "N1"): "Maintain leaves the same unique 5/3-wicket leaders.",
    ("match_0017", "N2"): "Miles Carter and Liam Brooks each have 4; visible runs 18 and 27 uniquely order them.",
    ("match_0026", "N0"): "Dylan Cole has 5 and Ben Carter 2; the next visible competitor has 1.",
    ("match_0026", "N1"): "Maintain leaves the same unique 5/2-wicket leaders.",
    ("match_0026", "N2"): "Dylan Cole has 4 and Ben Carter 3; every other visible wicket-taker has at most 1.",
    ("match_0030", "N0"): "Logan Vale has 4; Owen Price, Caleb Hart and Connor Blake each have 2. Competitor runs are absent.",
    ("match_0030", "N1"): "Maintain leaves the same three-way 2-wicket cutoff group without competitor runs.",
    ("match_0030", "N2"): "Owen Price and Logan Vale each have 3; visible runs 1 and 10 uniquely order them above the 2-wicket group.",
}


def find_task(batch_ids: list[str], match: str, model: str, arm: str, text_sha: str | None = None) -> dict:
    found = []
    for batch in batch_ids:
        for task in manifests[batch]["tasks"]:
            if task["match"] != match or task["model"] != model:
                continue
            task_arm = task["cond"].replace("T2_", "").split("_")[0]
            if task_arm != arm:
                continue
            if text_sha is not None and task["text_sha"] != text_sha:
                continue
            found.append(task | {"batch_id": batch})
    if len(found) != 1:
        raise AssertionError((batch_ids, match, model, arm, text_sha, len(found)))
    return found[0]


answerability_rows = []
chain_rows = []
for match in matches:
    sample = samples[match]
    for arm in ARMS:
        base_v3 = full_v3[(match, MODELS[0], arm)]
        expected_names = parse_rank_names(base_v3["semantic_rows"])
        answerable = match in answerable_roots[arm]
        answerability_rows.append(
            {
                "scoring_version": VERSION,
                "match": match,
                "innings": sample["innings"],
                "notification": arm,
                "top2_membership_and_order_determinable_from_model_text": answerable,
                "reason": answer_reasons[(match, arm)],
                "oracle_legal_top2": " | ".join(expected_names),
                "comparison_disposition": "include" if answerable else "exclude_not_executable_input",
            }
        )
        for model in MODELS:
            v3 = full_v3[(match, model, arm)]
            top_task = find_task(["B254", "B255"], match, model, arm)
            partial_task = find_task(["B253"] if arm == "N0" else ["B248"], match, model, arm, top_task["text_sha"])
            full_task = tasks_by_key[v3["task_key"]]
            if not (top_task["text_sha"] == partial_task["text_sha"] == full_task["text_sha"] == v3["text_sha256"]):
                raise AssertionError(f"text mismatch: {match} {model} {arm}")

            top_run = runs_by_key[top_task["task_key"]]
            partial_run = runs_by_key[partial_task["task_key"]]
            full_run = runs_by_key[full_task["task_key"]]
            top_parsed = recover_bowlers(top_run.get("raw_output", ""))
            partial_score = score_fields(partial_task, partial_run.get("raw_output", ""))
            pred_names = top_parsed["bowlers"]
            if not answerable:
                top_member = "not_executable_input"
                top_order = "not_executable_input"
            elif pred_names is None or len(pred_names) != 2 or len({norm_name(x) for x in pred_names}) != 2:
                top_member = "undetermined_output_identity"
                top_order = "undetermined_output_identity"
            else:
                expected_set = {norm_name(x) for x in expected_names}
                pred_set = {norm_name(x) for x in pred_names}
                top_member = "correct" if pred_set == expected_set else "wrong"
                top_order = "correct" if [norm_name(x) for x in pred_names] == [norm_name(x) for x in expected_names] else ("wrong" if top_member == "correct" else "wrong_member_set")

            full_member_oracle = v3["member_set_status"]
            full_order_oracle = v3["row_order_status"]
            full_member_fair = full_member_oracle if answerable else "not_executable_input"
            full_order_fair = full_order_oracle if answerable else "not_executable_input"
            top_correct = top_member == "correct"
            full_correct = full_member_oracle in ("correct", "correct_tie_accepted")
            if not answerable:
                direction = "not_comparable_input"
            elif top_correct and not full_correct:
                direction = "top2_correct_fulltable_wrong"
            elif not top_correct and full_correct:
                direction = "top2_wrong_fulltable_correct"
            elif top_correct and full_correct:
                direction = "both_member_sets_correct"
            else:
                direction = "both_member_sets_wrong_or_undetermined"

            observed_names = parse_rank_names(v3["observed_rows"])
            exp_set = {norm_name(x) for x in expected_names}
            obs_set = {norm_name(x) for x in observed_names if x not in ("None", "")}
            missing_expected = [x for x in expected_names if norm_name(x) not in obs_set]
            unexpected = [x for x in observed_names if norm_name(x) not in exp_set]
            if full_correct:
                full_identity_error = "none"
            elif len(obs_set) < 2:
                full_identity_error = "missing_or_duplicate_row"
            elif missing_expected and unexpected:
                full_identity_error = "replacement"
            else:
                full_identity_error = "other_identity_error"

            person_fields = [k for k in partial_task["fields"] if k != "innings_total_wickets"]
            person_results = [partial_score["cells"][k]["result"] for k in person_fields]
            if all(x == "correct" for x in person_results):
                partial_person_status = "correct"
            elif any(x == "undetermined" for x in person_results):
                partial_person_status = "wrong_and_or_undetermined" if any(x in ("wrong", "missing") for x in person_results) else "undetermined"
            else:
                partial_person_status = "wrong"
            total_result = partial_score["cells"]["innings_total_wickets"]["result"]

            legal_norm = {norm_name(x) for x in expected_names}
            named_A_legal = norm_name(sample["A"]) in legal_norm
            named_B_legal = norm_name(sample["B"]) in legal_norm
            chain_rows.append(
                {
                    "scoring_version": VERSION,
                    "match": match,
                    "innings": sample["innings"],
                    "event": sample["batter"],
                    "model": model,
                    "model_short": MODEL_SHORT[model],
                    "notification": arm,
                    "text_sha256": top_task["text_sha"],
                    "input_top2_determinable": answerable,
                    "input_answerability_reason": answer_reasons[(match, arm)],
                    "oracle_legal_top2": " | ".join(expected_names),
                    "named_A": sample["A"],
                    "named_B": sample["B"],
                    "named_A_in_legal_top2": named_A_legal,
                    "named_B_in_legal_top2": named_B_legal,
                    "top2_batch": top_task["batch_id"],
                    "top2_task_key": top_task["task_key"],
                    "top2_raw_output_sha256": sha_text(top_run.get("raw_output", "")),
                    "top2_raw_output": top_run.get("raw_output", ""),
                    "top2_recovered_names": " | ".join(pred_names or []),
                    "top2_strict_format_pass": top_parsed["strict_format_pass"],
                    "top2_recovery_source": top_parsed["recovery_source"],
                    "top2_member_set_status_fair": top_member,
                    "top2_row_order_status_fair": top_order,
                    "partial_batch": partial_task["batch_id"],
                    "partial_task_key": partial_task["task_key"],
                    "partial_raw_output_sha256": sha_text(partial_run.get("raw_output", "")),
                    "partial_raw_output": partial_run.get("raw_output", ""),
                    "partial_strict_format_pass": partial_score["strict_format_pass"],
                    "partial_recovery_source": partial_score["recovery_source"],
                    "partial_recovered_field_count": partial_score["recovered_field_count"],
                    "partial_person_values_correct": sum(x == "correct" for x in person_results),
                    "partial_person_values_total": len(person_fields),
                    "partial_person_values_status": partial_person_status,
                    "partial_team_total_status": total_result,
                    "fulltable_batch": full_task["batch_id"],
                    "fulltable_task_key": full_task["task_key"],
                    "fulltable_raw_output_sha256": sha_text(full_run.get("raw_output", "")),
                    "fulltable_raw_output": full_run.get("raw_output", ""),
                    "fulltable_strict_format_pass": bool_csv(v3["strict_format_pass"]),
                    "fulltable_recovery_source": v3["recovery_source"],
                    "fulltable_recovered_field_count": v3["recovered_field_count"],
                    "fulltable_observed_rows": v3["observed_rows"],
                    "fulltable_member_set_status_oracle": full_member_oracle,
                    "fulltable_row_order_status_oracle": full_order_oracle,
                    "fulltable_person_values_status_oracle": v3["identity_value_status"],
                    "fulltable_team_total_status": v3["total_status"],
                    "fulltable_member_set_status_fair": full_member_fair,
                    "fulltable_row_order_status_fair": full_order_fair,
                    "fulltable_person_values_status_fair": v3["identity_value_status"] if answerable else "not_executable_input",
                    "fulltable_identity_error_type": full_identity_error,
                    "fulltable_missing_expected_members": " | ".join(missing_expected),
                    "fulltable_unexpected_members": " | ".join(unexpected),
                    "member_set_comparison_direction": direction,
                }
            )

assert len(chain_rows) == 72
assert sum(r["input_top2_determinable"] for r in chain_rows) == 36


def summarize(rows: list[dict], group_fields: list[str], label: str) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[f] for f in group_fields)].append(row)
    out = []
    for key, group in sorted(groups.items(), key=lambda x: tuple(str(v) for v in x[0])):
        comparable = [r for r in group if r["input_top2_determinable"]]
        counts = Counter(r["member_set_comparison_direction"] for r in comparable)
        row = {"summary_level": label}
        row.update(dict(zip(group_fields, key)))
        row.update(
            {
                "all_rows": len(group),
                "comparable_rows_denominator": len(comparable),
                "comparable_independent_roots": len({r["match"] for r in comparable}),
                "top2_correct_fulltable_wrong": counts["top2_correct_fulltable_wrong"],
                "top2_wrong_fulltable_correct": counts["top2_wrong_fulltable_correct"],
                "both_member_sets_correct": counts["both_member_sets_correct"],
                "both_member_sets_wrong_or_undetermined": counts["both_member_sets_wrong_or_undetermined"],
                "top2_strict_format_pass": sum(r["top2_strict_format_pass"] for r in group),
                "partial_person_values_correct_tasks": sum(r["partial_person_values_status"] == "correct" for r in group),
                "partial_team_total_correct_tasks": sum(r["partial_team_total_status"] == "correct" for r in group),
                "fulltable_strict_format_pass": sum(r["fulltable_strict_format_pass"] for r in group),
                "fulltable_person_values_correct_comparable": sum(r["fulltable_person_values_status_fair"] == "correct" for r in comparable),
                "fulltable_team_total_correct_tasks": sum(r["fulltable_team_total_status"] == "correct" for r in group),
            }
        )
        out.append(row)
    return out


summary_model_notice = summarize(chain_rows, ["model_short", "notification"], "model_x_notification")
summary_model = summarize(chain_rows, ["model_short"], "model")
summary_notice = summarize(chain_rows, ["notification"], "notification")
summary_rows = summary_model_notice + summary_model + summary_notice

comparable_all = [r for r in chain_rows if r["input_top2_determinable"]]
forward_roots = sorted({r["match"] for r in comparable_all if r["member_set_comparison_direction"] == "top2_correct_fulltable_wrong"})
reverse_roots = sorted({r["match"] for r in comparable_all if r["member_set_comparison_direction"] == "top2_wrong_fulltable_correct"})


# B256 independent per-line expansion.
diffs = read_json(DIFFS_PATH)
arm_by_after_sha = {d["after_sha"]: d["arm"] for d in diffs}
b256_rows = []
for task in manifests["B256"]["tasks"]:
    run = runs_by_key[task["task_key"]]
    sample = samples[task["match"]]
    recovery = recover_scalar_fields(run.get("raw_output", ""))
    strict, strict_reason = strict_flat(recovery, task["fields"])
    values = []
    recovery_basis = "canonical_key"
    for expected_key in task["fields"]:
        canon_expected = re.sub(r"[^a-z0-9]", "", expected_key.casefold())
        candidates = [
            x for key, x in recovery["fields"].items()
            if re.sub(r"[^a-z0-9]", "", key.casefold()) == canon_expected and x["status"] != "conflict"
        ]
        values.append(int_value(candidates[0]["value"]) if len(candidates) == 1 else None)
    if any(v is None for v in values):
        ordered = [int_value(recovery["fields"][k]["value"]) for k in recovery["order"] if recovery["fields"][k]["status"] != "conflict"]
        ordered = [v for v in ordered if v is not None]
        if len(ordered) == 2:
            values = ordered
            recovery_basis = "two_numeric_values_in_output_order"
    pair = tuple(values) if len(values) == 2 and all(v is not None for v in values) else None
    old = (sample["Aw"], sample["Bw"])
    new = (sample["Aw"] - 1, sample["Bw"] + 1)
    if pair is None:
        category = "unrecoverable"
    elif pair == old:
        category = "fully_old"
    elif pair == new:
        category = "fully_new"
    elif pair == (new[0], old[1]):
        category = "only_original_minus1"
    elif pair == (old[0], new[1]):
        category = "only_new_plus1"
    else:
        category = "other_values"
    input_arm = arm_by_after_sha.get(task["text_sha"])
    if input_arm not in ("N2_F", "N2_W"):
        raise AssertionError(f"unknown B256 text sha: {task['text_sha']}")
    b256_rows.append(
        {
            "scoring_version": VERSION,
            "batch_id": "B256",
            "task_key": task["task_key"],
            "match": task["match"],
            "model": task["model"],
            "model_short": MODEL_SHORT[task["model"]],
            "input_arm": input_arm,
            "text_sha256": task["text_sha"],
            "raw_output_sha256": sha_text(run.get("raw_output", "")),
            "raw_output": run.get("raw_output", ""),
            "strict_format_pass": strict,
            "strict_reason": strict_reason,
            "recovery_source": recovery["source"],
            "recovery_basis": recovery_basis,
            "A_bowler": sample["A"],
            "B_bowler": sample["B"],
            "old_pair": f"{old[0]} | {old[1]}",
            "new_pair": f"{new[0]} | {new[1]}",
            "recovered_pair": "UNRECOVERABLE" if pair is None else f"{pair[0]} | {pair[1]}",
            "category": category,
            "old_pair_correct": category == "fully_old",
        }
    )
assert len(b256_rows) == 48

b256_summary = []
for (model, input_arm), group in sorted(
    defaultdict(list, {k: [r for r in b256_rows if (r["model_short"], r["input_arm"]) == k] for k in {(r["model_short"], r["input_arm"]) for r in b256_rows}}).items()
):
    c = Counter(r["category"] for r in group)
    b256_summary.append(
        {
            "scoring_version": VERSION,
            "model": model,
            "input_arm": input_arm,
            "denominator": len(group),
            "fully_old": c["fully_old"],
            "fully_new": c["fully_new"],
            "only_original_minus1": c["only_original_minus1"],
            "only_new_plus1": c["only_new_plus1"],
            "other_values": c["other_values"],
            "unrecoverable": c["unrecoverable"],
            "strict_format_pass": sum(r["strict_format_pass"] for r in group),
            "supported_statement": (
                f"{model} {input_arm}: old {c['fully_old']}/8, new {c['fully_new']}/8, "
                f"single-side {c['only_original_minus1'] + c['only_new_plus1']}/8, other/unrecoverable {c['other_values'] + c['unrecoverable']}/8."
            ),
        }
    )


chain_path = HERE / "TOP2_CHAIN_ROWS.csv"
answer_path = HERE / "TOP2_ANSWERABILITY.csv"
summary_path = HERE / "TOP2_CHAIN_SUMMARY.csv"
b256_path = HERE / "B256_LINE_REVIEW.csv"
b256_summary_path = HERE / "B256_MODEL_SUMMARY.csv"
write_csv(chain_path, chain_rows)
write_csv(answer_path, answerability_rows)
write_csv(summary_path, summary_rows)
write_csv(b256_path, b256_rows)
write_csv(b256_summary_path, b256_summary)

source_rows = []
for p in source_paths:
    source_rows.append({"path": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": sha_file(p), "bytes": p.stat().st_size, "access": "read-only"})
write_csv(HERE / "SOURCE_INVENTORY.csv", source_rows)

summary_json = {
    "scoring_version": VERSION,
    "rows": len(chain_rows),
    "comparable_rows": len(comparable_all),
    "comparable_unique_match_notification_pairs": len({(r["match"], r["notification"]) for r in comparable_all}),
    "answerable_roots_by_notification": {arm: len(answerable_roots[arm]) for arm in ARMS},
    "headline": {
        "top2_correct_fulltable_wrong_independent_roots": len(forward_roots),
        "top2_correct_fulltable_wrong_roots": forward_roots,
        "top2_wrong_fulltable_correct_independent_roots": len(reverse_roots),
        "top2_wrong_fulltable_correct_roots": reverse_roots,
    },
    "b256_rows": len(b256_rows),
}
write_json(HERE / "summary.json", summary_json)

gemma_full = next(r for r in b256_summary if r["model"] == "Gemma" and r["input_arm"] == "N2_F")
model_notice_lines = [
    "| 模型 | 通知 | 可比分母（根） | 单选对/整表错 | 单选错/整表对 | 都对 | 都错或未定 |",
    "|---|---:|---:|---:|---:|---:|---:|",
]
for x in summary_model_notice:
    model_notice_lines.append(
        f"| {x['model_short']} | {x['notification']} | {x['comparable_independent_roots']} | "
        f"{x['top2_correct_fulltable_wrong']} | {x['top2_wrong_fulltable_correct']} | "
        f"{x['both_member_sets_correct']} | {x['both_member_sets_wrong_or_undetermined']} |"
    )
model_notice_table = "\n".join(model_notice_lines)

b256_lines = [
    "| 模型 | 输入 | 旧值 | 完整新值 | 单边更新 | 其他/不可恢复 | 严格格式 |",
    "|---|---:|---:|---:|---:|---:|---:|",
]
for x in b256_summary:
    b256_lines.append(
        f"| {x['model']} | {x['input_arm']} | {x['fully_old']}/8 | {x['fully_new']}/8 | "
        f"{x['only_original_minus1'] + x['only_new_plus1']}/8 | "
        f"{x['other_values'] + x['unrecoverable']}/8 | {x['strict_format_pass']}/8 |"
    )
b256_table = "\n".join(b256_lines)
report = f"""# Top-2 单选、具名短问与直接整表逐行审计

版本：`{VERSION}`。本目录只读连接 B254/B255、B253/B248、B247/B228–B235，并独立展开 B256；未修改原始 JSONL、旧分数、SQLite、worker 或队列。

## 首页两个数

- 在可比较输入上，**单独 top-2 名单正确、直接整表却漏人或换人的情况涉及 {len(forward_roots)} 个独立比赛根**：{', '.join(forward_roots) if forward_roots else '无'}。
- 反方向，**单独 top-2 名单错误、直接整表名单反而正确的情况涉及 {len(reverse_roots)} 个独立比赛根**：{', '.join(reverse_roots) if reverse_roots else '无'}。

这两个根数是跨模型、跨通知去重后的并集。逐模型 × 通知的行数与实际分母见 `TOP2_CHAIN_SUMMARY.csv`；一行对应一个独立比赛根，因此该表每格的行数也就是该模型/通知下的根数。

## 实际分母

- N0：8 场中 3 场名单可由模型可见正文唯一确定；3 个模型合计 9/24 行进入名单比较。
- N1：8 场中 3 场可确定；合计 9/24 行进入比较。
- N2：按已核定口径 6/8 场可确定；合计 18/24 行进入比较。
- 总计 36/72 行进入名单集合与行序的公平比较。其余 36 行保留原答及 oracle 复核，但公平状态记为 `not_executable_input`。

N0/N1 不能仅因尾部列出 A/B 就视为可答。`0003`、`0010`、`0012`、`0015`、`0030` 的第二名处存在同 wicket 竞争者，而正文没有给出竞争者 runs，不能唯一确定截止线成员。N0/N1 可答根为 `0008`、`0017`、`0026`。

## 分模型 × 通知

{model_notice_table}

## 评分边界

- 名单集合和行序只在模型可见输入能唯一决定时评分。
- 具名短问按其明确点名的 A/B 分人物核对 wickets/runs，并独立核对 innings total；它不承担 top-2 成员选择。因此 N2 中原投手合法退出榜单时，不会被误记为整表漏行。
- 直接整表的成员集合、行序、人物数值和团队总数沿用 v3 的身份映射、同分和恢复规则；本表另加公平可执行状态。
- 三种输出分别按各自 prompt 的合法结构报告严格格式，并用与金标无关的恢复器报告可恢复内容。

## B256 修正

B256 已逐行展开 48 条。未经逐行支持的“Gemma 全文始终答完整新值”应删除：Gemma 全文实际为 **完整新值 {gemma_full['fully_new']}/8**、完整旧值 {gemma_full['fully_old']}/8、单边更新 {gemma_full['only_original_minus1'] + gemma_full['only_new_plus1']}/8、其他/不可恢复 {gemma_full['other_values'] + gemma_full['unrecoverable']}/8。各模型全文/窗口的完整分布见 `B256_MODEL_SUMMARY.csv`，每条原答与恢复数对见 `B256_LINE_REVIEW.csv`。

{b256_table}

## 输出

- `TOP2_CHAIN_ROWS.csv`：72 行主表，包含三类原答、哈希、批次/任务键及六个评分面。
- `TOP2_ANSWERABILITY.csv`：24 个比赛 × 通知的模型可见名单可答性依据。
- `TOP2_CHAIN_SUMMARY.csv`：按模型 × 通知、模型、通知汇总的实际分母和方向差异。
- `B256_LINE_REVIEW.csv`、`B256_MODEL_SUMMARY.csv`：B256 逐行分类与模型展开。
"""
(HERE / "TOP2_CHAIN_REVIEW.md").write_text(report, encoding="utf-8")

generated = [chain_path, answer_path, summary_path, b256_path, b256_summary_path, HERE / "SOURCE_INVENTORY.csv", HERE / "summary.json", HERE / "TOP2_CHAIN_REVIEW.md"]
manifest = {
    "scoring_version": VERSION,
    "status": "frozen_v1",
    "created_date": "2026-11-23",
    "generated_files": [{"path": p.name, "sha256": sha_file(p), "bytes": p.stat().st_size} for p in generated],
    "immutability": "Sources and prior versions are read-only. Any revision must use a new version directory.",
}
write_json(HERE / "VERSION_MANIFEST.json", manifest)

print(json.dumps(summary_json, ensure_ascii=False, indent=2))
print(json.dumps(b256_summary, ensure_ascii=False, indent=2))
