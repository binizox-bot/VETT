
"""Shared core for the VETT autonomous local experiment workflow.

All inference is local Ollama over 127.0.0.1. No external API is called.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT = ROOT / "VETT_INTEGRATED_20261113"
WF = INT / "analysis" / "vett_autonomous_20261117"
CONFIG_DIR = WF / "config"
STATE = WF / "state"
BATCHES = WF / "batches"
RUNS = WF / "runs"
REPORTS = WF / "reports"
LOGS = WF / "logs"
DB_PATH = Path(os.environ.get("VETT_DB_PATH") or (STATE / "workflow.db"))
CONFIG_PATH = CONFIG_DIR / "research_scope.json"
PYTHON = Path(r"C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe")
if not PYTHON.exists():
    PYTHON = Path(sys.executable)

sys.path.insert(0, str(INT / "scripts"))
import pilot_lib as L  # noqa: E402


def ensure_dirs() -> None:
    for p in (CONFIG_DIR, STATE, BATCHES, RUNS, REPORTS, LOGS):
        p.mkdir(parents=True, exist_ok=True)


def now_iso(offset_seconds: float = 0) -> str:
    return (datetime.now().astimezone() + timedelta(seconds=offset_seconds)).isoformat(timespec="seconds")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


CONFIG = load_config()
MODELS = CONFIG["models"]
TARGET_FIELDS = CONFIG["target_fields"]
OLLAMA = CONFIG["ollama"]

FULL43_PREFIX = ["match.result", "match.toss", "match.pom"]
SUMMARY_FIELDS = ["team", "total_runs", "total_wickets", "overs", "byes", "leg_byes", "no_balls", "wides"]


def full43_fields() -> list:
    fields = list(FULL43_PREFIX)
    for p in ("inn1", "inn2"):
        fields += [p + "." + f for f in SUMMARY_FIELDS]
        for r in (1, 2, 3):
            fields += [p + ".bat" + str(r) + "_name", p + ".bat" + str(r) + "_runs"]
        for r in (1, 2):
            fields += [p + ".bowl" + str(r) + "_name", p + ".bowl" + str(r) + "_wickets", p + ".bowl" + str(r) + "_runs"]
    return fields


FULL43 = full43_fields()
assert len(FULL43) == 43, len(FULL43)


# ---------------------------------------------------------------- database

def connect() -> sqlite3.Connection:
    ensure_dirs()
    con = sqlite3.connect(str(DB_PATH), timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA busy_timeout=30000")
    try:
        con.execute("PRAGMA journal_mode=WAL")
    except sqlite3.OperationalError:
        # WAL is persistent; a concurrent opener holding the lock is not fatal.
        pass
    con.execute("PRAGMA synchronous=NORMAL")
    return con


SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS batches (
  batch_id TEXT PRIMARY KEY, seq INTEGER, template TEXT, created_at TEXT,
  hypothesis TEXT, rationale TEXT, design_json TEXT, manifest_path TEXT,
  manifest_sha TEXT, status TEXT, score_json TEXT, accuracy REAL,
  parent_batch_id TEXT, trigger_json TEXT, cost_json TEXT, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS tasks (
  task_key TEXT PRIMARY KEY, batch_id TEXT, match TEXT, innings INTEGER,
  model TEXT, cond TEXT, field_scope TEXT, fields_json TEXT,
  prompt TEXT, prompt_sha TEXT, text_sha TEXT, num_predict INTEGER DEFAULT 300,
  status TEXT DEFAULT 'queued', attempts INTEGER DEFAULT 0,
  claimed_by INTEGER, claimed_at TEXT, created_at TEXT, updated_at TEXT,
  recoveries INTEGER DEFAULT 0, error TEXT
);
CREATE TABLE IF NOT EXISTS results (
  task_key TEXT PRIMARY KEY, batch_id TEXT, match TEXT, innings INTEGER,
  model TEXT, cond TEXT, raw_output TEXT, parsed_json TEXT,
  parse_ok INTEGER, score_json TEXT, correct INTEGER,
  duration_ms REAL, request_json TEXT, response_meta_json TEXT,
  created_at TEXT, error TEXT
);
CREATE TABLE IF NOT EXISTS decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, batch_id TEXT, created_at TEXT,
  observation TEXT, rule_id TEXT, action TEXT, next_batch_id TEXT, rationale TEXT
);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, kind TEXT, payload TEXT
);
CREATE TABLE IF NOT EXISTS candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT, batch_id TEXT, match TEXT, innings INTEGER,
  cond TEXT, model TEXT, eligible INTEGER, reason TEXT, created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_batch ON tasks(batch_id);
CREATE INDEX IF NOT EXISTS idx_results_batch ON results(batch_id);
CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
"""


def init_db() -> sqlite3.Connection:
    con = connect()
    con.executescript(SCHEMA)
    defaults = {
        "state": "new",
        "paused": "0",
        "stop_requested": "0",
        "external_api_calls": "0",
        "created_at": now_iso(),
        "method_version": CONFIG["method_version"],
        "last_status_at": "",
        "last_snapshot_at": "",
        "supervisor_pid": "",
        "worker_pid": "",
        "worker_started_at": "",
        "worker_restarts": "0",
        "batch_seq": "0",
        "exhausted": "0",
    }
    for k, v in defaults.items():
        con.execute("INSERT OR IGNORE INTO meta(key, value) VALUES (?, ?)", (k, v))
    con.commit()
    try:
        import v2
        v2.ensure_schema(con)
    except Exception as e:
        event("v2_migration_error", {"error": type(e).__name__ + ": " + str(e)}, con)
    return con


def meta_get(con: sqlite3.Connection, key: str, default: str = "") -> str:
    row = con.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def meta_set(con: sqlite3.Connection, key: str, value) -> None:
    con.execute("INSERT INTO meta(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, str(value)))


def event(kind: str, payload=None, con: sqlite3.Connection | None = None) -> None:
    own = con is None
    if own:
        con = connect()
    con.execute("INSERT INTO events(ts, kind, payload) VALUES (?, ?, ?)",
                (now_iso(), kind, json.dumps(payload or {}, ensure_ascii=False)))
    con.commit()
    if own:
        con.close()


def queue_counts(con: sqlite3.Connection) -> dict:
    rows = con.execute("SELECT status, COUNT(*) AS n FROM tasks GROUP BY status").fetchall()
    d = {r["status"]: r["n"] for r in rows}
    for k in ("queued", "claimed", "done", "failed"):
        d.setdefault(k, 0)
    return d


# ---------------------------------------------------------------- processes

def pid_alive(pid) -> bool:
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    STILL_ACTIVE = 259
    h = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h:
        return False
    code = ctypes.c_ulong()
    ok = ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
    ctypes.windll.kernel32.CloseHandle(h)
    return bool(ok) and code.value == STILL_ACTIVE


def kill_tree(pid) -> None:
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return
    if pid <= 0:
        return
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, text=True)


# ---------------------------------------------------------------- ollama

_TAG_CACHE = {"ts": 0.0, "models": {}}


def ollama_tags(force: bool = False) -> dict:
    if not force and time.time() - _TAG_CACHE["ts"] < 300 and _TAG_CACHE["models"]:
        return _TAG_CACHE["models"]
    url = OLLAMA["url"].replace("/api/generate", "/api/tags")
    with urllib.request.urlopen(url, timeout=10) as r:
        body = json.loads(r.read().decode("utf-8"))
    models = {m["name"]: m for m in body.get("models", [])}
    _TAG_CACHE["models"] = models
    _TAG_CACHE["ts"] = time.time()
    return models


def model_digest(model: str) -> str:
    try:
        return (ollama_tags().get(model) or {}).get("digest", "")
    except Exception:
        return ""


def ollama_generate(model: str, prompt: str, num_predict: int | None = None) -> dict:
    options = {
        "temperature": OLLAMA["temperature"],
        "seed": OLLAMA["seed"],
        "num_ctx": OLLAMA["num_ctx"],
        "num_predict": int(num_predict or OLLAMA["num_predict"]),
        "top_p": float(OLLAMA.get("top_p", 1.0)),
    }
    req = {"model": model, "prompt": prompt, "stream": False, "options": options}
    data = json.dumps(req, ensure_ascii=False).encode("utf-8")
    attempts = int(OLLAMA.get("max_retries", 2)) + 1
    last_err = ""
    t0 = time.time()
    for attempt in range(1, attempts + 1):
        try:
            http_req = urllib.request.Request(OLLAMA["url"], data=data,
                                              headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(http_req, timeout=OLLAMA.get("timeout_seconds", 900)) as r:
                body = json.loads(r.read().decode("utf-8"))
            meta = {k: body.get(k) for k in ("model", "done", "done_reason", "eval_count",
                                             "prompt_eval_count", "total_duration", "load_duration",
                                             "eval_duration")}
            meta["model_digest"] = model_digest(model)
            return {"raw": body.get("response", ""), "meta": meta,
                    "duration_ms": round((time.time() - t0) * 1000, 1),
                    "request": {"model": model, "options": options, "prompt_sha": sha256_text(prompt),
                                "prompt_chars": len(prompt), "url": OLLAMA["url"]},
                    "attempts": attempt, "error": None}
        except urllib.error.HTTPError as e:
            last_err = "HTTP " + str(e.code) + ": " + e.read().decode("utf-8", "replace")[:400]
            if 400 <= e.code < 500:
                break
        except Exception as e:
            last_err = type(e).__name__ + ": " + str(e)
        if attempt < attempts:
            time.sleep(2 * attempt)
    return {"raw": "", "meta": {}, "duration_ms": round((time.time() - t0) * 1000, 1),
            "request": {"model": model, "options": options, "prompt_sha": sha256_text(prompt),
                        "prompt_chars": len(prompt), "url": OLLAMA["url"]},
            "attempts": attempts, "error": last_err or "unknown error"}


# ---------------------------------------------------------------- parsing

def parse_json_object(raw: str):
    if not raw:
        return None
    s = raw.strip()
    fence = chr(96) * 3
    if s.startswith(fence):
        s = re.sub(r"^" + fence + r"[a-zA-Z]*\s*", "", s)
        s = re.sub(r"\s*" + fence + r"\s*$", "", s)
    i = s.find("{")
    if i < 0:
        return None
    depth = 0
    in_str = False
    esc = False
    for j in range(i, len(s)):
        ch = s[j]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(s[i:j + 1])
                except Exception:
                    return None
    return None


def int_value(v):
    if isinstance(v, dict):
        v = v.get("value")
    if isinstance(v, bool):
        return None
    try:
        return int(str(v).strip().replace(",", ""))
    except Exception:
        return None


# ---------------------------------------------------------------- gold

_BUNDLE_CACHE = {}


def load_bundle(match: str) -> dict:
    if match in _BUNDLE_CACHE:
        return _BUNDLE_CACHE[match]
    md = L.parse_scorecard_full((L.DATASET / match / "scorecard.md").read_text(encoding="utf-8"), match)
    text = (L.DATASET / match / "commentary.txt").read_text(encoding="utf-8")
    bundle = {"md": md, "text": text, "ss": L.sentences(text)}
    _BUNDLE_CACHE[match] = bundle
    return bundle


def gold43(md) -> dict:
    f = {"match.result": md.result, "match.toss": md.toss, "match.pom": md.player_of_match}
    for i, inn in enumerate(md.innings, 1):
        p = "inn" + str(i)
        f[p + ".team"] = inn.name
        f[p + ".total_runs"] = inn.total_runs
        f[p + ".total_wickets"] = inn.total_wickets
        f[p + ".overs"] = inn.overs
        f[p + ".byes"] = inn.byes
        f[p + ".leg_byes"] = inn.leg_byes
        f[p + ".no_balls"] = inn.no_balls
        f[p + ".wides"] = inn.wides
        for r, b in enumerate(sorted(inn.batters, key=lambda x: x.runs, reverse=True)[:3], 1):
            f[p + ".bat" + str(r) + "_name"] = b.name
            f[p + ".bat" + str(r) + "_runs"] = b.runs
        for r, b in enumerate(sorted(inn.bowlers, key=lambda x: (x.wickets, -x.runs_conceded), reverse=True)[:2], 1):
            f[p + ".bowl" + str(r) + "_name"] = b.name
            f[p + ".bowl" + str(r) + "_wickets"] = b.wickets
            f[p + ".bowl" + str(r) + "_runs"] = b.runs_conceded
    return f


def gold_target(md, innings: int) -> dict:
    if innings < 1 or innings > len(md.innings):
        return {}
    inn = md.innings[innings - 1]
    p = "inn" + str(innings)
    return {p + ".total_runs": inn.total_runs, p + ".total_wickets": inn.total_wickets}


# ---------------------------------------------------------------- conditions

def _team_tokens(team: str) -> list:
    toks = [t for t in re.findall(r"[A-Za-z]+", team) if len(t) > 2 and t.lower() != "xi"]
    return toks[:2]


_WICKET_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
                 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def _wicket_pattern(wickets: int) -> str:
    alts = [str(wickets)]
    if wickets in _WICKET_WORDS:
        alts.append(_WICKET_WORDS[wickets])
    return r"(?:\bfor\s+(?:" + "|".join(alts) + r")\b|/\s*" + str(wickets) + r"\b)"


def evidence_index(ss: list, team: str, runs: int, wickets: int):
    toks = _team_tokens(team)
    wkpat = _wicket_pattern(wickets)
    for i, s in enumerate(ss):
        if not re.search(r"(?<![0-9])" + str(runs) + r"(?![0-9])", s):
            continue
        if toks and not any(t.lower() in s.lower() for t in toks):
            continue
        if wickets >= 10 and re.search(r"all\s*out", s, re.I):
            return i
        if re.search(wkpat, s, re.I):
            return i
    for i, s in enumerate(ss):
        if re.search(r"(?<![0-9])" + str(runs) + r"(?![0-9])", s) and re.search(
                wkpat + r"|all\s*out", s, re.I):
            return i
    return None


def _mid_score_index(ss: list, exclude: set, team: str):
    toks = _team_tokens(team)
    fallback = None
    for i, s in enumerate(ss):
        if i in exclude:
            continue
        if not re.search(r"\b\d{1,3}\s*(?:/|for)\s*\d{1,2}\b", s, re.I):
            continue
        if toks and any(t.lower() in s.lower() for t in toks):
            return i
        if fallback is None:
            fallback = i
    return fallback


def _other_total_index(ss: list, exclude: set, other_inn):
    if other_inn is None:
        return None
    runs = other_inn.total_runs
    wk = other_inn.total_wickets
    for i, s in enumerate(ss):
        if i in exclude:
            continue
        if not re.search(r"(?<![0-9])" + str(runs) + r"(?![0-9])", s):
            continue
        if re.search(r"(?:\bfor\s+" + str(wk) + r"\b|/\s*" + str(wk) + r"\b|all\s*out|reached|posted|made)", s, re.I):
            return i
    return None


def build_conditions(match: str, innings: int) -> dict:
    bundle = load_bundle(match)
    md, ss = bundle["md"], bundle["ss"]
    if innings < 1 or innings > len(md.innings):
        return {"variants": {}, "reasons": {"innings": "out of range"}, "evidence_idx": None}
    inn = md.innings[innings - 1]
    ev = evidence_index(ss, inn.name, inn.total_runs, inn.total_wickets)
    variants = {"O": bundle["text"]}
    reasons = {}
    if ev is None:
        reasons["E"] = "no explicit total sentence found"
        return {"variants": variants, "reasons": reasons, "evidence_idx": None}
    variants["E"] = " ".join(ss[max(0, ev - 1):ev + 2])
    moved = [s for j, s in enumerate(ss) if j != ev]
    if moved:
        p_list = list(moved)
        p_list.insert(1 if len(p_list) > 1 else len(p_list), ss[ev])
        variants["P"] = " ".join(p_list)
        variants["L"] = " ".join(moved + [ss[ev]])
    comp = _mid_score_index(ss, {ev}, inn.name)
    if comp is not None:
        variants["WI"] = " ".join(s for j, s in enumerate(ss) if j != comp)
        cand = [j for j, s in enumerate(ss) if j not in (ev, comp)
                and abs(len(s) - len(ss[comp])) < max(80, len(ss[comp]) * 0.6)]
        if cand:
            variants["WIC"] = " ".join(s for j, s in enumerate(ss) if j != cand[0])
    else:
        reasons["WI"] = "no second mid-innings score sentence"
    other = md.innings[1] if len(md.innings) > 1 and innings == 1 else (md.innings[0] if len(md.innings) > 1 else None)
    oi = _other_total_index(ss, {ev}, other)
    if oi is not None:
        variants["OI"] = " ".join(s for j, s in enumerate(ss) if j != oi)
        cand = [j for j, s in enumerate(ss) if j not in (ev, oi)
                and abs(len(s) - len(ss[oi])) < max(80, len(ss[oi]) * 0.6)]
        if cand:
            variants["OIC"] = " ".join(s for j, s in enumerate(ss) if j != cand[0])
    else:
        reasons["OI"] = "no other-innings total sentence"

    def _nearest_control(ref_idx, exclude):
        ref_len = len(ss[ref_idx])
        best, best_diff = None, 10 ** 9
        target_runs = str(inn.total_runs)
        other_runs = str(other.total_runs) if other is not None else None
        for j, s in enumerate(ss):
            if j in exclude:
                continue
            if re.search(r"(?<![0-9])" + target_runs + r"(?![0-9])", s):
                continue
            if other_runs and re.search(r"(?<![0-9])" + other_runs + r"(?![0-9])", s):
                continue
            d = abs(len(s) - ref_len)
            if d < best_diff:
                best, best_diff = j, d
        return best

    if oi is not None:
        nei = _nearest_control(oi, {ev, oi})
        if nei is not None:
            variants["NEI_OI"] = " ".join(s for j, s in enumerate(ss) if j != nei)
    if comp is not None:
        nei = _nearest_control(comp, {ev, comp, oi if oi is not None else -1})
        if nei is not None:
            variants["NEI_WI"] = " ".join(s for j, s in enumerate(ss) if j != nei)
    return {"variants": variants, "reasons": reasons, "evidence_idx": ev}


# ---------------------------------------------------------------- prompts and scoring

def build_prompt(match: str, innings: int, cond: str, text: str, fields: list) -> str:
    if len(fields) == 43:
        intro = ("You are a cricket scorer. Fill every field from the commentary. Return ONLY JSON: "
                 '{"fields": {<field_id>: <value>}}. Use integers for numeric fields and exact names for names. '
                 "No prose.")
    else:
        intro = ("You are a cricket scorer. Read the commentary and return the requested values at the END of "
                 "the specified innings. Return ONLY a JSON object mapping each field id to its value. "
                 "Integers for numeric fields, exact names for names, null if not confirmable. No prose.")
    lines = "\n".join("- " + f for f in fields)
    return (intro + "\n\nMatch: " + match + "\nInnings: " + str(innings) +
            "\nFields:\n" + lines + "\n\nCommentary:\n" + text + "\n\nJSON:")


def _unwrap(parsed):
    if isinstance(parsed, dict) and isinstance(parsed.get("fields"), dict):
        return parsed["fields"]
    return parsed if isinstance(parsed, dict) else {}


def score_cells(gold: dict, parsed, fields: list) -> dict:
    vals = _unwrap(parsed)
    cells = {}
    correct = 0
    for f in fields:
        if f not in gold:
            continue
        pred = vals.get(f)
        if isinstance(pred, dict):
            pred = pred.get("value")
        g = gold[f]
        ok = False
        if pred is not None:
            if isinstance(g, (int, float)) and not isinstance(g, bool):
                ok = int_value(pred) == int(g)
            else:
                ok = str(pred).strip().strip('"').lower() == str(g).strip().lower()
        cells[f] = {"gold": g, "pred": pred, "ok": bool(ok)}
        correct += int(ok)
    total = len(cells)
    return {"cells": cells, "correct": correct, "total": total, "task_correct": total > 0 and correct == total}


def readiness() -> dict:
    try:
        tags = ollama_tags(force=True)
    except Exception as e:
        return {"ok": False, "error": type(e).__name__ + ": " + str(e), "models": {}}
    present = {m: (m in tags) for m in MODELS}
    return {"ok": all(present.values()), "present": present,
            "digests": {m: (tags.get(m) or {}).get("digest", "") for m in MODELS}}


def load_manifest(batch_id: str) -> dict:
    return json.loads((BATCHES / (batch_id + ".json")).read_text(encoding="utf-8"))
