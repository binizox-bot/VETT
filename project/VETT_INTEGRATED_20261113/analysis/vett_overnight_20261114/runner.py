import json,sys,hashlib,time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); P=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"vett_overnight_20261114"
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local")); from local_inference import service
M=json.loads((P/"manifest.json").read_text(encoding="utf-8")); MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
out=P/"runs"/"all.jsonl"; out.parent.mkdir(exist_ok=True)
rows=[json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()] if out.exists() else []
done={(r["phase"],r["match"],r.get("cond"),r["model"]) for r in rows}
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
    (P/"PROGRESS.md").write_text(f"# PROGRESS\n\n- requests {len(rows)}/27\n- updated {time.strftime('%H:%M:%S')}\n",encoding="utf-8")
# D
x=M["D"]
for cond in ["O","M","E"]:
    for model in MODELS:
        if ("D",x["match"],cond,model) in done: continue
        pr=("You are a cricket scorer. Read the commentary and return the batting team's total runs and wickets lost at the END of the specified innings. Return ONLY JSON with keys total_runs and total_wickets (integers). No prose.\n\nMatch: "+x["match"]+"\nInnings: first\nBatting team: "+x["team"]+"\n\nText:\n"+x[cond]+"\n\nJSON:")
        service.config.MODEL_TAG=model; info=service.model_info(model) or {}
        try: gen=service.generate(pr,num_ctx=8192,num_predict=300); raw=gen["raw_output"]
        except Exception: raw=""; gen={}
        row={"phase":"D","match":x["match"],"cond":cond,"model":model,"digest":info.get("digest"),"text_sha256":hashlib.sha256(x[cond].encode()).hexdigest(),"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":ex(raw),"parse_ok":False,"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
        row["parse_ok"]=isinstance(row["parsed"],dict); open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n"); rows.append(row); progress(); print("D",cond,model.split(":")[0],flush=True)
# T
for t in M["T"]:
    fields=list(t["gold"].keys())
    for model in MODELS:
        if ("T",t["match"],None,model) in done: continue
        pr=("You are a cricket scorer. Fill the table fields from the commentary. Return ONLY JSON with key fields mapping each field id to a value. Integers for numeric fields, exact names for names. No prose.\n\nFields:\n"+"\n".join("- "+f for f in fields)+"\n\nText:\n"+t["text"]+"\n\nJSON:")
        service.config.MODEL_TAG=model; info=service.model_info(model) or {}
        try: gen=service.generate(pr,num_ctx=8192,num_predict=1500); raw=gen["raw_output"]
        except Exception: raw=""; gen={}
        doc=ex(raw); fields_out=doc.get("fields") if isinstance(doc,dict) else None
        row={"phase":"T","match":t["match"],"cond":None,"model":model,"digest":info.get("digest"),"text_sha256":t["text_sha256"],"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":doc,"fields":fields_out,"parse_ok":isinstance(fields_out,dict),"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
        open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n"); rows.append(row); progress(); print("T",t["match"],model.split(":")[0],"parse",row["parse_ok"],flush=True)
print("done",len(rows))
