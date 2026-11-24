import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_220_r28_link_pilot"
M=json.loads((P/"manifest.json").read_text(encoding="utf-8"))["matches"]; MS={x["match"]:x for x in M}
R=[json.loads(l) for l in (P/"runs"/"paired.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
def doc(r):
    d=r.get("parsed") or {}
    return d if isinstance(d,dict) else {}
per={}
for s in M:
    A,B=s["A"],s["B"]
    for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
        for cond in ["none","retain","reassign"]:
            g=s["gold"][cond]; key=(s["match"],model,cond)
            ar=next(x for x in R if x["match"]==s["match"] and x["cond"]==cond and x["method"]=="A" and x["model"]==model); ad=doc(ar)
            astrict=eq(ad.get(f"{A}_wickets"),g[f"{A}_wickets"]) and eq(ad.get(f"{B}_wickets"),g[f"{B}_wickets"]) and eq(ad.get("innings_total_wickets"),g["innings_total_wickets"])
            anum=astrict
            br=next(x for x in R if x["match"]==s["match"] and x["cond"]==cond and x["method"]=="B" and x["model"]==model); bd=doc(br)
            rec={"A":ad,"B":bd,"A_ok":astrict,"A_strict":astrict}
            try:
                ow=int(bd[f"{A}_wickets_before"]); oth=int(bd[f"{B}_wickets_before"]); tot=int(bd["innings_total_wickets"]); orig=bd.get("original_bowler"); fin=bd.get("final_bowler")
                if orig==fin:
                    res=(ow,oth)
                else:
                    res=(ow-1,oth+1)
                rec.update({"B_exec":True,"B_ok":res==(g[f"{A}_wickets"],g[f"{B}_wickets"]) and tot==g["innings_total_wickets"],"B_res":res,"B_total":tot})
            except Exception: rec.update({"B_exec":False,"B_ok":False})
            per[key]=rec
agg={}
for method in ["A","B"]:
    for cond in ["none","retain","reassign"]: agg[f"{method}_{cond}"]={"n":0,"ok":0}
for k,v in per.items():
    m,model,cond=k
    for method in ["A","B"]:
        f=method+"_ok"; agg[f"{method}_{cond}"]["n"]+=1; agg[f"{method}_{cond}"]["ok"]+=v[f]
for method in ["A","B"]:
    for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
        rows=[v for k,v in per.items() if k[1]==model and k[2] in ("retain","reassign")]
        agg[f"{method}_joint_{model}"]=sum(1 for v in rows if v[method+"_ok"])
        rows3=[v for k,v in per.items() if k[1]==model]
        agg[f"{method}_all3_{model}"]=sum(1 for v in rows3 if v["none"][method+"_ok"] if False) if False else 0
json.dump({"agg":agg,"per":{f"{k[0]}|{k[1]}|{k[2]}":v for k,v in per.items()}},open(P/"scores.json","w"),ensure_ascii=False,indent=1)
print(json.dumps(agg,ensure_ascii=False,indent=1))
