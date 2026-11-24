import sys,json,hashlib,time,os
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; P=INT/"analysis"/"vett_overnight_20261114"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local")); from local_inference import service
MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
pos=[]
for i in range(1,221):
    m=f"match_{i:04d}"
    try:
        text=(L.DATASET/m/"commentary.txt").read_text(encoding="utf-8"); md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m)
    except Exception: continue
    for inn in md.innings:
        pos.append({"match":m,"innings":1 if inn is md.innings[0] else 2,"team":inn.name,"runs":inn.total_runs,"wickets":inn.total_wickets,"text":text,"sha":hashlib.sha256(text.encode()).hexdigest()})
out=P/"runs"/"u_full.jsonl"; out.parent.mkdir(exist_ok=True)
rows=[json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()] if out.exists() else []
done={(r["match"],r["innings"],r["model"]) for r in rows}
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
total=len(pos)*3
for x in pos:
    for model in MODELS:
        if (x["match"],x["innings"],model) in done: continue
        pr=("You are a cricket scorer. Read the commentary and find the batting team's total runs and wickets lost at the END of the specified innings. Return ONLY JSON with keys total_runs and total_wickets, each an object with status (explicit|derived|not_found|conflict|ambiguous), value (integer or UNKNOWN), quotes (verbatim strings), reason (one sentence). Do not use outside knowledge.\n\nMatch: "+x["match"]+"\nInnings: "+("first" if x["innings"]==1 else "second")+"\nBatting team: "+x["team"]+"\n\nText:\n"+x["text"]+"\n\nJSON:")
        service.config.MODEL_TAG=model; info=service.model_info(model) or {}
        try: gen=service.generate(pr,num_ctx=8192,num_predict=500); raw=gen["raw_output"]
        except Exception: raw=""; gen={}
        row={"phase":"U_full","match":x["match"],"innings":x["innings"],"team":x["team"],"model":model,"digest":info.get("digest"),"text_sha256":x["sha"],"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":ex(raw),"parse_ok":False,"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
        row["parse_ok"]=isinstance(row["parsed"],dict)
        open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n"); rows.append(row); done.add((x["match"],x["innings"],model))
        if len(rows)%10==0:
            (P/"U_PROGRESS.md").write_text(f"# U FULL PROGRESS\n\n- rows {len(rows)} / {total}\n- last {x['match']} inn{x['innings']} {model}\n- updated {time.strftime('%Y-%m-%dT%H:%M:%S')}\n",encoding="utf-8")
            (P/"U_STATE.json").write_text(json.dumps({"rows":len(rows),"planned":total,"last":x["match"],"updated":time.strftime("%Y-%m-%dT%H:%M:%S")},ensure_ascii=False),encoding="utf-8")
print("done",len(rows),total)
