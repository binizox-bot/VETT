import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_evidence_followup"
dev=json.loads((ROOT/"dev.json").read_text(encoding="utf-8")); hold=json.loads((ROOT/"holdout.json").read_text(encoding="utf-8"))
lina=json.loads((ROOT/"lina.json").read_text(encoding="utf-8"))["cases"]
def rows(n):
    p=ROOT/"runs"/n
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
def score_item(r,s):
    f=(r or {}).get("fields") or {}; g=s["fields"]; A=s.get("A_name") or "Nora_Vale"; B=s.get("B_name") or "Ruby_North"
    akey=f"{A}_wickets_credited" if f"{A}_wickets_credited" in g else f"{A}_wickets"
    bkey=f"{B}_wickets_credited" if f"{B}_wickets_credited" in g else f"{B}_wickets"
    arkey=f"{A}_bowling_runs_conceded" if f"{A}_bowling_runs_conceded" in g else f"{A}_runs"
    brkey=f"{B}_bowling_runs_conceded" if f"{B}_bowling_runs_conceded" in g else f"{B}_runs"
    tkey="innings_wickets_lost" if "innings_wickets_lost" in g else "innings_total_wickets"
    two=eq(f.get(akey),g[akey]) and eq(f.get(bkey),g[bkey]); tt=eq(f.get(tkey),g[tkey])
    return {"two":two,"total":tt,"three":two and tt,"runs":eq(f.get(arkey),g[arkey]) and eq(f.get(brkey),g[brkey]),
            "five":two and tt and eq(f.get(arkey),g[arkey]) and eq(f.get(brkey),g[brkey]),"pred":f,"ok":{k:eq(f.get(k),g[k]) for k in g}}
def cat(r,s):
    f=(r or {}).get("fields") or {}; A=s["A_name"]; B=s["B_name"]
    aw=f.get(f"{A}_wickets_credited"); bw=f.get(f"{B}_wickets_credited")
    if aw is None or bw is None: return "format"
    if eq(aw,s["old"]["Aw"]) and eq(bw,s["old"]["Bw"]): return "both_old"
    if eq(aw,s["old"]["Aw"]) and eq(bw,s["old"]["Bw"]+1): return "only_new_plus1"
    if eq(aw,s["old"]["Aw"]-1) and eq(bw,s["old"]["Bw"]): return "only_orig_minus1"
    if eq(aw,s["old"]["Aw"]+1) and eq(bw,s["old"]["Bw"]-1): return "direction_reversed"
    return "both_updated_wrong"
out={"dev":{},"hold":{},"lina":{},"retest":{}}
devr={(r["match"],r["condition"],r["model"]):r for r in rows("dev.jsonl")}
holdr={(r["match"],r["condition"],r["model"]):r for r in rows("hold.jsonl")}
for model in sorted({r["model"] for r in rows("dev.jsonl")}):
    e={"per":{},"agg":{},"cats":{}}
    for v in "ABC": e["agg"][v]={k:0 for k in ["two","total","three","runs","five"]}; e["cats"][v]={}
    for s in dev:
        e["per"][s["match"]]={}
        for v in "ABC":
            r=devr.get((s["match"],v,model)); sc=score_item(r,s)
            e["per"][s["match"]][v]=sc
            for k in e["agg"][v]: e["agg"][v][k]+=1 if sc[k] else 0
            c=cat(r,s); e["cats"][v][c]=e["cats"][v].get(c,0)+1
    out["dev"][model]=e
for model in sorted({r["model"] for r in rows("hold.jsonl")}):
    e={"per":{},"agg":{},"cats":{}}
    for v in "AB": e["agg"][v]={k:0 for k in ["two","total","three","runs","five"]}; e["cats"][v]={}
    for s in hold:
        e["per"][s["match"]]={}
        for v in "AB":
            r=holdr.get((s["match"],v,model)); sc=score_item(r,s)
            e["per"][s["match"]][v]=sc
            for k in e["agg"][v]: e["agg"][v][k]+=1 if sc[k] else 0
            c=cat(r,s); e["cats"][v][c]=e["cats"][v].get(c,0)+1
    out["hold"][model]=e
for r in rows("lina.jsonl"):
    c=r["match"]; s={"fields":lina[c]["gold"],"A_name":"Nora_Vale","B_name":"Ruby_North"}; sc=score_item(r,s)
    out["lina"].setdefault(c,{})[r["model"]]={"fields":sc["pred"],"five":sc["five"],"three":sc["three"]}
for r in rows("retest.jsonl"):
    base=devr.get((r["match"],"A",r["model"]))
    same=sum(1 for k in (r.get("fields") or {}) if eq((r["fields"] or {}).get(k),(base or {}).get("fields",{}).get(k))) if base else 0
    out["retest"].setdefault(r["model"],[]).append({"match":r["match"],"same":same,"n":5})
(ROOT/"scores.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for model,e in out["dev"].items():
    print("\nDEV",model,e["agg"]); print(" cats",e["cats"])
for model,e in out["hold"].items():
    print("\nHOLD",model,e["agg"]); print(" cats",e["cats"])
print("\nLINA",json.dumps(out["lina"],ensure_ascii=False)[:1200])
print("RETEST",out["retest"])
