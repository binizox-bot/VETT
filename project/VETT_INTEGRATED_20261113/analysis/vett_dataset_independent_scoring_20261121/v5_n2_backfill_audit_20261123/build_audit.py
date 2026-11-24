import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


VERSION = "score-v5-n2-backfill-v4-contract-20261123"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ANALYSIS = ROOT / "VETT_INTEGRATED_20261113" / "analysis"
WF = ANALYSIS / "vett_autonomous_20261117"
BATCHES = WF / "batches"
RUNS = WF / "runs"
V4 = ANALYSIS / "vett_dataset_independent_scoring_20261121" / "v4_top2_chain_audit_20261123"

sys.path.insert(0, str(WF))
import vettlib as V  # noqa: E402


MODELS = ["qwen2.5:7b-instruct-q4_K_M", "llama3.1:8b", "gemma2:9b"]
MODEL_SHORT = {
    "qwen2.5:7b-instruct-q4_K_M": "Qwen",
    "llama3.1:8b": "Llama",
    "gemma2:9b": "Gemma",
}
ROOTS = ["match_0170", "match_0096", "match_0049", "match_0180"]


class Pairs(list):
    pass


def sha_text(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def norm(value):
    if value is None:
        return None
    text = str(value).strip()
    while re.search(r"\s*\([^)]*\)\s*$", text):
        text = re.sub(r"\s*\([^)]*\)\s*$", "", text).strip()
    return re.sub(r"\s+", " ", text).casefold()


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


def parse_scalar(token):
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


def strict_fields(root):
    if not isinstance(root, Pairs):
        return False, "invalid_json_or_root"
    if [str(k) for k, _ in root] != ["fields"]:
        return False, "root_must_contain_only_fields"
    fields = root[0][1]
    if not isinstance(fields, Pairs):
        return False, "fields_not_object"
    keys = [str(k) for k, _ in fields]
    if len(keys) != len(set(keys)):
        return False, "duplicate_key"
    if any(isinstance(v, (Pairs, list)) for _, v in fields):
        return False, "nonscalar_field"
    return True, "pass"


def recover_fields(raw):
    raw = raw or ""
    root = None
    try:
        root = json.loads(raw, object_pairs_hook=Pairs)
    except Exception:
        root = None
    strict_pass, strict_reason = strict_fields(root)
    pairs = []
    source = None
    if root is not None:
        collect_pairs(root, pairs)
        source = "strict_json" if strict_pass else "json_non_strict"
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
            for match in SCALAR_RE.finditer(raw):
                try:
                    key = json.loads('"' + match.group("key") + '"')
                except Exception:
                    key = match.group("key")
                pairs.append((str(key), parse_scalar(match.group("value"))))
            if pairs:
                source = "token_recovery"
    grouped = defaultdict(list)
    for key, value in pairs:
        grouped[key].append(value)
    fields = {}
    for key, values in grouped.items():
        variants = {canonical(v) for v in values}
        fields[key] = {
            "status": "conflict" if len(variants) > 1 else ("duplicate_same" if len(values) > 1 else "unique"),
            "value": None if len(variants) > 1 else values[0],
            "values": values,
        }
    return {
        "strict_format_pass": strict_pass,
        "strict_reason": strict_reason,
        "recovery_source": source or "unrecoverable",
        "fields": fields,
        "recovered_field_count": len(fields),
    }


def recover_bowlers(raw):
    raw = raw or ""
    pairs_root = std_root = None
    try:
        pairs_root = json.loads(raw, object_pairs_hook=Pairs)
        std_root = json.loads(raw)
    except Exception:
        fenced = re.fullmatch(r"\s*```(?:json)?\s*(\{.*\})\s*```\s*", raw, re.I | re.S)
        if fenced:
            try:
                pairs_root = json.loads(fenced.group(1), object_pairs_hook=Pairs)
                std_root = json.loads(fenced.group(1))
            except Exception:
                pass
    strict = False
    strict_reason = "invalid_json"
    names = None
    source = "unrecoverable"
    if isinstance(pairs_root, Pairs) and isinstance(std_root, dict):
        keys = [str(k) for k, _ in pairs_root]
        candidate = std_root.get("bowlers")
        if keys == ["bowlers"] and isinstance(candidate, list) and len(candidate) == 2 and all(isinstance(x, str) for x in candidate):
            strict = True
            strict_reason = "pass"
        else:
            strict_reason = "wrong_schema"
        if isinstance(candidate, list) and len(candidate) >= 2:
            names = [str(candidate[0]), str(candidate[1])]
            source = "json" if strict else "json_non_strict"
    if names is None:
        match = re.search(r'"bowlers"\s*:\s*(\[[^\]]*\])', raw, re.I | re.S)
        if match:
            try:
                candidate = json.loads(match.group(1))
                if isinstance(candidate, list) and len(candidate) >= 2:
                    names = [str(candidate[0]), str(candidate[1])]
                    source = "token_recovery"
            except Exception:
                pass
    return {
        "strict_format_pass": strict,
        "strict_reason": strict_reason,
        "recovery_source": source,
        "bowlers": names,
    }


def field_value(recovery, key):
    item = recovery["fields"].get(key)
    if item is None:
        return "missing", None
    return item["status"], item["value"]


def compare(gold, pred):
    if pred is None:
        return False
    if isinstance(gold, (int, float)) and not isinstance(gold, bool):
        return int_value(pred) == int(gold)
    return str(pred).strip().casefold() == str(gold).strip().casefold()


def score_cells(gold, fields, recovery):
    out = {}
    counts = Counter()
    for key in fields:
        status, pred = field_value(recovery, key)
        if status == "conflict":
            result = "undetermined"
        elif status == "missing":
            result = "missing"
        elif compare(gold.get(key), pred):
            result = "correct"
        else:
            result = "wrong"
        counts[result] += 1
        out[key] = {"gold": gold.get(key), "pred": pred, "source_status": status, "result": result}
    return {"cells": out, "counts": counts, "task_correct": counts["correct"] == len(fields)}


def output_target(recovery, innings):
    rows = []
    for rank in (1, 2):
        prefix = f"inn{innings}.bowl{rank}"
        name_status, name = field_value(recovery, prefix + "_name")
        wicket_status, wickets = field_value(recovery, prefix + "_wickets")
        runs_status, runs = field_value(recovery, prefix + "_runs")
        rows.append({
            "rank": rank,
            "name_status": name_status,
            "name": name,
            "wicket_status": wicket_status,
            "wickets": int_value(wickets),
            "runs_status": runs_status,
            "runs": int_value(runs),
        })
    total_status, total = field_value(recovery, f"inn{innings}.total_wickets")
    return rows, total_status, int_value(total)


def score_identity(recovery, expected, innings, team_total):
    rows, total_source, total = output_target(recovery, innings)
    observed_names = [norm(r["name"]) for r in rows if r["name_status"] in ("unique", "duplicate_same")]
    expected_names = [norm(r["name"]) for r in expected]
    if len(observed_names) != 2 or len(set(observed_names)) != 2:
        member_status = "undetermined_output_identity"
    else:
        member_status = "correct" if set(observed_names) == set(expected_names) else "wrong"
    if member_status != "correct":
        order_status = "wrong_member_set" if member_status == "wrong" else "undetermined_output_identity"
    else:
        order_status = "correct" if observed_names == expected_names else "wrong"
    per_person = []
    for target in expected:
        matches = [r for r in rows if norm(r["name"]) == norm(target["name"])]
        present = len(matches) == 1
        if not present:
            per_person.append({"name": target["name"], "present": False, "wickets": "missing_member", "runs": "missing_member"})
            continue
        observed = matches[0]
        wicket_result = "correct" if observed["wicket_status"] != "conflict" and observed["wickets"] == target["wickets"] else ("undetermined" if observed["wicket_status"] == "conflict" else "wrong")
        runs_result = "correct" if observed["runs_status"] != "conflict" and observed["runs"] == target["runs"] else ("undetermined" if observed["runs_status"] == "conflict" else "wrong")
        per_person.append({"name": target["name"], "present": True, "wickets": wicket_result, "runs": runs_result})
    both_present = all(x["present"] for x in per_person)
    all_numeric = both_present and all(x["wickets"] == "correct" and x["runs"] == "correct" for x in per_person)
    total_result = "undetermined" if total_source == "conflict" else ("correct" if total == team_total else ("missing" if total_source == "missing" else "wrong"))
    return {
        "observed_rows": rows,
        "member_status": member_status,
        "order_status": order_status,
        "per_person": per_person,
        "both_present": both_present,
        "all_person_numeric_correct": all_numeric,
        "team_total_status": total_result,
        "team_total_pred": total,
    }


def compact_rows(rows):
    return " | ".join(f"{r.get('name')} {r.get('wickets')}/{r.get('runs')}" for r in rows)


def compact_person(scores):
    return " | ".join(f"{x['name']}:present={str(x['present']).lower()},W={x['wickets']},R={x['runs']}" for x in scores)


def read_batch(batch_id):
    manifest_path = BATCHES / f"{batch_id}.json"
    run_path = RUNS / f"{batch_id}.jsonl"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    run_rows = [json.loads(line) for line in run_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return manifest, {r["task_key"]: r for r in run_rows}, manifest_path, run_path


def prompt_commentary(prompt):
    return prompt.split("\n\nCommentary:\n", 1)[1].rsplit("\n\nJSON:", 1)[0]


def find_span(text, phrase):
    start = text.find(phrase)
    if start < 0:
        raise AssertionError(f"missing evidence phrase: {phrase}")
    return start, start + len(phrase)


def semantic_event(match, event_name):
    bundle = V.load_bundle(match)
    for innings_index, innings in enumerate(bundle["md"].innings, 1):
        batter = next((x for x in innings.batters if x.name == event_name), None)
        if batter is None:
            continue
        bowled = re.search(r"\bb\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)", batter.dismissal or "")
        if not bowled:
            raise AssertionError((match, event_name, batter.dismissal))
        original = bowled.group(1)
        ranked_old = sorted(innings.bowlers, key=lambda x: (-x.wickets, x.runs_conceded, x.name))
        recipient = next(x.name for x in ranked_old if x.name != original)
        revised = []
        for bowler in innings.bowlers:
            wickets = bowler.wickets - (bowler.name == original) + (bowler.name == recipient)
            revised.append({"name": bowler.name, "wickets": wickets, "runs": bowler.runs_conceded})
        revised.sort(key=lambda x: (-x["wickets"], x["runs"], x["name"]))
        return {
            "bundle": bundle,
            "innings": innings_index,
            "innings_obj": innings,
            "event": event_name,
            "A": original,
            "B": recipient,
            "expected": revised[:2],
            "ranked": revised,
            "total": innings.total_wickets,
        }
    raise AssertionError((match, event_name))


def revised_gold(task, event):
    gold = dict(task["gold"])
    innings = event["innings"]
    for rank, bowler in enumerate(event["expected"], 1):
        prefix = f"inn{innings}.bowl{rank}"
        gold[prefix + "_name"] = bowler["name"]
        gold[prefix + "_wickets"] = bowler["wickets"]
        gold[prefix + "_runs"] = bowler["runs"]
    gold[f"inn{innings}.total_wickets"] = event["total"]
    return gold


man258, run258, path258, runpath258 = read_batch("B258")
man259, run259, path259, runpath259 = read_batch("B259")
tasks258 = {t["task_key"]: t for t in man258["tasks"]}
tasks259 = {t["task_key"]: t for t in man259["tasks"]}


def one_task(manifest, match, model, cond):
    found = [t for t in manifest["tasks"] if t["match"] == match and t["model"] == model and t["cond"] == cond]
    if len(found) != 1:
        raise AssertionError((match, model, cond, len(found)))
    return found[0]


positions = {p["match"]: p for p in man258["design"]["positions"]}
events = {match: semantic_event(match, positions[match]["event"]) for match in ROOTS}

# Actual prompt answerability. These statements are derived only from model-visible commentary + appended ledger/notice.
answerability = {
    "match_0170": (False, "After reassignment Carter Flynn has 4. Ari Blake, Ben Carter and Isaac Ford each have 1; only Ari's runs (22) are in the appended ledger, so row 2 is not unique."),
    "match_0096": (True, "After reassignment Ryan North and Noah Vale each have 2; all other named wicket-takers have 1, and ledger runs 13/38 uniquely order Ryan then Noah."),
    "match_0049": (False, "After reassignment Carter Flynn has 4. Finn Mercer, Hudson Pike and Aiden Marsh each have 2; competitor runs are absent, so row 2 is not unique."),
    "match_0180": (False, "After reassignment Mason Price has 3. Finn Carter, Leo Marsh and Jasper Hall each have 1; competitor runs are absent, so row 2 is not unique."),
}

evidence_phrases = {
    "match_0170": "Carter Flynn finished with three wickets, Ari Blake struck twice, Ben Carter and Isaac Ford each found a wicket",
    "match_0096": "Azure Point’s bowling figures told the same story: Ryan North created the squeeze, Noah Vale supplied the main damage despite being attacked later, Owen Clark removed the captain at the right time, Leo Marin took the wicket that stopped Marco",
    "match_0049": "Finn Mercer took three and had the best early impact, Carter Flynn took three as well and kept fighting through the heavier scoring phases, Hudson Pike picked up two, and Aiden Marsh collected two late",
    "match_0180": "Mason Price and Finn Carter both took important wickets, Leo Marsh found the first breakthrough, Jasper Hall removed Milan Reed",
}

answerability_rows = []
for match in ROOTS:
    task = one_task(man258, match, MODELS[0], "T2_N2")
    commentary = prompt_commentary(task["prompt"])
    phrase = evidence_phrases[match]
    start, end = find_span(commentary, phrase)
    ledger_start = commentary.rfind("Pre-revision record:")
    notice_start = commentary.rfind("Match review:")
    event = events[match]
    answerable, reason = answerability[match]
    answerability_rows.append({
        "scoring_version": VERSION,
        "match": match,
        "innings": event["innings"],
        "event": event["event"],
        "text_sha256": task["text_sha"],
        "model_visible_top2_unique": answerable,
        "fair_disposition": "include" if answerable else "exclude_not_executable_input",
        "reason": reason,
        "private_oracle_top2": compact_rows(event["expected"]),
        "private_rank3": compact_rows(event["ranked"][:3]),
        "narrative_evidence": phrase,
        "narrative_char_start": start,
        "narrative_char_end_exclusive": end,
        "ledger_text": commentary[ledger_start:notice_start].strip(),
        "ledger_char_start": ledger_start,
        "notice_text": commentary[notice_start:].strip(),
        "notice_char_start": notice_start,
    })


rows12 = []
field_rows = []
for match in ROOTS:
    event = events[match]
    answerable, reason = answerability[match]
    for model in MODELS:
        direct_task = one_task(man258, match, model, "N2_F_fulltable_direct")
        list_task = one_task(man258, match, model, "T2_N2")
        hint_task = one_task(man259, match, model, "N2_F_fulltable_hint")
        if not (direct_task["text_sha"] == list_task["text_sha"] == hint_task["text_sha"]):
            raise AssertionError((match, model, "text_sha mismatch"))
        direct_raw = run258[direct_task["task_key"]].get("raw_output", "")
        list_raw = run258[list_task["task_key"]].get("raw_output", "")
        hint_raw = run259[hint_task["task_key"]].get("raw_output", "")
        direct_rec = recover_fields(direct_raw)
        hint_rec = recover_fields(hint_raw)
        list_rec = recover_bowlers(list_raw)
        gold = revised_gold(direct_task, event)
        direct_fixed = score_cells(gold, direct_task["fields"], direct_rec)
        hint_fixed = score_cells(gold, hint_task["fields"], hint_rec)
        direct_identity = score_identity(direct_rec, event["expected"], event["innings"], event["total"])
        hint_identity = score_identity(hint_rec, event["expected"], event["innings"], event["total"])
        pred_names = list_rec["bowlers"]
        if pred_names is None or len(pred_names) != 2 or len({norm(x) for x in pred_names}) != 2:
            list_member_oracle = "undetermined_output_identity"
            list_order_oracle = "undetermined_output_identity"
        else:
            expected_names = [x["name"] for x in event["expected"]]
            list_member_oracle = "correct" if {norm(x) for x in pred_names} == {norm(x) for x in expected_names} else "wrong"
            list_order_oracle = "correct" if [norm(x) for x in pred_names] == [norm(x) for x in expected_names] else ("wrong" if list_member_oracle == "correct" else "wrong_member_set")
        fair_member = list_member_oracle if answerable else "not_executable_input"
        fair_order = list_order_oracle if answerable else "not_executable_input"
        lost_person = list_member_oracle == "correct" and not hint_identity["both_present"]
        kept_two_wrong_number = list_member_oracle == "correct" and hint_identity["both_present"] and not hint_identity["all_person_numeric_correct"]
        only_team_total = list_member_oracle == "correct" and hint_identity["both_present"] and hint_identity["all_person_numeric_correct"] and hint_identity["team_total_status"] != "correct"
        if hint_rec["strict_format_pass"] and hint_identity["member_status"] == "correct" and hint_identity["all_person_numeric_correct"] and hint_identity["team_total_status"] == "correct":
            format_content_relation = "strict_pass_target_content_correct"
        elif hint_rec["strict_format_pass"]:
            format_content_relation = "strict_pass_target_content_wrong"
        elif hint_identity["member_status"] == "correct" and hint_identity["all_person_numeric_correct"] and hint_identity["team_total_status"] == "correct":
            format_content_relation = "strict_fail_target_content_recoverable_correct"
        else:
            format_content_relation = "strict_fail_target_content_recovered_but_wrong_or_incomplete"
        row = {
            "scoring_version": VERSION,
            "match": match,
            "innings": event["innings"],
            "event": event["event"],
            "model": model,
            "model_short": MODEL_SHORT[model],
            "text_sha256": direct_task["text_sha"],
            "model_visible_top2_unique": answerable,
            "fair_disposition": "include" if answerable else "exclude_not_executable_input",
            "answerability_reason": reason,
            "private_oracle_top2": compact_rows(event["expected"]),
            "direct_task_key": direct_task["task_key"],
            "direct_raw_sha256": sha_text(direct_raw),
            "direct_observed_target": compact_rows(direct_identity["observed_rows"]),
            "direct_member_set_oracle": direct_identity["member_status"],
            "direct_row_order_oracle": direct_identity["order_status"],
            "direct_person_values": compact_person(direct_identity["per_person"]),
            "direct_team_total_status": direct_identity["team_total_status"],
            "direct_team_total_pred": direct_identity["team_total_pred"],
            "direct_strict_format_pass": direct_rec["strict_format_pass"],
            "direct_recovery_source": direct_rec["recovery_source"],
            "direct_recovered_fields": direct_rec["recovered_field_count"],
            "direct_v4_fixed_correct": direct_fixed["counts"]["correct"],
            "direct_v4_fixed_total": len(direct_task["fields"]),
            "list_task_key": list_task["task_key"],
            "list_raw_sha256": sha_text(list_raw),
            "list_raw_output": list_raw.replace("\r", " ").replace("\n", " "),
            "list_recovered_names": " | ".join(pred_names or []),
            "list_member_set_oracle": list_member_oracle,
            "list_row_order_oracle": list_order_oracle,
            "list_member_set_fair": fair_member,
            "list_row_order_fair": fair_order,
            "list_strict_format_pass": list_rec["strict_format_pass"],
            "list_recovery_source": list_rec["recovery_source"],
            "hint_task_key": hint_task["task_key"],
            "hint_raw_sha256": sha_text(hint_raw),
            "hint_observed_target": compact_rows(hint_identity["observed_rows"]),
            "hint_member_set_oracle": hint_identity["member_status"],
            "hint_row_order_oracle": hint_identity["order_status"],
            "hint_both_legal_members_present": hint_identity["both_present"],
            "hint_person_values": compact_person(hint_identity["per_person"]),
            "hint_all_person_numeric_correct": hint_identity["all_person_numeric_correct"],
            "hint_team_total_status": hint_identity["team_total_status"],
            "hint_team_total_pred": hint_identity["team_total_pred"],
            "hint_strict_format_pass": hint_rec["strict_format_pass"],
            "hint_recovery_source": hint_rec["recovery_source"],
            "hint_recovered_fields": hint_rec["recovered_field_count"],
            "hint_v4_fixed_correct": hint_fixed["counts"]["correct"],
            "hint_v4_fixed_total": len(hint_task["fields"]),
            "hint_format_vs_recoverable_content": format_content_relation,
            "oracle_correct_list_then_hint_lost_person": lost_person,
            "oracle_correct_list_then_hint_kept_two_wrong_number": kept_two_wrong_number,
            "oracle_correct_list_then_hint_only_team_total_wrong": only_team_total,
        }
        rows12.append(row)

        # N2 field-level regression under both embedded-gold and revised-v4-gold views.
        old_direct = score_cells(direct_task["gold"], direct_task["fields"], direct_rec)
        old_hint = score_cells(hint_task["gold"], hint_task["fields"], hint_rec)
        for key in direct_task["fields"]:
            legacy_parsed_direct = (run258[direct_task["task_key"]].get("parsed") or {}).get("fields", {})
            legacy_parsed_hint = (run259[hint_task["task_key"]].get("parsed") or {}).get("fields", {})
            old_gold = direct_task["gold"].get(key)
            legacy_direct_ok = compare(old_gold, legacy_parsed_direct.get(key))
            legacy_hint_ok = compare(old_gold, legacy_parsed_hint.get(key))
            field_rows.append({
                "scope": "N2_12",
                "match": match,
                "model_short": MODEL_SHORT[model],
                "notification": "N2",
                "field": key,
                "legacy_embedded_gold": old_gold,
                "v4_revised_gold": gold.get(key),
                "legacy_direct_correct": legacy_direct_ok,
                "legacy_hint_correct": legacy_hint_ok,
                "legacy_direct_to_hint_regression": legacy_direct_ok and not legacy_hint_ok,
                "v4_direct_result": direct_fixed["cells"][key]["result"],
                "v4_hint_result": hint_fixed["cells"][key]["result"],
                "v4_direct_to_hint_regression": direct_fixed["cells"][key]["result"] == "correct" and hint_fixed["cells"][key]["result"] != "correct",
                "v4_direct_to_hint_gain": direct_fixed["cells"][key]["result"] != "correct" and hint_fixed["cells"][key]["result"] == "correct",
                "hint_strict_format_pass": hint_rec["strict_format_pass"],
                "hint_recovery_source": hint_rec["recovery_source"],
                "hint_empty_or_unrecoverable": hint_rec["recovered_field_count"] == 0,
            })


# Reconstruct the legacy 45-field-regression claim over all 24 N1+N2 direct/hint pairs.
legacy45_rows = []
for match in ROOTS:
    event = events[match]
    for arm in ("N1", "N2"):
        for model in MODELS:
            direct_task = one_task(man258, match, model, f"{arm}_F_fulltable_direct")
            hint_task = one_task(man259, match, model, f"{arm}_F_fulltable_hint")
            direct_run = run258[direct_task["task_key"]]
            hint_run = run259[hint_task["task_key"]]
            direct_rec = recover_fields(direct_run.get("raw_output", ""))
            hint_rec = recover_fields(hint_run.get("raw_output", ""))
            if arm == "N2":
                fair_gold = revised_gold(direct_task, event)
            else:
                fair_gold = dict(direct_task["gold"])
            fair_direct = score_cells(fair_gold, direct_task["fields"], direct_rec)
            fair_hint = score_cells(fair_gold, hint_task["fields"], hint_rec)
            legacy_direct_fields = (direct_run.get("parsed") or {}).get("fields", {})
            legacy_hint_fields = (hint_run.get("parsed") or {}).get("fields", {})
            for key in direct_task["fields"]:
                old_gold = direct_task["gold"].get(key)
                # The published "45 cells" used Python exact equality against the
                # semantic 43-field gold (including post-notice reranking), not the
                # v4 numeric/string recovery comparison.
                report_gold = fair_gold.get(key)
                reported_direct_ok = legacy_direct_fields.get(key) == report_gold
                reported_hint_ok = legacy_hint_fields.get(key) == report_gold
                legacy_direct_ok = compare(old_gold, legacy_direct_fields.get(key))
                legacy_hint_ok = compare(old_gold, legacy_hint_fields.get(key))
                legacy45_rows.append({
                    "scope": "ALL_24",
                    "match": match,
                    "model_short": MODEL_SHORT[model],
                    "notification": arm,
                    "field": key,
                    "reported_45_gold": report_gold,
                    "reported_45_direct_correct": reported_direct_ok,
                    "reported_45_hint_correct": reported_hint_ok,
                    "reported_45_direct_to_hint_regression": reported_direct_ok and not reported_hint_ok,
                    "legacy_direct_correct": legacy_direct_ok,
                    "legacy_hint_correct": legacy_hint_ok,
                    "legacy_direct_to_hint_regression": legacy_direct_ok and not legacy_hint_ok,
                    "v4_direct_result": fair_direct["cells"][key]["result"],
                    "v4_hint_result": fair_hint["cells"][key]["result"],
                    "v4_direct_to_hint_regression": fair_direct["cells"][key]["result"] == "correct" and fair_hint["cells"][key]["result"] != "correct",
                    "v4_direct_to_hint_gain": fair_direct["cells"][key]["result"] != "correct" and fair_hint["cells"][key]["result"] == "correct",
                    "hint_strict_format_pass": hint_rec["strict_format_pass"],
                    "hint_recovery_source": hint_rec["recovery_source"],
                    "hint_empty_or_unrecoverable": hint_rec["recovered_field_count"] == 0,
                    "direct_recovered_fields": direct_rec["recovered_field_count"],
                    "hint_recovered_fields": hint_rec["recovered_field_count"],
                })


# Reconcile the prior core-8 oracle denominator with its fair answerable-6 denominator.
with (V4 / "TOP2_CHAIN_ROWS.csv").open("r", encoding="utf-8-sig", newline="") as f:
    core_rows = [r for r in csv.DictReader(f) if r["notification"] == "N2"]
core8 = Counter()
fair6 = Counter()
for row in core_rows:
    try:
        recovered = json.loads(row["top2_recovered_names"].replace("'", '"'))
    except Exception:
        recovered = [x.strip() for x in row["top2_recovered_names"].split("|") if x.strip()]
    expected = [x.strip() for x in row["oracle_legal_top2"].split("|") if x.strip()]
    top_ok = len(recovered) == 2 and {norm(x) for x in recovered} == {norm(x) for x in expected}
    full_ok = row["fulltable_member_set_status_oracle"] in ("correct", "correct_tie_accepted")
    if top_ok and not full_ok:
        direction = "top2_correct_fulltable_wrong"
    elif not top_ok and full_ok:
        direction = "top2_wrong_fulltable_correct"
    elif top_ok and full_ok:
        direction = "both_member_sets_correct"
    else:
        direction = "both_member_sets_wrong_or_undetermined"
    core8[direction] += 1
    if row["input_top2_determinable"].casefold() == "true":
        fair6[direction] += 1


def write_csv(path, rows):
    rows = list(rows)
    if not rows:
        raise RuntimeError(f"refuse empty CSV: {path}")
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def json_dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


write_csv(HERE / "N2_12_CASES.csv", rows12)
write_csv(HERE / "N2_4ROOT_ANSWERABILITY.csv", answerability_rows)
write_csv(HERE / "FIELD_REGRESSION_ALL24.csv", legacy45_rows)

correct_list = [r for r in rows12 if r["list_member_set_oracle"] == "correct"]
fair_rows = [r for r in rows12 if r["model_visible_top2_unique"]]
reported45_reg = [r for r in legacy45_rows if r["reported_45_direct_to_hint_regression"]]
legacy_reg = [r for r in legacy45_rows if r["legacy_direct_to_hint_regression"]]
v4_reg = [r for r in legacy45_rows if r["v4_direct_to_hint_regression"]]
v4_gain = [r for r in legacy45_rows if r["v4_direct_to_hint_gain"]]

def grouped_count(rows, fields):
    counter = Counter(tuple(r[f] for f in fields) for r in rows)
    return [{**{f: key[i] for i, f in enumerate(fields)}, "count": value} for key, value in sorted(counter.items())]


summary = {
    "scoring_version": VERSION,
    "n2_rows": len(rows12),
    "n2_roots": len(ROOTS),
    "n2_answerable_roots": sum(bool(x["model_visible_top2_unique"]) for x in answerability_rows),
    "n2_fair_rows": len(fair_rows),
    "oracle_correct_independent_lists": len(correct_list),
    "oracle_correct_list_hint_lost_person": sum(r["oracle_correct_list_then_hint_lost_person"] for r in correct_list),
    "oracle_correct_list_hint_kept_two_wrong_number": sum(r["oracle_correct_list_then_hint_kept_two_wrong_number"] for r in correct_list),
    "oracle_correct_list_hint_only_team_total_wrong": sum(r["oracle_correct_list_then_hint_only_team_total_wrong"] for r in correct_list),
    "oracle_correct_list_hint_total_correct": sum(r["hint_team_total_status"] == "correct" for r in correct_list),
    "reported_45": {
        "denominator_fields": len(legacy45_rows),
        "regressions": len(reported45_reg),
        "by_match": grouped_count(reported45_reg, ["match"]),
        "by_match_model_notice": grouped_count(reported45_reg, ["match", "model_short", "notification"]),
        "hint_empty_or_unrecoverable_regressions": sum(r["hint_empty_or_unrecoverable"] for r in reported45_reg),
        "hint_non_strict_regressions": sum(not r["hint_strict_format_pass"] for r in reported45_reg),
        "legacy_compare_normalized_regressions": len(legacy_reg),
    },
    "v4_recovery_regression": {
        "denominator_fields": len(legacy45_rows),
        "regressions": len(v4_reg),
        "gains": len(v4_gain),
        "by_match": grouped_count(v4_reg, ["match"]),
        "by_match_model_notice": grouped_count(v4_reg, ["match", "model_short", "notification"]),
    },
    "core8_vs_fair6": {
        "core8_rows": len(core_rows),
        "fair6_rows": sum(fair6.values()),
        "excluded_rows": len(core_rows) - sum(fair6.values()),
        "core8_oracle_directions": dict(core8),
        "fair6_directions": dict(fair6),
    },
}
json_dump(HERE / "SUMMARY.json", summary)


source_paths = [path258, runpath258, path259, runpath259, V4 / "TOP2_CHAIN_ROWS.csv"]
for match in ROOTS:
    source_paths.append(ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches" / match / "scorecard.md")
    source_paths.append(ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches" / match / "commentary.txt")
write_csv(HERE / "SOURCE_INVENTORY.csv", [{
    "path": str(p.relative_to(ROOT)).replace("\\", "/"),
    "sha256": sha_file(p),
    "bytes": p.stat().st_size,
    "access": "read-only",
} for p in source_paths])

artifact_names = [
    "N2_BACKFILL_REVIEW.md",
    "N2_12_CASES.csv",
    "N2_4ROOT_ANSWERABILITY.csv",
    "FIELD_REGRESSION_ALL24.csv",
    "SUMMARY.json",
    "SOURCE_INVENTORY.csv",
]
if all((HERE / name).is_file() for name in artifact_names):
    json_dump(HERE / "VERSION_MANIFEST.json", {
        "scoring_version": VERSION,
        "status": "frozen_v1",
        "created_date": "2026-11-23",
        "source_policy": "read-only sealed B258/B259 manifests and JSONL; no Ollama, SQLite, worker, or queue access",
        "generated_files": [{
            "path": name,
            "sha256": sha_file(HERE / name),
            "bytes": (HERE / name).stat().st_size,
        } for name in artifact_names],
        "immutability": "Any change must use a new version directory.",
    })


print(json.dumps(summary, ensure_ascii=False, indent=2))
