import argparse, hashlib, json, re, sys, time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT=ROOT/"VETT_INTEGRATED_20261113"
OUT=INT/"analysis"/"pilot_next"/"runs"
sys.path.insert(0, str(ROOT/"VETT_R28_DIFFICULTY_20261112"/"03_build"/"local"))
from local_inference import service

SYSTEM=("You are a cricket scorecard reader. Read the commentary and fill the requested fields. "
        "Return ONLY one JSON object: {\"fields\": {<field_id>: <integer>}}. "
        "Use the string UNKNOWN if a field cannot be determined. No prose.")
MAIN_MODELS=["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]

def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()

def desc(fid):
    inn="first" if fid.startswith("inn1") else "second"
    tail=fid.split(".")[-1].replace("_"," ")
    return f"{inn} innings {tail}"

def prompt_main(s,t):
    fields="\n".join(f"- {k} ({desc(k)})" for k in t)
    return SYSTEM+f"\n\nFields:\n{fields}\n\nCommentary:\n{s}\n\nJSON:"

def prompt_lina(text):
    fields="\n".join(f"- {k} ({desc(k)})" for k in ["inn2.Nora_Vale.figures","inn2.Ruby_North.figures","inn2.team_wickets"])
    return SYSTEM+f"\n\nFields:\n{fields}\n\nCommentary:\n{text}\n\nReturn fields plus an evidence string. JSON:"

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
    ap.add_argument("--task",choices=["main","lina","smoke","retest"],default="main")
    ap.add_argument("--models",nargs="*",default=MAIN_MODELS)
    ap.add_argument("--conditions",nargs="*",default=["A","B","C","D"])
    ap.add_argument("--limit",type=int,default=0)
    ap.add_argument("--budget",type=int,default=120)
    args=ap.parse_args()
    samples=json.loads((INT/"analysis"/"pilot_next"/"samples.json").read_text(encoding="utf-8"))
    lina=json.loads((INT/"analysis"/"pilot_next"/"lina.json").read_text(encoding="utf-8"))["cases"]
    OUT.mkdir(parents=True,exist_ok=True)
    out=OUT/f"{args.task}.jsonl"
    used=sum(len(rows(p)) for p in OUT.glob("*.jsonl"))
    done={(r.get("match"),r.get("condition"),r.get("model")) for r in rows(out)}
    print(f"task={args.task} used={used}/{args.budget} out={out}")
    if args.task=="smoke":
        model=args.models[0] if args.models else "qwen2.5:7b-instruct-q4_K_M"
        s=samples[0]; prompt=prompt_main(s["texts"]["A"],s["fields"]); key=(s["match"],"A",model)
        items=[(key,prompt)]
    elif args.task=="retest":
        items=[]
        fixed={"match_0201","match_0065"}
        for model in args.models:
            for s in samples:
                if s["match"] in fixed:
                    items.append(((s["match"],"A",model),prompt_main(s["texts"]["A"],s["fields"])))
    elif args.task=="lina":
        items=[]
        for model in args.models:
            for cname,c in lina.items():
                items.append(((cname,"lina",model),prompt_lina(c["text"])))
    else:
        items=[]
        for model in args.models:
            for s in samples:
                for cond in args.conditions:
                    items.append(((s["match"],cond,model),prompt_main(s["texts"][cond],s["fields"])))
        if args.limit: items=items[:args.limit]
    for (match,cond,model),prompt in items:
        if (match,cond,model) in done: continue
        if used>=args.budget:
            print("BUDGET STOP",used); break
        service.config.MODEL_TAG=model
        info=service.model_info(model) or {}
        try:
            gen=service.generate(prompt,num_ctx=8192,num_predict=300)
            raw=gen["raw_output"]; err=None
        except Exception as exc:
            raw=""; gen={}; err=f"{type(exc).__name__}: {exc}"
        doc=extract(raw) if raw else None
        fields=doc.get("fields") if isinstance(doc,dict) else None
        row={"schema":"vett.pilot_next.run.v1","task":args.task,"match":match,"condition":cond,
             "model":model,"digest":info.get("digest"),"quant":info.get("quantization_level"),
             "prompt_sha256":sha(prompt),"prompt_chars":len(prompt),"raw_output":raw,
             "parsed":doc,"fields":fields,"parse_ok":isinstance(fields,dict),
             "error":err,"done_reason":gen.get("done_reason"),
             "eval_count":gen.get("eval_count"),"prompt_eval_count":gen.get("prompt_eval_count"),
             "wall_clock":gen.get("wall_clock"),"logged_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
        with open(out,"a",encoding="utf-8",newline="\n") as f:
            f.write(json.dumps(row,ensure_ascii=False)+"\n")
        used+=1; done.add((match,cond,model))
        print(match,cond,model.split(":")[0],"parse",row["parse_ok"],"eval",row["eval_count"],flush=True)
    print("done; used",used)

if __name__=="__main__": main()
