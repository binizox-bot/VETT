import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"))
import audit_lib as A
rows=A.load_rows()
pairs=[("match_0108","revised_hard"),("match_0035","revised_hard"),("match_0167","missing"),("match_0091","missing"),("match_0092","shuffled"),("match_0203","shuffled")]
for m,v in pairs:
    print("\n##",m,v)
    d=A.gold_doc(m,v)
    target=d.get("changed_fields") or d.get("unknown_fields") or []
    if v=="shuffled":
        model="qwen2.5:7b-instruct-q4_K_M" if m=="match_0092" else "llama3.1:8b"
        c=rows[(m,"control","direct",model)]; s=rows[(m,"shuffled","direct",model)]
        g=A.gold_map(m,"control")
        cw=[f["field_id"] for f in A.core_fields(m) if A.correct(g[f["field_id"]],c["pred"].get(f["field_id"])) and not A.correct(g[f["field_id"]],s["pred"].get(f["field_id"]))]
        stable=[f["field_id"] for f in A.core_fields(m) if A.correct(g[f["field_id"]],c["pred"].get(f["field_id"])) and A.correct(g[f["field_id"]],s["pred"].get(f["field_id"]))]
        print(" focus",model.split(":")[0],"C2W",cw)
        print(" stable",stable[:8])
        for fid in (cw[:6] if m=="match_0092" else stable[:4]):
            print("  ",fid,"ctrl",c["pred"].get(fid),"shuf",s["pred"].get(fid),"gold",g[fid])
    else:
        for fid in target:
            print("  ",fid,"ctrl_gold",A.gold_map(m,"control").get(fid),"var_gold",A.gold_map(m,v).get(fid))
    if v=="revised_hard":
        for fid in ["inn1.total_wickets","inn2.total_wickets"]:
            print("  total",fid,"ctrl",A.gold_map(m,"control").get(fid),"var",A.gold_map(m,v).get(fid),
                  "qwen",rows[(m,v,"direct","qwen2.5:7b-instruct-q4_K_M")]["pred"].get(fid),
                  "llama",rows[(m,v,"direct","llama3.1:8b")]["pred"].get(fid))
    if v in ("missing","shuffled"):
        for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b"]:
            r=rows.get((m,"control","direct",model))
            if r and target:
                print("  control",model.split(":")[0],{fid:r["pred"].get(fid) for fid in target})
