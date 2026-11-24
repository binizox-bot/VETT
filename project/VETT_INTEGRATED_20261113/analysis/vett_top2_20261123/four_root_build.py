import sys,json,re
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V, v2
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_top2_20261123")
SEL=["match_0170","match_0096","match_0049","match_0180"]
DECJ=json.dumps(v2.decode_config(900),sort_keys=True)
def event(m):
    b=V.load_bundle(m); txt=b["text"]
    for ii,inn in enumerate(b["md"].innings,1):
        t2=sorted(inn.bowlers,key=lambda x:(-x.wickets,x.runs_conceded,x.name))[:2]
        if len(t2)<2: continue
        for bat in inn.batters:
            if bat.is_not_out: continue
            mm=re.search(r"\bb\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)",bat.dismissal or "")
            a=mm.group(1) if mm else None
            if not a or a not in [x.name for x in t2]: continue
            A=next(x for x in t2 if x.name==a); B=next(x for x in t2 if x.name!=a)
            if A.wickets<1 or bat.name.split()[0] not in txt: continue
            return b,ii,inn,bat,A,B
    return None
def ledger(s):
    return ("Pre-revision record: "+s["A"]+" "+str(s["Aw"])+" wickets for "+str(s["Ar"])+" runs; "+s["B"]+" "+str(s["Bw"])+" wickets for "+str(s["Br"])+" runs; the innings total was "+str(s["total"])+" wickets.")
def notices(s):
    return {"N1":"Match review: the original attribution to "+s["A"]+" is maintained. No change to either bowler's figures.",
            "N2":"Match review: the dismissal of "+s["batter"]+" is formally reassigned from "+s["A"]+" to "+s["B"]+". Update both bowlers' figures; runs and innings total do not change."}
def ft_prompt(match,inn,text,fields):
    return ("You are a cricket scorer. Fill every field from the commentary. Return ONLY JSON: {\"fields\": {<field_id>: <value>}}. Use integers for numeric fields and exact names for names. No prose.\n\n"
            "Match: "+match+"\nInnings: "+str(inn)+"\nFields:\n"+"\n".join("- "+f for f in fields)+"\n\nCommentary:\n"+text+"\n\nJSON:")
def top2_prompt(match,inn,text):
    return ("You are a cricket scorer. Read the commentary for the specified innings. List the two bowlers who should occupy the top two rows of this innings' bowling table, best first. "
            "Return ONLY a JSON object: {\"bowlers\": [\"Name One\", \"Name Two\"]}. No prose.\n\nMatch: "+match+"\nInnings: "+str(inn)+"\n\nCommentary:\n"+text+"\n\nJSON:")
evs=[]
for m in SEL:
    r=event(m)
    if not r: raise SystemExit("no event "+m)
    b,ii,inn,bat,A,B=r
    s={"match":m,"innings":ii,"batter":bat.name,"A":A.name,"B":B.name,"Aw":A.wickets,"Ar":A.runs_conceded,"Bw":B.wickets,"Br":B.runs_conceded,"total":inn.total_wickets}
    old=V.gold43(b["md"]); pre="inn"+str(ii)
    def setrow(g,nm,w):
        for n in (1,2,3):
            if g.get(pre+".bowl"+str(n)+"_name")==nm:
                g[pre+".bowl"+str(n)+"_wickets"]=w; return
        raise SystemExit("row missing "+m+" "+nm)
    new=dict(old); setrow(new,s["A"],s["Aw"]-1); setrow(new,s["B"],s["Bw"]+1)
    s["old43"]=old; s["new43"]=new; s["ev"]=("full",b["text"],ii,inn)
    evs.append(s)
tasks=[]; c=V.connect(); seq=258; NOW=V.now_iso()
for s in evs:
    b,ii,inn,bat,A,B=event(s["match"]); led=ledger(s); notices_=notices(s)
    for arm in ("N1","N2"):
        text=b["text"].rstrip()+"\n\n"+led+" "+notices_[arm]
        gold=s["old43"] if arm=="N1" else s["new43"]
        fields=list(gold.keys())
        p=ft_prompt(s["match"],ii,text,fields); psha=V.sha256_text(p)
        for m in V.MODELS:
            dg=V.model_digest(m)
            key=v2.key_v2(s["match"],ii,m,dg,DECJ,v2.INPUT_VERSION,v2.PROMPT_VERSION,v2.REPLICATE_ID,"ft_direct",psha)
            tasks.append({"task_key":key,"legacy_task_key":"","match":s["match"],"innings":ii,"model":m,"cond":arm+"_F_fulltable_direct","field_scope":"ft_direct","fields":fields,"prompt":p,"prompt_sha":psha,"text_sha":V.sha256_text(text),"num_predict":900,"gold":gold,"model_digest":dg,"decode_json":DECJ,"input_version":v2.INPUT_VERSION,"prompt_version":v2.PROMPT_VERSION,"replicate_id":v2.REPLICATE_ID})
        tp=top2_prompt(s["match"],ii,text); tsha=V.sha256_text(tp)
        g2=[s["A"],s["B"]] if arm=="N1" else ([s["B"],s["A"]] if s["Bw"]+1>s["Aw"]-1 else [s["A"],s["B"]])
        for m in V.MODELS:
            dg=V.model_digest(m)
            key=v2.key_v2(s["match"],ii,m,dg,DECJ,v2.INPUT_VERSION,v2.PROMPT_VERSION,v2.REPLICATE_ID,"top2_direct",tsha)
            tasks.append({"task_key":key,"legacy_task_key":"","match":s["match"],"innings":ii,"model":m,"cond":"T2_"+arm,"field_scope":"top2_direct","fields":["bowlers"],"prompt":tp,"prompt_sha":tsha,"text_sha":V.sha256_text(text),"num_predict":300,"gold":{"bowlers":g2},"model_digest":dg,"decode_json":DECJ,"input_version":v2.INPUT_VERSION,"prompt_version":v2.PROMPT_VERSION,"replicate_id":v2.REPLICATE_ID})
bid="B258"
design={"template":"X_ft_direct_4root","hypothesis":"Direct 43-field table and independent top-2 on 4 new roots.","rationale":"Expansion after phenomenon in >=2 roots; 4 roots x 2 notices x 3 models x 2 methods.","positions":[{"match":s["match"],"innings":s["innings"],"event":s["batter"]} for s in evs],"fields":list(evs[0]["old43"].keys()),"conditions":["N1","N2"],"models":list(V.MODELS),"scoring":"43 fields; target rows separately","sources":["published commentary + ledger + notice"],"cost":{"requests":len(tasks),"est_seconds":len(tasks)*40,"external_api":0},"created_at":NOW}
man={"batch_id":bid,"seq":seq,"template":design["template"],"created_at":NOW,"design":design,"schema_version":v2.SCHEMA_VERSION,"scoring_version":v2.SCORING_VERSION,"tasks":[{k:t[k] for k in ("task_key","legacy_task_key","match","innings","model","cond","field_scope","fields","prompt","prompt_sha","text_sha","num_predict","gold","model_digest","decode_json","input_version","prompt_version","replicate_id")} for t in tasks],"rejected":[]}
mp=V.BATCHES/(bid+".json"); mp.write_text(json.dumps(man,ensure_ascii=False,indent=1),encoding="utf-8"); msha=V.sha256_text(mp.read_text(encoding="utf-8"))
if c.execute("SELECT 1 FROM batches WHERE batch_id=?",(bid,)).fetchone(): raise SystemExit("exists")
c.execute("INSERT INTO batches(batch_id,seq,template,created_at,hypothesis,rationale,design_json,manifest_path,manifest_sha,status,parent_batch_id,trigger_json,cost_json,updated_at,scoring_version,manifest_version,template_version,plan_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(bid,seq,design["template"],NOW,design["hypothesis"],design["rationale"],json.dumps(design,ensure_ascii=False),str(mp),msha,"running",None,"{}",json.dumps(design["cost"],ensure_ascii=False),NOW,v2.SCORING_VERSION,"v2","v2",0.0))
for t in tasks:
    c.execute("INSERT INTO tasks(task_key,batch_id,match,innings,model,cond,field_scope,fields_json,prompt,prompt_sha,text_sha,num_predict,status,attempts,created_at,updated_at,model_digest,decode_json,input_version,prompt_version,replicate_id,legacy_task_key,identity_status,gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(t["task_key"],bid,t["match"],t["innings"],t["model"],t["cond"],t["field_scope"],json.dumps(t["fields"]),t["prompt"],t["prompt_sha"],t["text_sha"],t["num_predict"],"queued",0,NOW,NOW,t["model_digest"],t["decode_json"],t["input_version"],t["prompt_version"],t["replicate_id"],"","v2",json.dumps(t["gold"],ensure_ascii=False)))
V.meta_set(c,"batch_seq",str(seq)); V.meta_set(c,"exhausted","0"); V.meta_set(c,"state","running"); c.commit(); c.close()
print(json.dumps({"batch":bid,"tasks":len(tasks),"roots":[{"match":s["match"],"innings":s["innings"],"A":s["A"],"B":s["B"],"Aw":s["Aw"],"Bw":s["Bw"]} for s in evs]},ensure_ascii=False))
