import sys,json,hashlib,re,argparse
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V, v2
import night_build as NB
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
CORPUS=NB.CORPUS; MODELS=list(V.MODELS)

def next_ids(n):
    con=V.connect(); seq=int(V.meta_get(con,"batch_seq","212") or 212); con.close()
    return [(seq+i,"B"+str(seq+i).zfill(3)) for i in range(1,n+1)]

def enqueue(tasks, template, hypothesis, rationale, positions, fields, conds, sources, cost_extra=None, num_predict=300):
    if not tasks: return None
    ids=next_ids(1); seq,bid=ids[0]
    con=V.connect()
    design={"template":template,"hypothesis":hypothesis,"rationale":rationale,"positions":positions,
            "fields":fields,"conditions":conds,"models":MODELS,"scoring":"exact integer per field",
            "sources":sources,"cost":{"requests":len(tasks),"est_seconds":len(tasks)*40,"external_api":0},"created_at":V.now_iso()}
    man={"batch_id":bid,"seq":seq,"template":template,"created_at":V.now_iso(),"design":design,
         "schema_version":v2.SCHEMA_VERSION,"scoring_version":v2.SCORING_VERSION,
         "tasks":[{k:t[k] for k in ("task_key","legacy_task_key","match","innings","model","cond","field_scope","fields","prompt","prompt_sha","text_sha","num_predict","gold","model_digest","decode_json","input_version","prompt_version","replicate_id")} for t in tasks],"rejected":[]}
    mp=V.BATCHES/(bid+".json"); mp.write_text(json.dumps(man,ensure_ascii=False,indent=1),encoding="utf-8")
    msha=V.sha256_text(mp.read_text(encoding="utf-8"))
    con.execute("INSERT INTO batches(batch_id,seq,template,created_at,hypothesis,rationale,design_json,manifest_path,manifest_sha,status,parent_batch_id,trigger_json,cost_json,updated_at,scoring_version,manifest_version,template_version,plan_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (bid,seq,template,V.now_iso(),hypothesis,rationale,json.dumps(design,ensure_ascii=False),str(mp),msha,"running",None,json.dumps({"rule_id":"N2","source":"night extend"},ensure_ascii=False),json.dumps(design["cost"],ensure_ascii=False),V.now_iso(),v2.SCORING_VERSION,"v2","v2",0.0))
    for t in tasks:
        con.execute("INSERT INTO tasks(task_key,batch_id,match,innings,model,cond,field_scope,fields_json,prompt,prompt_sha,text_sha,num_predict,status,attempts,created_at,updated_at,model_digest,decode_json,input_version,prompt_version,replicate_id,legacy_task_key,identity_status,gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (t["task_key"],bid,t["match"],t["innings"],t["model"],t["cond"],t["field_scope"],json.dumps(t["fields"]),t["prompt"],t["prompt_sha"],t["text_sha"],t["num_predict"],"queued",0,V.now_iso(),V.now_iso(),t["model_digest"],t["decode_json"],t["input_version"],t["prompt_version"],t["replicate_id"],"","v2",json.dumps(t["gold"],ensure_ascii=False)))
    V.meta_set(con,"batch_seq",str(seq)); V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running"); con.commit()
    V.event("batch_frozen",{"batch_id":bid,"template":template,"tasks":len(tasks),"note":"night extend"},con); con.commit(); con.close()
    return {"batch_id":bid,"tasks":len(tasks)}

def make(mean_scope, match, innings, cond, text, fields, gold, num_predict):
    p=V.build_prompt(match,innings,cond,text,fields); psha=V.sha256_text(p)
    out=[]
    decj=json.dumps(v2.decode_config(num_predict),sort_keys=True)
    for m in MODELS:
        dg=V.model_digest(m)
        key=v2.key_v2(match,innings,m,dg,decj,v2.INPUT_VERSION,v2.PROMPT_VERSION,v2.REPLICATE_ID,mean_scope,psha)
        out.append({"task_key":key,"legacy_task_key":"","match":match,"innings":innings,"model":m,"cond":cond,"field_scope":mean_scope,"fields":fields,"prompt":p,"prompt_sha":psha,"text_sha":V.sha256_text(text),"num_predict":num_predict,"gold":gold,"model_digest":dg,"decode_json":decj,"input_version":v2.INPUT_VERSION,"prompt_version":v2.PROMPT_VERSION,"replicate_id":v2.REPLICATE_ID})
    return out

def fulltable():
    ev=NB.load_events(); out=[]
    for s in ev:
        b=V.load_bundle(s["match"]); g=V.gold43(b["md"]); inn=int(str(s["innings"]).replace("inn",""))
        a=s["A"]; bb=s["B"]
        rows=[]
        for n in (1,2,3):
            name=g.get("inn"+str(inn)+".bowl"+str(n)+"_name")
            if name in (a,bb): rows.append((n,name))
        if len({r[1] for r in rows})<2:
            out.append({"match":s["match"],"eligible":False,"rows":rows}); continue
        adj=dict(g)
        for n,name in rows:
            k="inn"+str(inn)+".bowl"+str(n)+"_wickets"
            adj[k]=g[k]+(1 if name==bb else -1)
        built=NB.build_texts(s)
        tasks=[]
        for code in ("N1","N2"):
            text=built["arms"][code+"_F"][1]
            tasks += make("night_fulltable",s["match"],inn,code+"_F_fulltable",text,list(V.FULL43),adj,900)
        r=enqueue(tasks,"X_night_fulltable","Whole-table backfill of the same event under maintain and reassign.",
                  "Same full text as core; 43-field table; bowling wickets adjusted for A/B, total unchanged.",
                  [{"match":s["match"],"innings":inn,"event":s["batter"],"rows":rows}],list(V.FULL43),["N1_F_fulltable","N2_F_fulltable"],
                  ["published commentary + ledger + notice"],num_predict=900)
        out.append({"match":s["match"],"eligible":True,"rows":rows,"batch":r})
    print(json.dumps({"fulltable":out},ensure_ascii=False))

def fallback(n_roots):
    st=ROOT/"fallback_state.json"; state=json.loads(st.read_text(encoding="utf-8")) if st.exists() else {"cursor":1,"done":[]}
    core={s["match"] for s in NB.load_events()}
    roots=["match_"+str(i).zfill(4) for i in range(1,221) if not (121<=i<=160) and "match_"+str(i).zfill(4) not in core]
    start=state["cursor"]; used=0; tasks=[]; picked=[]
    for idx in range(start,len(roots)):
        m=roots[idx]
        try: b=V.load_bundle(m)
        except Exception: continue
        units=[]
        for inn in (1,2):
            g=V.gold_target(b["md"],inn)
            if not g: continue
            pat=re.compile(r"([A-Z][A-Za-z ]+?) closed on "+str(g.get("inn"+str(inn)+".total_runs"))+r" for "+str(g.get("inn"+str(inn)+".total_wickets")))
            mt=pat.search(b["text"])
            if not mt: continue
            sent=[x for x in re.split(r"(?<=[.!?])\s+",b["text"]) if "closed on "+str(g.get("inn"+str(inn)+".total_runs"))+" for "+str(g.get("inn"+str(inn)+".total_wickets")) in x]
            if not sent: continue
            units.append((inn,b["text"],sent[0],g))
        if not units: continue
        for inn,full,win,g in units[:1]:
            fields=["inn"+str(inn)+".total_runs","inn"+str(inn)+".total_wickets"]
            tasks += make("night_fallback",m,inn,"F_full",full,fields,g,300)
            tasks += make("night_fallback",m,inn,"F_window",win,fields,g,300)
        picked.append(m); used+=1; state["cursor"]=idx+1
        if used>=n_roots: break
    con=V.connect(); new=[]
    for t in tasks:
        if con.execute("SELECT 1 FROM tasks WHERE task_key=?",(t["task_key"],)).fetchone(): continue
        if con.execute("SELECT 1 FROM results WHERE task_key=?",(t["task_key"],)).fetchone(): continue
        new.append(t)
    con.close(); tasks=new
    r=enqueue(tasks,"X_night_fallback","Ordinary-root full vs terminal-window on the published commentary.",
              "Fallback coverage: non-held-out ordinary roots, one innings each, full vs same-source terminal window.",
              [{"match":m} for m in picked],[],"F_full,F_window",["published commentary"])
    state["done"]=state.get("done",[])+picked
    st.write_text(json.dumps(state,ensure_ascii=False,indent=1),encoding="utf-8")
    print(json.dumps({"fallback":{"roots":picked,"batch":r,"cursor":state["cursor"]}},ensure_ascii=False))


def fulltable_ordinary(n_roots):
    st=ROOT/"fulltable_state.json"; state=json.loads(st.read_text(encoding="utf-8")) if st.exists() else {"cursor":1,"done":[]}
    core={s["match"] for s in NB.load_events()}
    roots=["match_"+str(i).zfill(4) for i in range(1,221) if not (121<=i<=160) and "match_"+str(i).zfill(4) not in core]
    tasks=[]; picked=[]; idx=state["cursor"]
    while idx<len(roots) and len(picked)<n_roots:
        m=roots[idx]; idx+=1
        try: b=V.load_bundle(m); g=V.gold43(b["md"])
        except Exception: continue
        if not g: continue
        t=make("night_ft_ordinary",m,1,"O_fulltable",b["text"],list(V.FULL43),g,900)
        con=V.connect(); new=[x for x in t if not con.execute("SELECT 1 FROM tasks WHERE task_key=?",(x["task_key"],)).fetchone() and not con.execute("SELECT 1 FROM results WHERE task_key=?",(x["task_key"],)).fetchone()]; con.close()
        if not new: continue
        tasks+=new; picked.append(m); state["cursor"]=idx
        if len(picked)>=n_roots: break
    r=enqueue(tasks,"X_night_ft_ordinary","Ordinary-root 43-field full-table coverage.",
              "Fallback coverage after core/full-table branches: one whole-table task per root, 3 models.",
              [{"match":m} for m in picked],list(V.FULL43),["O_fulltable"],["published commentary"],num_predict=900)
    state["done"]=state.get("done",[])+picked; st.write_text(json.dumps(state,ensure_ascii=False,indent=1),encoding="utf-8")
    print(json.dumps({"ft_ordinary":{"roots":picked,"batch":r,"cursor":state["cursor"]}},ensure_ascii=False))

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("mode"); ap.add_argument("--n",type=int,default=10); a=ap.parse_args()
    if a.mode=="fulltable": fulltable()
    elif a.mode=="fallback": fallback(a.n)
    elif a.mode=="ft_ordinary": fulltable_ordinary(a.n)
