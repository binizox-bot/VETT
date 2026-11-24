import sys,json,re,hashlib
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"vett_local_evidence_long_run"; O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
# replay linkage
P=INT/"analysis"/"vett_220_r28_link_pilot"
sc=json.loads((P/"scores.json").read_text(encoding="utf-8"))
per=sc["per"]; agg={}
for method in ["A","B"]:
    for cond in ["none","retain","reassign"]:
        agg[f"{method}_{cond}"]=sum(1 for v in per.values() if v[method+"_ok"] and k.endswith("|"+cond)) if False else 0
# compute direct counts and joint/transitions
for method in ["A","B"]:
    for cond in ["none","retain","reassign"]:
        agg[f"{method}_{cond}"]=sum(1 for k,v in per.items() if k.endswith("|"+cond) and v[method+"_ok"])
    agg[f"{method}_joint"]=sum(1 for k,v in per.items() if k.endswith("|retain") and v[method+"_ok"] and per[k.replace("|retain","|reassign")][method+"_ok"])
    agg[f"{method}_all3"]=sum(1 for k,v in per.items() if k.endswith("|retain") and v[method+"_ok"] and per[k.replace("|retain","|reassign")][method+"_ok"] and per[k.replace("|retain","|none")][method+"_ok"])
print("linkage",agg)
# scan published totals
cands=[]
for i in range(1,221):
    m=f"match_{i:04d}"
    try:
        text=(L.DATASET/m/"commentary.txt").read_text(encoding="utf-8"); md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m)
    except Exception: continue
    ss=L.sentences(text)
    for inn in md.innings:
        hits=[]
        for s in ss:
            if inn.name.lower() in s.lower() and re.search(r"(closed on|finished on|all out|bowled out|ended on)",s,re.I) and re.search(r"\d{2,3}\s*(?:for|/)\s*\w+",s):
                hits.append(s)
        if not hits: continue
        for s in hits[:1]:
            mm=re.search(r"(\d{2,3})\s+(?:for|/)\s+(\w+)",s); words={"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10}
            if not mm: continue
            r=int(mm.group(1)); w=words.get(mm.group(2).lower(), int(mm.group(2)) if mm.group(2).isdigit() else -1)
            if r==inn.total_runs and w==inn.total_wickets:
                cands.append({"match":m,"innings":1 if inn is md.innings[0] else 2,"team":inn.name,"runs":r,"wickets":w,"sentence":s})
                break
        if any(x["match"]==m for x in cands): break
print("candidates",len(cands))
for x in cands[:20]: print(x["match"],x["innings"],x["team"],x["runs"],x["wickets"],"|",x["sentence"][:120])
(O/"published_totals_candidates.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in cands)+"\n",encoding="utf-8")
