
"""Batch planner: hypotheses, eligibility, freeze, and next-batch decisions."""
from __future__ import annotations

import json
import hashlib
import time
from pathlib import Path

import vettlib as V
import v2


def heldout_set() -> set:
    a, b = V.CONFIG["split"]["heldout_match_range"]
    return {"match_" + str(i).zfill(4) for i in range(int(a), int(b) + 1)}


HELDOUT = heldout_set()


def is_heldout(match: str) -> bool:
    return match in HELDOUT


def task_key(match: str, innings: int, model: str, cond: str, scope: str, prompt_sha: str,
             digest: str = "", decode_json: str = "") -> str:
    if digest and decode_json:
        return v2.key_v2(match, innings, model, digest, decode_json, v2.INPUT_VERSION,
                         v2.PROMPT_VERSION, v2.REPLICATE_ID, scope, prompt_sha)
    raw = "|".join([match, str(innings), model, cond, scope, prompt_sha])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _reject(rejects: list, match, innings, cond, reason):
    rejects.append({"match": match, "innings": innings, "cond": cond, "reason": reason})


def make_tasks(con, match: str, innings: int, conds: list, scope: str, models: list,
               rejects: list, allow_reuse: bool = False, num_predict: int = 300) -> list:
    if is_heldout(match):
        _reject(rejects, match, innings, "*", "held_out_root")
        return []
    used = {(r["match"], r["innings"]) for r in con.execute("SELECT DISTINCT match, innings FROM tasks").fetchall()}
    if (match, innings) in used and not allow_reuse:
        _reject(rejects, match, innings, "*", "root_already_used")
        return []
    try:
        bundle = V.load_bundle(match)
    except Exception as e:
        _reject(rejects, match, innings, "*", "load_failed:" + type(e).__name__)
        return []
    if len(bundle["text"]) > V.CONFIG["limits"]["max_text_chars"]:
        _reject(rejects, match, innings, "*", "text_too_long")
        return []
    built = V.build_conditions(match, innings)
    variants = built["variants"]
    if scope == "target2":
        fields = ["inn" + str(innings) + ".total_runs", "inn" + str(innings) + ".total_wickets"]
        gold = V.gold_target(bundle["md"], innings)
    else:
        fields = list(V.FULL43)
        gold = V.gold43(bundle["md"])
    if not gold:
        _reject(rejects, match, innings, "*", "no_gold")
        return []
    tasks = []
    seen = set()
    for cond in conds:
        if cond not in variants:
            _reject(rejects, match, innings, cond, "variant_unavailable")
            continue
        text = variants[cond]
        prompt = V.build_prompt(match, innings, cond, text, fields)
        psha = V.sha256_text(prompt)
        for model in models:
            digest = V.model_digest(model)
            dec_json = json.dumps(v2.decode_config(num_predict), sort_keys=True)
            legacy_key = task_key(match, innings, model, cond, scope, psha)
            key = task_key(match, innings, model, cond, scope, psha, digest, dec_json)
            if key in seen:
                _reject(rejects, match, innings, cond, "duplicate_in_batch")
                continue
            if con.execute("SELECT 1 FROM tasks WHERE task_key=?", (key,)).fetchone():
                _reject(rejects, match, innings, cond, "duplicate_existing_task")
                continue
            if con.execute("SELECT 1 FROM task_key_map WHERE new_key=?", (key,)).fetchone():
                _reject(rejects, match, innings, cond, "duplicate_existing_identity")
                continue
            if con.execute("SELECT 1 FROM results WHERE task_key=?", (key,)).fetchone():
                _reject(rejects, match, innings, cond, "duplicate_existing_result")
                continue
            seen.add(key)
            tasks.append({
                "task_key": key, "match": match, "innings": innings, "model": model,
                "cond": cond, "field_scope": scope, "fields": fields,
                "prompt": prompt, "prompt_sha": psha, "text_sha": V.sha256_text(text),
                "num_predict": num_predict, "gold": gold, "model_digest": digest,
                "decode_json": dec_json, "input_version": v2.INPUT_VERSION,
                "prompt_version": v2.PROMPT_VERSION, "replicate_id": v2.REPLICATE_ID,
                "legacy_task_key": legacy_key,
            })
    return tasks


def _design(template: str, hypothesis: str, rationale: str, con, tasks: list,
            conditions: list, models: list, sources: list, scoring: str) -> dict:
    positions = []
    seen = set()
    for t in tasks:
        k = (t["match"], t["innings"])
        if k in seen:
            continue
        seen.add(k)
        positions.append({"match": t["match"], "innings": t["innings"]})
    requests = len(tasks)
    actual_conditions = sorted({t["cond"] for t in tasks}) if tasks else conditions
    return {
        "template": template,
        "hypothesis": hypothesis,
        "rationale": rationale,
        "positions": positions,
        "fields": tasks[0]["fields"] if tasks else [],
        "conditions": actual_conditions,
        "models": models,
        "scoring": scoring,
        "sources": sources,
        "cost": {"requests": requests,
                 "est_seconds": requests * int(V.CONFIG["cost_model"]["estimate_seconds_per_request"]),
                 "external_api": 0},
        "created_at": V.now_iso(),
    }


def build_t1(con, reasons: dict) -> tuple:
    models = V.MODELS
    tasks, rejects = [], []
    roots = V.CONFIG["pools"]["dev"]
    for m in roots:
        if len(tasks) >= 2 * len(models):
            break
        tasks += make_tasks(con, m, 1, ["O"], "target2", models, rejects, num_predict=300)
    design = _design("T1_baseline_o",
                     "Target cells on development roots are near ceiling under original text; this is the baseline for escalation.",
                     reasons.get("rationale", "Initial baseline batch."),
                     con, tasks, ["O"], models,
                     ["commentary.txt", "scorecard.md"],
                     "exact integer match per field; task correct iff both target cells correct")
    return design, tasks, rejects


def build_t2(con, reasons: dict) -> tuple:
    models = V.MODELS
    tasks, rejects = [], []
    for pos in V.CONFIG["pools"]["hard"]:
        if len(tasks) >= 2 * len(models):
            break
        tasks += make_tasks(con, pos["match"], int(pos["innings"]), ["E"], "target2", models,
                            rejects, allow_reuse=False, num_predict=300)
    design = _design("T2_hard_excerpt",
                     "If hard-root failures come from long-context dilution, a 3-sentence evidence excerpt will recover both cells; otherwise the failure is field binding/localisation.",
                     reasons.get("rationale", "Escalate to hard roots with a short evidence excerpt."),
                     con, tasks, ["E"], models,
                     ["commentary.txt (excerpt)", "scorecard.md"],
                     "exact integer match per field; task correct iff both target cells correct")
    return design, tasks, rejects


def build_t3(con, reasons: dict) -> tuple:
    models = V.MODELS
    tasks, rejects = [], []
    focus = reasons.get("focus") or []
    allow = set((p["match"], p["innings"]) for p in focus)
    for pos in focus:
        if len(tasks) >= 3 * len(models):
            break
        tasks += make_tasks(con, pos["match"], int(pos["innings"]), ["O", "WI", "OI"], "target2", models,
                            rejects, allow_reuse=True, num_predict=300)
    if not tasks:
        for pos in V.CONFIG["pools"]["hard"]:
            tasks += make_tasks(con, pos["match"], int(pos["innings"]), ["O", "WI", "OI"], "target2", models,
                                rejects, allow_reuse=True, num_predict=300)
            if tasks:
                break
    design = _design("T3_matched_deletion",
                     "If deleting the same-innings mid-score (WI) costs more than deleting a matched unrelated sentence (OIC) or the other-innings total (OI), the target cell depends on that specific sentence.",
                     reasons.get("rationale", "Matched deletion control on failing positions."),
                     con, tasks, ["O", "WI", "OI"], models,
                     ["commentary.txt variants", "scorecard.md"],
                     "exact integer match per field; paired comparison is treatment minus O on the same root/model/field")
    return design, tasks, rejects


def build_t4(con, reasons: dict) -> tuple:
    models = V.MODELS
    tasks, rejects = [], []
    focus = reasons.get("focus") or []
    cond = reasons.get("cond", "O")
    cand = focus if focus else V.CONFIG["pools"]["hard"][:1]
    for pos in cand[:1]:
        tasks += make_tasks(con, pos["match"], int(pos["innings"]), [cond], "full43", models,
                            rejects, allow_reuse=True, num_predict=900)
    design = _design("T4_full_table",
                     "If target cells saturate on an excerpt but the 43-field table does not, the model has collateral field loss that target cells hide.",
                     reasons.get("rationale", "Full 43-field validation on one root."),
                     con, tasks, [cond], models,
                     ["commentary.txt", "scorecard.md"],
                     "exact match per field; report 43-field accuracy and target-cell subset")
    return design, tasks, rejects


def build_t5(con, reasons: dict) -> tuple:
    models = V.MODELS
    tasks, rejects = [], []
    for pos in V.CONFIG["pools"]["hard"]:
        if len(tasks) >= 2 * len(models):
            break
        tasks += make_tasks(con, pos["match"], int(pos["innings"]), ["O"], "target2", models,
                            rejects, allow_reuse=False, num_predict=300)
    design = _design("T5_hard_fulltext",
                     "When a hard root has no explicit total sentence, the excerpt variant is unavailable; full-text O on unused hard roots tests whether the failure is excerpt-specific or a genuinely unanswerable field.",
                     reasons.get("rationale", "No remaining hard root supports an evidence excerpt."),
                     con, tasks, ["O"], models,
                     ["commentary.txt", "scorecard.md"],
                     "exact integer match per field; task correct iff both target cells correct")
    return design, tasks, rejects


def e_eligible_positions(con) -> list:
    used = {(r["match"], r["innings"]) for r in con.execute("SELECT DISTINCT match, innings FROM tasks").fetchall()}
    out = []
    for pos in V.CONFIG["pools"]["hard"]:
        if (pos["match"], int(pos["innings"])) in used:
            continue
        try:
            built = V.build_conditions(pos["match"], int(pos["innings"]))
        except Exception:
            continue
        if "E" in built["variants"]:
            out.append(pos)
    return out


def make_probe_tasks(con, match: str, innings: int, cond: str, models: list, variants: list,
                     rejects: list, num_predict: int = 200) -> list:
    if is_heldout(match):
        _reject(rejects, match, innings, cond, "held_out_root")
        return []
    try:
        bundle = V.load_bundle(match)
    except Exception as e:
        _reject(rejects, match, innings, cond, "load_failed:" + type(e).__name__)
        return []
    built = V.build_conditions(match, innings)
    if cond not in built["variants"]:
        _reject(rejects, match, innings, cond, "variant_unavailable")
        return []
    text = built["variants"][cond]
    gold = V.gold_target(bundle["md"], innings)
    if not gold:
        _reject(rejects, match, innings, cond, "no_gold")
        return []
    tasks = []
    for label, fields in variants:
        prompt = V.build_prompt(match, innings, cond, text, fields)
        psha = V.sha256_text(prompt)
        for model in models:
            digest = V.model_digest(model)
            dec_json = json.dumps(v2.decode_config(num_predict), sort_keys=True)
            legacy_key = task_key(match, innings, model, cond, label, psha)
            key = v2.key_v2(match, innings, model, digest, dec_json, v2.INPUT_VERSION,
                            v2.PROMPT_VERSION, v2.REPLICATE_ID, label, psha)
            if con.execute("SELECT 1 FROM tasks WHERE task_key=?", (key,)).fetchone():
                _reject(rejects, match, innings, cond, "duplicate_existing_task")
                continue
            if con.execute("SELECT 1 FROM task_key_map WHERE new_key=?", (key,)).fetchone():
                _reject(rejects, match, innings, cond, "duplicate_existing_identity")
                continue
            tasks.append({
                "task_key": key, "legacy_task_key": legacy_key, "match": match, "innings": innings,
                "model": model, "cond": cond, "field_scope": label, "fields": fields,
                "prompt": prompt, "prompt_sha": psha, "text_sha": V.sha256_text(text),
                "num_predict": num_predict, "gold": gold, "model_digest": digest,
                "decode_json": dec_json, "input_version": v2.INPUT_VERSION,
                "prompt_version": v2.PROMPT_VERSION, "replicate_id": v2.REPLICATE_ID,
            })
    return tasks


def build_a(con, reasons: dict) -> tuple:
    models = V.MODELS
    tasks, rejects = [], []
    for m in V.CONFIG["pools"]["dev"]:
        if len(tasks) >= 2 * len(models) * 3:
            break
        built = V.build_conditions(m, 1)
        if "E" not in built["variants"]:
            _reject(rejects, m, 1, "E", "evidence_excerpt_unavailable")
            continue
        p = "inn1"
        variants = [("probe_runs", [p + ".total_runs"]),
                    ("probe_wickets", [p + ".total_wickets"]),
                    ("probe_both", [p + ".total_runs", p + ".total_wickets"])]
        tasks += make_probe_tasks(con, m, 1, "E", models, variants, rejects, num_predict=200)
    design = _design("A_field_probe",
                     "On the same evidence sentence, asking runs only, wickets only, or both separates field confusion from evidence localisation.",
                     reasons.get("rationale", "Field-probe branch on fixed evidence."),
                     con, tasks, ["E"], models,
                     ["commentary.txt (excerpt)", "scorecard.md"],
                     "exact integer match per field; compare runs-only vs wickets-only vs both by root/model")
    return design, tasks, rejects


def build_b(con, reasons: dict) -> tuple:
    models = V.MODELS
    tasks, rejects = [], []
    for pos in V.CONFIG["pools"]["hard"]:
        if tasks:
            break
        built = V.build_conditions(pos["match"], int(pos["innings"]))
        conds = [c for c in ("O", "E", "OI", "OIC") if c in built["variants"]]
        if "OI" not in conds:
            _reject(rejects, pos["match"], int(pos["innings"]), "OI", "other_innings_score_unavailable")
            continue
        tasks += make_tasks(con, pos["match"], int(pos["innings"]), conds, "target2", models,
                            rejects, allow_reuse=True, num_predict=300)
    design = _design("B_cross_innings",
                     "With the innings fixed explicitly, compare original, sufficient excerpt, deletion of the other-innings score, and a matched non-evidence deletion to test cross-innings binding.",
                     reasons.get("rationale", "Cross-innings binding branch."),
                     con, tasks, ["O", "E", "OI", "OIC"], models,
                     ["commentary.txt variants", "scorecard.md"],
                     "exact integer match per field; paired by root/model against O")
    return design, tasks, rejects


SWEEP_ROOTS = ["match_" + str(i).zfill(4) for i in range(1, 221) if not (121 <= i <= 160)]


def sweep_units():
    units = []
    for m in SWEEP_ROOTS:
        for inn in (1, 2):
            units.append((m, inn))
    return units


def build_sweep(con, reasons: dict) -> tuple:
    models = V.MODELS
    cursor = int(V.meta_get(con, "sweep_cursor", "0") or 0)
    units = sweep_units()
    tasks, rejects = [], []
    used = 0
    for m, inn in units[cursor:]:
        if used >= 4:
            break
        built = V.build_conditions(m, inn)
        conds = [c for c in ("O", "E", "WI", "OI") if c in built["variants"]]
        before = len(tasks)
        tasks += make_tasks(con, m, inn, conds, "target2", models, rejects,
                            allow_reuse=True, num_predict=300)
        if len(tasks) > before:
            used += 1
    design = _design("S_coverage_sweep",
                     "Stratified coverage sweep over non-held-out roots and both innings; distinct roots/conditions, not repeated deterministic calls.",
                     reasons.get("rationale", "Coverage sweep for unattended throughput."),
                     con, tasks, ["O", "E", "WI", "OI"], models,
                     ["commentary.txt variants", "scorecard.md"],
                     "exact integer match per field; coverage group kept separate from diagnostic hard-root group")
    design["sweep_next_cursor"] = cursor + used
    design["sweep_total_units"] = len(units)
    return design, tasks, rejects


ATTR_SAMPLES = V.INT / "analysis" / "attribution_followup" / "samples.json"


def _old_gold(s):
    a, b = s["A"], s["B"]
    return {a + "_wickets": s["Aw"], a + "_runs": s["Ar"],
            b + "_wickets": s["Bw"], b + "_runs": s["Br"],
            "innings_total_wickets": s["total"]}


def _c_prompt(s, cond, text, fields):
    intro = ("You are a cricket scorer. Read the record and return the five requested fields. "
             "Return ONLY a JSON object mapping each field id to its integer value. No prose.")
    return (intro + "\n\nMatch: " + s["match"] + "\nInnings: " + str(s["innings"]) +
            "\nFields:\n" + "\n".join("- " + f for f in fields) +
            "\n\nRecord:\n" + text + "\n\nJSON:")


def build_c(con, reasons: dict) -> tuple:
    models = V.MODELS
    samples = json.loads(ATTR_SAMPLES.read_text(encoding="utf-8"))
    picks = samples if reasons.get("all_samples") else [samples[i] for i in (0, 1, 5, 6) if i < len(samples)]
    tasks, rejects = [], []
    notices = {
        "C_change": "Match review: the dismissal is formally reassigned from {A} to {B}. Update both bowlers' figures; runs and innings total do not change.",
        "C_maintain": "Match review: the original attribution to {A} is maintained. No change to either bowler's figures.",
        "C_no_notice": "No review notice is provided. Use the pre-revision record as published.",
    }
    for s in picks:
        new_gold = dict(s["fields"])
        old_gold = _old_gold(s)
        base_text = ("In " + str(s["innings"]) + ", " + s["batter"] + " was dismissed. "
                     "Pre-revision record: " + s["A"] + " " + str(s["Aw"]) + " wickets for " + str(s["Ar"]) +
                     " runs; " + s["B"] + " " + str(s["Bw"]) + " wickets for " + str(s["Br"]) +
                     " runs; the innings total was " + str(s["total"]) + " wickets.")
        for cond, notice in notices.items():
            text = base_text + " " + notice.format(A=s["A"], B=s["B"])
            gold = new_gold if cond == "C_change" else old_gold
            fields = list(new_gold.keys())
            prompt = _c_prompt(s, cond, text, fields)
            psha = V.sha256_text(prompt)
            for model in models:
                digest = V.model_digest(model)
                dec_json = json.dumps(v2.decode_config(300), sort_keys=True)
                legacy_key = task_key(s["match"], 1, model, cond, "attribution", psha)
                key = v2.key_v2(s["match"], 1, model, digest, dec_json, v2.INPUT_VERSION,
                                v2.PROMPT_VERSION, v2.REPLICATE_ID, "attribution", psha)
                if con.execute("SELECT 1 FROM tasks WHERE task_key=?", (key,)).fetchone():
                    _reject(rejects, s["match"], 1, cond, "duplicate_existing_task")
                    continue
                tasks.append({
                    "task_key": key, "legacy_task_key": legacy_key, "match": s["match"], "innings": 1,
                    "model": model, "cond": cond, "field_scope": "attribution", "fields": fields,
                    "prompt": prompt, "prompt_sha": psha, "text_sha": V.sha256_text(text),
                    "num_predict": 300, "gold": gold, "model_digest": digest,
                    "decode_json": dec_json, "input_version": v2.INPUT_VERSION,
                    "prompt_version": v2.PROMPT_VERSION, "replicate_id": v2.REPLICATE_ID,
                })
    design = _design("C_adjudication",
                     "Same event under formal reassignment, maintained original, and no notice; separates notification understanding, old-value extraction, and propagation.",
                     reasons.get("rationale", "Adjudication branch on R28-linked attribution events."),
                     con, tasks, list(notices.keys()), models,
                     ["attribution_followup/samples.json", "scorecard-derived event"],
                     "exact integer match per field; change gold=new, maintain/no_notice gold=old")
    return design, tasks, rejects


def build_probe_sweep(con, reasons: dict) -> tuple:
    models = V.MODELS
    cursor = int(V.meta_get(con, "probe_cursor", "0") or 0)
    units = sweep_units()
    tasks, rejects = [], []
    used = 0
    for m, inn in units[cursor:]:
        if used >= 4:
            break
        variants = [("probe_runs", ["inn" + str(inn) + ".total_runs"]),
                    ("probe_wickets", ["inn" + str(inn) + ".total_wickets"]),
                    ("probe_both", ["inn" + str(inn) + ".total_runs", "inn" + str(inn) + ".total_wickets"])]
        before = len(tasks)
        tasks += make_probe_tasks(con, m, inn, "O", models, variants, rejects, num_predict=200)
        if len(tasks) > before:
            used += 1
    design = _design("P_field_sweep",
                     "Field-probe coverage: same full text, ask runs only, wickets only, or both; separates field confusion from evidence localisation across non-held-out roots.",
                     reasons.get("rationale", "Field-probe coverage after the condition sweep."),
                     con, tasks, ["probe_runs", "probe_wickets", "probe_both"], models,
                     ["commentary.txt", "scorecard.md"],
                     "exact integer match per field; coverage group kept separate from diagnostic branches")
    design["probe_next_cursor"] = cursor + used
    design["probe_total_units"] = len(units)
    return design, tasks, rejects


BUILDERS = {"T1_baseline_o": build_t1, "T2_hard_excerpt": build_t2,
            "T3_matched_deletion": build_t3, "T4_full_table": build_t4,
            "T5_hard_fulltext": build_t5, "A_field_probe": build_a,
            "B_cross_innings": build_b, "S_coverage_sweep": build_sweep,
            "C_adjudication": build_c, "P_field_sweep": build_probe_sweep}


def latest_scored(con):
    return con.execute("SELECT * FROM batches WHERE status='scored' ORDER BY seq DESC LIMIT 1").fetchone()


def decide(con) -> dict:
    if V.meta_get(con, "sweep_enabled", "0") == "1":
        cursor = int(V.meta_get(con, "sweep_cursor", "0") or 0)
        total = len(sweep_units())
        if cursor < total:
            return {"template": "S_coverage_sweep", "rule_id": "R12",
                    "observation": "coverage sweep enabled at unit " + str(cursor) + "/" + str(total),
                    "rationale": "Stratified coverage sweep takes precedence while valid units remain."}
    if V.meta_get(con, "probe_sweep_enabled", "0") == "1":
        pc = int(V.meta_get(con, "probe_cursor", "0") or 0)
        total = len(sweep_units())
        if pc < total:
            return {"template": "P_field_sweep", "rule_id": "R13",
                    "observation": "field-probe sweep at unit " + str(pc) + "/" + str(total),
                    "rationale": "Condition sweep exhausted; field-probe coverage takes over."}
    last = latest_scored(con)
    if last is None:
        return {"template": "T1_baseline_o", "rule_id": "R0", "observation": "no completed batch",
                "rationale": "Initial baseline: original text, development roots, target cells only."}
    score = json.loads(last["score_json"] or "{}")
    design = json.loads(last["design_json"] or "{}")
    acc = float(last["accuracy"] or 0)
    tpl = last["template"]
    focus = score.get("failing_positions") or design.get("positions") or []
    by_cond = score.get("by_condition") or {}
    base = {"observation": "batch " + last["batch_id"] + " " + tpl + " accuracy " + str(round(acc, 4)),
            "focus": focus}
    if tpl == "T1_baseline_o":
        if acc >= 0.90:
            return {**base, "template": "T2_hard_excerpt", "rule_id": "R1",
                    "rationale": "Baseline saturated at " + str(round(acc, 3)) + "; hard roots and a short excerpt are the next discriminator."}
        return {**base, "template": "T3_matched_deletion", "rule_id": "R2",
                "rationale": "Baseline below 0.90 at " + str(round(acc, 3)) + "; drill into the failing roots with matched deletion controls."}
    if tpl == "T2_hard_excerpt":
        if acc >= 0.90:
            return {**base, "template": "T4_full_table", "rule_id": "R3", "cond": "E",
                    "rationale": "Excerpt recovered target cells at " + str(round(acc, 3)) + "; test the full 43-field table for collateral loss."}
        return {**base, "template": "T3_matched_deletion", "rule_id": "R4",
                "rationale": "Excerpt still fails at " + str(round(acc, 3)) + "; matched deletion controls on the failing hard root."}
    if tpl == "T3_matched_deletion":
        wi = (by_cond.get("WI") or {}).get("accuracy")
        oi = (by_cond.get("OI") or {}).get("accuracy")
        if wi is not None and oi is not None and wi < oi:
            return {**base, "template": "T4_full_table", "rule_id": "R5", "cond": "O",
                    "rationale": "WI " + str(wi) + " < OI " + str(oi) + "; deletion-specific damage, validate the full table on original text."}
        if e_eligible_positions(con):
            return {**base, "template": "T2_hard_excerpt", "rule_id": "R6",
                    "rationale": "WI " + str(wi) + " >= OI " + str(oi) + "; no specificity, expand the hard-root excerpt batch."}
        return {**base, "template": "T5_hard_fulltext", "rule_id": "R8",
                "rationale": "No remaining hard root has an explicit total sentence for E; run full-text O on unused hard roots instead."}
    if tpl == "T4_full_table":
        if e_eligible_positions(con):
            return {**base, "template": "T2_hard_excerpt", "rule_id": "R6",
                    "rationale": "Full-table validation complete; expand coverage on the next unused hard roots."}
        return {**base, "template": "T5_hard_fulltext", "rule_id": "R8",
                "rationale": "Full-table validation complete and no remaining hard root supports E; run full-text O on unused hard roots."}
    if tpl == "T5_hard_fulltext":
        return {**base, "template": "A_field_probe", "rule_id": "R10",
                "rationale": "Hard full-text fallback complete; move to the field-probe branch on fixed evidence."}
    if tpl == "A_field_probe":
        return {**base, "template": "B_cross_innings", "rule_id": "R11",
                "rationale": "Field probe complete; move to cross-innings binding with explicit innings."}
    if tpl == "B_cross_innings":
        return {**base, "template": "S_coverage_sweep", "rule_id": "R12",
                "rationale": "Cross-innings branch complete; start the stratified coverage sweep."}
    if tpl == "S_coverage_sweep":
        cursor = int(V.meta_get(con, "sweep_cursor", "0") or 0)
        total = len(sweep_units())
        if cursor < total:
            return {**base, "template": "S_coverage_sweep", "rule_id": "R12",
                    "rationale": "Coverage sweep continues at unit " + str(cursor) + "/" + str(total) + "."}
        return {**base, "template": "P_field_sweep", "rule_id": "R13",
                "rationale": "Coverage sweep exhausted; start field-probe coverage."}
    if tpl == "P_field_sweep":
        pc = int(V.meta_get(con, "probe_cursor", "0") or 0)
        total = len(sweep_units())
        if pc < total:
            return {**base, "template": "P_field_sweep", "rule_id": "R13",
                    "rationale": "Field-probe sweep continues at unit " + str(pc) + "/" + str(total) + "."}
        return {**base, "template": "T1_baseline_o", "rule_id": "R9",
                "rationale": "Field-probe sweep exhausted; expand remaining development roots."}
    return {**base, "template": "T1_baseline_o", "rule_id": "R0", "rationale": "Fallback baseline."}


def freeze_batch(con, design: dict, tasks: list, rejects: list, plan_ms: float = 0.0) -> str:
    seq = int(V.meta_get(con, "batch_seq", "0")) + 1
    batch_id = "B" + str(seq).zfill(3)
    manifest = {
        "batch_id": batch_id, "seq": seq, "template": design["template"],
        "created_at": V.now_iso(), "design": design,
        "schema_version": v2.SCHEMA_VERSION, "scoring_version": v2.SCORING_VERSION,
        "tasks": [{k: t[k] for k in ("task_key", "legacy_task_key", "match", "innings", "model", "cond",
                                     "field_scope", "fields", "prompt", "prompt_sha", "text_sha",
                                     "num_predict", "gold", "model_digest", "decode_json",
                                     "input_version", "prompt_version", "replicate_id")} for t in tasks],
        "rejected": rejects,
    }
    path = V.BATCHES / (batch_id + ".json")
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    msha = V.sha256_text(path.read_text(encoding="utf-8"))
    con.execute("INSERT INTO batches(batch_id, seq, template, created_at, hypothesis, rationale, design_json, "
                "manifest_path, manifest_sha, status, parent_batch_id, trigger_json, cost_json, updated_at, "
                "scoring_version, manifest_version, template_version, plan_ms) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (batch_id, seq, design["template"], V.now_iso(), design["hypothesis"], design["rationale"],
                 json.dumps(design, ensure_ascii=False), str(path), msha, "running",
                 design.get("parent_batch_id"), json.dumps(design.get("trigger") or {}, ensure_ascii=False),
                 json.dumps(design["cost"], ensure_ascii=False), V.now_iso(),
                 v2.SCORING_VERSION, "v2", "v2", float(plan_ms)))
    for t in tasks:
        con.execute("INSERT INTO tasks(task_key, batch_id, match, innings, model, cond, field_scope, fields_json, "
                    "prompt, prompt_sha, text_sha, num_predict, status, attempts, created_at, updated_at, "
                    "model_digest, decode_json, input_version, prompt_version, replicate_id, legacy_task_key, "
                    "identity_status, gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (t["task_key"], batch_id, t["match"], t["innings"], t["model"], t["cond"],
                     t["field_scope"], json.dumps(t["fields"]), t["prompt"], t["prompt_sha"],
                     t["text_sha"], t["num_predict"], "queued", 0, V.now_iso(), V.now_iso(),
                     t["model_digest"], t["decode_json"], t["input_version"], t["prompt_version"],
                     t["replicate_id"], t["legacy_task_key"], "v2", json.dumps(t["gold"], ensure_ascii=False)))
        con.execute("INSERT OR IGNORE INTO task_key_map(old_key,new_key,batch_id,match,innings,model,cond,"
                    "replicate_id,created_at,reason) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (t["legacy_task_key"], t["task_key"], batch_id, t["match"], t["innings"], t["model"],
                     t["cond"], t["replicate_id"], V.now_iso(), "v2_new_task"))
    for r in rejects:
        con.execute("INSERT INTO candidates(batch_id, match, innings, cond, model, eligible, reason, created_at) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (batch_id, r.get("match"), r.get("innings"), r.get("cond"), None, 0, r.get("reason"), V.now_iso()))
    V.meta_set(con, "batch_seq", seq)
    con.commit()
    V.event("batch_frozen", {"batch_id": batch_id, "template": design["template"],
                             "tasks": len(tasks), "rejected": len(rejects), "manifest_sha": msha}, con)
    (V.BATCHES / (batch_id + "_DESIGN.md")).write_text(render_design_md(batch_id, design, tasks, rejects),
                                                       encoding="utf-8")
    return batch_id


def render_design_md(batch_id: str, design: dict, tasks: list, rejects: list) -> str:
    lines = ["# " + batch_id + " " + design["template"], "",
             "- hypothesis: " + design["hypothesis"], "- rationale: " + design["rationale"],
             "- created: " + design["created_at"],
             "- requests: " + str(design["cost"]["requests"]) + " (external API 0)",
             "- scoring: " + design["scoring"], "- sources: " + ", ".join(design["sources"]), "",
             "## Positions", ""]
    for p in design["positions"]:
        lines.append("- " + p["match"] + " innings " + str(p["innings"]))
    lines += ["", "## Conditions", "", ", ".join(design["conditions"]), "", "## Models", ""]
    lines += ["- " + m for m in design["models"]]
    lines += ["", "## Tasks", ""]
    for t in tasks:
        lines.append("- " + t["match"] + " inn" + str(t["innings"]) + " " + t["cond"] + " " + t["model"] +
                     " (" + t["field_scope"] + ") key=" + t["task_key"][:12])
    lines += ["", "## Rejected candidates", ""]
    if rejects:
        for r in rejects:
            lines.append("- " + str(r.get("match")) + " " + str(r.get("cond")) + ": " + str(r.get("reason")))
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def plan_and_freeze(con) -> dict:
    t0 = time.time()
    decision = decide(con)
    chain = [decision["template"]]
    if decision["template"] in ("T2_hard_excerpt", "T3_matched_deletion", "T4_full_table"):
        chain += ["T5_hard_fulltext", "T1_baseline_o"]
    elif decision["template"] == "T5_hard_fulltext":
        chain += ["T1_baseline_o"]
    elif decision["template"] == "S_coverage_sweep":
        chain += ["P_field_sweep"]
    all_rejects = []
    for idx, tpl in enumerate(chain):
        builder = BUILDERS.get(tpl)
        if builder is None:
            continue
        design, tasks, rejects = builder(con, decision)
        all_rejects += rejects
        if not tasks:
            if tpl == "S_coverage_sweep":
                V.meta_set(con, "sweep_cursor", len(sweep_units()))
                con.commit()
            continue
        rationale = decision["rationale"]
        rule_id = decision["rule_id"]
        if idx > 0:
            rationale = rationale + " | fallback: " + decision["template"] + " produced no eligible task; executed " + tpl + "."
            rule_id = decision["rule_id"] + "F"
        design["rationale"] = rationale
        design["parent_batch_id"] = decision.get("parent_batch_id")
        design["trigger"] = {"rule_id": rule_id, "observation": decision["observation"], "rationale": rationale}
        plan_ms = round((time.time() - t0) * 1000, 1)
        batch_id = freeze_batch(con, design, tasks, all_rejects, plan_ms=plan_ms)
        if "sweep_next_cursor" in design:
            V.meta_set(con, "sweep_cursor", design["sweep_next_cursor"])
            con.commit()
        if "probe_next_cursor" in design:
            V.meta_set(con, "probe_cursor", design["probe_next_cursor"])
            con.commit()
        last = latest_scored(con)
        source_batch_id = last["batch_id"] if last else None
        source_ids = []
        trigger_metrics = {"observation": decision["observation"]}
        if last:
            sc = json.loads(last["score_json"] or "{}")
            source_ids = sorted({e.get("task_key") for e in sc.get("errors", []) if e.get("task_key")})
            trigger_metrics.update({"accuracy": last["accuracy"],
                                    "by_condition": sc.get("by_condition"),
                                    "failing_positions": sc.get("failing_positions")})
        con.execute("INSERT INTO decisions(batch_id, created_at, observation, rule_id, action, next_batch_id, "
                    "rationale, source_batch_id, source_result_ids, rule_version, trigger_metrics_json) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (source_batch_id or "genesis", V.now_iso(), decision["observation"],
                     rule_id, tpl, batch_id, rationale, source_batch_id,
                     json.dumps(source_ids, ensure_ascii=False), v2.RULE_VERSION,
                     json.dumps(trigger_metrics, ensure_ascii=False)))
        con.commit()
        V.event("decision", {"rule": rule_id, "next": batch_id, "rationale": rationale}, con)
        return {"ok": True, "batch_id": batch_id, "decision": decision, "template": tpl,
                "fallback": idx > 0, "tasks": len(tasks), "rejected": len(all_rejects)}
    return {"ok": False, "reason": "no_eligible_tasks", "decision": decision, "rejects": all_rejects}
