
import sys, json
sys.path.insert(0, ".")
import vettlib as V, planner

con = V.init_db()
models = V.MODELS
tasks, rejects = [], []
tasks += planner.make_tasks(con, "match_0002", 2, ["NEI_OI", "NEI_WI"], "target2", models,
                            rejects, allow_reuse=True, num_predict=300)
design = planner._design("B2_matched_control",
    "Length-matched non-evidence deletion controls for B003: NEI_OI matched to the 364-char other-innings sentence, NEI_WI matched to the 269-char mid-score sentence.",
    "B003 O/WI/OI lacked a closely length-matched non-evidence control; B013 OIC deleted only 234 chars vs OI 364.",
    con, tasks, ["NEI_OI", "NEI_WI"], models,
    ["commentary.txt variants", "scorecard.md"],
    "exact integer match per field; pair NEI against historical O and against the corresponding WI/OI deletion")
if tasks:
    bid = planner.freeze_batch(con, design, tasks, rejects, plan_ms=3.0)
    print("frozen", bid, "tasks", len(tasks), "rejects", len(rejects))
    print("conds", [dict(r) for r in con.execute("SELECT cond,COUNT(*) n FROM tasks WHERE batch_id=? GROUP BY cond", (bid,))])
else:
    print("no tasks", rejects[:5])

b = V.build_conditions("match_0002", 2)["variants"]
ss = V.L.sentences(V.load_bundle("match_0002")["text"])
audit = {"root": "match_0002", "innings": 2, "variants": {}}
for cond in ("O", "WI", "OI", "NEI_OI", "NEI_WI"):
    deleted = [s for s in ss if s not in b[cond]]
    audit["variants"][cond] = {"chars": len(b[cond]), "deleted": [{"chars": len(s), "text": s} for s in deleted]}
audit["length_deltas"] = {"NEI_OI_vs_OI": abs(313-364), "NEI_WI_vs_WI": abs(251-269)}
Path = __import__("pathlib").Path
Path("reports/AUDIT_B003_NEI.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")
print("audit", audit["length_deltas"])
