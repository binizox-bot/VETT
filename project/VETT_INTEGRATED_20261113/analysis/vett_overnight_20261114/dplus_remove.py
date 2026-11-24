import sys,json,re,hashlib,time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; P=INT/"analysis"/"vett_overnight_20261114"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local")); from local_inference import service
roots=[]
for f in ["expansion_manifest.json"]:
    roots += json.loads((P/f).read_text(encoding="utf-8"))
_d=json.loads((P/"manifest.json").read_text(encoding="utf-8")).get("D")
if isinstance(_d,dict): roots.append(_d)
roots += json.loads((INT/"analysis"/"vett_evidence_position_transfer"/"manifest.json").read_text(encoding="utf-8"))
seen=set(); tasks=[]
for x in roots:
    m=x["match"]
    if m in seen: continue
    seen.add(m)
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); ss=L.sentences(x.get("O") or x.get("text") or "")
    final=x.get("evidence") or ""
    comp=next((s for s in ss if s!=final and re.search(r"\d{2,3}\s+(?:for|/)\s+\w+",s) and not re.search(rf"\b{x.get('runs',-1)}\b",s)),"")
    if not comp: continue
    M=" ".join(s for s in ss if s!=comp)
    tasks.append({"match":m,"innings":x.get("innings",1),"team":x.get("team"),"runs":x.get("runs"),"wickets":x.get("wickets"),"text":M,"removed":comp})
(P/"dplus_remove_manifest.json").write_text(json.dumps(tasks,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
out=P/"runs"/"dplus_remove.jsonl"; rows=[json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()] if out.exists() else []
done={(r["match"],r["model"]) for r in rows}; MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
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
for x in tasks:
    for model in MODELS:
        if (x["match"],model) in done: continue
        pr=("You are a cricket scorer. Read the commentary and return the batting team's total runs and wickets lost at the END of the specified innings. Return ONLY JSON with keys total_runs and total_wickets (integers). No prose.\n\nMatch: "+x["match"]+"\nInnings: first\nBatting team: "+str(x["team"])+"\n\nText:\n"+x["text"]+"\n\nJSON:")
        service.config.MODEL_TAG=model; info=service.model_info(model) or {}
        try: gen=service.generate(pr,num_ctx=8192,num_predict=300); raw=gen["raw_output"]
        except Exception: raw=""; gen={}
        row={"phase":"Dplus_remove","match":x["match"],"model":model,"digest":info.get("digest"),"text_sha256":hashlib.sha256(x["text"].encode()).hexdigest(),"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":ex(raw),"parse_ok":False,"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
        row["parse_ok"]=isinstance(row["parsed"],dict)
        open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n"); rows.append(row)
        (P/"DPLUS_PROGRESS.md").write_text(f"# D+ remove\n\n- rows {len(rows)} / {len(tasks)*3}\n- {time.strftime('%H:%M:%S')}\n",encoding="utf-8")
        print(x["match"],model.split(":")[0],flush=True)
print("done",len(tasks),len(rows))
