# GATE_J 快照与锚点政策（S 系列）

| | |
|---|---|
| **适用范围** | `04_verify/` 下 J 门产物（`J_GATE.json` / `J_GATE.md` / `J8_REOPEN_RUNBOOK.md` / 3 个脚本） |
| **当前状态** | **S2 = ACTIVE（唯一锚点）**；S1 = SUPERSEDED_NO_ANCHOR（历史保留） |
| **锚点文件** | [`GATE_J_SNAPSHOT.json`](GATE_J_SNAPSHOT.json)（现为 **GATE-J-S2 / ACTIVE**；S1 记录在 `s1_record`） |
| **判定工具** | `python scripts/verify_snapshot.py --expect S2`（S2 发布后） |
| **权威裁决** | captain（2026-11-12）："与其反复失效，不如如实声明 t20 期间 `J_GATE` 是活跃产物，不出锚点。" |

---

## 1. 为什么需要这份政策（一段历史，别删）

一个**验证门每次被运行就重写自己的产物**，则任何"锚点"都会在正常复核中被打破：

| 轮次 | 事件 | 结果 |
|---|---|---|
| S1 发布 | 记录 6 个产物的字节 sha256 | t8 开始按它核对 |
| S1 后数分钟 | t20 的 **plain `j_gate.py`** 运行（它在做 J8 闭合复核，完全合法）重写了 `J_GATE.json`（新 `generated_at_utc`） | `acb06196…` → `6f534158…`，**锚点失效** |
| 定性（captain） | 根因**不是谁违规**，而是**默认写行为**：跑验证 ≠ 产物变更，两者被耦合了 | 修法：`j_gate.py` 默认只读，写盘必须显式 `--write` |
| 结论 | 反复"发布 S1.5 / S2 / S3"没有意义 | **t20 关闭前不设锚点**；关闭后一次性发 S2 |

同轮还暴露第二层问题（F8b）：内容摘要**不可被第三方复现**——旧口径只剔顶层 `generated_at_utc`，
但 J0 证据在 JSON 里出现两份、其中一份仍带着上游 `verify_checked_at_utc`；且没写明 canonical 化细节。
**一个别人算不出来的不变量，不能进验收清单。**

---

## 2. 双轨哈希规则（S2 起写死，S1 的教训）

每个 snapshot **必须同时**给出两类哈希，并写明各自能否被独立复算：

| 轨道 | 定义 | 用途 | 变动含义 |
|---|---|---|---|
| **A. 字节哈希** `sha256` | 文件的原始字节 | t8 做逐字节核对；发布/归档 | 任何变动都算变动 |
| **B. 内容摘要** `content_sha256` | `vett-gate-content-digest/v2`（见 §3） | 判定"是否只是元数据在动" | 只有 B 变才算**内容**变了 |

**判定表**

| A 字节 | B 内容 | 结论 | 下游动作 |
|---|---|---|---|
| 同 | 同 | `IDENTICAL` | 无需动作 |
| 异 | 同 | **`METADATA_ONLY`（仅元数据变动）** | **不触发重验**；只需重新引用新的字节哈希 |
| 异 | 异 | `CONTENT_CHANGED` | 锚点失效；必须发新 snapshot_id 并经 captain 确认 |

这条规则的目的：让"运行验证"与"产物变更"在**核对层面**解耦，而不是要求所有人都不许跑工具。

---

## 3. 内容摘要配方 `vett-gate-content-digest/v2`（可复现）

```
1) 读取 JSON 文件
2) 删除以下点号路径（仅当父对象存在时删除；深度拷贝，不改原文件）：
     generated_at_utc
     protocol_precondition.evidence.verify_checked_at_utc
     items.J0_protocol_precondition.evidence.verify_checked_at_utc
3) 序列化：json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
   —— UTF-8 编码、键升序、紧凑分隔符、无尾随换行、不做空白归一
4) SHA-256(上述字符串的 UTF-8 字节)
```

排除项的**全部理由**：三个键都是时间戳（两个来自上游 `protocol_verify.py --check` 的运行时刻，
会随任何人的重跑而变）。**artifacts / verdicts / evidence 的数字与结构全部参与哈希，不做任何归一化。**

**两份独立实现（互为对照，证明配方可被第三方复现）**

```powershell
# 实现 A（独立实现，不 import 别的模块）
D:\Conda\python.exe 04_verify\scripts\recompute_content_hash.py
D:\Conda\python.exe 04_verify\scripts\recompute_content_hash.py --recipe
D:\Conda\python.exe 04_verify\scripts\recompute_content_hash.py --compare old.json new.json

# 实现 B（快照校验器内置）
D:\Conda\python.exe 04_verify\scripts\verify_snapshot.py --content-digest [file]
D:\Conda\python.exe 04_verify\scripts\verify_snapshot.py --recipe
```

2026-11-12 实测：两实现对 `J_GATE.json` 输出**逐位一致** `9b0f4d40…`；`--compare` 对"只改时间戳"
的两份文件判 `EQUAL (metadata-only change)`、exit 0。**S2 起，任何快照里的内容摘要都必须能被这两条命令复算出来**，
否则不得写进验收清单。

---

## 4. S2 发布时必须包含的字段（checklist）

1. `snapshot_id`（新值，S2）与 `supersedes`（S1）；
2. **全量** artifact 列表：`bytes` + `sha256`（轨道 A）＋能算内容摘要的每个 JSON 的 `content_sha256`（轨道 B）；
3. 变更理由与时间线：S1 何时破、被谁、为什么合法（plain run）、根因与修法；
4. 内容摘要配方版本号 + 两份实现路径 + 一次实测一致值；
5. 稳定性政策：谁可以写、写之前要做什么（见 §5）；
6. 历史小节：**不删任何一条已发生的缺陷**（F1/F2/F4/F5/F6/F7/F8/F8b…）；
7. **指纹块必须机械生成，禁止手抄**：`python scripts/verify_snapshot.py --fingerprints` 直接产出
   Markdown 表格（bytes + sha256）与 `content_sha256_v2`。理由：S1 期间我曾手抄过一次过期的
   `GATE_J_SNAPSHOT.json` 字节数（9,593 vs 实际 9,710），被 verifier 抓到——手抄是 F 类缺陷的温床。

---

## 5. 写入权限与流程

- **默认只读**：`j_gate.py` 默认不写盘；`--check-md`、`--no-write` 亦只读；**只有显式 `--write` 才落盘**。
- **谁能写**：只有 judge_architect（J 门 owner）在得到 captain 指令或新事实（如 t21 交付 C1、t20 复核要求改判）时写。
- **写之前**：先发 S(n+1) 草案（新 snapshot_id + 全量 digest + 理由），经 captain 确认后落盘，再由 t8 引用。
- **其他 agent 想刷新产物**：请用 `--write` 并**主动告知** owner（这会改变字节哈希，属 `METADATA_ONLY` 或
  `CONTENT_CHANGED`，需按 §2 判定）；或者不要刷新，直接读现有文件 + 用 `--content-digest` 比对。
- **t20 的 `run_closed_loop_verification.py`** 会跑 `j_gate.py` 再读 `J_GATE.json`：plain 运行**不再**刷新文件，
  若它的目的是"以最新状态复核"，请改用 `python 04_verify/scripts/j_gate.py --write --json-only`（显式写入，
  并告知 owner）；若只是读取判定，plain 运行 + 读文件即可。

---

## 6. 当前（t20 已关闭，S2 生效）的实际规则

1. **S2 = ACTIVE，是唯一锚点**；S1 状态 `SUPERSEDED_NO_ANCHOR`（历史保留，不再引用）；
2. 核对命令：`python scripts/verify_snapshot.py --expect S2` → 期望"6/6 artifacts match GATE-J-S2"；
3. **S2 之后任何 `--write` 都是受控事件**：
   - 写之前：owner 先说明理由（captain 指令 / 新事实 / 下游要求），并预估是否只动元数据；
   - 写之后：立刻用 `--fingerprints` 出新的字节表 + `content_sha256_v2`，
     再用 `verify_snapshot.py --expect S2` 看分类：
     - `METADATA_ONLY`（内容摘要没变）→ **t8 不需重验**，只需接受新字节哈希；
     - `CONTENT_CHANGED`（内容摘要变了）→ **S2 锚点失效**，必须发 S3 并经 captain 确认后 t8 才引用；
   - 任何情况下不得"静默重写"：写盘者必须主动在团队里报新的字节哈希与内容摘要；
4. 其他 agent 若需要刷新产物：用 `--write`，并**先告知 owner**；t20 的 `run_closed_loop_verification.py`
   若只需判定，plain 运行 + 读现有文件即可（plain 不写盘）。
