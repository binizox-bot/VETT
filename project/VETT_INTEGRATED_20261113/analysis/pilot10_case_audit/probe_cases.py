import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"))
import audit_lib as A

rows = A.load_rows()
print("rows:", len(rows))
m0 = "match_0090"
cf = A.core_fields(m0)
print("core count:", len(cf))
print("core ids:", [f["field_id"] for f in cf])

# revised_hard candidates
print("\n== revised_hard ==")
for (m,v,s,model), r in sorted(rows.items()):
    if v != "revised_hard": continue
    d = A.gold_doc(m, v); ch = d["changed_fields"]; g = A.gold_map(m, v)
    flags = [(fid, A.correct(g[fid], r["pred"].get(fid)), r["pred"].get(fid), g[fid]) for fid in ch]
    print(m, s, model.split(":")[0], "changed:", ch, "->", flags)

# missing candidates
print("\n== missing ==")
for (m,v,s,model), r in sorted(rows.items()):
    if v != "missing" or s != "direct": continue
    d = A.gold_doc(m, v); unk = d.get("unknown_fields", [])
    preds = [(fid, r["pred"].get(fid), "MISSING" if fid not in r["pred"] else ("UNKNOWN" if str(r["pred"].get(fid)).upper()=="UNKNOWN" else "VALUE")) for fid in unk]
    print(m, model.split(":")[0], "unknown:", unk, "pred:", preds)

# shuffled transitions for direct
print("\n== shuffled transitions (direct) ==")
for m in sorted({k[0] for k in rows}):
    for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b"]:
        c = rows.get((m,"control","direct",model)); s = rows.get((m,"shuffled","direct",model))
        if not c or not s: continue
        g = A.gold_map(m,"control"); cf = A.core_fields(m)
        cw=[]; wc=[]
        for f in cf:
            fid=f["field_id"]; gc=A.correct(g[fid],c["pred"].get(fid)); gs=A.correct(g[fid],s["pred"].get(fid))
            if gc and not gs: cw.append(fid)
            if (not gc) and gs: wc.append(fid)
        print(m, model.split(":")[0], "C->W", len(cw), cw[:4], "| W->C", len(wc), wc[:3])
