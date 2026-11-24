"""Compute paired-diagnostic metrics from eval_pilot10 raw jsonl."""
import json, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT = ROOT/"VETT_INTEGRATED_20261113"
PILOT = INT/"pilot10"
RUNS = INT/"runs"/"eval_pilot10"
OUT = INT/"analysis"
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(INT/"scripts"))
import eval_pilot10 as E

sel = json.loads((PILOT/"selection.json").read_text(encoding="utf-8"))
matches = [m["match"] for m in sel["matches"]]
FIELDS = {m: E.load_fields(m) for m in matches}


def rows():
    out = []
    for p in sorted(RUNS.glob("*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


def num(v):
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


def pred(r, fid):
    return (r or {}).get("pred", {}).get(fid)


def correct(r, fid, gold):
    return E.value_match(gold, pred(r, fid))


def closure_ok(r, mid):
    checks = []
    for i in (1, 2):
        p = f"inn{i}"
        g = lambda k: num(pred(r, f"{p}.{k}"))
        bat, ext, tot = g("batting_runs_sum"), g("total_extras"), g("total_runs")
        byes, lb, nb, wd = g("byes"), g("leg_byes"), g("no_balls"), g("wides")
        bowl = g("bowling_runs_charged")
        if None not in (bat, ext, tot):
            checks.append(bat + ext == tot)
        if None not in (byes, lb, nb, wd, ext):
            checks.append(byes + lb + nb + wd == ext)
        if None not in (tot, byes, lb, bowl):
            checks.append(bowl == tot - byes - lb)
    return (sum(checks), len(checks)) if checks else (0, 0)


def main():
    rs = rows()
    by = {(r["match"], r["variant"], r["system"], r["model"]): r for r in rs}
    empties = defaultdict(lambda: [0, 0])
    for r in rs:
        if not r.get("pred"):
            empties[(r["model"], r["system"])][0] += 1
        empties[(r["model"], r["system"])][1] += 1
    models = sorted({r["model"] for r in rs})
    systems = sorted({r["system"] for r in rs})
    report = {"schema": "vett.integrated.pilot10.metrics.v1", "n_rows": len(rs),
              "models": models, "systems": systems, "by_model_system": {}}

    for model in models:
        for system in systems:
            key = (model, system)
            entry = {}
            def acc_of(r, m, v):
                g = E.expected_gold(m, v)
                fs = FIELDS[m]
                return sum(1 for f in fs if E.value_match(g[f["field_id"]], pred(r, f["field_id"]))) / len(fs)
            control_rows = [(m, by[(m,"control",system,model)]) for m in matches if (m,"control",system,model) in by]
            entry["control_acc"] = round(sum(acc_of(r,m,"control") for m,r in control_rows)/len(control_rows),4) if control_rows else None
            per_variant = {}
            for v in ("control","shuffled","revised","conflict","missing","distractor","revision_inline"):
                rs2 = [by[(m,v,system,model)] for m in matches if (m,v,system,model) in by]
                per_variant[v] = round(sum(acc_of(r,m,v) for r,m in [(by[(m,v,system,model)],m) for m in matches if (m,v,system,model) in by])/len(rs2),4) if rs2 else None
            entry["variant_acc"] = per_variant

            same_shuf = same_dist = n_cmp = 0
            cw = cw_den = 0
            rev_changed_ok = rev_changed_n = 0
            stale = stale_n = 0
            ret_ok = ret_n = 0
            unk_ok = unk_n = 0
            overclaim = 0
            closure_num = closure_den = 0
            paired_strict = paired_n = 0
            conflict_ok = conflict_n = 0
            inline_ok = inline_old = inline_n = 0
            hard_ok = hard_n = hard_stale = 0
            paired_field_ok = paired_field_n = 0
            empty_pred = total_rows = 0
            for m in matches:
                c = by.get((m,"control",system,model)); s = by.get((m,"shuffled",system,model))
                rv = by.get((m,"revised",system,model)); mi = by.get((m,"missing",system,model))
                cf = by.get((m,"conflict",system,model)); di = by.get((m,"distractor",system,model))
                if not c: continue
                g_ctrl = E.expected_gold(m,"control")
                if s:
                    for f in FIELDS[m]:
                        n_cmp += 1
                        if pred(c,f["field_id"]) == pred(s,f["field_id"]): same_shuf += 1
                        if correct(c,f["field_id"],g_ctrl[f["field_id"]]):
                            cw_den += 1
                            if not correct(s,f["field_id"],g_ctrl[f["field_id"]]): cw += 1
                if di:
                    for f in FIELDS[m]:
                        if pred(c,f["field_id"]) == pred(di,f["field_id"]): same_dist += 1
                if rv:
                    doc = json.loads((PILOT/m/"variants/revised/gold.json").read_text(encoding="utf-8"))
                    g_rev = E.expected_gold(m,"revised")
                    changed = set(doc["changed_fields"])
                    for f in FIELDS[m]:
                        fid = f["field_id"]
                        if fid in changed:
                            rev_changed_n += 1
                            if correct(rv,fid,g_rev[fid]): rev_changed_ok += 1
                            stale_n += 1
                            if pred(rv,fid) is not None and str(pred(rv,fid)).strip() == str(g_ctrl[fid]).strip(): stale += 1
                        else:
                            ret_n += 1
                            if correct(rv,fid,g_rev[fid]): ret_ok += 1
                    # strict paired success on this match
                    changed_ok = all(correct(rv,f["field_id"],g_rev[f["field_id"]]) for f in FIELDS[m] if f["field_id"] in changed)
                    unchanged_ok = all(correct(rv,f["field_id"],g_rev[f["field_id"]]) for f in FIELDS[m] if f["field_id"] not in changed)
                    control_ok = all(correct(c,f["field_id"],g_ctrl[f["field_id"]]) for f in FIELDS[m])
                    paired_n += 1
                    paired_strict += 1 if (changed_ok and unchanged_ok and control_ok) else 0
                    for f in FIELDS[m]:
                        fid = f["field_id"]
                        good = correct(rv,fid,g_rev[fid]) if fid in changed else (correct(c,fid,g_ctrl[fid]) and correct(rv,fid,g_rev[fid]))
                        paired_field_n += 1
                        paired_field_ok += 1 if good else 0
                if mi:
                    doc = json.loads((PILOT/m/"variants/missing/gold.json").read_text(encoding="utf-8"))
                    for fid in doc.get("unknown_fields", []):
                        unk_n += 1
                        if str(pred(mi,fid)).strip().upper() == "UNKNOWN": unk_ok += 1
                        else: overclaim += 1
                ri = by.get((m,"revision_inline",system,model))
                if ri:
                    doc = json.loads((PILOT/m/"variants/revision_inline/gold.json").read_text(encoding="utf-8"))
                    newv = doc["gold"]["match.pom"]; oldv = doc["edit"].get("old")
                    inline_n += 1
                    if E.value_match(newv, pred(ri,"match.pom")): inline_ok += 1
                    if oldv and E.value_match(oldv, pred(ri,"match.pom")): inline_old += 1
                rh = by.get((m,"revised_hard",system,model))
                if rh:
                    doc = json.loads((PILOT/m/"variants/revised_hard/gold.json").read_text(encoding="utf-8"))
                    g_hard = E.expected_gold(m,"revised_hard")
                    for fid in doc["changed_fields"]:
                        hard_n += 1
                        if correct(rh,fid,g_hard[fid]): hard_ok += 1
                        if str(pred(rh,fid)).strip() == str(g_ctrl[fid]).strip(): hard_stale += 1
                if cf:
                    conflict_n += 1
                    if correct(cf,"inn1.total_extras", g_ctrl["inn1.total_extras"]): conflict_ok += 1
                if c:
                    a,b = closure_ok(c,m); closure_num += a; closure_den += b
            entry.update({
                "order_same_pred": round(same_shuf/n_cmp,4) if n_cmp else None,
                "order_correct_to_wrong": round(cw/cw_den,4) if cw_den else None,
                "revised_changed_acc": round(rev_changed_ok/rev_changed_n,4) if rev_changed_n else None,
                "stale_rate": round(stale/stale_n,4) if stale_n else None,
                "unchanged_retention": round(ret_ok/ret_n,4) if ret_n else None,
                "missing_unknown_acc": round(unk_ok/unk_n,4) if unk_n else None,
                "missing_overclaim": overclaim,
                "conflict_field_acc": round(conflict_ok/conflict_n,4) if conflict_n else None,
                "distractor_same_pred": round(same_dist/n_cmp,4) if n_cmp else None,
                "closure_rate": round(closure_num/closure_den,4) if closure_den else None,
                "paired_strict": f"{paired_strict}/{paired_n}",
                "paired_field_rate": round(paired_field_ok/paired_field_n,4) if paired_field_n else None,
                "inline_revision_acc": round(inline_ok/inline_n,4) if inline_n else None,
                "inline_old_value_rate": round(inline_old/inline_n,4) if inline_n else None,
                "hard_changed_acc": round(hard_ok/hard_n,4) if hard_n else None,
                "hard_stale_rate": round(hard_stale/hard_n,4) if hard_n else None,
            })
            entry["parse_empty"] = f"{empties[(model, system)][0]}/{empties[(model, system)][1]}"
            report["by_model_system"][f"{model}|{system}"] = entry

    (OUT/"pilot10_metrics.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    fields = ["control_acc","order_correct_to_wrong","revised_changed_acc","stale_rate",
              "unchanged_retention","missing_unknown_acc","closure_rate","paired_field_rate",
              "inline_revision_acc","inline_old_value_rate","parse_empty"]
    print(f"{'model|system':40s} " + " ".join(f"{h[:9]:>9s}" for h in fields))
    for k,v in report["by_model_system"].items():
        print(f"{k:40s} " + " ".join(f"{str(v.get(h)):>9s}" for h in fields))

if __name__ == "__main__":
    main()
