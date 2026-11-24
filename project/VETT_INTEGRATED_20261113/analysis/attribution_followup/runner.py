import argparse, hashlib, json, re, sys, time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT=ROOT/"VETT_INTEGRATED_20261113"
OUT=INT/"analysis"/"attribution_followup"
sys.path.insert(0,str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local"))
from local_inference import service
MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]
SYSTEM=("You are a cricket scorer. Read the text and fill the requested integer fields. "
        "Return ONLY one JSON object: {\"fields\": {<field_id>: <integer>}}. "
        "Use the string UNKNOWN if a field cannot be determined. No prose.")

def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()
def hint(fid):
    return fid.replace("_"," ")

def main_prompt(text,fields):
    lines=[f"- {k} ({hint(k)})" for k in fields]
    return SYSTEM+"\n\nFields:\n"+"\n".join(lines)+"\n\nText:\n"+text+"\n\nJSON:"

def method_prompt(s):
    keys="batter, original_bowler, new_bowler, orig_wickets, orig_runs, new_wickets, new_runs, innings_total_wickets"
    return ("You are a cricket scorer. Extract the revision event from the text. Return ONLY JSON with keys: "
            +keys+". Use integers. Text:\n"+s["texts"]["derivation"]+"\n\nJSON:")

def extract(raw):
    if not raw: return None
    s=raw.strip()
    if s.startswith("```"):
        s=re.sub(r"^```\w*\n?","",s); s=re.sub(r"\n?```$","",s)
    i=s.find("{")
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
    if not p.exists(): return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--task",choices=["main","lina","method","retest","smoke"],default="main")
    ap.add_argument("--models",nargs="*",default=MODELS)
    ap.add_argument("--budget",type=int,default=120)
    args=ap.parse_args()
    samples=json.loads((OUT/"samples.json").read_text(encoding="utf-8"))
    lina=json.loads((OUT/"lina.json").read_text(encoding="utf-8"))["cases"]
    runs=OUT/"runs"; runs.mkdir(parents=True,exist_ok=True)
    out=runs/f"{args.task}.jsonl"
    used=sum(len(rows(p)) for p in runs.glob("*.jsonl"))
    done={(r.get("match"),r.get("version"),r.get("model")) for r in rows(out)}
    print("task",args.task,"used",used,"/",args.budget)
    if args.task=="lina":
        items=[((c,"lina",m),main_prompt(lina[c]["text"],["Nora_Vale_wickets","Nora_Vale_runs","Ruby_North_wickets","Ruby_North_runs","innings_total_wickets"]))
               for m in args.models for c in lina]
    elif args.task=="main":
        items=[]
        for m in args.models:
            for s in samples:
                for v in ["explicit","derivation","short"]:
                    items.append(((s["match"],v,m),main_prompt(s["texts"][v],s["fields"].keys())))
    elif args.task=="method":
        items=[((s["match"],"method",m),method_prompt(s)) for m in args.models for s in samples]
    elif args.task=="retest":
        fixed={"match_0003","match_0017"}
        items=[((s["match"],"derivation",m),main_prompt(s["texts"]["derivation"],s["fields"].keys()))
               for m in args.models for s in samples if s["match"] in fixed]
    else:
        s=samples[0]; items=[((s["match"],"explicit",args.models[0]),main_prompt(s["texts"]["explicit"],s["fields"].keys()))]
    for (match,ver,model),prompt in items:
        if (match,ver,model) in done: continue
        if used>=args.budget: print("BUDGET STOP"); break
        service.config.MODEL_TAG=model
        info=service.model_info(model) or {}
        try:
            gen=service.generate(prompt,num_ctx=8192,num_predict=320); raw=gen["raw_output"]; err=None
        except Exception as exc:
            raw=""; gen={}; err=f"{type(exc).__name__}: {exc}"
        doc=extract(raw) if raw else None
        fields=doc.get("fields") if isinstance(doc,dict) else None
        row={"schema":"vett.attribution_followup.run.v1","task":args.task,"match":match,"version":ver,
             "model":model,"digest":info.get("digest"),"quant":info.get("quantization_level"),
             "prompt_sha256":sha(prompt),"prompt_chars":len(prompt),"raw_output":raw,"parsed":doc,
             "fields":fields,"parse_ok":isinstance(fields,dict),"error":err,
             "done_reason":gen.get("done_reason"),"eval_count":gen.get("eval_count"),
             "prompt_eval_count":gen.get("prompt_eval_count"),"logged_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
        with open(out,"a",encoding="utf-8",newline="\n") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
        used+=1; done.add((match,ver,model))
        print(match,ver,model.split(":")[0],"parse",row["parse_ok"],flush=True)
    print("done used",used)
if __name__=="__main__": main()
