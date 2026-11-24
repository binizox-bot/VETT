import sys,json,hashlib,re,argparse
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V, v2
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
CORPUS=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches")
SAMPLES=WF.parent/"attribution_followup"/"samples.json"
DEC=v2.decode_config(300); DEC_JSON=json.dumps(DEC,sort_keys=True)
MODELS=list(V.MODELS)

def sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+",t) if s.strip()]

def load_events():
    return json.loads(SAMPLES.read_text(encoding="utf-8"))

def dismissal_sentence(txt, batter):
    parts=sentences(txt); first=batter.split()[0]
    cand=[s for s in parts if first in s]
    return cand[0] if cand else None

def build_texts(s):
    txt=(CORPUS/s["match"]/"commentary.txt").read_text(encoding="utf-8",errors="replace")
    ds=dismissal_sentence(txt,s["batter"])
    if not ds: return None
    ledger=("Pre-revision record: "+s["A"]+" "+str(s["Aw"])+" wickets for "+str(s["Ar"])+" runs; "+
            s["B"]+" "+str(s["Bw"])+" wickets for "+str(s["Br"])+" runs; the innings total was "+str(s["total"])+" wickets.")
    notices={"N0":"No review notice is provided. Use the pre-revision record as published.",
             "N1":"Match review: the original attribution to "+s["A"]+" is maintained. No change to either bowler's figures.",
             "N2":"Match review: the dismissal of "+s["batter"]+" is formally reassigned from "+s["A"]+" to "+s["B"]+". Update both bowlers' figures; runs and innings total do not change."}
    old={s["A"]+"_wickets":s["Aw"],s["A"]+"_runs":s["Ar"],s["B"]+"_wickets":s["Bw"],s["B"]+"_runs":s["Br"],"innings_total_wickets":s["total"]}
    new=dict(s["fields"])
    out={}
    for code,notice in notices.items():
        full=txt.rstrip()+"\n\n"+ledger+" "+notice
        window=ds+" "+ledger+" "+notice
        gold=new if code=="N2" else old
        out[code+"_F"]=("full",full,gold); out[code+"_W"]=("window",window,gold)
    return {"full":txt,"window":ds,"ledger":ledger,"notices":notices,"old":old,"new":new,"arms":out}

def prompt_for(match,innings,text,fields):
    intro=("You are a cricket scorer. Read the commentary and return the five requested fields. "
           "Return ONLY a JSON object mapping each field id to its integer value. No prose.")
    return (intro+"\n\nMatch: "+match+"\nInnings: "+str(innings)+"\nFields:\n"+"\n".join("- "+f for f in fields)+
            "\n\nCommentary:\n"+text+"\n\nJSON:")

def enqueue_root(s, batch_id, seq):
    fields=list(s["fields"].keys())
    inn=int(str(s["innings"]).replace("inn",""))
    built=build_texts(s)
    if not built: return None
    tasks=[]
    for cond,(mode,text,gold) in built["arms"].items():
        p=prompt_for(s["match"],inn,text,fields); psha=hashlib.sha256(p.encode("utf-8")).hexdigest()
        for m in MODELS:
            dg=V.model_digest(m); decj=DEC_JSON
            key=v2.key_v2(s["match"],inn,m,dg,decj,v2.INPUT_VERSION,v2.PROMPT_VERSION,v2.REPLICATE_ID,"night_core",psha)
            tasks.append({"task_key":key,"legacy_task_key":"","match":s["match"],"innings":inn,"model":m,"cond":cond,
                          "field_scope":"night_core","fields":fields,"prompt":p,"prompt_sha":psha,
                          "text_sha":hashlib.sha256(text.encode("utf-8")).hexdigest(),"num_predict":300,
                          "gold":gold,"model_digest":dg,"decode_json":decj,"input_version":v2.INPUT_VERSION,
                          "prompt_version":v2.PROMPT_VERSION,"replicate_id":v2.REPLICATE_ID})
    con=V.connect()
    if con.execute("SELECT 1 FROM batches WHERE batch_id=?",(batch_id,)).fetchone(): con.close(); return None
    design={"template":"X_night_core_event","hypothesis":"Same dismissal, 3 notices x 2 inputs x 3 models on one long published commentary with explicit ledger.",
            "rationale":"Core night experiment; match "+s["match"]+" event "+s["batter"],
            "positions":[{"match":s["match"],"innings":inn,"event":s["batter"],"source":"published_local_edit"}],
            "fields":fields,"conditions":sorted(built["arms"].keys()),"models":MODELS,
            "scoring":"exact integer per field; N2 gold=new, N0/N1 gold=old",
            "sources":["published commentary + appended pre-revision ledger + notice"],
            "cost":{"requests":len(tasks),"est_seconds":len(tasks)*30,"external_api":0},"created_at":V.now_iso(),
            "text_pressure":{"full_chars":len(built["full"]),"window_chars":len(built["window"]),
                             "event_count":len(sentences(built["full"])),"mentions_A":built["full"].count(s["A"]),
                             "mentions_B":built["full"].count(s["B"]),"mentions_batter":built["full"].count(s["batter"].split()[0])}}
    man={"batch_id":batch_id,"seq":seq,"template":design["template"],"created_at":V.now_iso(),"design":design,
         "schema_version":v2.SCHEMA_VERSION,"scoring_version":v2.SCORING_VERSION,
         "tasks":[{k:t[k] for k in ("task_key","legacy_task_key","match","innings","model","cond","field_scope","fields","prompt","prompt_sha","text_sha","num_predict","gold","model_digest","decode_json","input_version","prompt_version","replicate_id")} for t in tasks],"rejected":[]}
    mp=V.BATCHES/(batch_id+".json"); mp.write_text(json.dumps(man,ensure_ascii=False,indent=1),encoding="utf-8")
    msha=V.sha256_text(mp.read_text(encoding="utf-8"))
    con.execute("INSERT INTO batches(batch_id,seq,template,created_at,hypothesis,rationale,design_json,manifest_path,manifest_sha,status,parent_batch_id,trigger_json,cost_json,updated_at,scoring_version,manifest_version,template_version,plan_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (batch_id,seq,design["template"],V.now_iso(),design["hypothesis"],design["rationale"],json.dumps(design,ensure_ascii=False),str(mp),msha,"running",None,json.dumps({"rule_id":"N1","source":"night core"},ensure_ascii=False),json.dumps(design["cost"],ensure_ascii=False),V.now_iso(),v2.SCORING_VERSION,"v2","v2",0.0))
    for t in tasks:
        con.execute("INSERT INTO tasks(task_key,batch_id,match,innings,model,cond,field_scope,fields_json,prompt,prompt_sha,text_sha,num_predict,status,attempts,created_at,updated_at,model_digest,decode_json,input_version,prompt_version,replicate_id,legacy_task_key,identity_status,gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (t["task_key"],batch_id,t["match"],t["innings"],t["model"],t["cond"],t["field_scope"],json.dumps(t["fields"]),t["prompt"],t["prompt_sha"],t["text_sha"],t["num_predict"],"queued",0,V.now_iso(),V.now_iso(),t["model_digest"],t["decode_json"],t["input_version"],t["prompt_version"],t["replicate_id"],"","v2",json.dumps(t["gold"],ensure_ascii=False)))
    V.meta_set(con,"batch_seq",str(seq)); V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running"); con.commit()
    V.event("batch_frozen",{"batch_id":batch_id,"template":design["template"],"tasks":len(tasks),"note":"night core"},con); con.commit()
    con.close()
    ROOT.mkdir(parents=True,exist_ok=True)
    with open(ROOT/"plan.jsonl","a",encoding="utf-8",newline="\n") as f:
        f.write(json.dumps({"batch_id":batch_id,"match":s["match"],"event":s["batter"],"tasks":len(tasks),"design":design},ensure_ascii=False)+"\n")
    return {"batch_id":batch_id,"tasks":len(tasks),"full_chars":len(built["full"]),"window_chars":len(built["window"])}

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("mode"); ap.add_argument("--index",type=int,default=0)
    a=ap.parse_args(); ev=load_events()
    if a.mode=="first":
        r=enqueue_root(ev[0],"B213",213); print(json.dumps({"first":r},ensure_ascii=False))
    elif a.mode=="rest":
        out=[]
        con=V.connect(); seq=int(V.meta_get(con,"batch_seq","0") or 0); con.close()
        for s in ev[1:8]:
            seq+=1
            r=enqueue_root(s,"B"+str(seq).zfill(3),seq)
            if r: out.append(r)
        print(json.dumps({"rest":out},ensure_ascii=False))
    elif a.mode=="list":
        for i,s in enumerate(ev):
            b=build_texts(s); print(i,s["match"],s["batter"],"ok" if b else "NO_DISMISSAL",len(b["full"]) if b else 0)
