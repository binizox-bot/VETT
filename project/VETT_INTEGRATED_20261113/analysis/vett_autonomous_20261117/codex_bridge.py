"""Codex exchange: export sealed historical batches + enqueue the two-match pilot."""
from __future__ import annotations
import hashlib, json, os, re, sys, zipfile, datetime
from pathlib import Path

WF = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0, str(WF))
import vettlib as V
import v2
import planner

INT = V.INT
AN = V.INT / "analysis"
EX = AN / "codex_exchange"
SAMPLE_PATH = AN / "attribution_followup" / "samples.json"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")

def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def notices_for(s):
    return {
        "C_no_notice": "No review notice is provided. Use the pre-revision record as published.",
        "C_maintain": "Match review: the original attribution to {A} is maintained. No change to either bowler's figures.".format(A=s["A"]),
        "C_change": "Match review: the dismissal is formally reassigned from {A} to {B}. Update both bowlers' figures; runs and innings total do not change.".format(A=s["A"], B=s["B"]),
    }

def strip_review(text: str) -> str:
    i = text.find("Match review:")
    return (text[:i] if i > 0 else text).strip()

def build_pilot():
    tasks, positions = [], []
    # 1) locator case: published commentary, full text vs same-source terminal window
    b = V.load_bundle("match_0087")
    full = b["text"]
    gold87 = V.gold_target(b["md"], 2)
    assert gold87.get("inn2.total_runs") == 198 and gold87.get("inn2.total_wickets") == 6, gold87
    sents = re.split(r"(?<=[.!?])\s+", full)
    idx = next(i for i, s in enumerate(sents) if "198 for 6" in s)
    window = " ".join(sents[max(0, idx - 1): idx + 1]).strip()
    assert "198 for 6" in window and len(window) < len(full)
    f87 = ["inn2.total_runs", "inn2.total_wickets"]
    for cond, text in (("X_full", full), ("X_window", window)):
        tasks.extend(make_task("match_0087", 2, cond, "target2", f87, gold87, text, V.build_prompt, 300))
    positions.append({"match": "match_0087", "innings": 2, "role": "locator", "gold": gold87,
                      "full_chars": len(full), "window_chars": len(window)})

    # 2) accounting case: one of the 8 adjudication events, full render vs compact window
    s = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))[0]
    fields = list(s["fields"].keys())
    old_gold = {s["A"] + "_wickets": s["Aw"], s["A"] + "_runs": s["Ar"],
                s["B"] + "_wickets": s["Bw"], s["B"] + "_runs": s["Br"],
                "innings_total_wickets": s["total"]}
    full_src = strip_review(s["texts"]["explicit"])
    win_src = strip_review(s["texts"]["short"])
    for mode, src in (("full", full_src), ("window", win_src)):
        for cond, notice in notices_for(s).items():
            text = src + " " + notice
            gold = dict(s["fields"]) if cond == "C_change" else dict(old_gold)
            cname = cond + "_" + mode
            tasks.extend(make_task(s["match"], 1, cname, "attribution", fields, gold, text, planner._c_prompt, 300, sample=s))
    positions.append({"match": s["match"], "innings": 1, "role": "accounting", "batter": s["batter"],
                      "A": s["A"], "B": s["B"], "old": old_gold, "new": s["fields"],
                      "full_chars": len(full_src), "window_chars": len(win_src)})

    design = {
        "template": "X_codex_abc_pilot",
        "hypothesis": "Two-case pilot: a published locator case (full text vs same-source terminal window) and an accounting case (no-notice / maintain / reassign, each in full render and compact window).",
        "rationale": "Protocol check before the next Codex-frozen batch: verify sent body, truncation, and output attribution.",
        "positions": positions,
        "fields": [],
        "conditions": sorted({t["cond"] for t in tasks}),
        "models": V.MODELS,
        "scoring": "exact integer per field; change gold=new, maintain/no_notice gold=old",
        "sources": ["published commentary match_0087", "attribution_followup/samples.json match_0003"],
        "cost": {"requests": len(tasks), "est_seconds": len(tasks) * 30, "external_api": 0},
        "created_at": NOW,
    }
    return design, tasks

def make_task(match, innings, cond, scope, fields, gold, text, prompt_fn, num_predict, sample=None):
    if prompt_fn is planner._c_prompt:
        prompt = prompt_fn(sample, cond, text, fields)
    else:
        prompt = prompt_fn(match, innings, cond, text, fields)
    psha = V.sha256_text(prompt)
    model = None
    out = []
    for model in V.MODELS:
        digest = V.model_digest(model)
        dec_json = json.dumps(v2.decode_config(num_predict), sort_keys=True)
        legacy = planner.task_key(match, innings, model, cond, scope, psha)
        key = v2.key_v2(match, innings, model, digest, dec_json, v2.INPUT_VERSION,
                        v2.PROMPT_VERSION, v2.REPLICATE_ID, scope, psha)
        out.append({"task_key": key, "legacy_task_key": legacy, "match": match, "innings": innings,
                    "model": model, "cond": cond, "field_scope": scope, "fields": fields,
                    "prompt": prompt, "prompt_sha": psha, "text_sha": V.sha256_text(text),
                    "num_predict": num_predict, "gold": gold, "model_digest": digest,
                    "decode_json": dec_json, "input_version": v2.INPUT_VERSION,
                    "prompt_version": v2.PROMPT_VERSION, "replicate_id": v2.REPLICATE_ID})
    return out

def flatten(design, tasks):
    return design, [t for group in tasks for t in (group if isinstance(group, list) else [group])]

def export():
    EX.mkdir(parents=True, exist_ok=True)
    con = V.connect(); con.row_factory = None
    # sealed adjudication batches
    bdir = EX / "SEALED_B019_B022"
    all_tasks, all_results = [], []
    for bid in ("B019", "B022"):
        rows = con.execute("SELECT * FROM tasks WHERE batch_id=? ORDER BY match, innings, cond, model", (bid,)).fetchall()
        names = [d[0] for d in con.execute("SELECT * FROM tasks LIMIT 1").description]
        for r in rows:
            d = dict(zip(names, r))
            all_tasks.append({k: d.get(k) for k in ("task_key","legacy_task_key","batch_id","match","innings","model","cond","field_scope","fields_json","prompt","prompt_sha","text_sha","num_predict","model_digest","decode_json","input_version","prompt_version","replicate_id","gold_json")})
        rrows = con.execute("SELECT * FROM results WHERE batch_id=? ORDER BY match, innings, cond, model", (bid,)).fetchall()
        rnames = [d[0] for d in con.execute("SELECT * FROM results LIMIT 1").description]
        for r in rrows:
            d = dict(zip(rnames, r))
            all_results.append({k: d.get(k) for k in ("task_key","batch_id","match","innings","model","cond","raw_output","parsed_json","parse_ok","score_json","correct","duration_ms","request_json","response_meta_json","model_digest","decode_json","created_at")})
    write_jsonl(bdir / "tasks.jsonl", all_tasks)
    write_jsonl(bdir / "results.jsonl", all_results)
    for bid in ("B019", "B022"):
        src = V.BATCHES / (bid + ".json")
        if src.exists(): (bdir / (bid + ".json")).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    # published D runs (prompt not stored; rebuild material included)
    pdir = EX / "PUBLISHED_D_RUNS"
    pdir.mkdir(parents=True, exist_ok=True)
    src = AN / "vett_overnight_20261114" / "runs" / "expand.jsonl"
    (pdir / "expand.jsonl").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    (pdir / "REBUILD.md").write_text(
        "# Published D runs: rebuild material\n\n"
        "expand.jsonl stores prompt_sha256 and text_sha256 but NOT the prompt body. Rebuild the exact prompt with:\n\n"
        "    python VETT_INTEGRATED_20261113/analysis/vett_overnight_20261114/expand.py\n\n"
        "and verify each row's prompt_sha256 and text_sha256 before reuse. Source text is the published commentary under Self-cricket-clean_text_scorecard_v1_220_matches/match_*/commentary.txt.\n", encoding="utf-8")
    for name in ("expand.py", "build.py"):
        p = AN / "vett_overnight_20261114" / name
        if p.exists(): (pdir / name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

    # pilot manifest (exact prompts, same content as B209Z)
    design, groups = build_pilot()
    tasks = [t for g in groups for t in (g if isinstance(g, list) else [g])]
    pdir2 = EX / "PILOT_B209Z"
    write_json(pdir2 / "design.json", design)
    write_jsonl(pdir2 / "tasks.jsonl", tasks)
    (pdir2 / "README.md").write_text(
        "# B209Z two-match pilot\n\n"
        "- 2 positions x 8 condition-variants x 3 models = 24 requests.\n"
        "- Locator: match_0087 inn2, published full text vs same-source terminal window, gold 198/6.\n"
        "- Accounting: match_0003 inn1, no-notice/maintain/reassign x full render/compact window; gold old or new per condition.\n"
        "- Prompts are exact; verify prompt_sha before reuse.\n", encoding="utf-8")

    # manifest v1
    samples = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    events = [{"match": s["match"], "innings": s["innings"], "batter": s["batter"], "A": s["A"], "B": s["B"],
               "A_old": [s["Aw"], s["Ar"]], "B_old": [s["Bw"], s["Br"]], "total": s["total"],
               "new": s["fields"], "old": planner._old_gold(s)} for s in samples]
    manifest = {
        "version": "codex-exchange-v1", "created_at": NOW,
        "protocol": "freeze -> run -> seal -> recompute; DSH is sole writer to Ollama and workflow.db",
        "models": V.MODELS, "decode": v2.decode_config(300),
        "input_version": v2.INPUT_VERSION, "prompt_version": v2.PROMPT_VERSION, "replicate_id": v2.REPLICATE_ID,
        "events": events,
        "pilots": design["positions"],
        "files": [],
        "notes": ["B019/B022 prompts are exact DB values.", "D runs store hashes only; rebuild with expand.py.",
                  "Pilot accounting full render may omit pre-revision figures; this is recorded, not hidden."],
    }
    for root, _, files in os.walk(EX):
        for fn in sorted(files):
            if fn.endswith(".zip") or fn == "SHA256SUMS.txt": continue
            p = Path(root) / fn
            rel = str(p.relative_to(EX)).replace("\\", "/")
            manifest["files"].append({"path": rel, "bytes": p.stat().st_size, "sha256": sha_bytes(p.read_bytes())})
    write_json(EX / "MANIFEST_v1.json", manifest)
    (EX / "README.md").write_text(
        "# Codex exchange v1\n\n"
        "DSH writes Ollama and workflow.db; Codex reads sealed material and returns score corrections.\n\n"
        "1. Codex freezes a manifest (sample ids + prompt hashes + model config).\n"
        "2. DSH integrates at the next batch boundary, reuses verifiable historical results.\n"
        "3. DSH seals each finished batch here (tasks, raw answers, request metadata, scores).\n"
        "4. Codex recomputes offline; DSH re-runs only if model input was wrong or a matching condition is missing.\n\n"
        "Layout:\n"
        "- MANIFEST_v1.json: protocol, models, 8 events, pilot design, file hashes.\n"
        "- SEALED_B019_B022/: 72 adjudication tasks with exact prompts, raw answers, scores.\n"
        "- PUBLISHED_D_RUNS/: O/M/E run rows; prompts must be rebuilt and hash-checked.\n"
        "- PILOT_B209Z/: exact prompts for the 24-request two-match pilot.\n", encoding="utf-8")

    # checksums + zip
    lines = []
    for root, _, files in os.walk(EX):
        for fn in sorted(files):
            if fn.endswith(".zip") or fn == "SHA256SUMS.txt": continue
            p = Path(root) / fn
            lines.append(sha_bytes(p.read_bytes()) + "  " + str(p.relative_to(EX)).replace("\\", "/"))
    (EX / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    zpath = EX / ("codex_exchange_20261121.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(EX):
            for fn in sorted(files):
                p = Path(root) / fn
                if p == zpath: continue
                z.write(p, str(p.relative_to(EX)).replace("\\", "/"))
    con.close()
    return {"export": str(EX), "tasks": len(all_tasks), "results": len(all_results), "pilot_tasks": len(tasks), "zip": str(zpath), "zip_bytes": zpath.stat().st_size}

def enqueue():
    design, groups = build_pilot()
    tasks = [t for g in groups for t in (g if isinstance(g, list) else [g])]
    con = V.connect()
    if con.execute("SELECT 1 FROM batches WHERE batch_id='B209Z'").fetchone():
        return {"ok": False, "error": "B209Z already exists"}
    batch_id, seq = "B209Z", 209
    manifest = {"batch_id": batch_id, "seq": seq, "template": design["template"], "created_at": NOW,
                "design": design, "schema_version": v2.SCHEMA_VERSION, "scoring_version": v2.SCORING_VERSION,
                "tasks": [{k: t[k] for k in ("task_key","legacy_task_key","match","innings","model","cond",
                                             "field_scope","fields","prompt","prompt_sha","text_sha",
                                             "num_predict","gold","model_digest","decode_json",
                                             "input_version","prompt_version","replicate_id")} for t in tasks],
                "rejected": []}
    mpath = V.BATCHES / (batch_id + ".json")
    mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    msha = V.sha256_text(mpath.read_text(encoding="utf-8"))
    con.execute("INSERT INTO batches(batch_id, seq, template, created_at, hypothesis, rationale, design_json, manifest_path, manifest_sha, status, parent_batch_id, trigger_json, cost_json, updated_at, scoring_version, manifest_version, template_version, plan_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (batch_id, seq, design["template"], NOW, design["hypothesis"], design["rationale"],
                 json.dumps(design, ensure_ascii=False), str(mpath), msha, "running", None, "{}",
                 json.dumps(design["cost"], ensure_ascii=False), NOW, v2.SCORING_VERSION, "v2", "v2", 0.0))
    for t in tasks:
        con.execute("INSERT INTO tasks(task_key, batch_id, match, innings, model, cond, field_scope, fields_json, prompt, prompt_sha, text_sha, num_predict, status, attempts, created_at, updated_at, model_digest, decode_json, input_version, prompt_version, replicate_id, legacy_task_key, identity_status, gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (t["task_key"], batch_id, t["match"], t["innings"], t["model"], t["cond"], t["field_scope"],
                     json.dumps(t["fields"]), t["prompt"], t["prompt_sha"], t["text_sha"], t["num_predict"],
                     "queued", 0, NOW, NOW, t["model_digest"], t["decode_json"], t["input_version"],
                     t["prompt_version"], t["replicate_id"], t["legacy_task_key"], "v2", json.dumps(t["gold"], ensure_ascii=False)))
        con.execute("INSERT OR IGNORE INTO task_key_map(old_key,new_key,batch_id,match,innings,model,cond,replicate_id,created_at,reason) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (t["legacy_task_key"], t["task_key"], batch_id, t["match"], t["innings"], t["model"], t["cond"], t["replicate_id"], NOW, "v2_new_task"))
    con.commit()
    V.event("batch_frozen", {"batch_id": batch_id, "template": design["template"], "tasks": len(tasks), "rejected": 0, "manifest_sha": msha, "note": "codex pilot, priority seq 209"}, con)
    con.commit()
    con.close()
    return {"ok": True, "batch_id": batch_id, "tasks": len(tasks), "manifest": str(mpath), "manifest_sha": msha}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "export"
    out = export() if mode == "export" else enqueue()
    print(json.dumps(out, ensure_ascii=False))
