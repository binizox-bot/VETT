import sys,json,re
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF)); sys.path.insert(0,str(WF.parent/"vett_night_20261121"))
import vettlib as V, v2, night_build as NB
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_top2_20261123")
c=V.connect(); design=json.loads(c.execute("SELECT design_json FROM batches WHERE batch_id='B258'").fetchone()[0])
DECJ=json.dumps(v2.decode_config(900),sort_keys=True)
tasks=[]; NOW=V.now_iso()
for p in design["positions"]:
    b=V.load_bundle(p["match"]); ii=p["innings"]
    inn=b["md"].innings[ii-1]; bat=next(x for x in inn.batters if x.name==p["event"])
    mm=re.search(r"\bb\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)",bat.dismissal or ""); A=mm.group(1)
    t2=sorted(inn.bowlers,key=lambda x:(-x.wickets,x.runs_conceded,x.name)); B=next(x for x in t2 if x.name!=A)
    s={"match":p["match"],"innings":ii,"batter":bat.name,"A":A,"B":B.name,"Aw":next(x.wickets for x in t2 if x.name==A),"Ar":next(x.runs_conceded for x in t2 if x.name==A),"Bw":B.wickets,"Br":B.runs_conceded,"total":inn.total_wickets}
    led=("Pre-revision record: "+s["A"]+" "+str(s["Aw"])+" wickets for "+str(s["Ar"])+" runs; "+s["B"]+" "+str(s["Bw"])+" wickets for "+str(s["Br"])+" runs; the innings total was "+str(s["total"])+" wickets.")
    notices={"N1":"Match review: the original attribution to "+s["A"]+" is maintained. No change to either bowler's figures.","N2":"Match review: the dismissal of "+s["batter"]+" is formally reassigned from "+s["A"]+" to "+s["B"]+". Update both bowlers' figures; runs and innings total do not change."}
    old=V.gold43(b["md"]); pre="inn"+str(ii)
    def setrow(g,nm,w):
        for n in (1,2,3):
            if g.get(pre+".bowl"+str(n)+"_name")==nm: g[pre+".bowl"+str(n)+"_wickets"]=w; return
    new=dict(old); setrow(new,s["A"],s["Aw"]-1); setrow(new,s["B"],s["Bw"]+1)
    for arm in ("N1","N2"):
        text=b["text"].rstrip()+"\n\n"+led+" "+notices[arm]; gold=old if arm=="N1" else new; fields=list(gold.keys())
        for m in V.MODELS:
            row=c.execute("SELECT parsed_json FROM results WHERE batch_id='B258' AND match=? AND model=? AND cond=? ORDER BY rowid DESC LIMIT 1",(s["match"],m,"T2_"+arm)).fetchone()
            tb=json.loads(row[0] or "{}").get("bowlers") if row else None
            if not tb: continue
            p0=("You are a cricket scorer. Fill every field from the commentary. Return ONLY JSON: {\"fields\": {<field_id>: <value>}}. Use integers for numeric fields and exact names for names. No prose.\n\n"
                "Match: "+s["match"]+"\nInnings: "+str(ii)+"\nFields:\n"+"\n".join("- "+f for f in fields)+
                "\n\nReference top-2 bowlers to use in the bowling rows: "+", ".join(tb)+".\n\nCommentary:\n"+text+"\n\nJSON:")
            psha=V.sha256_text(p0); dg=V.model_digest(m)
            key=v2.key_v2(s["match"],ii,m,dg,DECJ,v2.INPUT_VERSION,v2.PROMPT_VERSION,v2.REPLICATE_ID,"ft_hint4",psha)
            tasks.append({"task_key":key,"legacy_task_key":"","match":s["match"],"innings":ii,"model":m,"cond":arm+"_F_fulltable_hint","field_scope":"ft_hint4","fields":fields,"prompt":p0,"prompt_sha":psha,"text_sha":V.sha256_text(text),"num_predict":900,"gold":gold,"model_digest":dg,"decode_json":DECJ,"input_version":v2.INPUT_VERSION,"prompt_version":v2.PROMPT_VERSION,"replicate_id":v2.REPLICATE_ID})
bid="B259"; seq=259
design2={"template":"X_ft_hint_4root","hypothesis":"Each model's own independent top-2 list as a table hint.","rationale":"4 roots x2 notices x3 models.","positions":design["positions"],"fields":list(old.keys()),"conditions":["N1","N2"],"models":list(V.MODELS),"scoring":"43 fields; target rows","sources":["published commentary + ledger + notice"],"cost":{"requests":len(tasks),"est_seconds":len(tasks)*40,"external_api":0},"created_at":NOW}
man={"batch_id":bid,"seq":seq,"template":design2["template"],"created_at":NOW,"design":design2,"schema_version":v2.SCHEMA_VERSION,"scoring_version":v2.SCORING_VERSION,"tasks":[{k:t[k] for k in ("task_key","legacy_task_key","match","innings","model","cond","field_scope","fields","prompt","prompt_sha","text_sha","num_predict","gold","model_digest","decode_json","input_version","prompt_version","replicate_id")} for t in tasks],"rejected":[]}
mp=V.BATCHES/(bid+".json"); mp.write_text(json.dumps(man,ensure_ascii=False,indent=1),encoding="utf-8"); msha=V.sha256_text(mp.read_text(encoding="utf-8"))
if c.execute("SELECT 1 FROM batches WHERE batch_id=?",(bid,)).fetchone(): raise SystemExit("exists")
c.execute("INSERT INTO batches(batch_id,seq,template,created_at,hypothesis,rationale,design_json,manifest_path,manifest_sha,status,parent_batch_id,trigger_json,cost_json,updated_at,scoring_version,manifest_version,template_version,plan_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(bid,seq,design2["template"],NOW,design2["hypothesis"],design2["rationale"],json.dumps(design2,ensure_ascii=False),str(mp),msha,"running",None,"{}",json.dumps(design2["cost"],ensure_ascii=False),NOW,v2.SCORING_VERSION,"v2","v2",0.0))
for t in tasks:
    c.execute("INSERT INTO tasks(task_key,batch_id,match,innings,model,cond,field_scope,fields_json,prompt,prompt_sha,text_sha,num_predict,status,attempts,created_at,updated_at,model_digest,decode_json,input_version,prompt_version,replicate_id,legacy_task_key,identity_status,gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(t["task_key"],bid,t["match"],t["innings"],t["model"],t["cond"],t["field_scope"],json.dumps(t["fields"]),t["prompt"],t["prompt_sha"],t["text_sha"],t["num_predict"],"queued",0,NOW,NOW,t["model_digest"],t["decode_json"],t["input_version"],t["prompt_version"],t["replicate_id"],"","v2",json.dumps(t["gold"],ensure_ascii=False)))
V.meta_set(c,"batch_seq",str(seq)); V.meta_set(c,"exhausted","0"); V.meta_set(c,"state","running"); c.commit(); c.close()
print(json.dumps({"batch":bid,"tasks":len(tasks)}))
