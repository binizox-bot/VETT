import sys,json
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
rows=c.execute("SELECT r.match,r.model,r.cond,r.correct,r.score_json,t.gold_json,r.parsed_json,r.raw_output FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_field' AND r.cond LIKE 'N2_F_%_wickets' LIMIT 5").fetchall()
for x in rows: print(x[0],x[1].split(":")[0],x[2],x[3],x[4],x[5],x[6],"RAW",x[7][:80].replace(chr(10)," "))
c.close()
