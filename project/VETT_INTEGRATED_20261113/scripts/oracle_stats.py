import json, sys
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT = ROOT/"VETT_INTEGRATED_20261113"
sys.path.insert(0, str(INT/"scripts"))
import eval_pilot10 as E
R = INT/"runs"/"eval_pilot10"
for p in sorted(R.glob("*.jsonl")):
    rows=[json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    ctrl={r["match"]:r for r in rows if r["variant"]=="control" and r["system"]=="direct"}
    orc={r["match"]:r for r in rows if r["variant"]=="oracle" and r["system"]=="direct"}
    pairs=[(m,ctrl[m],orc[m]) for m in ctrl if m in orc]
    if not pairs: continue
    def acc(r,m,v):
        g=E.expected_gold(m,v); fs=E.load_fields(m)
        return sum(1 for f in fs if E.value_match(g[f["field_id"]], r["pred"].get(f["field_id"])))/len(fs)
    c=sum(acc(r,m,"control") for m,r,_ in pairs)/len(pairs)
    o=sum(acc(r,m,"control") for m,_,r in pairs)/len(pairs)
    print(p.stem, "n=",len(pairs), "control=%.3f"%c, "oracle=%.3f"%o, "delta=%+.3f"%(o-c))
