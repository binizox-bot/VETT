
"""Offline audit of B002-B009 against source text and gold. No model calls."""
import json, re, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vettlib as V
import v2

DB = V.DB_PATH
BATCHES = ["B002", "B003", "B004", "B005", "B007", "B009"]


def sentences(text):
    return V.L.sentences(text)


WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def has_final(text, runs, wk):
    alts = [str(wk)] + ([WORDS[wk]] if wk in WORDS else [])
    pat = r"(?:\bfor\s+(?:" + "|".join(alts) + r")\b|/\s*" + str(wk) + r"\b|all\s*out)"
    return bool(re.search(r"(?<![0-9])" + str(runs) + r"(?![0-9])", text) and re.search(pat, text, re.I))


def result_rows(con, bid):
    rows = con.execute("SELECT r.*, t.fields_json, t.cond FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id=?",
                       (bid,)).fetchall()
    return [dict(r) for r in rows]


def audit_excerpt(bid, manifest, results):
    out = []
    for t in manifest["tasks"]:
        if t["cond"] != "E":
            continue
        bundle = V.load_bundle(t["match"])
        ss = sentences(bundle["text"])
        ev = V.evidence_index(ss, bundle["md"].innings[t["innings"] - 1].name,
                              bundle["md"].innings[t["innings"] - 1].total_runs,
                              bundle["md"].innings[t["innings"] - 1].total_wickets)
        rebuilt = " ".join(ss[max(0, ev - 1):ev + 2]) if ev is not None else ""
        out.append({"task_key": t["task_key"], "match": t["match"], "innings": t["innings"],
                    "verbatim": rebuilt == t["prompt"].split("Commentary:\n", 1)[-1].rsplit("\n\nJSON:", 1)[0] if "Commentary:\n" in t["prompt"] else False,
                    "evidence_index": ev, "excerpt_sentences": len(ss[max(0, ev - 1):ev + 2]) if ev is not None else 0,
                    "source_sentences": len(ss),
                    "excerpt_has_final": has_final(rebuilt, t["gold"].get("inn%d.total_runs" % t["innings"]),
                                                   t["gold"].get("inn%d.total_wickets" % t["innings"])) if rebuilt else False,
                    "rebuilt_sha": V.sha256_text(rebuilt)})
    return out


def audit_b003(manifest, results):
    diffs = []
    for t in manifest["tasks"]:
        if t["cond"] not in ("WI", "OI"):
            continue
        bundle = V.load_bundle(t["match"])
        built = V.build_conditions(t["match"], t["innings"])
        base = built["variants"].get("O", "")
        variant = built["variants"].get(t["cond"], "")
        deleted = [s for s in sentences(base) if s not in variant]
        target = built["variants"].get("E", "")
        diffs.append({"match": t["match"], "innings": t["innings"], "cond": t["cond"],
                      "deleted": deleted, "deleted_count": len(deleted),
                      "target_evidence_preserved": bool(target) and target in variant,
                      "variant_chars": len(variant), "base_chars": len(base)})
    return diffs


def audit_b004(manifest, results):
    t = manifest["tasks"][0]
    bundle = V.load_bundle(t["match"])
    text = bundle["text"]
    gold = t["gold"]
    checked = {}
    for f, g in gold.items():
        s = str(g)
        checked[f] = s in text
    fields = [r["field"] for r in [{"field": f} for f in gold]]
    out = {"match": t["match"], "fields_total": len(gold),
           "fields_both_innings": all(p in gold for p in ("inn1.total_runs", "inn2.total_runs")),
           "string_present": checked,
           "present_count": sum(1 for v in checked.values() if v),
           "target_subset": [f for f in gold if f.endswith("total_runs") or f.endswith("total_wickets")]}
    return out


def audit_hard(bid, manifest, results):
    out = []
    for t in manifest["tasks"]:
        bundle = V.load_bundle(t["match"])
        inn = bundle["md"].innings[t["innings"] - 1]
        ev = V.evidence_index(sentences(bundle["text"]), inn.name, inn.total_runs, inn.total_wickets)
        out.append({"task_key": t["task_key"], "match": t["match"], "innings": t["innings"],
                    "explicit_total_sentence": ev is not None,
                    "classification": "explicit_total_present" if ev is not None else "no_explicit_total_sentence",
                    "gold": t["gold"]})
    return out


def main():
    con = V.init_db()
    report = {"generated_at": datetime.now().astimezone().isoformat(timespec="seconds"), "batches": {}}
    for bid in BATCHES:
        manifest = V.load_manifest(bid)
        results = result_rows(con, bid)
        sc = json.loads(con.execute("SELECT score_json FROM batches WHERE batch_id=?", (bid,)).fetchone()["score_json"] or "{}")
        entry = {"template": manifest["template"], "accuracy": sc.get("accuracy"),
                 "n_tasks": len(manifest["tasks"]), "n_results": len(results)}
        if bid in ("B002", "B005"):
            entry["excerpt"] = audit_excerpt(bid, manifest, results)
        if bid == "B003":
            entry["deletions"] = audit_b003(manifest, results)
            entry["pairs"] = sc.get("by_condition")
        if bid == "B004":
            entry["full_table"] = audit_b004(manifest, results)
        if bid in ("B007", "B009"):
            entry["evidence_check"] = audit_hard(bid, manifest, results)
        report["batches"][bid] = entry
        (V.REPORTS / ("AUDIT_" + bid + ".json")).write_text(json.dumps(entry, ensure_ascii=False, indent=1), encoding="utf-8")
    (V.REPORTS / "SCIENCE_AUDIT.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = ["# VETT science audit (offline)", "", "- generated: " + report["generated_at"], ""]
    for bid, e in report["batches"].items():
        lines += ["## " + bid + " " + e["template"], "", "- accuracy: " + str(e["accuracy"]) +
                  ", tasks: " + str(e["n_tasks"]) + ", results: " + str(e["n_results"]), ""]
        if "excerpt" in e:
            okv = sum(1 for x in e["excerpt"] if x["verbatim"])
            lines.append("- excerpt verbatim: " + str(okv) + "/" + str(len(e["excerpt"])))
            for x in e["excerpt"][:4]:
                lines.append("  - " + x["match"] + " inn" + str(x["innings"]) + " evidence_idx=" +
                             str(x["evidence_index"]) + " final=" + str(x["excerpt_has_final"]))
        if "deletions" in e:
            for d in e["deletions"][:4]:
                lines.append("- " + d["match"] + " " + d["cond"] + " deleted=" + json.dumps(d["deleted"], ensure_ascii=False)[:220] +
                             " target_preserved=" + str(d["target_evidence_preserved"]))
        if "full_table" in e:
            ft = e["full_table"]
            lines.append("- 43 fields; both innings present: " + str(ft["fields_both_innings"]) +
                         "; gold string present in text: " + str(ft["present_count"]) + "/" + str(ft["fields_total"]))
        if "evidence_check" in e:
            c = {}
            for x in e["evidence_check"]:
                c[x["classification"]] = c.get(x["classification"], 0) + 1
            lines.append("- evidence classification: " + json.dumps(c))
        lines.append("")
    (V.REPORTS / "SCIENCE_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({b: {"accuracy": e["accuracy"], "keys": list(e.keys())} for b, e in report["batches"].items()}, ensure_ascii=False))
    con.close()


if __name__ == "__main__":
    main()
