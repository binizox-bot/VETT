
import sys
sys.path.insert(0,".")
import vettlib as V, planner
con=V.init_db()
used={(r["match"],int(r["innings"])) for r in con.execute("SELECT DISTINCT match,innings FROM tasks WHERE field_scope='full43'")}
o=[]; e=[]
for m in planner.SWEEP_ROOTS:
    for inn in (1,2):
        if (m,inn) in used: continue
        try: b=V.build_conditions(m,inn)
        except Exception: continue
        if "O" in b["variants"]: o.append((m,inn))
        if "E" in b["variants"]: e.append((m,inn))
print("used",len(used),"remaining_O",len(o),"remaining_E",len(e))
print("O_tasks",len(o)*3,"E_tasks",len(e)*3)
print("first",o[:5],"last",o[-3:])
