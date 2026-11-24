import argparse,json,re,sys,time,hashlib
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); P=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_update_and_full_table"
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local"))
from local_inference import service
MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
SYS=("You are a cricket scorer. Read the text and fill the requested integer fields. "
     "Return ONLY JSON. No prose.")
def hint(f):
    for k,v in {"wickets_credited":"wickets credited","bowling_runs_conceded":"bowling runs conceded","innings_wickets_lost":"wickets lost by the batting side in the innings (not runs)"}.items():
        if f.endswith(k): return v
    return ""
def prompt(text,fields,step=False):
    lines=[f"- {f} ({hint(f)})" for f in fields]
    ext=(" First extract the dismissal event and pre-revision figures under key extraction, then give final fields. "
         "Structure: {\"extraction\":{\"batter\",\"original_bowler\",\"new_bowler\",\"orig_wickets\",\"orig_runs\",\"new_wickets\",\"new_runs\",\"innings_wickets_lost\"},\"fields\":{...}}." if step else "")
    return SYS+ext+"\n\nFields:\n"+"\n".join(lines)+"\n\nText:\n"+text+"\n\nJSON:"
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
def rows(p): return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--task",choices=["dev","lina","retest"],required=True); ap.add_argument("--budget",type=int,default=120)
    a=ap.parse_args()
    dev=json.loads((P/"dev.json").read_text(encoding="utf-8"))
    lina=json.loads((P/"lina.json").read_text(encoding="utf-8"))["cases"] if (P/"lina.json").exists() else {}
    runs=P/"runs"; runs.mkdir(parents=True,exist_ok=True); out=runs/f"{a.task}.jsonl"
    used=sum(len(rows(p)) for p in runs.glob("*.jsonl")); done={(r["match"],r["cond"],r["model"]) for r in rows(out)}
    if a.task=="dev":
        items=[((s["match"],c,m),prompt(s[c],s["fields"].keys(),step=(c=="C"))) for m in MODELS for s in dev for c in "ABC"]
    elif a.task=="lina":
        items=[((c,"lina",m),prompt(lina[c]["text"],lina[c]["gold"].keys(),step=False)) for m in ["qwen2.5:7b-instruct-q4_K_M","gemma2:9b"] for c in lina]
    else:
        fixed={"match_0014","match_0016"}
        items=[((s["match"],"A",m),prompt(s["A"],s["fields"].keys())) for m in MODELS for s in dev if s["match"] in fixed]
    print("task",a.task,"used",used,"items",len(items))
    for (match,cond,model),pr in items:
        if (match,cond,model) in done: continue
        if used>=a.budget: print("BUDGET"); break
        service.config.MODEL_TAG=model; info=service.model_info(model) or {}
        try:
            npred=600 if cond=="C" else 400
            gen=service.generate(pr,num_ctx=8192,num_predict=npred); raw=gen["raw_output"]; err=None
        except Exception as e:
            raw=""; gen={}; err=f"{type(e).__name__}: {e}"
        doc=ex(raw) if raw else None
        fields=(doc.get("fields") if isinstance(doc.get("fields"),dict) else {k:v for k,v in doc.items() if k!="extraction"}) if isinstance(doc,dict) else None
        extraction=doc.get("extraction") if isinstance(doc,dict) else None
        row={"match":match,"cond":cond,"model":model,"digest":info.get("digest"),"quant":info.get("quantization_level"),
             "prompt_sha256":hashlib.sha256(pr.encode()).hexdigest(),"prompt_chars":len(pr),"raw_output":raw,"parsed":doc,
             "fields":fields,"extraction":extraction,"parse_ok":isinstance(fields,dict),"error":err,
             "done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count"),"prompt_eval_count":gen.get("prompt_eval_count")}
        with open(out,"a",encoding="utf-8",newline="\n") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
        used+=1; done.add((match,cond,model)); print(match,cond,model.split(":")[0],"parse",row["parse_ok"],flush=True)
    print("done",used)
if __name__=="__main__": main()
