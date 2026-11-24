import sys,json,hashlib,time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"vett_multidimensional_20261116"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local")); from local_inference import service
ROOTS=["match_0193","match_0194","match_0195","match_0196"]
T=[]
for m in ROOTS:
    text=(L.DATASET/m/"commentary.txt").read_text(encoding="utf-8"); md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m)
    gold={"match.result":md.result,"match.toss":md.toss,"match.pom":md.player_of_match}
    for i,inn in enumerate(md.innings,1):
        p=f"inn{i}"; gold[p+".team"]=inn.name; gold[p+".total_runs"]=inn.total_runs; gold[p+".total_wickets"]=inn.total_wickets; gold[p+".overs"]=inn.overs
        for j,b in enumerate(sorted(inn.batters,key=lambda x:x.runs,reverse=True)[:3],1): gold[f"{p}.bat{j}_name"]=b.name; gold[f"{p}.bat{j}_runs"]=b.runs
        for j,b in enumerate(sorted(inn.bowlers,key=lambda x:(x.wickets,-x.runs_conceded),reverse=True)[:2],1): gold[f"{p}.bowl{j}_name"]=b.name; gold[f"{p}.bowl{j}_wickets"]=b.wickets; gold[f"{p}.bowl{j}_runs"]=b.runs_conceded
    T.append({"match":m,"text":text,"gold":gold,"sha":hashlib.sha256(text.encode()).hexdigest()})
(O/"A_DEV3_MANIFEST.json").write_text(json.dumps(T,ensure_ascii=False,indent=1)+"\n",encoding="utf-8")
out=O/"RUNS"/"a_dev3.jsonl"; rows=[json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()] if out.exists() else []
done={(r["match"],r["model"]) for r in rows}; MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
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
for t in T:
    fields=list(t["gold"].keys())
    for model in MODELS:
        if (t["match"],model) in done: continue
        pr=("You are a cricket scorer. Fill the table fields from the commentary. Return ONLY JSON with key fields mapping each field id to a value. Integers for numeric fields, exact names for names. No prose.\n\nFields:\n"+"\n".join("- "+f for f in fields)+"\n\nText:\n"+t["text"]+"\n\nJSON:")
        service.config.MODEL_TAG=model; info=service.model_info(model) or {}
        try: gen=service.generate(pr,num_ctx=8192,num_predict=1500); raw=gen["raw_output"]
        except Exception: raw=""; gen={}
        doc=ex(raw); f=doc.get("fields") if isinstance(doc,dict) else (doc if isinstance(doc,dict) else None)
        row={"phase":"A_dev3","match":t["match"],"model":model,"digest":info.get("digest"),"text_sha256":t["sha"],"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":doc,"fields":f,"parse_ok":isinstance(f,dict),"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
        open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n"); rows.append(row)
        (O/"PROGRESS.md").write_text(f"# A dev3\n\n- rows {len(rows)} / {len(T)*3}\n- {time.strftime('%H:%M:%S')}\n",encoding="utf-8")
        print(t["match"],model.split(":")[0],"parse",row["parse_ok"],flush=True)
print("done",len(T),len(rows))
