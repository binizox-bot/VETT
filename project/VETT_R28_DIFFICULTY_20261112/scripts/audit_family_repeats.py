"""族内重复的结构：验证"同一答案 + 不同卷宗"这台机器是否已经存在。"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WS = ROOT.parent
PROJ = WS / "VETT_Cricket_v0.22_R16_Multisource_Dilemmas"
R2615 = PROJ / "r26_15_content_dependency_candidate_v3"
sys.path.insert(0, str(PROJ / "src"))

from vett_r25.solver import flatten_record  # noqa: E402


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, default=str)


def main():
    rows = []
    for gold in sorted((R2615 / "private").glob("*/private_gold.json")):
        mid = gold.parent.name
        d = json.loads(gold.read_text(encoding="utf-8"))
        for a in d.get("decision_answers", []):
            rows.append((mid, a))

    by_fam = collections.defaultdict(list)
    for mid, a in rows:
        by_fam[a.get("scenario_family")].append((mid, a))

    print(f"族数 {len(by_fam)}")
    print(f"{'family':<28} {'n':>3} {'#facts':>7} {'#rec':>5} {'#dossier':>9} {'levels':<8}")
    print("-" * 78)
    same_facts = 0
    multi_facts = 0
    for fam, items in sorted(by_fam.items()):
        facts = [canon(a.get("solver_facts", {})) for _, a in items]
        recs = [canon(a.get("decision_record_flat") or flatten_record(a["decision_record"])) for _, a in items]
        doss = {(mid, a.get("question_id")) for mid, a in items}
        lv = sorted({a.get("level") for _, a in items})
        nf, nr = len(set(facts)), len(set(recs))
        if nf == 1:
            same_facts += 1
        else:
            multi_facts += 1
        print(f"{fam:<28} {len(items):>3} {nf:>7} {nr:>5} {len(doss):>9} {','.join(lv):<8}")
    print("-" * 78)
    print(f"族内事实完全一致: {same_facts} / {len(by_fam)}")
    print(f"族内事实有变化  : {multi_facts} / {len(by_fam)}")

    # 事实 -> 族 的反向：一个事实集被几个族复用
    f2fam = collections.defaultdict(set)
    for fam, items in by_fam.items():
        for _, a in items:
            f2fam[canon(a.get("solver_facts", {}))].add(fam)
    print(f"\n互异事实集 {len(f2fam)}；被 ≥2 个族共用的事实集 "
          f"{sum(1 for v in f2fam.values() if len(v) > 1)}")
    for f, fams in f2fam.items():
        if len(fams) > 1:
            print(f"   {sorted(fams)}")

    # 每个事实集对应几个记录
    f2rec = collections.defaultdict(set)
    for mid, a in rows:
        f2rec[canon(a.get("solver_facts", {}))].add(
            canon(a.get("decision_record_flat") or flatten_record(a["decision_record"])))
    print(f"\n一个事实集对应多个记录的事实集数: {sum(1 for v in f2rec.values() if len(v) > 1)}")

    # 内容相关性：同一族的 4 个副本，卷宗是否真的不同
    print("\n--- 单族 4 副本的卷宗差异 ---")
    fam = sorted(by_fam)[0]
    for mid, a in by_fam[fam]:
        print(f"   {mid}  qid={a.get('question_id')}  level={a.get('level')}")

    # 事实键覆盖：哪些键在全样本里只出现单一有效组合
    keys = sorted({k for _, a in rows for k in a.get("solver_facts", {})})
    print("\n--- 事实键取值分布（检查组合覆盖是否稀疏）---")
    for k in keys:
        vals = collections.Counter(canon(a.get("solver_facts", {}).get(k)) for _, a in rows)
        top = vals.most_common(3)
        print(f"   {k:<34} {dict(top)}")


if __name__ == "__main__":
    main()
