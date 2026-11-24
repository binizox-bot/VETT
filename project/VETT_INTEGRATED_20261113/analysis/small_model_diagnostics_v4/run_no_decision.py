import json,sys,hashlib
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); P=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v4"; P.mkdir(parents=True,exist_ok=True)
V3=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v3"
S=json.loads((V3/"SAMPLE_MANIFEST.json").read_text(encoding="utf-8"))
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local")); from local_inference import service
MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
out=P/"runs"/"no_decision.jsonl"; out.parent.mkdir(exist_ok=True)
rows=[json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()] if out.exists() else []
done={(r["match"],r["notice"],r["model"]) for r in rows}
def prompt(t):
    return ("You are a cricket scorer. Extract the review facts. Return ONLY JSON with keys dismissed_batter, original_bowler, final_bowler, original_bowler_wickets_before, other_bowler_wickets_before. Strings for names; integers for wickets; UNKNOWN if insufficient. No prose.\n\nText:\n"+t+"\n\nJSON:")
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
    for notice in ["reassign","retain"]:
        text=s["reassign_text"] if notice=="reassign" else s["retain_text"]
        for model in MODELS:
            if (s["match"],notice,model) in done: continue
            pr=prompt(text); service.config.MODEL_TAG=model; info=service.model_info(model) or {}
            try: gen=service.generate(pr,num_ctx=8192,num_predict=400); raw=gen["raw_output"]
            except Exception: raw=""; gen={}
            doc=ex(raw) if raw else None
            row={"match":s["match"],"notice":notice,"model":model,"digest":info.get("digest"),"text_chars":len(text),"text_sha256":hashlib.sha256(text.encode()).hexdigest(),"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":doc,"parse_ok":isinstance(doc,dict),"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
            open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n")
            print(s["match"],notice,model.split(":")[0],"parse",row["parse_ok"],flush=True)
print("done")
