import json, hashlib, re, sys, time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
P=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_followup"
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local"))
from local_inference import service
SYSTEM=("You are a cricket scorer. Read the text and fill the requested integer fields. "
        "Return ONLY one JSON object: {\"fields\": {<field_id>: <integer>}}. No prose.")
def extract(raw):
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
lina=json.loads((P/"lina.json").read_text(encoding="utf-8"))["cases"]
s=json.loads((P/"samples.json").read_text(encoding="utf-8"))[0]
rows=[]
# corrected Lina: qwen + gemma
for model in ["qwen2.5:7b-instruct-q4_K_M","gemma2:9b"]:
    for case in ["original","explicit","derivation"]:
        fields=["Nora_Vale_wickets","Nora_Vale_runs_conceded","Ruby_North_wickets","Ruby_North_runs_conceded","innings_total_wickets"]
        hints=["Nora Vale bowling wickets","Nora Vale bowling runs conceded","Ruby North bowling wickets","Ruby North bowling runs conceded","total wickets in the innings (not runs)"]
        prompt=SYSTEM+"\n\nFields:\n"+"\n".join(f"- {f} ({h})" for f,h in zip(fields,hints))+"\n\nText:\n"+lina[case]["text"]+"\n\nJSON:"
        service.config.MODEL_TAG=model
        gen=service.generate(prompt,num_ctx=8192,num_predict=320)
        doc=extract(gen["raw_output"]) or {}
        rows.append({"task":"lina_fix","case":case,"model":model,"digest":service.model_info(model).get("digest"),"fields":doc.get("fields"),"raw_output":gen["raw_output"]})
        print("lina",case,model.split(":")[0],doc.get("fields"))
# corrected explicit main match_0003: qwen + llama
for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b"]:
    fields=["Evan_Clarke_wickets","Evan_Clarke_runs_conceded","Connor_Reed_wickets","Connor_Reed_runs_conceded","innings_total_wickets"]
    hints=["Evan Clarke bowling wickets","Evan Clarke bowling runs conceded","Connor Reed bowling wickets","Connor Reed bowling runs conceded","total wickets in the innings (not runs)"]
    prompt=SYSTEM+"\n\nFields:\n"+"\n".join(f"- {f} ({h})" for f,h in zip(fields,hints))+"\n\nText:\n"+s["texts"]["explicit"]+"\n\nJSON:"
    service.config.MODEL_TAG=model
    gen=service.generate(prompt,num_ctx=8192,num_predict=320)
    doc=extract(gen["raw_output"]) or {}
    rows.append({"task":"explicit_fix","case":"match_0003","model":model,"digest":service.model_info(model).get("digest"),"fields":doc.get("fields"),"raw_output":gen["raw_output"]})
    print("explicit match_0003",model.split(":")[0],doc.get("fields"))
(P/"runs"/"fix.jsonl").write_text("\n".join(json.dumps(r,ensure_ascii=False) for r in rows)+"\n",encoding="utf-8")
print("rows",len(rows))
