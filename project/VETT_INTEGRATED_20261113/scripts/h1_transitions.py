"""H1 correctness-transition recomputation (read-only over frozen jsonl).

Classifies every (item, field) cell for three comparisons:
  P1 vs P2  = same-prompt retest   (noise floor)
  P1 vs V0  = order permutation    (order effect)
  P1 vs E1  = cross max_tokens     (reference only)

Five cells: C->C, C->W, W->C, W->W(same wrong), W->W(different wrong).
Writes only under VETT_INTEGRATED_20261113/analysis/.
"""
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
RUN = ROOT / "VETT_R28_DIFFICULTY_20261112" / "eval_runs"
OUT = ROOT / "VETT_INTEGRATED_20261113" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

FIELDS = ["batter_runs","bowler_runs","counts_in_over","delivery_status","dismissal",
          "ledger.BATTER","ledger.BYE","ledger.LEG_BYE","ledger.NO_BALL_EXTRA",
          "ledger.PENALTY","ledger.WIDE_EXTRA","total_runs"]

def rows(p):
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]

def index(rs, keep=lambda r: True):
    d = {}
    for r in rs:
        if keep(r):
            d[r["item_id"]] = r
    return d

retest = rows(RUN / "t19_retest_20261113" / "retest_raw.jsonl")
e4 = rows(RUN / "t19_e1e5_20261112" / "e4_raw.jsonl")
e1 = rows(RUN / "t19_e1e5_20261112" / "e1_raw.jsonl")

p1 = index(retest, lambda r: r.get("arm") == "p1" and r.get("parse_ok"))
p2 = index(retest, lambda r: r.get("arm") == "p2" and r.get("parse_ok"))
v0 = index(e4, lambda r: r.get("arm") == "v_order" and r.get("parse_ok"))
e1i = index(e1, lambda r: r.get("variant") == "published" and r.get("parse_ok"))

items = [i for i in p1 if i in p2]
print("retest items:", len(items), "v0 overlap:", len([i for i in items if i in v0]), "e1 overlap:", len([i for i in items if i in e1i]))

def gold_of(i):
    for src in (p1.get(i), v0.get(i), e1i.get(i)):
        if src and src.get("record_gold"):
            return src["record_gold"]
    return None

def classify(a, b, g):
    """a,b = pred records; g = gold. Returns Counter over the 5 cells."""
    c = Counter()
    for f in FIELDS:
        ca = a.get(f) == g.get(f)
        cb = b.get(f) == g.get(f)
        if ca and cb: c["C->C"] += 1
        elif ca and not cb: c["C->W"] += 1
        elif (not ca) and cb: c["W->C"] += 1
        else:
            c["W->W_same" if a.get(f) == b.get(f) else "W->W_diff"] += 1
    return c

def run_cmp(name, other):
    total = Counter()
    per_field = {f: Counter() for f in FIELDS}
    per_item = {}
    n = 0
    for i in items:
        if i not in other: continue
        g = gold_of(i)
        if not g: continue
        a, b = p1[i]["record_pred"], other[i]["record_pred"]
        c = classify(a, b, g)
        total.update(c)
        for f, cc in zip(FIELDS, [c[k] for k in c]):
            pass
        # per-field recompute (explicit)
        for f in FIELDS:
            ca = a.get(f) == g.get(f); cb = b.get(f) == g.get(f)
            if ca and cb: per_field[f]["C->C"] += 1
            elif ca and not cb: per_field[f]["C->W"] += 1
            elif (not ca) and cb: per_field[f]["W->C"] += 1
            else: per_field[f]["W->W_same" if a.get(f)==b.get(f) else "W->W_diff"] += 1
        ca_all = all(a.get(f)==g.get(f) for f in FIELDS)
        cb_all = all(b.get(f)==g.get(f) for f in FIELDS)
        per_item[i] = {
            "a_correct_fields": sum(a.get(f)==g.get(f) for f in FIELDS),
            "b_correct_fields": sum(b.get(f)==g.get(f) for f in FIELDS),
            "a_exact": ca_all, "b_exact": cb_all,
        }
        n += 1
    tot = sum(total.values())
    summary = {k: total.get(k,0) for k in ["C->C","C->W","W->C","W->W_same","W->W_diff"]}
    summary["n_cells"] = tot
    summary["n_items"] = n
    summary["record_exact_a"] = sum(1 for v in per_item.values() if v["a_exact"])
    summary["record_exact_b"] = sum(1 for v in per_item.values() if v["b_exact"])
    summary["mean_correct_fields_a"] = round(sum(v["a_correct_fields"] for v in per_item.values())/n, 3) if n else 0
    summary["mean_correct_fields_b"] = round(sum(v["b_correct_fields"] for v in per_item.values())/n, 3) if n else 0
    improvement = sum(1 for v in per_item.values() if v["b_correct_fields"] > v["a_correct_fields"])
    worsening = sum(1 for v in per_item.values() if v["b_correct_fields"] < v["a_correct_fields"])
    same = n - improvement - worsening
    summary["items_improve"] = improvement
    summary["items_worsen"] = worsening
    summary["items_same_count"] = same
    return {"summary": summary,
            "per_field": {f: {k: v.get(k,0) for k in ["C->C","C->W","W->C","W->W_same","W->W_diff"]} for f,v in per_field.items()},
            "per_item": per_item,
            "n_items": n}

res = {
  "source": str(RUN),
  "fields": FIELDS,
  "retest_p1_vs_p2": run_cmp("p1_p2", p2),
  "order_p1_vs_v0": run_cmp("p1_v0", v0),
  "cross_p1_vs_e1": run_cmp("p1_e1", e1i),
}
(OUT / "h1_transitions.json").write_text(json.dumps(res, indent=2), encoding="utf-8")

for name in ["retest_p1_vs_p2","order_p1_vs_v0","cross_p1_vs_e1"]:
    s = res[name]["summary"]
    print(f"\n== {name}  n_items={s['n_items']} cells={s['n_cells']}")
    print("   C->C %5d | C->W %5d | W->C %5d | W->W_same %5d | W->W_diff %5d" % (
        s["C->C"], s["C->W"], s["W->C"], s["W->W_same"], s["W->W_diff"]))
    print("   exact_a %d exact_b %d | mean_correct %.2f -> %.2f | items imp/wor/same %d/%d/%d" % (
        s["record_exact_a"], s["record_exact_b"], s["mean_correct_fields_a"], s["mean_correct_fields_b"],
        s["items_improve"], s["items_worsen"], s["items_same_count"]))
    pf = res[name]["per_field"]
    top = sorted(pf.items(), key=lambda kv: kv[1]["C->W"] + kv[1]["W->C"], reverse=True)[:5]
    print("   top changed fields:", [(f, v["C->W"], v["W->C"], v["W->W_diff"]) for f,v in top])
print("\nwrote", OUT / "h1_transitions.json")
