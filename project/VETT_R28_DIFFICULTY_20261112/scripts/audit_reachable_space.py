"""迭代上限实测：从 FACT_DOMAINS 枚举合法事实 -> 互异记录，能撑到多大规模。

只读，不写任何数据文件。
"""
from __future__ import annotations

import collections
import itertools
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WS = ROOT.parent
PROJ = WS / "VETT_Cricket_v0.22_R16_Multisource_Dilemmas"
sys.path.insert(0, str(PROJ / "src"))

from vett_r25.generator import FACT_DOMAINS  # noqa: E402
from vett_r25.solver import flatten_record, solve  # noqa: E402


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, default=str)


def main():
    print(f"FACT_DOMAINS 字段数: {len(FACT_DOMAINS)}")
    total = 1
    for k, v in FACT_DOMAINS.items():
        total *= len(v)
    print(f"笛卡尔积上界: {total:,}")

    # 只抽"相关键"少而合法的事实：从空字典开始，逐步加入键
    rng = random.Random(20261112)
    keys = list(FACT_DOMAINS)

    def random_facts(min_keys=2, max_keys=8):
        n = rng.randint(min_keys, max_keys)
        ks = rng.sample(keys, n)
        return {k: rng.choice(FACT_DOMAINS[k]) for k in ks}

    seen = {}
    errs = collections.Counter()
    trials = 20000
    for _ in range(trials):
        f = random_facts()
        try:
            rec = solve(f)
        except Exception as exc:  # noqa: BLE001
            errs[type(exc).__name__ + ": " + str(exc)[:40]] += 1
            continue
        flat = canon(flatten_record(rec))
        if flat not in seen:
            seen[flat] = f
    print(f"\n随机 {trials} 组事实 -> 合法 {trials - sum(errs.values())}，互异记录 {len(seen)}")
    if errs:
        print("  主要失败原因：")
        for k, v in errs.most_common(5):
            print(f"    {v:>6}  {k}")

    # 常数字段覆盖
    cov = collections.Counter()
    for flat in seen:
        d = json.loads(flat)
        for fld in ("ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY"):
            if d.get(fld, 0) != 0:
                cov[fld] += 1
    print(f"\n315 类记录空间里的非零覆盖（本次采样）：")
    for fld in ("ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY"):
        print(f"   {fld:<16} 非零记录 {cov[fld]:>4} / {len(seen)}")

    # 达到 160 个互异记录需要多少次抽样
    print(f"\n达到 160 个互异记录的抽样成本估计：")
    print(f"   本次 {trials} 次得到 {len(seen)} 个；若目标 160，需要约 "
          f"{int(trials * 160 / max(len(seen), 1)):,} 次量级")

    # 分布：记录按 total_runs / status / dismissal
    dist = collections.Counter()
    for flat in seen:
        d = json.loads(flat)
        dist[d["delivery_status"]] += 1
    print(f"\n互异记录按 delivery_status 分布: {dict(dist)}")

    dis = collections.Counter()
    for flat in seen:
        d = json.loads(flat)
        dis[d["dismissal"]] += 1
    print(f"互异记录按 dismissal 分布: {dict(dis)}")

    # 关键：同一个记录能否对应多个事实（双渲染的前提）
    rec2fact = collections.Counter()
    for flat, f in seen.items():
        rec2fact[flat] += 1
    multi = sum(1 for v in rec2fact.values() if v > 1)
    print(f"\n同一记录被多个事实集产生（在本次采样中）: {multi}")

    # 数值范围
    totals = sorted({json.loads(x)["total_runs"] for x in seen})
    print(f"total_runs 取值: {totals}")


if __name__ == "__main__":
    main()
