#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch_contract_md_n320.py — 补齐 R28_CONTRACT.md 的 N=320 改动。"""
import pathlib

p = pathlib.Path(__file__).resolve().parents[1] / "R28_CONTRACT.md"
t = p.read_text(encoding="utf-8")

REPL = [
    ("**校验器：** `02_contract/scripts/contract_verify.py`（`--freeze` 111/111 PASS；`--check` 110/110 PASS）",
     "**校验器：** `02_contract/scripts/contract_verify.py`（AMEND-001 后逐项结果见 `contract_verify_result.json`）"),
    ("| **发布集** | `public/` + `private/` | 160 题，一题一记录，逐题分配剂量 | 互异率 = **1.0** |",
     "| **发布集** | `public/` + `private/` | 320 题，一题一记录，逐题分配剂量 | 互异率 = **1.0** |"),
    ("| **对照集** | `variants/` | 每题一份配对渲染（四剂量全 0） | `solver_facts` 与 `decision_record_flat` 逐字节相同 |",
     "| **对照集** | `variants/` | 每题一份配对渲染（四剂量全 0） | `solver_facts` 与 `decision_record_flat` 逐字节相同 320/320 |"),
    ("| **实验集** | `eval_runs/` | 160 × 2 = **320 次推理** | 题内配对（McNemar） |",
     "| **实验集** | `eval_runs/` | 320 × 2 = **640 次推理** | 题内配对（McNemar） |"),
    ("> **纠正旧版冲突：** \"互异记录 ≥0.9×题数\"与\"同金标双渲染\"数学上冲突（160=80×2 时互异率上限 0.5）。R28 拆成两个集合：发布集 160 个互异记录 + `variants/` 160 份配对渲染。发布集一题一记录，互异率 = 1.0。",
     "> **纠正旧版冲突：** \"互异记录 ≥0.9×题数\"与\"同金标双渲染\"数学上冲突（160=80×2 时互异率上限 0.5）。R28 拆成两个集合：发布集 **320** 个互异记录 + `variants/` **320** 份配对渲染。发布集一题一记录，互异率 = 1.0。"),
    ("### 5.2 N 是显式参数（不得硬编码 160）", "### 5.2 N 是显式参数（不得硬编码）"),
    ("- 生成器/构建/评测/报告模板**均不得硬编码 160**；所有计数写入 `MANIFEST/config_digest`。",
     "- 生成器/构建/评测/报告模板**均不得硬编码 n_published**；所有计数写入 `MANIFEST/config_digest`。"),
    ("- amendment 只需改 `n_published` 一个数；配额用 `quota_rescale_v1` 自动重标定（按 N/160 放大 → 截断到可达上限 → 最大余数补足 → 2/5 vs 3/5 分块），再由 t8 复算、用户签字。",
     "- amendment 只需改 `n_published` 一个数；配额用 `quota_rescale_v1`（AMEND-001 修正版：合法 dismissal 封顶 ≤11、缺口优先补 NONE→RUN_OUT→OBS/HIT、NONE ≤38.75%）重标定，再由 t8 复算、用户签字。"),
    ("**记录空间安全规则：** `可达下界 ≥ N + 40(held_out) + 0.10 × N`。默认 160 → 216 ≤ 761 ✅；N=320 → 392 ≤ 761 ✅；N=400 → 480 ≤ 761 ✅。",
     "**记录空间安全规则：** `可达下界 ≥ N + 40(held_out) + 0.10 × N`。**N=320 → 392 ≤ 761 ✅**（历史 160 → 216 ✅）。"),
    ("### 7.2 配额（默认 N=160，逐层写死）", "### 7.2 配额（N=320，逐层写死）"),
    ("- 发布集 160 = `development`；`held_out_test` = 40（16 因子格 ×1 + 12 剂量格 ×2），记录与发布集互异，**不进入公开包**。",
     "- 发布集 **320** = `development`；`held_out_test` = 40（16 因子格 ×1 + 12 剂量格 ×2），记录与发布集互异，**不进入公开包**。"),
    ("- 记录需求：160 + 40 = **200 个互异记录**（可达下界 761，余量充足）。",
     "- 记录需求：320 + 40 = **360 个互异记录**（含 10% 余量 392 ≤ 可达下界 761，余量充足）。"),
    ("| HA17 | N 参数化 | 代码/配置无硬编码 160；计数由 `n_published` 派生 | ✅ |",
     "| HA17 | N 参数化 | 代码/配置无硬编码 n_published；计数由 `n_published` 派生 | ✅ |"),
    ("**有效 n：** R28 = 160 题 / 160 族 / 160 互异记录；与 R26.15 比较 n_eff ≤25 族 / 16 记录、按族 bootstrap；禁止把 100 题或 320 次推理当独立样本。",
     "**有效 n：** R28 = 320 题 / 320 族 / 320 互异记录；与 R26.15 比较 n_eff ≤25 族 / 16 记录、按族 bootstrap；禁止把 100 题或 640 次推理当独立样本。"),
    ("5. 硬编码 `n_published=160`（否则 amendment 失效）。",
     "5. 硬编码 `n_published`（否则 amendment 失效）。"),
    ("| (F) 两块结构 64+96=160/32 场 | §5.1 |", "| (F) 两块结构 128+192=320/64 场 | §5.1 |"),
    ("- **CEIL-2** | `BOWLED` / `LBW` / `CAUGHT` 各只有 **2 个可达记录**，`STUMPED` 4 个（合法 dismissal 合计 ≤10） | 合法 dismissal 合计最多 10 题；不得重复记录凑分布 |",
     "- **CEIL-2** | `BOWLED` / `LBW` / `CAUGHT` 各只有 **2 个可达记录**，`STUMPED` 4 个（合法 dismissal 合计 ≤10） | 合法 dismissal 合计最多 10 题 + DEAD 1 = **11 封顶**；N=320 不放大；不得重复记录凑分布 |"),
]
missing = []
for old, new in REPL:
    if old in t:
        t = t.replace(old, new)
    elif new not in t:
        missing.append(old[:70])

# §14：把"待决策"正文替换为已决记录，保留选项表作为历史
start = t.index("## 14. 已决：功效/N（用户 2026-11-12 授权 B2 → N=320）")
end = t.index("## 15. 验证与复现")
new14 = """## 14. 已决：功效/N（用户 2026-11-12 授权 B2 → N=320）

**决定：** Q1=B2 → `n_published=320`（10pp 功效 80.7%、MDE 9.91pp、CI 半宽 ±6.93pp、记录需求 392 ≤ 761）；Q2 接受结构天花板但合法 dismissal 封顶 ≤11；Q3 接受 D2/D3 renderer 扩展（须证明生效）。合同版本升级 1.0.0→1.1.0，AMEND-001 记录见 `contract_amendments.jsonl`。

**决策前评估（历史记录）：**

| 选项 | N | 10pp 功效 | 80% MDE | 互异记录需求* | 结论 |
|---|---:|---:|---:|---:|---|
| A 保持 | 160 | 51.6% | 14.01pp | 216 | 未采用 |
| B 扩量 | 240 | 68.8% | 11.44pp | 304 | 未采用 |
| **B2 扩量（选定）** | **320** | **80.7%** | **9.91pp** | **392** | **已授权并应用** |
| C 改口径 | 160 | 51.6% | 14.01pp | 216 | 未采用 |

\\* 含 40 题 held_out + 10% 安全余量。当前设计按 320 题、640 次 E1 推理执行；未再扩量。

"""
t = t[:start] + new14 + t[end:]
p.write_text(t, encoding="utf-8")

# 更新冻指纹中的 MD 哈希与 CONTRACT.sha256
import hashlib
import json

cdir = p.parent
freeze_path = cdir / "contract_freeze.json"
sha_path = cdir / "CONTRACT.sha256"
freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
md_bytes = p.read_bytes()
freeze["doc_files"]["R28_CONTRACT.md"] = {
    "bytes": len(md_bytes),
    "sha256": hashlib.sha256(md_bytes).hexdigest(),
}
freeze_path.write_text(json.dumps(freeze, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
contract_sha = freeze["file"]["sha256"]
sha_path.write_text(
    f"{contract_sha}  r28_contract.json\n{freeze['doc_files']['R28_CONTRACT.md']['sha256']}  R28_CONTRACT.md\n",
    encoding="utf-8")
print("patched; missing:", missing if missing else "none")
print("contract md sha256:", freeze["doc_files"]["R28_CONTRACT.md"]["sha256"])
