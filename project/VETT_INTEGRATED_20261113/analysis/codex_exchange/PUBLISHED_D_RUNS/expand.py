import sys,json,re,hashlib,time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; P=INT/"analysis"/"vett_overnight_20261114"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local")); from local_inference import service
used={"match_0001","match_0002","match_0003","match_0007","match_0008","match_0010","match_0012","match_0013","match_0014","match_0015","match_0016","match_0017","match_0018","match_0019","match_0021","match_0026","match_0027","match_0030","match_0031","match_0032","match_0042","match_0043","match_0044","match_0047","match_0048","match_0051","match_0063","match_0064","match_0065","match_0066","match_0067","match_0073","match_0075","match_0078","match_0082","match_0085","match_0086","match_0087","match_0090","match_0091","match_0092","match_0096","match_0099","match_0100","match_0102","match_0106","match_0108","match_0111","match_0120","match_0130","match_0140","match_0150","match_0159","match_0160","match_0165","match_0167","match_0174","match_0175","match_0180","match_0181","match_0182","match_0198","match_0201","match_0203","match_0209"}
words={"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10}
cand=[]
for i in range(1,221):
    m=f"match_{i:04d}"
    if m in used: continue
    try:
        text=(L.DATASET/m/"commentary.txt").read_text(encoding="utf-8"); md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m)
    except Exception: continue
    ss=L.sentences(text)
    for inn in md.innings:
        for s in ss:
            if inn.name.split()[0].lower() not in s.lower(): continue
            mm=re.search(r"(\d{2,3})\s+(?:for|/)\s+(\w+)",s)
            if not mm: continue
            r=int(mm.group(1)); w=words.get(mm.group(2).lower(),int(mm.group(2)) if mm.group(2).isdigit() else -1)
            if r==inn.total_runs and w==inn.total_wickets:
                idx=ss.index(s); M=" ".join(ss[1:]+[s]) if idx==0 else " ".join([ss[0],s]+ss[1:idx]+ss[idx+1:]); E=" ".join(ss[max(0,idx-1):idx+2])
                cand.append({"match":m,"innings":1 if inn is md.innings[0] else 2,"team":inn.name,"runs":r,"wickets":w,"evidence":s,"O":text,"M":M,"E":E,"ev_index":idx,"n_sent":len(ss),"O_sha":hashlib.sha256(text.encode()).hexdigest()})
                break
        if any(x["match"]==m for x in cand): break
cand=cand[:12]
(P/"expansion_manifest.json").write_text(json.dumps(cand,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
out=P/"runs"/"expand.jsonl"; out.parent.mkdir(exist_ok=True)
done={(r["match"],r["cond"],r["model"]) for r in ([json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()] if out.exists() else [])}
MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
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
for x in cand:
    for cond in ["O","M","E"]:
        for model in MODELS:
            if (x["match"],cond,model) in done: continue
            pr=("You are a cricket scorer. Read the commentary and return the batting team's total runs and wickets lost at the END of the specified innings. Return ONLY JSON with keys total_runs and total_wickets (integers); UNKNOWN if not confirmable. No prose.\n\nMatch: "+x["match"]+"\nInnings: "+("first" if x["innings"]==1 else "second")+"\nBatting team: "+x["team"]+"\n\nText:\n"+x[cond]+"\n\nJSON:")
            service.config.MODEL_TAG=model; info=service.model_info(model) or {}
            try: gen=service.generate(pr,num_ctx=8192,num_predict=300); raw=gen["raw_output"]
            except Exception: raw=""; gen={}
            row={"phase":"D_expand","match":x["match"],"innings":x["innings"],"cond":cond,"model":model,"digest":info.get("digest"),"text_sha256":hashlib.sha256(x[cond].encode()).hexdigest(),"prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"raw_output":raw,"parsed":ex(raw),"parse_ok":False,"done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count")}
            row["parse_ok"]=isinstance(row["parsed"],dict)
            open(out,"a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n"); done.add((x["match"],cond,model))
    (P/"PROGRESS.md").write_text(f"# PROGRESS\n\n- expansion roots {len({x['match'] for x in cand})}\n- requests {len(done)}\n- updated {time.strftime('%H:%M:%S')}\n",encoding="utf-8")
print("done",len(cand),len(done))
