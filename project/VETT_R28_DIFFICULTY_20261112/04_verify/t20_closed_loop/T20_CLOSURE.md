# t20 收口（closure）

- 任务：闭环验证 — 故障注入 / 降级演练 / 字节级重放 / resume / dry-run
- 状态：**PASS（10/10）**，单命令复现见下。
- 作用：t20 是 t8 的最后一个依赖；本文件落盘即表示 t20 可交 t8/t9/t23/t11。

## 单命令复现

```powershell
cd D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\05_pipeline
D:\Conda\python.exe verify\run_closed_loop_verification.py --config r28.toml
```

预期：`t20 closed-loop verification: 10/10 PASS -> PASS`，退出码 0。

## 10 项结果

| 项 | 内容 | 结果 |
|---|---|---|
| D0 | 协议 7 冻结件校验 22/22 + 盲包 64/0 违规 + 4 条点名注入全部被对应规则阻断 | PASS |
| D1 | kill -9 后 `--resume`：无重复模型调用（12=clean 12）、重复 miss key 0、产物哈希一致 | PASS |
| D2 | 本地服务停用：机械回退、3 条 DEGRADED、coverage 0、链路到报告、0 云端 | PASS |
| D3 | 篡改缓存结果：`result_sha256` 校验失败 → 隔离 + 重算，产物不变、篡改标记未进入产物 | PASS |
| D4 | 同命令两遍：第二遍 miss 0 / hit 12 / calls 12，产物哈希相同，replay identical | PASS |
| D5 | `--dry-run` 全绿（23 门），真实目录哈希/mtime 未变，R26.15 165/93,346,177 零漂移 | PASS |
| D6 | 905 条 raw_output 重解析 0 失配；T1 312/320=0.975 一致；pipeline live 重放 judge_identical；**R-R7：806/806 cache key v2 一致、旧模板 0、解析器不兼容 0**；重放≠重生成（152 样本 1 个分数移动 1 分） | PASS |
| D7 | 路由卡 4 ALLOW/9 DENY；T1 改 DENY → exit 4 + `G_ROUTING_CARD` FAIL；静态扫描 0 绕过；0 硬编码协议 digest | PASS |
| D8 | 320 题每族 ≤1、一题一记录；族 bootstrap 1000 次 CI95 [0.95625, 0.990625]，同 seed digest 相同 | PASS |
| D9 | J8 独立复核：71/71 缓存命中全冻结模板、0 choice、quarantine 35 文件在 runs 外、config 字段结构性消失、守卫测试 PASS、`blocking=[]` | PASS |

## 协议绑定口径（防假告警）

- 只认 `protocol_freeze.json` 的 **7 个冻结 artifact**。
- `02_design/protocol_verify_result.json` 是 `--check` 每次重写的派生件，**不得计入漂移**；`G_PROTOCOL_FROZEN` 显式排除并在 evidence 记录 `excluded_derived`。
- 盲包模式：PAMEND-004 形状规则（10 条 tuple，含合并的 `BP-R28-ID` + `BP-R28-HELDOUT-ITEM` + `BP-R28-FAMILY`）；`reaudit_packets --inject-selftest` 的点名注入全部 BLOCKED。

## 并发副作用如实记录（J_GATE 锚点 S1）

- **现象**：t20 早期（约 23:18–23:24 +08:00）用 plain `j_gate.py`（当时默认写盘）复核，重写了 `04_verify/J_GATE.json`，导致 verifier 的锚点 S1（`acb06196…`）失效；t20 观察到 `6f534158…`，之后 verifier 又刷新为 `442436fb…` / `ac823c45…` / `971a6840…`。
- **原因**：多 agent 并发复核 + 旧版工具默认写盘；t20 未预知该副作用。
- **处置**：自 23:24 起 t20 只用 `j_gate.py --check-md`（judge 已把落盘改为显式 `--write` opt-in）；D9 在调用前后记录 `J_GATE.json` sha256，本次为 `971a6840… → 971a6840…`（未变）。按 `GATE_J_SNAPSHOT_POLICY.md`，t20 关闭前不设锚点，verifier 随后发 S2；判"内容是否变"请用内容摘要：当前 `9b0f4d4027221358…1d9def54b2`（剔除 3 个时间戳路径，`recompute_content_hash.py` 独立实现）。
- **教训（给 t8 独立性报告）**：并发复核工具必须默认只读；锚点文件被任何一方写盘都会使另一方快照失效。

## 产物

- `04_verify/t20_closed_loop/CLOSED_LOOP_VERIFICATION.json` / `.md`
- `04_verify/t20_closed_loop/PIPELINE_VERIFICATION.json`（t13 基线 + t20 收口合并，v2）
- `04_verify/t20_closed_loop/LOG_INDEX.json`（18 份日志的路径/sha256）
- `05_pipeline/PIPELINE_VERIFICATION.json`（同一合并版，供流水线侧引用）
- 日志明细：`05_pipeline/verify/out/`；实现：`05_pipeline/vett_r28/pipeline/`；验证器：`05_pipeline/verify/run_closed_loop_verification.py`

## 诚实边界

- 故障（`kill_*`、local/cloud/disk）是注入演练，不是真实断电/停服；本地 VRAM 事件（7708/8192 MiB，free 310）引用 t14 实测记录，仅作因果说明。
- 重放只从已落盘 `raw_output` 重算，**不声称**重跑模型能复现相同字节。
- t14 的 96 条 S1 mechanical provenance 与 71 条缓存命中没有模型 ledger raw_output，按"无模型调用可重放"计数，不算失配。
- J8 的 C2 采用双通道（raw bytes `choice.v1` + JSON 结构模板键），散文 "choice between …" 不计为变体。



## 修复后复跑（Windows GBK，无 PYTHONUTF8）—— t8 F10 supplemental

t8 在 vanilla Windows GBK 控制台复现到：D0 读取子进程输出时抛 `UnicodeDecodeError`，9/10 FAIL。已修，且**不把环境当先决条件**。

- **环境（本次运行，未设任何 UTF-8 前置）**：console `chcp 936`；`PYTHONUTF8`、`PYTHONIOENCODING`、`PYTHONLEGACYWINDOWSSTDIO` 均未设置；harness 启动时 `sys.stdout.encoding=gbk`；Python 3.14.7 / Windows 11。
- **结果**：**10/10 PASS，exit 0**（D0 不再有 UnicodeDecodeError）。日志 `04_verify/t20_closed_loop/postfix_gbk_console.log`。
- **代码修复**：
  1. `run_proc()` 对每个子进程强制 `PYTHONUTF8=1` + `PYTHONIOENCODING=utf-8`，父进程用 `subprocess.run(text=True, encoding='utf-8', errors='replace')` 解码，不依赖控制台代码页；
  2. harness 自身 `sys.stdout/stderr.reconfigure(encoding='utf-8', errors='replace')`，避免父进程自己打印非 GBK 字符时崩溃。
- **文档口径**：README/单命令页仍建议 Windows 设 `PYTHONUTF8=1`（belt-and-braces），但**命令行本身不设前置也能跑通**；本次实证即未设。
- **哈希（保留原 10/10 记录，未回填时间戳）**：
  - 修复前（原 10/10，ambient UTF-8，保留于 `archive_prefix_utf8/`）：
    - `CLOSED_LOOP_VERIFICATION.json` `87031999b1e9411afa9593445cbf51e291976dbe7828fa97fad4a78ba62125fe`
    - `CLOSED_LOOP_VERIFICATION.md` `37bde9afbcbd7025b208efe60fe95887f31e9c6ca116c8972d99c0219aaeb5bb`
  - 修复后（GBK 无前置）：
    - `CLOSED_LOOP_VERIFICATION.json` `7b5b5fa90952d4db6878b4be607ae9eda273213579e4da2f36b1b7c26ff7d020`
    - `CLOSED_LOOP_VERIFICATION.md` `d5d0f0369d6f70365980abf55da96fbb48be6c11099809c0c725b379c9cd2b7c`
  - 两版并列保存，未覆盖原时间戳；审计产物不做时间回填。
