import sys,json,re,time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; P=INT/"analysis"/"attribution_update_and_full_table"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local"))
from local_inference import service
MATCHES=["match_0003","match_0008","match_0010","match_0012","match_0015","match_0017"]
MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
def gold(m):
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); f={}
    f["match.result"]=md.result; f["match.toss"]=md.toss; f["match.pom"]=md.player_of_match
    for i,inn in enumerate(md.innings,1):
        p=f"inn{i}"
        f[p+".team"]=inn.name; f[p+".total_runs"]=inn.total_runs; f[p+".total_wickets"]=inn.total_wickets
        f[p+".overs"]=inn.overs; f[p+".byes"]=inn.byes; f[p+".leg_byes"]=inn.leg_byes; f[p+".no_balls"]=inn.no_balls; f[p+".wides"]=inn.wides
        for r,b in enumerate(sorted(inn.batters,key=lambda x:x.runs,reverse=True)[:3],1):
            f[f"{p}.bat{r}_name"]=b.name; f[f"{p}.bat{r}_runs"]=b.runs
        for r,b in enumerate(sorted(inn.bowlers,key=lambda x:(x.wickets,-x.runs_conceded),reverse=True)[:2],1):
            f[f"{p}.bowl{r}_name"]=b.name; f[f"{p}.bowl{r}_wickets"]=b.wickets; f[f"{p}.bowl{r}_runs"]=b.runs_conceded
    return f
def prompt(text,f):
    lines=[f"- {k}" for k in f]
    return ("You are a cricket scorer. Fill every field from the commentary. Return ONLY JSON: {\"fields\": {<field_id>: <value>}}. "
            "Use integers for numeric fields and exact names for names. No prose.\n\nFields:\n"+"\n".join(lines)+"\n\nCommentary:\n"+text+"\n\nJSON:")
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
runs=P/"runs"; runs.mkdir(parents=True,exist_ok=True); out=runs/"ft.jsonl"
done={(r["match"],r["model"]) for r in ([json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()] if out.exists() else [])}
used=sum(len([1 for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]) for p in runs.glob("*.jsonl"))
for m in MATCHES:
    g=gold(m); text=(L.DATASET/m/"commentary.txt").read_text(encoding="utf-8")
    for model in MODELS:
        if (m,model) in done: continue
        if used>=120: print("BUDGET"); break
        service.config.MODEL_TAG=model; info=service.model_info(model) or {}
        pr=prompt(text,g)
        try:
            gen=service.generate(pr,num_ctx=8192,num_predict=1200); raw=gen["raw_output"]; err=None
        except Exception as e:
            raw=""; gen={}; err=f"{type(e).__name__}: {e}"
        doc=ex(raw) if raw else None; fields=doc.get("fields") if isinstance(doc,dict) else None
        row={"match":m,"model":model,"fields":fields,"parse_ok":isinstance(fields,dict),"raw_output":raw,"error":err,
             "done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count"),"prompt_chars":len(pr)}
        with open(out,"a",encoding="utf-8",newline="\n") as fh: fh.write(json.dumps(row,ensure_ascii=False)+"\n")
        used+=1; print(m,model.split(":")[0],"parse",row["parse_ok"],"eval",row["eval_count"],flush=True)
print("used",used)
