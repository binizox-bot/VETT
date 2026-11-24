"""R28 目标与设计有效性审计（只读，不改任何数据）。

回答三个问题：
  A 目标是否成立：当前任务的信息含量有多大？答案是否被少数事实决定？
  B 设计是否有效：同金标双渲染在现有数据里是否真的存在"同一答案不同难度"的实例？
  C 能否持续迭代：220 场底料能否支撑记录空间扩张？

用法：
  $env:PYTHONPATH='src'; & 'D:\Conda\python.exe' audit_design_validity.py
"""
from __future__ import annotations

import collections
import itertools
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # VETT_R28_DIFFICULTY_20261112
WORKSPACE = ROOT.parent                              # 交付根
PROJ = WORKSPACE / "VETT_Cricket_v0.22_R16_Multisource_Dilemmas"
R2615 = PROJ / "r26_15_content_dependency_candidate_v3"
R24220 = PROJ / "dataset_r24_220"
SRC220 = WORKSPACE / "Self-cricket-clean_text_scorecard_v1_220_matches"

sys.path.insert(0, str(PROJ / "src"))

from vett_r25.solver import flatten_record, solve  # noqa: E402


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)


def load_gold_dir(base: Path):
    """返回 [(match_id, answer_dict), ...]，按 private/*/private_gold.json 扫描。"""
    rows = []
    priv = base / "private"
    for gold in sorted(priv.glob("*/private_gold.json")):
        mid = gold.parent.name
        data = json.loads(gold.read_text(encoding="utf-8"))
        for ans in data.get("decision_answers", []):
            rows.append((mid, ans))
    return rows


def section(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def main():
    rows = load_gold_dir(R2615)
    print(f"R26.15 题目数: {len(rows)}  场次: {len({m for m, _ in rows})}")

    # ---------------------------------------------------------------- A1
    section("A1 答案与事实的去重")
    rec_keys = [canon(a.get("decision_record_flat") or flatten_record(a["decision_record"])) for _, a in rows]
    fact_keys = [canon(a.get("solver_facts", {})) for _, a in rows]
    fams = [a.get("scenario_family") for _, a in rows]
    levels = [a.get("level") for _, a in rows]
    print(f"互异 decision_record : {len(set(rec_keys)):>4} / {len(rows)}")
    print(f"互异 solver_facts    : {len(set(fact_keys)):>4} / {len(rows)}")
    print(f"互异 scenario_family : {len(set(fams)):>4} / {len(rows)}")
    print(f"互异 (family, level) : {len(set(zip(fams, levels))):>4} / {len(rows)}")

    # 族 -> 记录 是否函数关系
    fam_to_rec = collections.defaultdict(set)
    for f, r in zip(fams, rec_keys):
        fam_to_rec[f].add(r)
    const_fam = sum(1 for v in fam_to_rec.values() if len(v) == 1)
    print(f"族名唯一决定记录的族数: {const_fam} / {len(fam_to_rec)}")

    # 记录 -> 事实 是否一对多（这就是"同答案不同卷宗"的存在性）
    rec_to_facts = collections.defaultdict(set)
    for r, f in zip(rec_keys, fact_keys):
        rec_to_facts[r].add(f)
    multi = {r: len(v) for r, v in rec_to_facts.items() if len(v) > 1}
    print(f"一个记录对应多种事实的记录数: {len(multi)} / {len(rec_to_facts)}")
    if multi:
        top = sorted(multi.items(), key=lambda kv: -kv[1])[:5]
        for r, n in top:
            vals = json.loads(r)
            print(f"   {n:>2} 种事实 -> total={vals.get('total_runs')} status={vals.get('delivery_status')} "
                  f"dismissal={vals.get('dismissal')}")

    # ---------------------------------------------------------------- A2
    section("A2 求解器确定性：solve(solver_facts) 是否等于金标")
    ok = bad = 0
    bad_examples = []
    for mid, a in rows:
        facts = a.get("solver_facts")
        if facts is None:
            continue
        try:
            got = flatten_record(solve(facts))
        except Exception as exc:  # noqa: BLE001
            bad += 1
            bad_examples.append((mid, a.get("question_id"), f"EXC {exc}"))
            continue
        want = a.get("decision_record_flat") or flatten_record(a["decision_record"])
        if canon(got) == canon(want):
            ok += 1
        else:
            bad += 1
            if len(bad_examples) < 3:
                bad_examples.append((mid, a.get("question_id"), "MISMATCH"))
    print(f"重推一致: {ok}  不一致: {bad}")
    for e in bad_examples:
        print("   ", e)

    # ---------------------------------------------------------------- A3
    section("A3 事实维度：哪些事实在变、变多少")
    all_facts = [a.get("solver_facts", {}) for _, a in rows]
    keys = sorted({k for f in all_facts for k in f})
    varying, constant = [], []
    for k in keys:
        vals = [canon(f.get(k)) for f in all_facts]
        if len(set(vals)) > 1:
            varying.append((k, len(set(vals))))
        else:
            constant.append((k, vals[0]))
    print(f"事实键总数 {len(keys)}；变化 {len(varying)}；恒定 {len(constant)}")
    print("-- 变化的事实（键, 取值数）--")
    for k, n in sorted(varying, key=lambda kv: -kv[1]):
        print(f"   {k:<34} {n}")
    if constant:
        print("-- 恒定事实 --")
        for k, v in constant:
            print(f"   {k:<34} {v}")

    # ---------------------------------------------------------------- A4
    section("A4 最小充分事实集：删到几个事实答案就定了")
    # 逐事实做"缺失后记录是否还唯一"的贪心剔除
    def rec_of(fd):
        try:
            return canon(flatten_record(solve(fd)))
        except Exception:  # noqa: BLE001
            return "ERR"

    base_idx = list(range(len(rows)))
    keep = list(keys)
    changed = True
    while changed and len(keep) > 1:
        changed = False
        for k in list(keep):
            trial = [x for x in keep if x != k]
            ok_all = True
            for i in base_idx:
                fd = {kk: all_facts[i][kk] for kk in trial if kk in all_facts[i]}
                if rec_of(fd) != rec_keys[i]:
                    ok_all = False
                    break
            if ok_all:
                keep = trial
                changed = True
    print(f"原始事实键 {len(keys)} -> 最小充分键 {len(keep)}")
    print(f"   保留: {keep}")
    print(f"   剔除: {[k for k in keys if k not in keep]}")

    # ---------------------------------------------------------------- A4b
    section("A4b 13 键充分性是否在随机事实空间上仍成立")
    import random
    rng = random.Random(20261112)
    domains = {k: sorted({canon(f.get(k)) for f in all_facts}) for k in keys}
    trials = 4000
    agree = 0
    reach = set()
    for _ in range(trials):
        fd = {}
        for k in keys:
            fd[k] = json.loads(rng.choice(domains[k]))
        full = rec_of(fd)
        part = rec_of({k: fd[k] for k in keep})
        reach.add(full)
        if full == part and full != "ERR":
            agree += 1
    print(f"随机抽取 {trials} 组事实：13 键与 24 键结果一致 {agree} ({agree/trials:.1%})")
    print(f"随机空间里出现的互异记录数: {len(reach)}")

    # ---------------------------------------------------------------- B1
    section("B1 泄漏检查：public 里有没有答案")
    pub = R2615 / "public"
    hits = collections.Counter()
    sample = sorted(pub.glob("*/public_instance.json"))[:20]
    for p in sample:
        raw = p.read_text(encoding="utf-8")
        hits["decision_record"] += raw.count("decision_record")
        hits["decision_record_flat"] += raw.count("decision_record_flat")
        hits["solver_facts"] += raw.count("solver_facts")
        hits["ledger.BYE"] += raw.count("ledger.BYE")
        hits["minimum_evidence_spans"] += raw.count("minimum_evidence_spans")
        hits["difficulty_vector"] += raw.count("difficulty_vector")
    print(f"扫描 {len(sample)} 个 public 文件：")
    for k, v in hits.items():
        print(f"   {k:<26} {v}")

    # 逐题检查：金标的 total_runs 是否以答案形式出现在 public
    inst = json.loads((pub / "match_0003" / "public_instance.json").read_text(encoding="utf-8"))
    print(f"public 顶层键: {sorted(inst.keys())}")
    docs = inst.get("documents", [])
    print(f"documents 数量: {len(docs)}  总字符: {sum(len(d.get('text') or '') for d in docs)}")
    ts = inst.get("target_schema")
    print(f"target_schema 类型: {type(ts).__name__}")
    if isinstance(ts, list):
        print(f"target_schema 条目数: {len(ts)}")
        print(f"   前 3 条: {json.dumps(ts[:3], ensure_ascii=False)[:400]}")
    elif isinstance(ts, dict):
        print(f"target_schema 键: {sorted(ts.keys())}")

    # 精确检查：把每题金标的 12 字段值，逐题去 public 文本里找
    section("B2 逐题答案文本泄漏检查")
    leaks = 0
    checked = 0
    for gold in sorted((R2615 / "private").glob("*/private_gold.json")):
        mid = gold.parent.name
        pubf = pub / mid / "public_instance.json"
        if not pubf.exists():
            continue
        raw = pubf.read_text(encoding="utf-8")
        data = json.loads(gold.read_text(encoding="utf-8"))
        for ans in data.get("decision_answers", []):
            flat = ans.get("decision_record_flat") or flatten_record(ans["decision_record"])
            qid = ans.get("question_id", "")
            checked += 1
            # 答案里最有辨识度的组合：status + dismissal + total
            probe = f"{flat['delivery_status']}|{flat['dismissal']}|{flat['total_runs']}"
            if qid and qid in raw and probe.replace("|", "") in raw.replace(" ", ""):
                leaks += 1
    print(f"检查 {checked} 题；question_id 与答案组合同时出现在 public 的题数: {leaks}")

    # ---------------------------------------------------------------- C1
    section("C1 220 场底料：能否支撑记录空间扩张")
    if R24220.exists():
        r220 = load_gold_dir(R24220)
        print(f"dataset_r24_220 题目数: {len(r220)}  场次: {len({m for m, _ in r220})}")
        if r220:
            r220_rec = [canon(a.get("decision_record_flat") or flatten_record(a["decision_record"])) for _, a in r220]
            r220_fact = [canon(a.get("solver_facts", {})) for _, a in r220]
            print(f"   互异 decision_record : {len(set(r220_rec))}")
            print(f"   互异 solver_facts    : {len(set(r220_fact))}")
    else:
        print("   dataset_r24_220 不存在")

    # ---------------------------------------------------------------- C2
    section("C2 原始底料结构（220 场源）")
    if SRC220.exists():
        md = sorted([p for p in SRC220.iterdir() if p.is_dir()])[:3]
        for d in md:
            print(f"-- {d.name} --")
            for f in sorted(d.iterdir()):
                print(f"   {f.name:<40} {f.stat().st_size:>10} B")
    else:
        print("   源目录不存在")

    # ---------------------------------------------------------------- A5
    section("A5 记录分布 vs 可达空间")
    reach_api = PROJ / ".." / "VETT_V2_MEASUREMENT_20261112" / "01_measurement_repair" / "answer_space_audit.json"
    reach_api = reach_api.resolve()
    if reach_api.exists():
        d = json.loads(reach_api.read_text(encoding="utf-8"))
        keys_show = [k for k in d.keys()][:12]
        print(f"answer_space_audit.json 顶层键: {keys_show}")
        for k in keys_show:
            v = d[k]
            if isinstance(v, (int, float, str)):
                print(f"   {k} = {v}")
            elif isinstance(v, dict) and len(v) < 12:
                print(f"   {k} = {v}")
    cur = collections.Counter(rec_keys)
    print(f"当前使用记录数 {len(cur)}；最常见记录出现 {max(cur.values())} 次；"
          f"记录熵 {entropy(list(cur.values())):.3f} bits")


def entropy(counts):
    import math
    total = sum(counts)
    return -sum((c / total) * math.log2(c / total) for c in counts if c)


if __name__ == "__main__":
    main()
