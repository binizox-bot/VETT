import json,collections
rows=[json.loads(l) for l in open(r"D:/Download/VETT_Cricket_Complete_Delivery_R19_20261017/VETT_INTEGRATED_20261113/analysis/codex_exchange/PILOT_B209Z/tasks.jsonl",encoding="utf-8")]
print("N",len(rows))
print("CONDS",dict(collections.Counter(r["cond"] for r in rows)))
print("MODELS",dict(collections.Counter(r["model"] for r in rows)))
for r in rows:
    if r["match"]=="match_0087" and r["model"].startswith("qwen"):
        print("GOLD87",r["gold"]); print("PROMPT87",r["prompt"][-260:].replace(chr(10)," | "))
for r in rows:
    if r["cond"]=="C_change_full" and r["model"].startswith("qwen"):
        print("GOLD03",r["gold"]); print("PROMPT03",r["prompt"][-420:].replace(chr(10)," | "))
