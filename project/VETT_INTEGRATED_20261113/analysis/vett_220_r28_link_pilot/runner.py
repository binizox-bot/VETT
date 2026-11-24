import json,sys,hashlib
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); P=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"vett_220_r28_link_pilot"
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local")); from local_inference import service
S=json.loads((P/"manifest.json").read_text(encoding="utf-8"))["matches"]; MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
out=P/"runs"/"paired.jsonl"; out.parent.mkdir(exist_ok=True)
rows=[json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()] if out.exists() else []
done={(r["match"],r["cond"],r["method"],r["model"]) for r in rows}
def ap(t,s):
    A,B=s["A"],s["B"]
    return ("You are a cricket scorer. Read the text and return the final table values. Return ONLY JSON with keys "
            f"{A}_wickets, {B}_wickets, innings_total_wickets. Integers, no prose.\n\nText:\n"+t+"\n\nJSON:")
def bp(t,s):
    A,B=s["A"],s["B"]
    return ("You are a cricket scorer. Extract the review facts. Return ONLY JSON with keys decision (reassign|retain|UNKNOWN), dismissed_batter, original_bowler, final_bowler, "
            f"{A}_wickets_before, {B}_wickets_before, innings_total_wickets. Both wicket values are pre-review. UNKNOWN if insufficient. No prose.\n\nText:\n"+t+"\n\nJSON:")
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
for s in S:
    for cond in ["none","retain","reassign"]:
        t=s["texts"][cond]
        for model in MODELS:
            for method in ["A","B"]:
                if (s["match"],cond,method,model) in done: continue
                pr=ap(t,s) if method=="A" else bp(t,s)
                service.config.MODEL_TAG=model; info=service.model_info(model) or {}
                try: gen=service.generate(pr,num_ctx=8192,num_predict=450); raw=gen["raw_output"]
                except Exception: raw=""; gen={}
                doc=ex(raw) if raw else None
                row={"match":s["match"],"cond":cond,"method":method,"model":model,"digest":info.get("digest"),"text_chars":len(t),"text_sha256":hashlib.sha256(t.encode()).hexdigest(),"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":doc,"parse_ok":isinstance(doc,dict),"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
                open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n")
                print(s["match"],cond,method,model.split(":")[0],flush=True)
print("done")
