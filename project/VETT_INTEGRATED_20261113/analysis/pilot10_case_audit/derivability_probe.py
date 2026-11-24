import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot10_case_audit"))
import audit_lib as A

for m in ["match_0167","match_0091"]:
    print("\n### MISSING",m)
    d=A.gold_doc(m,"missing"); print("deleted:",d["edit"]["deleted"])
    txt=A.text(m,"missing")
    for s in A.sentences(txt):
        low=s.lower()
        if any(k in low for k in ["bye","wide","no-ball","no ball","extra","batting","reached","total","innings closed"]):
            print("  REM:",s[:300])
    f={x["field_id"]:x["value"] for x in A.fields(m)}
    for k in ["inn1.total_runs","inn1.batting_runs_sum","inn1.total_extras","inn1.byes","inn1.leg_byes","inn1.no_balls","inn1.wides"]:
        print("  gold",k,f.get(k))

for m in ["match_0108","match_0035"]:
    print("\n### HARD",m)
    d=A.gold_doc(m,"revised_hard"); print("edit:",d["edit"])
    var=A.text(m,"revised_hard")
    before=d["edit"].get("before",{})
    for label,name in [("top",before.get("top")),("src",before.get("src"))]:
        if name: print("  ",label,name,"in text:", name in var)
    f={x["field_id"]:x["value"] for x in A.fields(m)}
    print("  total_wickets:", {k:v for k,v in f.items() if k.endswith("total_wickets")})
    for s in A.sentences(var):
        low=s.lower()
        if any(k in low for k in ["struck","fell","wicket","bowling effort","pressure on"]):
            print("  NARR:", s[:240])
