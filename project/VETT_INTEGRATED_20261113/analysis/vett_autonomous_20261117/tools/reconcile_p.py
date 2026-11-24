
import sqlite3, json, sys
sys.path.insert(0,".")
import planner
c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row
b=json.loads(c.execute("SELECT design_json FROM batches WHERE batch_id='B197'").fetchone()["design_json"])
print("B197", b.get("positions"), "cursor", b.get("probe_next_cursor"))
rows=c.execute("SELECT r.match,r.innings,r.model,t.field_scope,b.template FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE r.match IN ('match_0219','match_0220')").fetchall()
print("RESULTS_LAST",len(rows))
keys={}
for r in rows:
    if r["template"]=="P_field_sweep": keys.setdefault((r["match"],r["innings"],r["model"]),set()).add(r["field_scope"])
print("LAST_P_KEYS",len(keys), {k:len(v) for k,v in list(keys.items())[:6]})
allp=c.execute("SELECT r.match,r.innings,r.model FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='P_field_sweep'").fetchall()
uk=set((r["match"],r["innings"],r["model"]) for r in allp)
units=set(planner.sweep_units())
covered=set((m,i) for (m,i,_) in uk)
print("UNITS",len(units),"COVERED_UNITS",len(covered),"MISSING_UNITS",sorted(units-covered)[:10],"EXTRA",len(covered-units))
