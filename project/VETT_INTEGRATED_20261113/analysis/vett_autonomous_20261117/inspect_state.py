import sqlite3, json, os, sys
db = r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\state\workflow.db"
con = sqlite3.connect("file:" + db + "?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()
print("DB", os.path.getsize(db), "bytes")
tables = [r[0] for r in cur.execute("select name from sqlite_master where type='table'")]
print("TABLES", tables)
for t in ["meta","batches","tasks","results","events","decisions"]:
    try:
        cols = [d[1] for d in cur.execute("pragma table_info(" + t + ")")]
        print("COLS", t, cols)
    except Exception as e:
        print("ERR", t, e)
print("META")
for r in cur.execute("select * from meta order by key"):
    print(" ", dict(r))
print("TASK_STATUS")
for r in cur.execute("select status, count(*) n from tasks group by status"):
    print(" ", dict(r))
print("RESULT_COUNT", cur.execute("select count(*) from results").fetchone()[0])
print("LAST_RESULTS")
for r in cur.execute("select * from results order by rowid desc limit 3"):
    d = dict(r)
    d.pop("raw_response", None)
    print(" ", json.dumps(d, ensure_ascii=False)[:500])
print("LAST_EVENTS")
for r in cur.execute("select * from events order by rowid desc limit 8"):
    print(" ", json.dumps(dict(r), ensure_ascii=False)[:300])
print("BATCHES_TAIL")
for r in cur.execute("select batch_id, template, status, accuracy, cells_correct, cells_total from batches order by seq desc limit 6"):
    print(" ", dict(r))
print("B019_TASKS", cur.execute("select count(*) from tasks where batch_id in ('B019','B022')").fetchone()[0])
