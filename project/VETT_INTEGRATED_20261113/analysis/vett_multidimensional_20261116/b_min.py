import sys,json,re,hashlib,time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"vett_multidimensional_20261116"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local")); from local_inference import service
ROOTS=["match_0066","match_0085","match_0087","match_0096","match_0165","match_0021","match_0183","match_0184"]
tasks=[]
for m in ROOTS:
    md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); text=(L.DATASET/m/"commentary.txt").read_text(encoding="utf-8"); ss=L.sentences(text)
    inn=md.innings[0]; ev=next((s for s in ss if inn.name.split()[0].lower() in s.lower() and str(inn.total_runs) in s and re.search(rf"for\s+{inn.total_wickets}|{inn.total_wickets}\s*(?:wickets|/)",s)),"")
    if not ev: continue
    idx=ss.index(ev); base={"match":m,"innings":1,"team":inn.name,"runs":inn.total_runs,"wickets":inn.total_wickets}
    conds={"O":text}
    if idx>0: conds["P"]=" ".join([ss[0],ev]+ss[1:idx]+ss[idx+1:])
    if idx<len(ss)-1: conds["L"]=" ".join([s for s in ss if s!=ev]+[ev])
    conds["E"]=" ".join(ss[max(0,idx-1):idx+2])
    # competitor same innings
    comp=next((s for s in ss if s!=ev and re.search(r"\d{1,3}\s+for\s+\d",s)),"")
    if comp:
        conds["WI"]=" ".join(s for s in ss if s!=comp)
        cand=[s for s in ss if s not in (ev,comp) and abs(len(s)-len(comp))<max(80,len(comp)*0.6)]
        if cand: conds["WIC"]=" ".join(s for s in ss if s!=cand[0])
    if len(md.innings)>1:
        other=md.innings[1]; ocomp=next((s for s in ss if str(other.total_runs) in s and re.search(r"\d+\s+for",s)),"")
        if ocomp:
            conds["OI"]=" ".join(s for s in ss if s!=ocomp)
            cand=[s for s in ss if s not in (ev,ocomp) and abs(len(s)-len(ocomp))<max(80,len(ocomp)*0.6)]
            if cand: conds["OIC"]=" ".join(s for s in ss if s!=cand[0])
    for c,t in conds.items(): tasks.append({**base,"cond":c,"text":t,"sha":hashlib.sha256(t.encode()).hexdigest()})
(O/"B_MIN_MANIFEST.json").write_text(json.dumps(tasks,ensure_ascii=False,indent=1)+"\n",encoding="utf-8")
out=O/"RUNS"/"b_min.jsonl"; out.parent.mkdir(exist_ok=True)
rows=[json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()] if out.exists() else []
done={(r["match"],r["cond"],r["model"]) for r in rows}; MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
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
for x in tasks:
    for model in MODELS:
        if (x["match"],x["cond"],model) in done: continue
        pr=("You are a cricket scorer. Read the commentary and return the batting team's total runs and wickets lost at the END of the specified innings. Return ONLY JSON with keys total_runs and total_wickets (integers); UNKNOWN if not confirmable. No prose.\n\nMatch: "+x["match"]+"\nInnings: first\nBatting team: "+x["team"]+"\n\nText:\n"+x["text"]+"\n\nJSON:")
        service.config.MODEL_TAG=model; info=service.model_info(model) or {}
        try: gen=service.generate(pr,num_ctx=8192,num_predict=300); raw=gen["raw_output"]
        except Exception: raw=""; gen={}
        row={"phase":"B_min","match":x["match"],"cond":x["cond"],"model":model,"digest":info.get("digest"),"text_sha256":x["sha"],"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":ex(raw),"parse_ok":False,"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
        row["parse_ok"]=isinstance(row["parsed"],dict)
        open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n"); rows.append(row)
        (O/"PROGRESS.md").write_text(f"# B min\n\n- rows {len(rows)} / {len(tasks)*3}\n- {time.strftime('%H:%M:%S')}\n",encoding="utf-8")
        print(x["match"],x["cond"],model.split(":")[0],flush=True)
print("done",len(tasks),len(rows))
