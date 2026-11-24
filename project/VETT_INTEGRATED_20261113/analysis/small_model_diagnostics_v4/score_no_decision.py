import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); V3=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v3"; V4=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v4"
S={s["match"]:s for s in json.loads((V3/"SAMPLE_MANIFEST.json").read_text(encoding="utf-8"))}
R=[json.loads(l) for l in (V4/"runs"/"no_decision.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
agg={}; per={}
for s in S.values():
    A,B=s["A"],s["B"]; old=s["old"]
    for notice in ["reassign","retain"]:
        for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
            r=next(x for x in R if x["match"]==s["match"] and x["notice"]==notice and x["model"]==model); d=r.get("parsed") or {}
            k=(notice,model); agg.setdefault(k,{"n":0,"exec":0,"ok":0,"mis":0})
            per.setdefault((s["match"],model),{})[notice]={"doc":d}
            try:
                ow=int(d["original_bowler_wickets_before"]); oth=int(d["other_bowler_wickets_before"])
                orig=d.get("original_bowler"); fin=d.get("final_bowler")
            except Exception: ow=None
            if ow is None or orig not in (A,B) or fin not in (A,B) or orig==fin and orig!=A:
                per[(s["match"],model)][notice]["exec"]=False; continue
            if orig==fin:
                prog=(ow,oth); kind="retain"
            else:
                prog=(ow-1,oth+1); kind="reassign"
            gold=s["reassign_gold"] if notice=="reassign" else s["retain_gold"]
            ok=prog==(gold[f"{A}_wickets"],gold[f"{B}_wickets"])
            mis=(notice=="retain" and prog!=(old["Aw"],old["Bw"]))
            per[(s["match"],model)][notice].update({"exec":True,"prog":prog,"kind":kind,"ok":ok})
            agg[k]["n"]+=1; agg[k]["exec"]+=1; agg[k]["ok"]+=ok; agg[k]["mis"]+=mis
json.dump({"agg":{f"{k[0]}|{k[1]}":v for k,v in agg.items()},"per":{f"{k[0]}|{k[1]}":v for k,v in per.items()}},open(V4/"no_decision_scores.json","w"),ensure_ascii=False,indent=1)
for k,v in agg.items(): print(k,v)
for k,v in per.items(): print(k,{n:(x.get("ok"),x.get("exec"),x.get("kind"),x.get("prog")) for n,x in v.items()})
