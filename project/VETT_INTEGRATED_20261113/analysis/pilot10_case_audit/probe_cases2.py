import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"))
import audit_lib as A
rows = A.load_rows()

print("== MISSING (direct) ==")
for (m,v,s,model), r in sorted(rows.items()):
    if v != "missing" or s != "direct": continue
    d = A.gold_doc(m, v); unk = d.get("unknown_fields", [])
    preds = []
    for fid in unk:
        p = r["pred"].get(fid)
        state = "MISSING" if fid not in r["pred"] else ("UNKNOWN" if str(p).upper()=="UNKNOWN" else "VALUE")
        preds.append((fid, p, state))
    print(m, model.split(":")[0], "deleted_len", len(d["edit"].get("deleted","")), "unknown", unk, "pred", preds)

print("\n== SHUFFLED (direct) transitions ==")
for m in sorted({k[0] for k in rows}):
    for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b"]:
        c = rows.get((m,"control","direct",model)); s = rows.get((m,"shuffled","direct",model))
        if not c or not s: continue
        g = A.gold_map(m,"control"); cf = A.core_fields(m)
        cw=[]; wc=[]; same=0
        for f in cf:
            fid=f["field_id"]; gc=A.correct(g[fid],c["pred"].get(fid)); gs=A.correct(g[fid],s["pred"].get(fid))
            if gc and not gs: cw.append(fid)
            elif (not gc) and gs: wc.append(fid)
            elif gc and gs: same+=1
        print(m, model.split(":")[0], "C2W", len(cw), cw, "| W2C", len(wc), wc, "| stable_correct", same)
