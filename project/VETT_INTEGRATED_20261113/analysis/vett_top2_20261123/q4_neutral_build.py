import sys,json
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF)); sys.path.insert(0,str(WF.parent/"vett_night_20261121"))
import vettlib as V, v2, night_build as NB
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_top2_20261123")
DECJ=json.dumps(v2.decode_config(300),sort_keys=True); MODELS=list(V.MODELS)
S=NB.load_events()
IMP="Update both bowlers' figures; runs and innings total do not change."
REP="Runs and innings total do not change."
diffs=[]; tasks=[]
for s in S:
    inn=int(str(s["innings"]).replace("inn","")); b=NB.build_texts(s)
    for arm in ("N2_F","N2_W"):
        text=b["arms"][arm][1]
        if text.count(IMP)!=1: raise SystemExit("imperative count "+s["match"]+" "+arm+" "+str(text.count(IMP)))
        i=text.index(IMP); neu=text[:i]+REP+text[i+len(IMP):]
        if neu.count("Update both bowlers")!=0: raise SystemExit("residual")
        diffs.append({"match":s["match"],"innings":inn,"arm":arm,"imperative":IMP,"replacement":REP,
                      "offset":i,"before_tail":text[max(0,i-60):i+len(IMP)+20],"after_tail":neu[max(0,i-60):i+len(REP)+20],
                      "before_sha":V.sha256_text(text),"after_sha":V.sha256_text(neu),"before_len":len(text),"after_len":len(neu)})
        fields=[str(s["A"])+"_wickets",str(s["B"])+"_wickets"]
        q=("You are a cricket scorer. Read the commentary and answer the question. Return ONLY a JSON object mapping each field id to its value. No prose.\n\n"
           "Match: "+s["match"]+"\nInnings: "+str(inn)+"\nQuestion: Give the pre-revision wicket counts of the two bowlers named in the record.\nFields:\n"+
           "\n".join("- "+f for f in fields)+"\n\nCommentary:\n"+neu+"\n\nJSON:")
        psha=V.sha256_text(q); gold={fields[0]:s["Aw"],fields[1]:s["Bw"]}
        for m in MODELS:
            dg=V.model_digest(m)
            key=v2.key_v2(s["match"],inn,m,dg,DECJ,v2.INPUT_VERSION,v2.PROMPT_VERSION,v2.REPLICATE_ID,"q4_neutral",psha)
            tasks.append({"task_key":key,"legacy_task_key":"","match":s["match"],"innings":inn,"model":m,"cond":"q4_old_neutral_"+arm[:2],"field_scope":"q4_neutral","fields":fields,"prompt":q,"prompt_sha":psha,"text_sha":V.sha256_text(neu),"num_predict":300,"gold":gold,"model_digest":dg,"decode_json":DECJ,"input_version":v2.INPUT_VERSION,"prompt_version":v2.PROMPT_VERSION,"replicate_id":v2.REPLICATE_ID})
(ROOT/"NEUTRAL_DIFFS.json").write_text(json.dumps(diffs,ensure_ascii=False,indent=1),encoding="utf-8")
L=["# q4 单因素中和文本差异（冻结）","","只改 N2 通知里的更新祈使句；保留改判事实与旧值问题。","","| 比赛 | 输入 | 字符位置 | 中和前 | 中和后 |","|---|---|---:|---|---|"]
for d in diffs: L.append("| "+d["match"]+" | "+d["arm"]+" | "+str(d["offset"])+" | "+d["imperative"]+" | "+d["replacement"]+" |")
L+=["","- 全文/窗口各 8 条，共 16 条差异；替换只删除“Update both bowlers' figures; ”，保留“runs and innings total do not change.”。",""]
(ROOT/"NEUTRAL_DIFFS.md").write_text("\n".join(L),encoding="utf-8")
c=V.connect(); bid="B256"; NOW=V.now_iso(); seq=256
design={"template":"X_q4_neutral","hypothesis":"Neutralize the update imperative in N2; old-value question unchanged.","rationale":"Single-factor q4 contrast on 8 audited N2 events.","positions":[{"match":s["match"],"innings":int(str(s["innings"]).replace("inn",""))} for s in S],"fields":["A_wickets","B_wickets"],"conditions":["q4_old_neutral_N2_F","q4_old_neutral_N2_W"],"models":MODELS,"scoring":"strict keys first; recoverable numeric values separately","sources":["published commentary + ledger + neutralized notice"],"cost":{"requests":len(tasks),"est_seconds":len(tasks)*20,"external_api":0},"created_at":NOW}
man={"batch_id":bid,"seq":seq,"template":design["template"],"created_at":NOW,"design":design,"schema_version":v2.SCHEMA_VERSION,"scoring_version":v2.SCORING_VERSION,"tasks":[{k:t[k] for k in ("task_key","legacy_task_key","match","innings","model","cond","field_scope","fields","prompt","prompt_sha","text_sha","num_predict","gold","model_digest","decode_json","input_version","prompt_version","replicate_id")} for t in tasks],"rejected":[]}
mp=V.BATCHES/(bid+".json"); mp.write_text(json.dumps(man,ensure_ascii=False,indent=1),encoding="utf-8"); msha=V.sha256_text(mp.read_text(encoding="utf-8"))
con=V.connect()
if con.execute("SELECT 1 FROM batches WHERE batch_id=?",(bid,)).fetchone(): print("EXISTS"); raise SystemExit
con.execute("INSERT INTO batches(batch_id,seq,template,created_at,hypothesis,rationale,design_json,manifest_path,manifest_sha,status,parent_batch_id,trigger_json,cost_json,updated_at,scoring_version,manifest_version,template_version,plan_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(bid,seq,design["template"],NOW,design["hypothesis"],design["rationale"],json.dumps(design,ensure_ascii=False),str(mp),msha,"running",None,"{}",json.dumps(design["cost"],ensure_ascii=False),NOW,v2.SCORING_VERSION,"v2","v2",0.0))
for t in tasks:
    con.execute("INSERT INTO tasks(task_key,batch_id,match,innings,model,cond,field_scope,fields_json,prompt,prompt_sha,text_sha,num_predict,status,attempts,created_at,updated_at,model_digest,decode_json,input_version,prompt_version,replicate_id,legacy_task_key,identity_status,gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(t["task_key"],bid,t["match"],t["innings"],t["model"],t["cond"],t["field_scope"],json.dumps(t["fields"]),t["prompt"],t["prompt_sha"],t["text_sha"],t["num_predict"],"queued",0,NOW,NOW,t["model_digest"],t["decode_json"],t["input_version"],t["prompt_version"],t["replicate_id"],"","v2",json.dumps(t["gold"],ensure_ascii=False)))
V.meta_set(con,"batch_seq",str(seq)); V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running"); con.commit(); con.close()
print(json.dumps({"batch":bid,"tasks":len(tasks),"diffs":len(diffs)}))
