import sys,json,hashlib,time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; P=INT/"analysis"/"vett_overnight_20261114"; O=INT/"analysis"/"vett_evidence_upgrade_20261115"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local")); from local_inference import service
S1=json.loads((O/"U_SAMPLE_MANIFEST.json").read_text(encoding="utf-8")); used={(x["match"],x["innings"]) for x in S1}
R=[json.loads(l) for l in (P/"runs"/"u_full.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
cache={}
def gold(m,inn):
    if m not in cache:
        md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); cache[m]=md
    return cache[m].innings[inn-1]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
gmap={}
for r in R:
    inn=gold(r["match"],r["innings"]); d=r.get("parsed") or {}
    def v(k):
        x=d.get(k) or {}; return x.get("value") if isinstance(x,dict) else None
    okr=eq(v("total_runs"),inn.total_runs); okw=eq(v("total_wickets"),inn.total_wickets)
    g="both" if okr and okw else "runs_only" if okr else "wk_only" if okw else "neither"
    gmap.setdefault((r["match"],r["innings"]),[]).append(g)
sel=[]; seen=set()
for g in ["both","runs_only","wk_only","neither"]:
    n=0
    for (m,inn),gs in sorted(gmap.items()):
        if (m,inn) in used or m in seen: continue
        if g in gs:
            seen.add(m); sel.append((g,m,inn)); n+=1
        if n>=6: break
manifest=[]
for g,m,inn in sel:
    innobj=gold(m,inn); text=(L.DATASET/m/"commentary.txt").read_text(encoding="utf-8")
    manifest.append({"group":g,"match":m,"innings":inn,"team":innobj.name,"runs":innobj.total_runs,"wickets":innobj.total_wickets,"text":text,"sha":hashlib.sha256(text.encode()).hexdigest()})
(O/"U_SAMPLE2_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=1)+"\n",encoding="utf-8")
out=O/"RUNS"/"u_sample2.jsonl"; rows=[json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()] if out.exists() else []
done={(r["match"],r["innings"],r["model"]) for r in rows}; MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
def ex(raw):
    if not raw: return None
    s=raw.strip(); i=s.find("{")
    if i<0: return None
    d=0
    for j in range(i,len(s)):
        if s[j]=="{": d+=1
        elif s[j]=="}":
            d-=1
            if d==0:
                try: return json.loads(s[i:j+1])
                except Exception: return None
    return None
for x in manifest:
    for model in MODELS:
        if (x["match"],x["innings"],model) in done: continue
        pr=("You are a cricket scorer. Read the commentary and find the batting team's total runs and wickets lost at the END of the specified innings. Return ONLY JSON with keys total_runs and total_wickets, each an object with status, value, quotes, reason. UNKNOWN if not confirmable.\n\nMatch: "+x["match"]+"\nInnings: "+("first" if x["innings"]==1 else "second")+"\nBatting team: "+x["team"]+"\n\nText:\n"+x["text"]+"\n\nJSON:")
        service.config.MODEL_TAG=model; info=service.model_info(model) or {}
        try: gen=service.generate(pr,num_ctx=8192,num_predict=500); raw=gen["raw_output"]
        except Exception: raw=""; gen={}
        row={"phase":"U_sample2","group":x["group"],"match":x["match"],"innings":x["innings"],"team":x["team"],"model":model,"digest":info.get("digest"),"text_sha256":x["sha"],"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":ex(raw),"parse_ok":False,"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
        row["parse_ok"]=isinstance(row["parsed"],dict)
        open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n"); rows.append(row)
        (O/"PROGRESS.md").write_text(f"# U sample2\n\n- rows {len(rows)} / {len(manifest)*3}\n- {time.strftime('%H:%M:%S')}\n",encoding="utf-8")
        print(x["match"],x["innings"],model.split(":")[0],flush=True)
print("done",len(manifest),len(rows))
