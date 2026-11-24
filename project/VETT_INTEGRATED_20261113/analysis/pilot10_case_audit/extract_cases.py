import sys, json, difflib
from pathlib import Path
AUD = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"
sys.path.insert(0, str(AUD))
import audit_lib as A

pairs = [
 {"id":"A","match":"match_0108","variant":"revised_hard","kind":"attribution"},
 {"id":"B","match":"match_0035","variant":"revised_hard","kind":"attribution"},
 {"id":"C","match":"match_0167","variant":"missing","kind":"missing"},
 {"id":"D","match":"match_0091","variant":"missing","kind":"missing"},
 {"id":"E","match":"match_0092","variant":"shuffled","kind":"order","focus_model":"qwen2.5:7b-instruct-q4_K_M"},
 {"id":"F","match":"match_0203","variant":"shuffled","kind":"order","focus_model":"llama3.1:8b"},
]

def line_index():
    idx={}
    for p in sorted(A.RUNS.glob("*.jsonl")):
        for i,line in enumerate(p.read_text(encoding="utf-8").splitlines(),1):
            if not line.strip(): continue
            r=json.loads(line); idx[(r["match"],r["variant"],r["system"],r["model"])]=(str(p),i)
    return idx
LIDX=line_index()

out=[]
for spec in pairs:
    m=spec["match"]; v=spec["variant"]
    ctrl=A.text(m,"control"); var=A.text(m,v)
    a=A.sentences(ctrl); b=A.sentences(var)
    target=[]
    if v=="revised_hard":
        target=A.gold_doc(m,v)["changed_fields"]
    elif v=="missing":
        target=A.gold_doc(m,v).get("unknown_fields",[])
    else:
        model=spec["focus_model"]
        c=A.load_rows()[(m,"control","direct",model)]; s=A.load_rows()[(m,"shuffled","direct",model)]
        g=A.gold_map(m,"control")
        for f in A.core_fields(m):
            fid=f["field_id"]
            if A.correct(g[fid],c["pred"].get(fid)) and not A.correct(g[fid],s["pred"].get(fid)):
                target.append(fid)
        target=target[:8]
    # diffs
    sm=difflib.SequenceMatcher(None,a,b); ops=[]
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=="equal": continue
        ops.append({"op":tag,
            "control":[{"idx":i,"char":ctrl.find(a[i]),"text":a[i]} for i in range(i1,min(i2,i1+3))],
            "variant":[{"idx":j,"char":var.find(b[j]),"text":b[j]} for j in range(j1,min(j2,j1+3))]})
        if len(ops)>=4: break
    gold_c=A.gold_map(m,"control"); gold_v=A.gold_map(m,v)
    models={}
    for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b"]:
        models[model]={}
        for sysname in ["direct","closure"]:
            r=A.load_rows().get((m,v,sysname,model))
            if not r: continue
            models[model][sysname]={
                "loc":LIDX[(m,v,sysname,model)],
                "empty": not bool(r.get("pred")),
                "pred":{fid:r["pred"].get(fid) for fid in target},
                "present":{fid:(fid in r["pred"]) for fid in target},
                "correct":{fid:A.correct(gold_v.get(fid),r["pred"].get(fid)) for fid in target},
            }
    out.append({"id":spec["id"],"match":m,"variant":v,"kind":spec["kind"],
        "text_paths":{"control":str(A.PILOT/m/"variants"/"control"/"commentary.txt"),
                      "variant":str(A.PILOT/m/"variants"/v/"commentary.txt")},
        "gold_control":{fid:gold_c.get(fid) for fid in target},
        "gold_variant":{fid:gold_v.get(fid) for fid in target},
        "target_fields":target,"diffs":ops,"models":models,
        "n_sent_control":len(a),"n_sent_variant":len(b)})

(AUD/"case_data.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("wrote", AUD/"case_data.json")
for c in out:
    print("\n##",c["id"],c["match"],c["variant"],"targets",c["target_fields"])
    print("  gold ctrl",c["gold_control"])
    print("  gold var ",c["gold_variant"])
    for model,ss in c["models"].items():
        for sysname,r in ss.items():
            print("  ",model.split(":")[0],sysname,"empty",r["empty"],"pred",r["pred"],"correct",r["correct"],"loc",r["loc"])
