"""220-match dataset audit: sizes, evidence levels, scorecard structure."""
import json, re, statistics
from pathlib import Path
from collections import Counter

ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
DS = ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches"
OUT = ROOT / "VETT_INTEGRATED_20261113" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

def toks(b):
    return int(round(b / 4.0))

per = []
missing = []
for d in sorted(DS.glob("match_*")):
    need = ["commentary.txt","scorecard.md","evidence_chain.md","meta.json"]
    miss = [f for f in need if not (d/f).exists()]
    if miss:
        missing.append({"match": d.name, "missing": miss})
        continue
    cb = (d/"commentary.txt").stat().st_size
    sb = (d/"scorecard.md").stat().st_size
    eb = (d/"evidence_chain.md").stat().st_size
    sc = (d/"scorecard.md").read_text(encoding="utf-8", errors="replace")
    ev = (d/"evidence_chain.md").read_text(encoding="utf-8", errors="replace")
    cm = (d/"commentary.txt").read_text(encoding="utf-8", errors="replace")
    levels = Counter(re.findall(r"^\|\s*(L[123])\s*\|", ev, re.M))
    innings = len(re.findall(r"^##\s+", sc, re.M))
    tables = len(re.findall(r"^###\s+", sc, re.M))
    data_rows = sum(1 for ln in sc.splitlines() if ln.startswith("| ") and not set(ln) <= set("|- "))
    result = ""
    m = re.search(r"^\| Result \| (.+?) \|$", sc, re.M)
    if m: result = m.group(1).strip()
    words = len(cm.split())
    sents = len([s for s in re.split(r"(?<=[.!?])\s+", cm) if s.strip()])
    per.append({"match": d.name, "commentary_bytes": cb, "commentary_tokens": toks(cb),
                "commentary_words": words, "sentences": sents,
                "scorecard_bytes": sb, "scorecard_tokens": toks(sb),
                "evidence_bytes": eb, "evidence_tokens": toks(eb),
                "L1": levels.get("L1",0), "L2": levels.get("L2",0), "L3": levels.get("L3",0),
                "innings_sections": innings, "tables": tables, "table_data_rows": data_rows,
                "result": result})

def stats(vals):
    vals = sorted(vals)
    n = len(vals)
    def pct(p):
        return vals[min(n-1, max(0, int(round(p*(n-1)))))] if n else 0
    return {"n": n, "min": vals[0] if n else 0, "p10": pct(.1), "median": pct(.5),
            "p90": pct(.9), "max": vals[-1] if n else 0,
            "mean": round(sum(vals)/n,1) if n else 0}

kit = {k: stats([p[k] for p in per]) for k in
       ["commentary_tokens","scorecard_tokens","evidence_tokens","sentences","table_data_rows","L1","L2","L3"]}
leak = {
  "commentary_gt_8192_tokens": sum(1 for p in per if p["commentary_tokens"] > 8192),
  "scorecard_gt_2048_tokens": sum(1 for p in per if p["scorecard_tokens"] > 2048),
  "scorecard_gt_640_tokens": sum(1 for p in per if p["scorecard_tokens"] > 640),
  "evidence_gt_commentary": sum(1 for p in per if p["evidence_bytes"] > p["commentary_bytes"]),
}
res = {"n_matches": len(per), "missing": missing, "stats": kit, "flags": leak,
       "result_types": Counter(p["result"] for p in per).most_common(12),
       "per_match": per}
(OUT / "dataset_audit.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
print("matches:", len(per), "missing:", len(missing))
for k,v in kit.items():
    print(f"  {k:20s} min={v['min']:5d} p10={v['p10']:5d} med={v['median']:5d} p90={v['p90']:5d} max={v['max']:5d} mean={v['mean']}")
print("flags:", leak)
print("result types:", res["result_types"])
print("wrote", OUT / "dataset_audit.json")
