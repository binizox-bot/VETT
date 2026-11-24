"""Read-only helpers for Pilot-10 case audit."""
import json, re, sys
from pathlib import Path

ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT = ROOT / "VETT_INTEGRATED_20261113"
PILOT = INT / "pilot10"
RUNS = INT / "runs" / "eval_pilot10"
OUT = INT / "analysis" / "pilot10_case_audit"

sys.path.insert(0, str(INT / "scripts"))
import eval_pilot10 as E


def load_rows():
    by = {}
    for p in sorted(RUNS.glob("*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            by[(r["match"], r["variant"], r["system"], r["model"])] = r
    return by


def fields(mid):
    return [json.loads(l) for l in (PILOT/mid/"fields.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def core_fields(mid):
    return [f for f in fields(mid) if E.is_core(f["field_id"])]


def gold_doc(mid, variant):
    return json.loads((PILOT/mid/"variants"/variant/"gold.json").read_text(encoding="utf-8"))


def gold_map(mid, variant):
    d = gold_doc(mid, variant)
    g = dict(d["gold"])
    for k in d.get("unknown_fields", []):
        g[k] = "UNKNOWN"
    return g


def correct(gold, pred):
    return E.value_match(gold, pred)


def text(mid, variant):
    return (PILOT/mid/"variants"/variant/"commentary.txt").read_text(encoding="utf-8")


def sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s.strip()]
