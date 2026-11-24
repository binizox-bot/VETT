# t20 闭环验证（故障注入 / 降级 / 字节级重放 / resume / dry-run）

**结论：10/10 PASS（`overall = PASS`，elapsed 18.9 s）**。验证对象是 `05_pipeline` 的闭环流水线，外加协议绑定、盲包复扫、J8 模板卫生与族抽样单位。

## 单命令复现

```powershell
cd D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\05_pipeline
D:\Conda\python.exe verify\run_closed_loop_verification.py --config r28.toml
```

- 报告：`04_verify/t20_closed_loop/CLOSED_LOOP_VERIFICATION.json`（机器可读）+ `.md`（人读）。
- 每次运行的日志：`05_pipeline/verify/out/*.log`，逐条路径与 sha256 见 `LOG_INDEX.json`。
- 单跑某项：`--only D1` / `--only D1,D6,D9`。

## 逐项结果

| # | 验证项 | 结果 | 关键证据 | 日志 |
|---|---|---|---|---|
| D0 | 协议绑定 22/22 + 盲包模式复扫（PAMEND-004，形状规则） | **PASS** | `protocol_verify --check` 22/22；64 包 0 违规；四条点名注入全部被**对应规则**阻断（`r28q_0001→BP-R28-ID`、`r28h_0005→BP-R28-HELDOUT-ITEM`、`rfam_…→BP-R28-FAMILY`、`r28fact_…→BP-R28-ID`）；外部 `reaudit_packets.py --inject-selftest` exit 0 | `00_protocol_verify.log`、`00_reaudit_packets.log` |
| D1 | `kill -9` 后 `--resume`：无重复调用、产物一致 | **PASS** | `kill_after_report` → exit 9，resume 6/6 阶段跳过、0 次调用；`kill_mid_annotate` 在第 4 条标注后真杀进程，resume 后总模型调用 **12 = clean 12**，重复 cache-miss key **0**，resume 产物与重跑产物哈希逐一相同 | `01_kill_report.log`、`01_resume_after_report.log`、`01_kill_mid.log`、`01_resume_mid.log`、`01_rerun_mid.log` |
| D2 | 本地服务停掉 → 自动降级机械回退，链路不中断 | **PASS** | exit 0；`LOCAL_SERVICE_UNAVAILABLE` 3 条（T1/S1/C1）、`mechanical_only`、coverage 0.0；链路到达 `REPORT.md`；0 云端调用；证据同时引用 t14 真实 VRAM 事件（7708/8192 MiB，free 310 < 1536 下限） | `02_degrade_local.log` |
| D3 | 篡改缓存文件 → 校验失败 → 重算，不静默使用 | **PASS** | `cache.quarantined≥1`、`misses≥1`；产物哈希与篡改前逐项相同；篡改标记未出现在 `annotations.json`；`.quarantine` 文件落盘 | `03_tamper_first.log`、`03_tamper_second.log` |
| D4 | 同一命令跑两次：第二遍全命中缓存、产物哈希相同 | **PASS** | run1 `miss=12/hit=0`；run2 `miss=0/hit=12` 且 calls=12；`ARTIFACT_HASHES.json` 逐字节相同；`REPLAY_CHECK.identical=true` | `04_double_first.log`、`04_double_second.log` |
| D5 | `--dry-run` 全绿且不写真实目录 | **PASS** | 23 门全 PASS；数据集目录文件列表与 5 个关键冻结件 hash/mtime 全未变；run 目录限于 `05_pipeline/runs/_dryrun`；R26.15 `165 文件 / 93,346,177 B` 零漂移 | `05_dryrun.log` || D6 | 从落盘 `raw_output` 重算全部指标；重放≠重生成 | **PASS** | t14 主路径 **905 条账本**重解析 0 失配；960 条标注比对 864 命中 + 96 条机械/缓存跳过、**0 失配**；T1 重算 **312/320 = 0.975** 与首次一致；pipeline 自身 live run（6 条）重放 `judge_identical=true`；**R-R7 独立复算：806/806 cache key v2 逐位一致、主路径旧模板 0 条、解析器不兼容 0 条**；`regenerated_model_output=false`、`model_calls_during_replay=0`；引用 `nondeterminism_evidence.json`（152 样本中 1 个 5 分制分数跨运行移动 1 分，判定不变） | `06_replay_t14.log`、`06_replay_live.log` |
| D7 | 路由卡是 ALLOW/DENY 唯一来源，无绕过调用 | **PASS** | routing_card：4 ALLOW / 9 DENY；把 T1 改成 DENY 后流水线 **exit 4 / FROZEN_VIOLATION** 且 `G_ROUTING_CARD=FAIL`、0 次模型调用；静态扫描 0 处 `service.generate`/网络/越权 `api.annotate`；代码中 0 处硬编码协议 digest | `07_routing_tamper.log` |
| D8 | 每族至多 1 题、一题一记录、按族 bootstrap 可跑 | **PASS** | published 320：族 320、最大每族 1 题、互异记录 320；T1 逐题正确率 0.975；族级 bootstrap 1000 次（seed 20261112）CI95 **[0.95625, 0.990625]**；同 seed 重跑 digest 相同（确定性） | `08_family_bootstrap.json` |
| D9 | J8 模板卫生关闭（独立复核，不采信自报） | **PASS** | 独立重算 71 次缓存命中：T1 29 + T2 42，25 个唯一 key，`choice_hits=0`，每 key 对应 cache object 模板一致；与 local_operator 的 71 条审计记录**逐条集合相同**；`t14/runs/**` `choice.v1` **0 命中**（双通道：raw bytes + JSON 结构）；`t14/quarantine/` 在 runs 之外、35 文件 + MANIFEST；`config.t2_choice_template_version` 结构性不存在；`FROZEN_TEMPLATES + assert_frozen_templates` 守卫测试 exit 0；主结果 13 个文件哈希未变（仅 config 与报告按预期变化）；`j_gate.py --check-md`（只读）J8=PASS、`blocking=[]`，调用前后 `J_GATE.json` sha256 不变（`971a6840…`） | `09_j8_guard_test.log`、`09_j_gate.log` |

## 协议冻结口径（避免假告警）

- 冻结集只认 7 个 artifact：`protocol.json`、`PROTOCOL.md`、`judge_protocol.py`、`protocol_verify.py`、`build_protocol.py`、`tests/test_judge_protocol.py`、`evidence/routing_evidence_snapshot.json`（以 `protocol_freeze.json` 为准）。
- **`02_design/protocol_verify_result.json` 是派生结果，不属冻结集**；流水线 `G_PROTOCOL_FROZEN` 明确排除它，并在 gate evidence 里记录 `excluded_derived` 与理由。否则每跑一次 `--check` 都会假漂移。
- `judge_protocol.BLIND_FORBIDDEN_PATTERNS` 当前是 **10 条 tuple**：PAMEND-004 把 R28 span 家族合并为形状规则 `BP-R28-ID`，另加 `BP-R28-HELDOUT-ITEM`、`BP-R28-FAMILY`；`reaudit_packets.py --inject-selftest` 的 11 条点名注入全部 BLOCKED（见 D0 日志）。协议不按"条目数"判门，按"点名形态是否拦住 + 既有 64 包是否误伤"判门。

## t8 F10 UTF-8 修复（supplemental，append-only）

t8 在 vanilla Windows GBK 控制台复现到 D0 `UnicodeDecodeError`（9/10 FAIL）。已修：`run_proc()` 对所有子进程强制 `PYTHONUTF8=1` + `PYTHONIOENCODING=utf-8`，父进程 `subprocess.run(..., text=True, encoding='utf-8', errors='replace')` 解码；harness 自身 stdout/stderr 也 reconfigure 为 UTF-8/errors=replace。

- **本次验证环境（未设前置）**：`chcp 936`；`PYTHONUTF8`/`PYTHONIOENCODING`/`PYTHONLEGACYWINDOWSSTDIO` 均未设置；harness 启动时 stdout=gbk；Python 3.14.7 / Windows 11。
- **结果**：**10/10 PASS，exit 0**；日志 `postfix_gbk_console.log`。
- **文档口径**：README 仍建议 Windows 设 `PYTHONUTF8=1`（belt-and-braces），但**不设也能跑通**（本次实证）。
- **新旧哈希（原记录保留在 `archive_prefix_utf8/`，未回填时间戳）**：
  - pre：`CLOSED_LOOP_VERIFICATION.json` `87031999…25fe`；`.md` `37bde9af…b5bb`
  - post：`CLOSED_LOOP_VERIFICATION.json` `7b5b5fa9…d020`；`.md` `d5d0f036…2b7c`

## 并发副作用（如实记录，不隐去）

- **现象**：t20 早期（约 2026-11-12T23:18–23:24+08:00）用 plain `j_gate.py`（当时默认写盘）做复核，重写了 `04_verify/J_GATE.json`，使 verifier 的锚点 S1（`acb06196…`）失效；t20 当时观察到 `6f534158…`，其后 verifier 又刷新为 `442436fb…` / `ac823c45…` / `971a6840…`。
- **原因**：多 agent 并发复核 + 旧版工具默认写盘；t20 未预知该副作用。
- **处置**：自 23:24 起 t20 只用 `j_gate.py --check-md`（judge 已把落盘改为显式 `--write` opt-in）；D9 在调用前后记录 `J_GATE.json` sha256，本次为 `971a6840… → 971a6840…`（未变）。按 `GATE_J_SNAPSHOT_POLICY.md`，t20 关闭前不设锚点，verifier 随后发 S2；判"内容是否变"用内容摘要（剔除 3 个时间戳路径），当前 `9b0f4d4027221358…1d9def54b2`，`recompute_content_hash.py` 与 `verify_snapshot.py --content-digest` 两实现一致。
- **教训（供 t8 独立性报告）**：并发复核工具必须默认只读；任何一方写盘都会使另一方快照/锚点失效。

## 诚实边界

- 故障注入（`--fault kill_after_*` / `kill_mid_annotate`）是**模拟进程死亡**，用于验证 resume/缓存语义；不是真实断电测试。
- 本地停服演练用注入故障路径；真实 VRAM 事件（7708/8192 MiB，free 310）来自 t14 记录，仅作因果引用，不重放当时硬件状态。
- 重放验证的是"从已落盘 raw_output 重算"；**不**声称重跑模型能得到相同字节（152 样本中 1 个分数移动 1 分已写进证据）。
- D6 的 96 条"S1 mechanical provenance / cache hit"没有 ledger raw_output，按"无模型调用可重放"计数，不当作失配。
- D9 的 C2 用双通道；散文里的 "choice between …" 不算变体声明（`choice.v1` raw 0 命中、JSON 模板键 0 命中）。
- 本目录只放验证结果；实现与运行日志在 `05_pipeline/`。

## 产物

- `CLOSED_LOOP_VERIFICATION.json` / `.md` — 10 项逐项 PASS/FAIL、命令、证据
- `PIPELINE_VERIFICATION.json` — t13 基线 + t20 收口合并版（v2），含协议绑定、J8、R-R7、并发副作用
- `T20_CLOSURE.md` — 收口页（解锁 t8/t9/t23/t11 的依据）
- `LOG_INDEX.json` — 18 份日志的路径/字节/sha256
- `README.md` — 本文件
