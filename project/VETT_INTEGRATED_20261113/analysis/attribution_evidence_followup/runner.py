import argparse, hashlib, json, re, sys, time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
P=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_evidence_followup"
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local"))
from local_inference import service
MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
SYSTEM=("You are a cricket scorer. Read the text and fill the five integer fields. "
        "Return ONLY JSON: {\"fields\": {<field_id>: <integer>}}. No prose.")
def sha(t): return hashlib.sha256(t.encode()).hexdigest()
def prompt(text,fields):
    hint={"wickets_credited":"wickets credited","bowling_runs_conceded":"bowling runs conceded","innings_wickets_lost":"wickets lost by the batting side in the innings (not runs)"}
    lines=[]
    for f in fields:
        h=""
        for k,v in hint.items():
            if f.endswith(k): h=v
        lines.append(f"- {f} ({h})")
    return SYSTEM+"\n\nFields:\n"+"\n".join(lines)+"\n\nText:\n"+text+"\n\nJSON:"
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
def rows(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--task",choices=["dev","hold","lina","retest"],required=True)
    ap.add_argument("--budget",type=int,default=120)
    args=ap.parse_args()
    dev=json.loads((P/"dev.json").read_text(encoding="utf-8"))
    hold=json.loads((P/"holdout.json").read_text(encoding="utf-8"))
    lina=json.loads((P/"lina.json").read_text(encoding="utf-8"))["cases"]
    runs=P/"runs"; runs.mkdir(parents=True,exist_ok=True)
    out=runs/f"{args.task}.jsonl"
    used=sum(len(rows(p)) for p in runs.glob("*.jsonl"))
    done={(r["match"],r["condition"],r["model"]) for r in rows(out)}
    if args.task=="dev":
        items=[((s["match"],c,m),prompt(s[c],s["fields"].keys())) for m in MODELS for s in dev for c in "ABC"]
    elif args.task=="hold":
        items=[((s["match"],c,m),prompt(s[c],s["fields"].keys())) for m in MODELS for s in hold for c in "AB"]
    elif args.task=="lina":
        items=[((c,"lina",m),prompt(lina[c]["text"],lina[c]["gold"].keys())) for m in ["qwen2.5:7b-instruct-q4_K_M","gemma2:9b"] for c in lina]
    else:
        fixed={"match_0008","match_0017"}
        items=[((s["match"],"A",m),prompt(s["A"],s["fields"].keys())) for m in MODELS for s in dev if s["match"] in fixed]
    print("task",args.task,"used",used,"items",len(items))
    for (match,cond,model),pr in items:
        if (match,cond,model) in done: continue
        if used>=args.budget: print("BUDGET STOP"); break
        service.config.MODEL_TAG=model
        info=service.model_info(model) or {}
        try:
            gen=service.generate(pr,num_ctx=8192,num_predict=300); raw=gen["raw_output"]; err=None
        except Exception as exc:
            raw=""; gen={}; err=f"{type(exc).__name__}: {exc}"
        doc=extract(raw) if raw else None
        fields=doc.get("fields") if isinstance(doc,dict) else None
        row={"match":match,"condition":cond,"model":model,"digest":info.get("digest"),"quant":info.get("quantization_level"),
             "prompt_sha256":sha(pr),"prompt_chars":len(pr),"raw_output":raw,"parsed":doc,"fields":fields,
             "parse_ok":isinstance(fields,dict),"error":err,"done_reason":gen.get("done_reason"),
             "eval_count":gen.get("eval_count"),"logged_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
        with open(out,"a",encoding="utf-8",newline="\n") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
        used+=1; done.add((match,cond,model))
        print(match,cond,model.split(":")[0],"parse",row["parse_ok"],flush=True)
    print("done",used)
if __name__=="__main__": main()
