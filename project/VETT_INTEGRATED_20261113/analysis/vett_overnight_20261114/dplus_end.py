import sys,json,re,hashlib,time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; P=INT/"analysis"/"vett_overnight_20261114"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local")); from local_inference import service
M=json.loads((P/"dplus_remove_manifest.json").read_text(encoding="utf-8")); tasks=[]
for x in M:
    text=(L.DATASET/x["match"]/"commentary.txt").read_text(encoding="utf-8"); ss=L.sentences(text)
    ev=next((s for s in ss if str(x["runs"]) in s and f"{x.get('wickets')}" in s),"")
    if not ev: continue
    moved=" ".join([s for s in ss if s!=ev]+[ev])
    if moved==text: continue
    tasks.append({"match":x["match"],"team":x["team"],"runs":x["runs"],"wickets":x["wickets"],"text":moved})
(P/"dplus_end_manifest.json").write_text(json.dumps(tasks,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
out=P/"runs"/"dplus_end.jsonl"; rows=[json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()] if out.exists() else []
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
        row={"phase":"Dplus_end","match":x["match"],"model":model,"digest":info.get("digest"),"text_sha256":hashlib.sha256(x["text"].encode()).hexdigest(),"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":ex(raw),"parse_ok":False,"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
        row["parse_ok"]=isinstance(row["parsed"],dict)
        open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n"); rows.append(row)
        (P/"DPLUS2_PROGRESS.md").write_text(f"# D+ end\n\n- rows {len(rows)} / {len(tasks)*3}\n- {time.strftime('%H:%M:%S')}\n",encoding="utf-8")
        print(x["match"],model.split(":")[0],flush=True)
print("done",len(tasks),len(rows))
