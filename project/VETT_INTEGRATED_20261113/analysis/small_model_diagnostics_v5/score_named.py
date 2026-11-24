import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); V3=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v3"; V5=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v5"
S={s["match"]:s for s in json.loads((V3/"SAMPLE_MANIFEST.json").read_text(encoding="utf-8"))}
R=[json.loads(l) for l in (V5/"runs"/"named_old.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
agg={}; per={}
for s in S.values():
    A,B=s["A"],s["B"]; old=s["old"]
    for notice in ["reassign","retain"]:
        for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
            r=next(x for x in R if x["match"]==s["match"] and x["notice"]==notice and x["model"]==model); d=r.get("parsed") or {}
            k=(notice,model); agg.setdefault(k,{"n":0,"exec":0,"ok":0,"oldboth":0,"mis":0,"unknown":0,"contra":0})
            try: ow=int(d["original_bowler_wickets_before"]); oth=int(d["other_bowler_wickets_before"])
            except Exception:
                ow=None; agg[k]["unknown"]+=1
            orig=d.get("original_bowler"); fin=d.get("final_bowler")
            rec={"doc":d,"exec":False}
            if ow is not None and orig in (A,B) and fin in (A,B):
                # map old values to A/B
                oldA,oldB=(ow,oth) if orig==A else (oth,ow)
                if orig==fin:
                    prog=(oldA,oldB); kind="retain"
                else:
                    # transfer from orig to fin: one off orig, one on fin
                    a=oldA; b=oldB
                    if orig==A: a-=1; b+=1
                    else: b-=1; a+=1
                    prog=(a,b); kind="reassign"
                gold=s["reassign_gold"] if notice=="reassign" else s["retain_gold"]
                ok=prog==(gold[f"{A}_wickets"],gold[f"{B}_wickets"])
                rec.update({"exec":True,"prog":prog,"kind":kind,"ok":ok,"oldA":oldA,"oldB":oldB})
                agg[k]["exec"]+=1; agg[k]["ok"]+=ok
                agg[k]["oldboth"]+=(oldA==old["Aw"] and oldB==old["Bw"])
                agg[k]["mis"]+=(notice=="retain" and prog!=(old["Aw"],old["Bw"]))
                agg[k]["contra"]+=(d.get("decision")=="reassign" and orig==fin)
            agg[k]["n"]+=1
            per.setdefault((s["match"],model),{})[notice]=rec
json.dump({"agg":{f"{k[0]}|{k[1]}":v for k,v in agg.items()},"per":{f"{k[0]}|{k[1]}":v for k,v in per.items()}},open(V5/"named_old_scores.json","w"),ensure_ascii=False,indent=1)
for k,v in agg.items(): print(k,v)
for k,v in per.items(): print(k,{n:(x.get("ok"),x.get("exec"),x.get("prog"),x.get("oldA"),x.get("oldB")) for n,x in v.items()})
