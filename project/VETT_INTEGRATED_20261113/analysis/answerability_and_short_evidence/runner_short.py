import json,re,sys,time,hashlib
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); P=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"answerability_and_short_evidence"
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local"))
from local_inference import service
MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
S=json.loads((P/"short_samples.json").read_text(encoding="utf-8"))
def prompt(text,fields,step=False):
    h={"wickets_credited":"wickets credited","bowling_runs_conceded":"bowling runs conceded","innings_wickets_lost":"wickets lost by the batting side (not runs)"}
    lines=[f"- {f} ({next((v for k,v in h.items() if f.endswith(k)),'')})" for f in fields]
    ext=(" First output extraction {batter,original_bowler,new_bowler,orig_wickets,new_wickets,innings_wickets_lost}, then fields." if step else "")
    return ("You are a cricket scorer. Read the text and fill the integer fields. Return ONLY JSON. No prose."+ext+"\n\nFields:\n"+"\n".join(lines)+"\n\nText:\n"+text+"\n\nJSON:")
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
out=P/"runs"/"short.jsonl"; out.parent.mkdir(exist_ok=True)
used=0
for s in S:
    for c in "ABC":
        for model in MODELS:
            text=s[c]; pr=prompt(text,s["fields"].keys(),step=(c=="C"))
            service.config.MODEL_TAG=model; info=service.model_info(model) or {}
            try:
                gen=service.generate(pr,num_ctx=8192,num_predict=600 if c=="C" else 400); raw=gen["raw_output"]
            except Exception as e:
                raw=""; gen={}
            doc=ex(raw) if raw else None
            fields=doc.get("fields") if isinstance(doc,dict) and isinstance(doc.get("fields"),dict) else (doc if isinstance(doc,dict) else None)
            row={"match":s["match"],"cond":c,"model":model,"digest":info.get("digest"),"quant":info.get("quantization_level"),
                 "text_chars":len(text),"text_sha256":hashlib.sha256(text.encode()).hexdigest(),"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),
                 "raw_output":raw,"parsed":doc,"fields":fields,"extraction":doc.get("extraction") if isinstance(doc,dict) else None,
                 "parse_ok":isinstance(fields,dict),"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
            open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n")
            used+=1; print(s["match"],c,model.split(":")[0],"parse",row["parse_ok"],flush=True)
print("used",used)
