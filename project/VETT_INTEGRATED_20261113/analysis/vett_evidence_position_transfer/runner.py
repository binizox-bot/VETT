import json,sys,hashlib,time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); P=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"vett_evidence_position_transfer"
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local")); from local_inference import service
S=json.loads((P/"manifest.json").read_text(encoding="utf-8")); MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
out=P/"runs"/"ome.jsonl"; out.parent.mkdir(exist_ok=True)
rows=[json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()] if out.exists() else []
done={(r["match"],r["cond"],r["model"]) for r in rows}
def prompt(t,x):
    return ("You are a cricket scorer. Read the commentary and return the batting team's total runs and wickets lost at the END of the specified innings. Return ONLY JSON with keys total_runs and total_wickets (integers); UNKNOWN if not confirmable. No prose.\n\nMatch: "+x["match"]+"\nInnings: "+("first" if x["innings"]==1 else "second")+"\nBatting team: "+x["team"]+"\n\nText:\n"+t+"\n\nJSON:")
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
for x in S:
    for cond in ["O","M","E"]:
        t=x[cond]
        for model in MODELS:
            if (x["match"],cond,model) in done: continue
            pr=prompt(t,x); service.config.MODEL_TAG=model; info=service.model_info(model) or {}
            try: gen=service.generate(pr,num_ctx=8192,num_predict=300); raw=gen["raw_output"]
            except Exception: raw=""; gen={}
            row={"match":x["match"],"cond":cond,"model":model,"digest":info.get("digest"),"text_chars":len(t),"text_sha256":hashlib.sha256(t.encode()).hexdigest(),"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":ex(raw),"parse_ok":isinstance(row.get("parsed"),dict) if False else False,"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
            row["parse_ok"]=isinstance(row["parsed"],dict)
            open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n"); rows.append(row)
            (P/"PROGRESS.md").write_text(f"# PROGRESS\n\n- requests {len(rows)}/45\n- updated {time.strftime('%H:%M:%S')}\n",encoding="utf-8")
            print(x["match"],cond,model.split(":")[0],flush=True)
print("done",len(rows))
