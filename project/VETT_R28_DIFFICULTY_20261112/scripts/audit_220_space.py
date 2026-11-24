"""220 场底料的记录空间审计：回答"能不能持续迭代扩张"。

只读 dataset_r24_220 与 220 场源文本，不改任何文件。
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WS = ROOT.parent
PROJ = WS / "VETT_Cricket_v0.22_R16_Multisource_Dilemmas"
D220 = PROJ / "dataset_r24_220"
SRC220 = WS / "Self-cricket-clean_text_scorecard_v1_220_matches"
sys.path.insert(0, str(PROJ / "src"))

from vett_r25.solver import flatten_record, solve  # noqa: E402


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, default=str)


def main():
    split = json.loads((D220 / "SCENARIO_SPLIT.json").read_text(encoding="utf-8"))
    print("SCENARIO_SPLIT 顶层键:", list(split.keys())[:10])
    for k, v in split.items():
        if isinstance(v, list):
            print(f"  {k}: list len={len(v)}")
        elif isinstance(v, dict):
            print(f"  {k}: dict keys={list(v.keys())[:8]}")
        else:
            print(f"  {k}: {v!r}")

    golds = sorted((D220 / "private").glob("*/private_gold.json"))
    print(f"\nprivate_gold 文件数: {len(golds)}")
    g0 = json.loads(golds[0].read_text(encoding="utf-8"))
    print(f"第一份 gold 顶层键: {sorted(g0.keys())}")

    # 找到承载题目的键
    ans_key = None
    for k in ("decision_answers", "answers", "questions", "instances", "items"):
        if k in g0 and isinstance(g0[k], list):
            ans_key = k
            break
    print(f"题目容器键: {ans_key}")
    if ans_key is None:
        for k, v in g0.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                print(f"  候选 {k}: list len={len(v)} 首元素键={sorted(v[0].keys())[:12]}")
        return

    rows = []
    for g in golds:
        d = json.loads(g.read_text(encoding="utf-8"))
        for a in d.get(ans_key, []):
            rows.append((g.parent.name, a))
    print(f"题目总数: {len(rows)}")

    recs, facts, fams, levels = [], [], [], []
    for mid, a in rows:
        r = a.get("decision_record_flat")
        if r is None and a.get("decision_record"):
            r = flatten_record(a["decision_record"])
        if r is None and a.get("solver_facts"):
            r = flatten_record(solve(a["solver_facts"]))
        recs.append(canon(r) if r is not None else "MISSING")
        facts.append(canon(a.get("solver_facts", {})))
        fams.append(a.get("scenario_family") or a.get("family"))
        levels.append(a.get("level"))

    print(f"互异 decision_record : {len(set(recs))} / {len(rows)}")
    print(f"互异 solver_facts    : {len(set(facts))} / {len(rows)}")
    print(f"互异 scenario_family : {len(set(fams))} / {len(rows)}")
    print(f"互异 level           : {sorted({l for l in levels if l})}")

    # 族 -> 记录 是否常数
    f2r = collections.defaultdict(set)
    for f, r in zip(fams, recs):
        f2r[f].add(r)
    const = sum(1 for v in f2r.values() if len(v) == 1)
    print(f"族名唯一决定记录: {const} / {len(f2r)}")

    # 记录 -> 事实 是否一对多
    r2f = collections.defaultdict(set)
    for r, f in zip(recs, facts):
        r2f[r].add(f)
    multi = {r: len(v) for r, v in r2f.items() if len(v) > 1}
    print(f"一个记录对应多种事实的记录数: {len(multi)} / {len(r2f)}")
    if multi:
        print("  例：同记录不同事实的样例")
        for r in list(multi)[:3]:
            vals = json.loads(r)
            print(f"    {multi[r]} 种事实 -> total={vals.get('total_runs')} "
                  f"status={vals.get('delivery_status')} dismissal={vals.get('dismissal')}")

    # 解题确定性
    ok = bad = miss = 0
    for mid, a in rows:
        sf = a.get("solver_facts")
        want = a.get("decision_record_flat")
        if want is None and a.get("decision_record"):
            want = flatten_record(a["decision_record"])
        if sf is None or want is None:
            miss += 1
            continue
        try:
            got = flatten_record(solve(sf))
        except Exception:  # noqa: BLE001
            bad += 1
            continue
        ok += 1 if canon(got) == canon(want) else 0
        bad += 0 if canon(got) == canon(want) else 1
    print(f"重推一致 {ok} / 不一致 {bad} / 缺字段 {miss}")

    # 记录分布
    dist = collections.Counter(recs)
    print(f"\n最常见记录出现 {dist.most_common(1)[0][1]} 次；"
          f"只出现 1 次的记录 {(sum(1 for c in dist.values() if c == 1))} 个")

    # 源文本规模
    if SRC220.exists():
        sizes = []
        for d in SRC220.iterdir():
            if d.is_dir():
                sizes.append(sum(f.stat().st_size for f in d.iterdir()))
        print(f"\n220 场源：{len(sizes)} 场，单场平均 {sum(sizes)//max(len(sizes),1)} B，"
              f"总计 {sum(sizes)/1024/1024:.1f} MB")


if __name__ == "__main__":
    main()
