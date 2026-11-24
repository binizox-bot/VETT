"""Independent per-field recheck of R28 E1/E4 raw outputs.

Read-only. Does not touch frozen artifacts. Writes per_field_recheck.json
next to this script.

Conventions:
- e1_raw.jsonl: dedupe by (item_id, arm), keep the last logged row (rerun wins).
- only parse_ok rows enter the paired analysis.
- pair = item present in both arms.
"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(
    os.path.dirname(HERE),
    "VETT_R28_DIFFICULTY_20261112",
    "eval_runs",
    "t19_e1e5_20261112",
)


def load(name):
    path = os.path.join(RUN, name)
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def field_eq(rec, gold, field):
    return rec.get(field) == gold.get(field)


def record_eq(rec, gold, fields):
    return all(field_eq(rec, gold, f) for f in fields)


def main():
    e1 = [
        r
        for r in load("e1_raw.jsonl")
        if r.get("label") in ("e1", "e1_rerun")
    ]
    e4 = load("e4_raw.jsonl")
    fields = list(e4[0]["record_gold"].keys())

    last = {}
    for r in e1:
        last[(r["item_id"], r["arm"])] = r
    by = collections.defaultdict(dict)
    for r in last.values():
        if r.get("parse_ok"):
            by[r["item_id"]][r["arm"]] = r
    pairs = [v for v in by.values() if len(v) == 2]

    per_field = {}
    for f in fields:
        hard = [v["published"] for v in pairs]
        ctrl = [v["control"] for v in pairs]
        h = sum(field_eq(r["record_pred"], r["record_gold"], f) for r in hard) / len(hard)
        c = sum(field_eq(r["record_pred"], r["record_gold"], f) for r in ctrl) / len(ctrl)
        b = sum(
            1
            for v in pairs
            if field_eq(v["published"]["record_pred"], v["published"]["record_gold"], f)
            and not field_eq(v["control"]["record_pred"], v["control"]["record_gold"], f)
        )
        cc = sum(
            1
            for v in pairs
            if field_eq(v["control"]["record_pred"], v["control"]["record_gold"], f)
            and not field_eq(v["published"]["record_pred"], v["published"]["record_gold"], f)
        )
        prior = collections.Counter(
            str(v["published"]["record_gold"].get(f)) for v in pairs
        ).most_common(1)[0][1] / len(pairs)
        per_field[f] = {
            "hard": round(h, 6),
            "control": round(c, 6),
            "diff_pp": round(100 * (h - c), 4),
            "mcnemar_hard_only_correct": b,
            "mcnemar_control_only_correct": cc,
            "gold_marginal_mode_share": round(prior, 6),
        }

    exact = {
        arm: sum(
            record_eq(v[arm]["record_pred"], v[arm]["record_gold"], fields)
            for v in pairs
        )
        for arm in ("published", "control")
    }
    distinct = {
        arm: len(
            {
                json.dumps(
                    {f: v[arm]["record_pred"].get(f) for f in fields}, sort_keys=True
                )
                for v in pairs
            }
        )
        for arm in ("published", "control")
    }

    base = {v["published"]["item_id"]: v["published"]["record_pred"] for v in pairs}
    e4_out = {}
    for arm in ("v_order", "v_minus", "v_plus"):
        rows = [r for r in e4 if r["arm"] == arm]
        if arm == "v_minus":
            rows = [r for r in rows if r["variant"] == "non_decisive_substitution"]
        n = len(rows)
        same_as_base = sum(
            1 for r in rows if record_eq(r["record_pred"], base.get(r["item_id"], {}), fields)
        ) if arm != "v_plus" else None
        equals_gold = sum(
            1 for r in rows if record_eq(r["record_pred"], r["record_gold"], fields)
        )
        flips = {}
        for f in fields:
            flips[f] = sum(
                1
                for r in rows
                if r["item_id"] in base
                and r["record_pred"].get(f) != base[r["item_id"]].get(f)
            )
        e4_out[arm] = {
            "n": n,
            "record_equals_gold": equals_gold,
            "record_same_as_base": same_as_base,
            "per_field_changed_vs_base": flips,
        }

    out = {
        "schema": "vett.r28.review.per_field_recheck.v1",
        "source": {
            "e1_raw": "eval_runs/t19_e1e5_20261112/e1_raw.jsonl",
            "e4_raw": "eval_runs/t19_e1e5_20261112/e4_raw.jsonl",
        },
        "pairing": {"n_pairs": len(pairs), "drop_rule": "parse_ok both arms"},
        "e1": {
            "record_exact": exact,
            "distinct_predicted_records": distinct,
            "per_field": per_field,
        },
        "e4": e4_out,
    }
    path = os.path.join(HERE, "per_field_recheck.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print("n_pairs", len(pairs))
    print("exact", exact)
    print("distinct", distinct)
    for f, v in per_field.items():
        print(
            f"{f:22s} hard={v['hard']:.3f} ctrl={v['control']:.3f} "
            f"diff={v['diff_pp']:+.2f}pp b/c={v['mcnemar_hard_only_correct']}/"
            f"{v['mcnemar_control_only_correct']} mode={v['gold_marginal_mode_share']:.3f}"
        )
    print("e4", json.dumps(e4_out, ensure_ascii=False))


if __name__ == "__main__":
    main()
