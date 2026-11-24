import sys,json,re,hashlib
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; P=INT/"analysis"/"vett_overnight_20261114"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local")); from local_inference import service
M=json.loads((P/"manifest.json").read_text(encoding="utf-8")); T=M["T"]; MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
tasks=[]
for t in T:
    md=L.parse_scorecard_full((L.DATASET/t["match"]/"scorecard.md").read_text(encoding="utf-8"),t["match"]); ss=L.sentences(t["text"]); ev=[]
    for inn in md.innings:
        for s in ss:
            if inn.name.split()[0].lower() in s.lower() and f"{inn.total_runs}" in s and re.search(rf"for\s+{inn.total_wickets}|{inn.total_wickets}\s*(?:wickets|/)",s): ev.append(s); break
    changed=t["text"]+"\n\nCandidate evidence:\n"+"\n".join(ev)
    tasks.append({"match":t["match"],"text":changed,"gold":t["gold"],"evidence":ev})
(P/"t_locator_manifest.json").write_text(json.dumps(tasks,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
out=P/"runs"/"t_locator.jsonl"; rows=[json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()] if out.exists() else []
done={(r["match"],r["model"]) for r in rows}
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
for t in tasks:
    fields=list(t["gold"].keys())
    for model in MODELS:
        if (t["match"],model) in done: continue
        pr=("You are a cricket scorer. Fill the table fields from the commentary. Return ONLY JSON with key fields mapping each field id to a value. Integers for numeric fields, exact names for names. No prose.\n\nFields:\n"+"\n".join("- "+f for f in fields)+"\n\nText:\n"+t["text"]+"\n\nJSON:")
        service.config.MODEL_TAG=model; info=service.model_info(model) or {}
        try: gen=service.generate(pr,num_ctx=8192,num_predict=1500); raw=gen["raw_output"]
        except Exception: raw=""; gen={}
        doc=ex(raw); fields_out=doc.get("fields") if isinstance(doc,dict) else (doc if isinstance(doc,dict) else None)
        row={"match":t["match"],"model":model,"digest":info.get("digest"),"text_sha256":hashlib.sha256(t["text"].encode()).hexdigest(),"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":doc,"fields":fields_out,"parse_ok":isinstance(fields_out,dict),"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
        open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n")
        print(t["match"],model.split(":")[0],"parse",row["parse_ok"],flush=True)
print("done")
