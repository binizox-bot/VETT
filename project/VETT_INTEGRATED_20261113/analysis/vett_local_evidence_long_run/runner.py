import json,sys,hashlib,time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); P=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"vett_local_evidence_long_run"
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local")); from local_inference import service
M=json.loads((P/"manifest.json").read_text(encoding="utf-8")); MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
out=P/"runs"/"all.jsonl"; out.parent.mkdir(exist_ok=True)
rows=[json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()] if out.exists() else []
done={(r["phase"],r["match"],r.get("method"),r["model"]) for r in rows}
def evp(t,x):
    return ("You are a cricket scorer. Read the commentary and find the batting team's total runs and wickets lost at the END of the specified innings. Return ONLY JSON with keys total_runs and total_wickets, each an object with status (explicit|derived|not_found|conflict|ambiguous), value (integer or UNKNOWN), quotes (verbatim strings), reason (one sentence). Do not use outside knowledge.\n\nMatch: "+x["match"]+"\nInnings: "+("first" if x["innings"]==1 else "second")+"\nBatting team: "+x["team"]+"\n\nText:\n"+t+"\n\nJSON:")
def abcp(t,method):
    extra=(" Cite the verbatim evidence after the numbers under key evidence." if method=="C" else "")
    return ("You are a cricket scorer. Read the commentary and return the batting team's final total runs and wickets for the specified innings. Return ONLY JSON with keys total_runs and total_wickets (integers)."+extra+" No prose.\n\nText:\n"+t+"\n\nJSON:")
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
def progress():
    done=len(rows); (P/"PROGRESS.md").write_text(f"# PROGRESS\n\n- requests {done}/60\n- updated {time.strftime('%H:%M:%S')}\n",encoding="utf-8")
for x in M["evidence"]:
    for model in MODELS:
        if ("evidence",x["match"],None,model) in done: continue
        pr=evp(x["text"],x); service.config.MODEL_TAG=model; info=service.model_info(model) or {}
        try: gen=service.generate(pr,num_ctx=8192,num_predict=500); raw=gen["raw_output"]
        except Exception: raw=""; gen={}
        row={"phase":"evidence","match":x["match"],"innings":x["innings"],"team":x["team"],"model":model,"digest":info.get("digest"),"text_sha256":x["text_sha256"],"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":ex(raw),"parse_ok":False,"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
        row["parse_ok"]=isinstance(row["parsed"],dict)
        open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n"); rows.append(row); progress(); print("ev",x["match"],model.split(":")[0],flush=True)
for x in M["abc"]:
    for model in MODELS:
        if ("abc",x["match"],x["method"],model) in done: continue
        pr=abcp(x["text"],x["method"]); service.config.MODEL_TAG=model; info=service.model_info(model) or {}
        try: gen=service.generate(pr,num_ctx=8192,num_predict=300); raw=gen["raw_output"]
        except Exception: raw=""; gen={}
        row={"phase":"abc","match":x["match"],"innings":x["innings"],"team":x["team"],"method":x["method"],"model":model,"digest":info.get("digest"),"text_sha256":hashlib.sha256(x["text"].encode()).hexdigest(),"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":ex(raw),"parse_ok":False,"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
        row["parse_ok"]=isinstance(row["parsed"],dict)
        open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n"); rows.append(row); progress(); print("abc",x["match"],x["method"],model.split(":")[0],flush=True)
print("done",len(rows))
