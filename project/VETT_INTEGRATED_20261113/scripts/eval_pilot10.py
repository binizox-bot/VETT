"""Pilot-10 evaluation: direct vs closure-propagation, 6 variants, local models."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT = ROOT / "VETT_INTEGRATED_20261113"
PILOT = INT / "pilot10"
RUNS = INT / "runs" / "eval_pilot10"
FIELDS_CACHE = {}
FIELD_SET = "core"


def is_core(fid: str) -> bool:
    if fid.startswith("match."):
        return fid in {"match.pom", "match.result", "match.toss", "match.venue"}
    tail = fid.split(".")[-1]
    if tail in {"total_runs", "total_wickets", "total_extras", "wides", "byes", "leg_byes",
                "no_balls", "batting_runs_sum", "bowling_runs_charged", "max_partnership"}:
        return True
    if "bat1_" in fid and tail == "runs":
        return True
    if "bowl1_" in fid and tail == "figures":
        return True
    return False

SYSTEM = (
    "You are a cricket scorecard reconstructor. Read the commentary and fill every requested field.\n"
    "Rules:\n"
    "- Use the field ids exactly as the JSON keys.\n"
    "- Integers must be JSON integers. Overs use \"X.Y\". Figures use \"W/R\".\n"
    "- If the text does not determine a field, use the string \"UNKNOWN\".\n"
    "- Do not invent players. Return ONLY one JSON object: {\"fields\": {...}}.\n"
)


def load_fields(mid: str) -> list[dict]:
    if mid not in FIELDS_CACHE:
        rows = [json.loads(l) for l in (PILOT/mid/"fields.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        if FIELD_SET == "core":
            rows = [r for r in rows if is_core(r["field_id"])]
        FIELDS_CACHE[mid] = rows
    return FIELDS_CACHE[mid]


RULES = (
    "Accounting rules you must satisfy: "
    "innings total = sum of batting runs + total extras; "
    "total extras = byes + leg byes + no balls + wides; "
    "bowling runs charged = innings total - byes - leg byes.\n"
    "Return ONLY the JSON object with a single key \"fields\". No prose, no markdown fences, no explanation.\n"
)


def build_prompt(mid: str, text: str, system: str = "direct") -> str:
    fields = load_fields(mid)
    lines = [f"- {f['field_id']} ({f['table']} {f['row']} {f['col']})" for f in fields]
    extra = RULES if system == "guided" else ""
    return SYSTEM + extra + "\nFields:\n" + "\n".join(lines) + "\n\nCommentary:\n" + text + "\n\nJSON:"


def extract_json(raw: str):
    if not raw:
        return None
    s = raw.strip()
    if s.startswith("```"):
        s = re.sub(r"^```\w*\n?", "", s)
        s = re.sub(r"\n?```$", "", s)
    start = s.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(s[start:i+1])
                except json.JSONDecodeError:
                    return None
    return None


def norm(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return str(v).lower()
    s = str(v).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def value_match(gold, pred) -> bool:
    g, p = norm(gold), norm(pred)
    if g == p:
        return True
    if re.fullmatch(r"-?\d+", g):
        if re.fullmatch(r"-?\d+", p):
            return int(g) == int(p)
        if re.fullmatch(r"-?\d+\.0+", p):
            return int(g) == int(float(p))
        return False
    if re.fullmatch(r"\d+\.\d+", g):
        m = re.match(r"\d+(?:\.\d+)?", p)
        return bool(m) and abs(float(g) - float(m.group(0))) < 1e-9
    m1 = re.fullmatch(r"(\d+)\s*/\s*(\d+)", g)
    if m1:
        m2 = re.search(r"(\d+)\s*[/-]\s*(\d+)", p)
        return bool(m2) and (int(m1.group(1)), int(m1.group(2))) == (int(m2.group(1)), int(m2.group(2)))
    return False


def propagate(pred: dict, fields: list[dict]) -> dict:
    """Closure propagation: recompute derived fields from components when possible."""
    out = dict(pred)
    def as_int(k):
        try:
            return int(str(out.get(k, "")).strip())
        except (TypeError, ValueError):
            return None
    for i in (1, 2):
        p = f"inn{i}"
        parts = [as_int(f"{p}.{x}") for x in ("byes", "leg_byes", "no_balls", "wides")]
        if all(x is not None for x in parts):
            out[f"{p}.total_extras"] = sum(parts)
        bat = as_int(f"{p}.batting_runs_sum")
        ext = as_int(f"{p}.total_extras")
        if bat is not None and ext is not None:
            out[f"{p}.total_runs"] = bat + ext
        tot, byes, lb = as_int(f"{p}.total_runs"), as_int(f"{p}.byes"), as_int(f"{p}.leg_byes")
        if tot is not None and byes is not None and lb is not None:
            out[f"{p}.bowling_runs_charged"] = tot - byes - lb
    return out


def oracle_text(mid: str) -> str:
    """Control commentary reduced to sentences that carry graded field evidence."""
    base = (PILOT/mid/"variants"/"control"/"commentary.txt").read_text(encoding="utf-8")
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", base.strip()) if s.strip()]
    idx = set()
    for f in load_fields(mid):
        idx.update(f.get("evidence_sentences", []))
    if not idx:
        return base
    return " ".join(sents[i] for i in sorted(idx) if i < len(sents))


def expected_gold(mid: str, variant: str) -> dict:
    doc = json.loads((PILOT/mid/"variants"/variant/"gold.json").read_text(encoding="utf-8"))
    exp = dict(doc["gold"])
    for k in doc.get("unknown_fields", []):
        exp[k] = "UNKNOWN"
    return exp


def score(pred_fields: dict, exp: dict, fields: list[dict]) -> dict:
    per_field, correct, total = {}, 0, 0
    for f in fields:
        fid = f["field_id"]
        g = exp.get(fid)
        p = pred_fields.get(fid)
        good = value_match(g, p)
        per_field[fid] = {"gold": g, "pred": p, "correct": good, "level": f["level"]}
        total += 1
        correct += 1 if good else 0
    return {"n": total, "correct": correct, "acc": round(correct/total, 6) if total else 0, "per_field": per_field}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--systems", nargs="*", default=["direct", "closure", "guided"])
    ap.add_argument("--variants", nargs="*", default=None)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--field-set", choices=["core", "full"], default="core")
    args = ap.parse_args()
    global FIELD_SET
    FIELD_SET = args.field_set

    sel = json.loads((PILOT/"selection.json").read_text(encoding="utf-8"))
    matches = [m["match"] for m in sel["matches"]]
    if args.limit:
        matches = matches[: args.limit]
    variants = args.variants or ["control", "shuffled", "revised", "conflict", "missing", "distractor"]

    if args.dry:
        for mid in matches[:2]:
            for v in variants[:2]:
                text = (PILOT/mid/"variants"/v/"commentary.txt").read_text(encoding="utf-8")
                p = build_prompt(mid, text)
                print(mid, v, "prompt_chars=", len(p), "est_tokens=", len(p)//4)
        return 0

    sys.path.insert(0, str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local"))
    from local_inference import service  # noqa: E402

    models = args.models or ["qwen2.5:7b-instruct-q4_K_M", "llama3.1:8b", "gemma2:9b"]
    RUNS.mkdir(parents=True, exist_ok=True)
    for tag in models:
        service.config.MODEL_TAG = tag
        info = service.model_info(tag) or {}
        print(f"=== {tag} digest={info.get('digest')} quant={info.get('quantization_level')}", flush=True)
        out = RUNS / f"{tag.replace(':','_').replace('/','_')}.jsonl"
        done = set()
        if out.exists():
            for line in out.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line); done.add((r["match"], r["variant"], r["system"]))
        with open(out, "a", encoding="utf-8", newline="\n") as f:
            for mid in matches:
                fields = load_fields(mid)
                for v in variants:
                    if v == "oracle":
                        text = oracle_text(mid)
                        exp = expected_gold(mid, "control")
                    else:
                        text = (PILOT/mid/"variants"/v/"commentary.txt").read_text(encoding="utf-8")
                        exp = expected_gold(mid, v)
                    for system in args.systems:
                        if (mid, v, system) in done:
                            continue
                        prompt = build_prompt(mid, text, system)
                        try:
                            npred = 900 if system == "guided" else 700
                            gen = service.generate(prompt, num_ctx=8192, num_predict=npred)
                            raw = gen["raw_output"]
                        except Exception as exc:  # noqa: BLE001
                            raw = ""; gen = {"eval_count": 0}
                        doc = extract_json(raw) or {}
                        pred = doc.get("fields") if isinstance(doc.get("fields"), dict) else {}
                        pred = {str(k): v for k, v in pred.items()}
                        if system == "closure":
                            pred = propagate(pred, fields)
                        sc = score(pred, exp, fields)
                        row = {"match": mid, "variant": v, "system": system, "model": tag,
                               "model_digest": info.get("digest"), "pred": pred,
                               "score": {"n": sc["n"], "correct": sc["correct"], "acc": sc["acc"]},
                               "eval_count": gen.get("eval_count"), "raw_sha256": None}
                        f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"); f.flush()
                        print(f"  {mid} {v} {system} acc={sc['acc']:.3f} ({sc['correct']}/{sc['n']})", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
