import sys,json,re
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
CORE={s["match"] for s in json.loads((WF.parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))}
c=V.connect(); USED={r[0] for r in c.execute("SELECT DISTINCT match FROM tasks t JOIN batches b USING(batch_id) WHERE b.template='X_night_ft_ordinary'")}; c.close()
DATASET=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches")
allm=sorted([p.name for p in DATASET.glob("match_*") if (p/"commentary.txt").exists()])
def top2(inn):
    arr=sorted(inn.bowlers,key=lambda b:(-b.wickets,b.runs_conceded,b.name))
    return arr[:2]
def bowler_of(d):
    m=re.search(r"\bb\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)",d or "")
    return m.group(1) if m else None
cands=[]
for m in allm:
    if m in CORE: continue
    if 121<=int(m.split("_")[1])<=160: continue
    try: b=V.load_bundle(m)
    except Exception: continue
    txt=b["text"]
    for ii,inn in enumerate(b["md"].innings,1):
        t2=top2(inn)
        if len(t2)<2: continue
        for bat in inn.batters:
            if bat.is_not_out: continue
            a=bowler_of(bat.dismissal)
            if not a or a not in [x.name for x in t2]: continue
            A=next(x for x in t2 if x.name==a); B=next(x for x in t2 if x.name!=a)
            if A.wickets<1: continue
            first=bat.name.split()[0]
            if first not in txt or A.name not in txt or B.name not in txt: continue
            # evidence: explicit figure near A/B
            def fig(name,w):
                pats=[name+r"[^.]{0,80}\bfor\s+"+str(w)+r"\b", name+r"[^.]{0,80}\b"+str(w)+r"\s*wickets", r"\b"+str(w)+r"\s*for\b[^.]{0,40}"+name]
                return any(re.search(p,txt,re.I) for p in pats)
            score=int(fig(A.name,A.wickets))+int(fig(B.name,B.wickets))
            cands.append({"match":m,"innings":ii,"batter":bat.name,"A":A.name,"B":B.name,"Aw":A.wickets,"Ar":A.runs_conceded,"Bw":B.wickets,"Br":B.runs_conceded,"total":inn.total_wickets,"score":score,"len":len(txt)})
            break
# one per match, best score then id
best={}
for x in cands:
    k=x["match"]
    if k not in best or (x["score"],-x["len"])>(best[k]["score"],-best[k]["len"]): best[k]=x
sel=sorted(best.values(),key=lambda x:(-x["score"],x["len"]*-1,x["match"]))
print(json.dumps({"pool":len(allm),"used":len(USED),"candidates":len(sel),"top":sel[:10]},ensure_ascii=False,indent=1))
