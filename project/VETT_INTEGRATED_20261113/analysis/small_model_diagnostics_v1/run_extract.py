import json,re,sys,time,hashlib
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); P=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v1"; P.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local"))
from local_inference import service
S=json.loads((ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"answerability_and_short_evidence"/"short_samples.json").read_text(encoding="utf-8"))
MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
KEYS=["dismissed_batter","original_bowler","new_bowler","original_bowler_wickets_before","new_bowler_wickets_before"]
def prompt(text):
    return ("You are a cricket scorer. Extract the dismissal revision event and the two bowlers' pre-revision wicket counts. "
            "Return ONLY JSON with keys dismissed_batter, original_bowler, new_bowler, original_bowler_wickets_before, new_bowler_wickets_before. "
            "Strings for names; integers for wicket counts; UNKNOWN if insufficient. No prose.\n\nText:\n"+text+"\n\nJSON:")
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
out=P/"runs"/"extract.jsonl"; out.parent.mkdir(exist_ok=True)
for s in S:
    for model in MODELS:
        pr=prompt(s["B"]); service.config.MODEL_TAG=model; info=service.model_info(model) or {}
        try: gen=service.generate(pr,num_ctx=8192,num_predict=300); raw=gen["raw_output"]
        except Exception as e: raw=""; gen={}
        doc=ex(raw) if raw else None
        row={"match":s["match"],"model":model,"digest":info.get("digest"),"quant":info.get("quantization_level"),
             "text_sha256":hashlib.sha256(s["B"].encode()).hexdigest(),"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),
             "text_chars":len(s["B"]),"raw_output":raw,"parsed":doc,"parse_ok":isinstance(doc,dict),
             "keys_ok":isinstance(doc,dict) and all(k in doc for k in KEYS),"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
        open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n")
        print(s["match"],model.split(":")[0],"parse",row["parse_ok"],"keys",row["keys_ok"],flush=True)
print("done 6")
