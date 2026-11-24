import sys, json, re
from pathlib import Path
AUD = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"
sys.path.insert(0, str(AUD))
import audit_lib as A

def fig_norm(s):
    m=re.fullmatch(r"\s*(\d+)\s*(?:for|/|-)\s*(\d+)\s*", str(s).strip().lower())
    return (int(m.group(1)), int(m.group(2))) if m else None

def eq(g,p):
    fg, fp = fig_norm(g), fig_norm(p)
    if fg is not None and fp is not None:
        return fg == fp
    return A.correct(g,p)

def planned28(m):
    out=[]
    for f in A.core_fields(m):
        fid=f["field_id"]
        if ".bowl" in fid and fid.endswith(".wides"):
            continue
        out.append(f)
    return out

def metrics(mid, model, fieldset, variant, use_fig):
    c=A.load_rows()[(mid,"control","direct",model)]
    s=A.load_rows()[(mid,variant,"direct",model)]
    g=A.gold_map(mid,"control")
    eqf = eq if use_fig else A.correct
    ca=sum(1 for f in fieldset if eqf(g[f["field_id"]],c["pred"].get(f["field_id"])))/len(fieldset)
    sa=sum(1 for f in fieldset if eqf(g[f["field_id"]],s["pred"].get(f["field_id"])))/len(fieldset)
    cw=[f["field_id"] for f in fieldset if eqf(g[f["field_id"]],c["pred"].get(f["field_id"])) and not eqf(g[f["field_id"]],s["pred"].get(f["field_id"]))]
    return round(ca,4), round(sa,4), cw

rows=A.load_rows(); matches=sorted({k[0] for k in rows})
res={"schema":"vett.pilot10.shuffled_recompute.v1","by_model":{}}
for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b"]:
    entry={"actual32_old":[],"actual32_new":[],"planned28_old":[],"planned28_new":[],"cw_new":[]}
    for m in matches:
        f32=A.core_fields(m); f28=planned28(m)
        for label,fs,usefig in [("actual32_old",f32,False),("actual32_new",f32,True),
                                ("planned28_old",f28,False),("planned28_new",f28,True)]:
            ca,sa,cw=metrics(m,model,fs,"shuffled",usefig)
            entry[label].append({"match":m,"control":ca,"shuffled":sa,"cw":cw})
        # cross-innings for new scoring
        s=rows[(m,"shuffled","direct",model)]; c=rows[(m,"control","direct",model)]; g=A.gold_map(m,"control")
        gs=A.gold_map(m,"shuffled")
        for f in f32:
            fid=f["field_id"]
            if not (eq(g[fid],c["pred"].get(fid)) and not eq(g[fid],s["pred"].get(fid))): continue
            other=fid.replace("inn1.","inn2.") if "inn1." in fid else fid.replace("inn2.","inn1.")
            og=gs.get(other); oc=c["pred"].get(other)
            entry["cw_new"].append({"match":m,"field":fid,"control":c["pred"].get(fid),
                "shuffled":s["pred"].get(fid),"gold":g[fid],
                "other_field":other if other in gs else None,
                "other_gold":og,"other_control_pred":oc,
                "equals_other_gold": str(s["pred"].get(fid)).strip()==str(og).strip() if og is not None else None,
                "equals_other_control": str(s["pred"].get(fid)).strip()==str(oc).strip() if oc is not None else None})
    def mean(rs,key): return round(sum(r[key] for r in rs)/len(rs),4)
    entry["summary"]={k:{"control":mean(v,"control"),"shuffled":mean(v,"shuffled")} for k,v in entry.items() if isinstance(v,list) and k!="cw_new"}
    res["by_model"][model]=entry

(AUD/"shuffled_recompute.json").write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for model,e in res["by_model"].items():
    print("\n##",model)
    for k,v in e["summary"].items(): print("  ",k,v)
    print("  C2W new:",[(x["field"],x["other_field"],x["equals_other_gold"],x["equals_other_control"]) for x in e["cw_new"][:10]])

# posthoc closure on direct outputs
post={"schema":"vett.pilot10.posthoc_closure.v1","by_model":{}}
for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b"]:
    entry={}
    for variant in ["control","shuffled","revised","revised_hard","missing","conflict","distractor","revision_inline"]:
        num=den=0
        for m in matches:
            r=rows.get((m,variant,"direct",model))
            if not r: continue
            g=A.gold_map(m,variant); f32=A.core_fields(m)
            p=A.E.propagate(dict(r["pred"]), f32)
            num+=sum(1 for f in f32 if A.correct(g[f["field_id"]],p.get(f["field_id"]))); den+=len(f32)
        entry[variant]=round(num/den,4) if den else None
    post["by_model"][model]=entry
(AUD/"posthoc_closure.json").write_text(json.dumps(post,indent=2)+"\n",encoding="utf-8")
print("\nposthoc closure (direct + propagate):")
for k,v in post["by_model"].items(): print(" ",k,v)
