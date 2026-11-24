import sys,json
sys.path.insert(0,r"D:/Download/VETT_Cricket_Complete_Delivery_R19_20261017/VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117")
import vettlib as V
c=V.connect()
reuse=json.loads((V.BATCHES/"B209Z_REUSE.json").read_text(encoding="utf-8"))
nc=nt=0
for r in reuse:
    t=c.execute("SELECT gold_json FROM tasks WHERE task_key=?", (r["task_key"],)).fetchone()
    q=c.execute("SELECT parsed_json,raw_output FROM results WHERE task_key=?", (r["task_key"],)).fetchone()
    gold=json.loads(t[0]); pred=json.loads(q[0] or "{}")
    okn=sum(1 for k,g in gold.items() if isinstance(pred.get(k),(int,float)) and int(pred[k])==int(g))
    nc+=okn; nt+=len(gold)
    print(r["cond"],r["model"],"gold",gold,"pred",pred,"ok",okn,"/",len(gold))
print("REUSED_CELLS",nc,nt,"COMBINED",77+nc,96+nt)
c.close()
