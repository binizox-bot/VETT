import json,sys,hashlib
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); P=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v2"
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local")); from local_inference import service
S=json.loads((P/"SAMPLE_MANIFEST.json").read_text(encoding="utf-8")); out=P/"runs"/"paired.jsonl"
rows=[json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
done={(r["match"],r["kind"],r["model"]) for r in rows}
def dp(t,s):
    ks=[f"{s['A']}_wickets",f"{s['B']}_wickets"]
    return ("You are a cricket scorer. Read the text and return the two final wicket counts after the review. Return ONLY JSON with keys "+", ".join(ks)+". Integers, no prose.\n\nText:\n"+t+"\n\nJSON:")
def ep(t,s):
    return ("You are a cricket scorer. Extract the review decision and pre-review facts. Return ONLY JSON with keys decision (reassign|retain|UNKNOWN), dismissed_batter, original_bowler, final_bowler, original_bowler_wickets_before, other_bowler_wickets_before. Strings for names, integers for wickets, UNKNOWN if insufficient. final_bowler may equal original_bowler. No prose.\n\nText:\n"+t+"\n\nJSON:")
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
MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
for s in S:
    for kind in ["direct_reassign","extract_reassign","extract_retain"]:
        text=s["reassign_text"] if "reassign" in kind else s["retain_text"]
        for model in MODELS:
            if (s["match"],kind,model) in done: continue
            pr=dp(text,s) if kind=="direct_reassign" else ep(text,s)
            service.config.MODEL_TAG=model; info=service.model_info(model) or {}
            try: gen=service.generate(pr,num_ctx=8192,num_predict=400); raw=gen["raw_output"]
            except Exception as e: raw=""; gen={}
            doc=ex(raw) if raw else None
            row={"match":s["match"],"kind":kind,"model":model,"digest":info.get("digest"),"quant":info.get("quantization_level"),"text_chars":len(text),"text_sha256":hashlib.sha256(text.encode()).hexdigest(),"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":doc,"parse_ok":isinstance(doc,dict),"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
            open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n")
            print(s["match"],kind,model.split(":")[0],"parse",row["parse_ok"],flush=True)
print("resumed done")
