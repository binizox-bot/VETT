import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); V3=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v3"; V4=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v4"
S={s["match"]:s for s in json.loads((V3/"SAMPLE_MANIFEST.json").read_text(encoding="utf-8"))}
R=[json.loads(l) for l in (V3/"runs"/"paired.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
def doc(r):
    d=r.get("parsed") or {}
    if isinstance(d,dict) and isinstance(d.get("fields"),dict): d=d["fields"]
    return d if isinstance(d,dict) else {}
out=[]; agg={k:{"n":0,"strict":0,"num":0,"exec":0,"ok":0,"mis":0} for k in ["direct_reassign","direct_retain","extract_reassign","extract_retain"]}
replay={k:{"n":0,"exec":0,"ok":0,"mis":0} for k in ["reassign","retain"]}
for s in S.values():
    A,B=s["A"],s["B"]; old=s["old"]
    for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
        for kind in ["direct_reassign","direct_retain","extract_reassign","extract_retain"]:
            r=next((x for x in R if x["match"]==s["match"] and x["kind"]==kind and x["model"]==model),None); d=doc(r or {})
            rec={"match":s["match"],"model":model,"kind":kind,"raw":(r or {}).get("raw_output","")}
            if kind.startswith("direct"):
                gold=s["reassign_gold"] if "reassign" in kind else s["retain_gold"]
                exact=eq(d.get(f"{A}_wickets"),gold[f"{A}_wickets"]) and eq(d.get(f"{B}_wickets"),gold[f"{B}_wickets"])
                norm={str(k).replace("_"," "):v for k,v in d.items()}
                num=eq(norm.get(f"{A} wickets"),gold[f"{A}_wickets"]) and eq(norm.get(f"{B} wickets"),gold[f"{B}_wickets"])
                rec.update({"strict":exact,"num":num,"pred":d}); agg[kind]["n"]+=1; agg[kind]["strict"]+=exact; agg[kind]["num"]+=num
            else:
                rec["doc"]=d
                try: ow=int(d["original_bowler_wickets_before"]); oth=int(d["other_bowler_wickets_before"])
                except Exception: ow=oth=None
                legal_old=False; prog=None
                if ow is not None:
                    if kind=="extract_reassign":
                        legal_old=d.get("decision")=="reassign" and d.get("original_bowler")==A and d.get("final_bowler")==B
                        prog=(ow-1,oth+1) if legal_old else None
                    else:
                        legal_old=d.get("decision")=="retain" and d.get("original_bowler")==A and d.get("final_bowler")==A
                        prog=(ow,oth) if legal_old else None
                gold=s["reassign_gold"] if kind=="extract_reassign" else s["retain_gold"]
                ok=prog==(gold[f"{A}_wickets"],gold[f"{B}_wickets"]) if prog else False
                rec.update({"exec":prog is not None,"prog":prog,"ok":ok,"mis":(kind=="extract_retain" and prog is not None and prog!=(old["Aw"],old["Bw"]))})
                agg[kind]["n"]+=1; agg[kind]["exec"]+=prog is not None; agg[kind]["ok"]+=ok; agg[kind]["mis"]+=rec["mis"]
                # attribution replay (ignore decision)
                if ow is not None and d.get("original_bowler") in (A,B) and d.get("final_bowler") in (A,B):
                    if d["original_bowler"]==d["final_bowler"]:
                        rp=(ow,oth); rk="retain"
                    else:
                        rp=(ow-1,oth+1); rk="reassign"
                    gold=s["reassign_gold"] if rk=="reassign" else s["retain_gold"]
                    rok=rp==(gold[f"{A}_wickets"],gold[f"{B}_wickets"])
                    replay[rk]["n"]+=1; replay[rk]["exec"]+=1; replay[rk]["ok"]+=rok
                    replay[rk]["mis"]+=(rk=="retain" and rp!=(old["Aw"],old["Bw"]))
                    rec["replay"]={"kind":rk,"prog":rp,"ok":rok}
            out.append(rec)
json.dump(out,open(V4/"v3_rescore.jsonl","w"),ensure_ascii=False,indent=1)
print("agg",agg)
print("replay",replay)
for r in out:
    if r["kind"].startswith("direct") and not r["num"]: print("NUMFAIL",r["match"],r["model"].split(":")[0],r["kind"],r["pred"])
