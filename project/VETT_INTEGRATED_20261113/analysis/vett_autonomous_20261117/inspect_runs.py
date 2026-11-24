import json, os, glob
base = r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_overnight_20261114"
for name in ["runs/expand.jsonl","runs/t_locator.jsonl","runs/u_audit.jsonl","runs/dplus_remove.jsonl"]:
    p = os.path.join(base, name)
    if not os.path.exists(p):
        print(name, "MISSING"); continue
    with open(p, encoding="utf-8") as f:
        line = f.readline()
    try:
        d = json.loads(line)
        print("ROW", name, "keys=", list(d.keys()))
        for k in ["match","innings","model","cond","condition","prompt","prompt_sha","text_sha","raw","raw_output","response","score","gold","correct"]:
            if k in d: print("   ", k, "=", str(d[k])[:350])
    except Exception as e:
        print(name, "ERR", e, line[:200])
p = r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\attribution_followup\samples.json"
obj = json.load(open(p, encoding="utf-8"))
s = obj[0]
print("TEXTS_KEYS", list(s["texts"].keys()))
for k, v in s["texts"].items(): print("  ", k, "len", len(v), "head", v[:200].replace("\n"," "))
print("EVIDENCE", json.dumps(s.get("evidence"), ensure_ascii=False)[:800])
print("CHECKS", json.dumps(s.get("checks"), ensure_ascii=False)[:400])
print("ALL_EVENTS")
for x in obj: print(" ", x["match"], x["innings"], x["batter"], x["A"], x["B"], x["Aw"], x["Ar"], x["Bw"], x["Br"], x["total"])
