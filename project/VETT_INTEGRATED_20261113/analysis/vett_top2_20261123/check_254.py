import sys,json
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
rows=[dict(r) for r in c.execute("SELECT r.model,r.cond,r.parsed_json,r.raw_output,r.correct,t.gold_json FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id='B254' ORDER BY r.cond,r.model")]
for r in rows: print(r["cond"],r["model"].split(":")[0],r["parsed_json"],"GOLD",r["gold_json"],"RAW",r["raw_output"][:80].replace(chr(10)," "))
print("N",len(rows))
c.close()
