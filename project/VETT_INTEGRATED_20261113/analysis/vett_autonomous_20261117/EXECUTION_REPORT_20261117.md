
# VETT 本地自治实验工作流执行报告

- 执行日期：2026-11-17
- 执行窗口：21:40:02 – 21:49:32（Asia/Shanghai）
- 报告整理：2026-11-18
- 最终状态：stopped（可 resume）
- 外部 API：0

## 1. 执行摘要

本次执行把 VETT 从“聊天里手动跑批”改造成可脱离会话的本地实验工作流，并完成实际启动与验收。

| 项目 | 结果 |
|---|---:|
| 已评分批次 | 10（B001–B010） |
| 已冻结待跑批次 | 1（B011，3 个任务） |
| 本地模型请求 / 结果行 | 54 / 54 |
| 任务行 / 唯一键 | 57 / 57 |
| 决策记录 | 11 |
| 使用比赛根 | 14 |
| 保留根越界 | 0 |
| 外部 API 调用 | 0 |
| 实验内容人工介入 | 0（验收的 kill/stop 为测试操作） |

验收结论：**通过**。12 项验收全部 PASS，详见第 7 节。

## 2. 环境与入口检查

实际执行并以真实输出为准：

    dsh --version
    0.2.2-rc.1

    dsh --help
    dsh web
    dsh headless "run the tests"
    dsh tui --resume <session>
    dsh plugin --profile tui add <package>

会话内另有 schedule_create / schedule_edit 定时任务工具。

判断：

- DSH 具备 CLI、一次性 headless、TUI 会话恢复与定时任务入口。
- 但 headless 与聊天入口都会驱动外部模型，无法满足“外部 API 0”。
- 因此实验执行器采用独立本地 Python 进程，直接调用 127.0.0.1:11434 的 Ollama；DSH 只保留交互与恢复入口。
- Python：C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe（3.12.14，sqlite 3.53.1）。系统 python 是 WindowsApps 占位，未使用。
- Ollama 0.40.16；Qwen2.5:7b-instruct-q4_K_M、Llama3.1:8b、Gemma2:9b 均在本地，digest 写入每条结果。

## 3. 交付物

工作目录：VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117

    vettctl.py      启动、状态、暂停、恢复、停止、快照、报告
    supervisor.py   单实例调度、恢复、评分、决策、计时器
    worker.py       唯一 GPU 推理进程，一次一个请求
    planner.py      T1–T5 模板、资格检查、冻结、R0–R9 决策与回退
    scorer.py       批次评分、配对、反例、研究记忆
    reporting.py    15 分钟状态、小时快照、覆盖审计
    vettlib.py      SQLite、Ollama、条件变体、金标与评分基础库
    state/workflow.db
    batches/ runs/ reports/ logs/

状态库表：meta、batches、tasks、results、decisions、events、candidates。

请求唯一键：

    task_key = sha256(match | innings | model | cond | field_scope | prompt_sha)

领取使用 BEGIN IMMEDIATE + 条件更新，记录 claimed_by、claimed_at、attempts、recoveries；worker 死亡或心跳超 150 秒自动退回 queued；结果已落盘则标记 recovered_with_existing_result，避免重复推理。

## 4. 运行时间线（主要节点）

| 时间 | 事件 |
|---|---|
| 21:40:02 | start；supervisor 24948 / worker 24696；B001 冻结 |
| 21:40:38 | B001 评分 1.0，R1 冻结 B002 |
| 21:40:42 | 模拟中断：worker 24696 被杀；任务恢复，worker 9872 重启 |
| 21:41:06 | B002 0.8333，R4 冻结 B003 |
| 21:41:48 | B003 0.1667；WI 0.0 < OI 0.5，R5 冻结 B004 |
| 21:42:40 | B004 0.1938，R6 冻结 B005 |
| 21:42:54 | B005 0.8333，R4 冻结 B006 |
| 21:43:40 | stop，pids 清空 |
| 21:43:41 | restart；R8 冻结 B007 |
| 21:44:09 | B007 0.0，R9 冻结 B008 |
| 21:44:20 | stop，requeued_claimed=1 |
| 21:44:42 | restart，B008 继续 |
| 21:47:23 | B008 0.9167，R1F 回退冻结 B009；stop |
| 21:47:51 | B009 0.0，R9 冻结 B010 |
| 21:47:53 | stop |
| 21:48:49 | restart；21:48:50 强制快照；21:49:05 stop |
| 21:49:22 | restart；B010 评分 1.0；21:49:32 R1F 冻结 B011 并 stop |

最终 B011 的 3 个任务在 queued，state=stopped。

## 5. 批次结果

| 批次 | 模板 | 根 | 条件 | 请求 | 格正确 | 准确率 |
|---|---|---|---:|---:|---:|---:|
| B001 | T1 基线 | 0066, 0085 | O | 6 | 12/12 | 1.0000 |
| B002 | T2 困难摘录 | 0002, 0003 | E | 6 | 10/12 | 0.8333 |
| B003 | T3 配对删除 | 0002 | O/WI/OI | 9 | 3/18 | 0.1667 |
| B004 | T4 整表 | 0002 | O | 3 | 25/129 | 0.1938 |
| B005 | T2 困难摘录 | 0008 | E | 3 | 5/6 | 0.8333 |
| B006 | T3 配对删除 | 0008 | O（WI/OI 不可用） | 3 | 0/6 | 0.0000 |
| B007 | T5 困难全文 | 0009, 0010 | O | 6 | 0/12 | 0.0000 |
| B008 | T1 基线扩展 | 0087, 0096 | O | 6 | 11/12 | 0.9167 |
| B009 | T5 困难全文 | 0011, 0013 | O | 6 | 0/12 | 0.0000 |
| B010 | T1 基线扩展 | 0165, 0021 | O | 6 | 12/12 | 1.0000 |
| B011 | T5 困难全文 | 0015 | O | 3 待跑 | — | — |

批次差异：

- B001/B008/B010：开发根原文基线。
- B002/B005：困难根三句证据摘录。
- B003/B006：同根 O / 删同局局中比分 WI / 删另一局总分 OI 配对对照。
- B004：单根 43 字段整表。
- B007/B009/B011：无可用 E 时的困难根全文回退。

## 6. 决策链

| 时间 | 规则 | 选择 | 下一批 | 理由摘要 |
|---|---|---|---|---|
| 21:40:02 | R0 | T1 | B001 | 初始基线 |
| 21:40:38 | R1 | T2 | B002 | 基线 1.0 饱和 |
| 21:41:06 | R4 | T3 | B003 | 摘录仍 0.833 |
| 21:41:48 | R5 | T4 | B004 | WI 0.0 < OI 0.5，删除特异 |
| 21:42:40 | R6 | T2 | B005 | 整表完成，扩下一组困难根 |
| 21:42:54 | R4 | T3 | B006 | 摘录仍 0.833 |
| 21:43:41 | R8 | T5 | B007 | 无剩余困难根支持 E |
| 21:44:09 | R9 | T1 | B008 | 困难全文完成，扩剩余开发根 |
| 21:47:23 | R1F | T5 | B009 | T2 无合格任务，回退 T5 |
| 21:47:51 | R9 | T1 | B010 | 扩剩余开发根 |
| 21:49:32 | R1F | T5 | B011 | T2 无合格任务，回退 T5 |

每条决策的 observation、rationale、next_batch_id 在 decisions 表；RESEARCH_MEMORY.md 同步了可读版本。

## 7. 验收结论

| 验收项 | 结果 | 证据 |
|---|---|---|
| 无人工介入完成≥3 批差异实验 | PASS | 10 批已评分 |
| 上一批结果触发下一批并保存理由 | PASS | 11 条 decisions |
| 模拟可恢复中断并续跑 | PASS | 21:40:42 恢复，任务 attempts=2/recoveries=1，仅 1 条结果 |
| 关闭启动终端仍有响应落盘 | PASS | 21:40:02 启动；调用结束后 21:40:26 已 3 条完成 |
| stop 同时停派发与监督器重启 | PASS | 最终 21:49:32；12 秒内 results 54=54，pids 清空 |
| 单 GPU worker | PASS | PowerShell 1 worker / 1 supervisor；领取 pid 串行 |
| 15 分钟状态 / 小时快照 | PASS | 阈值测试 7/7；快照后 48→52 条结果 |
| 外部 API 0 | PASS | meta.external_api_calls=0；URL 全部 127.0.0.1 |
| 保留根隔离 | PASS | 14 根，0121–0160 越界 0 |
| 唯一键、工作锁、恢复记录 | PASS | 57/57 唯一键 |
| 43 字段整表复用 | PASS | B004 129 格，沿用 full_table.py 定义 |
| 研究记忆与原始路径 | PASS | RESEARCH_MEMORY.json/md，runs/B0xx.jsonl |

## 8. 主要发现

- 开发根目标格接近饱和：B001 12/12、B008 11/12、B010 12/12。
- 困难根加三句证据摘录仍只有 0.8333（B002 10/12、B005 5/6），不支持“失败完全由长上下文稀释造成”。
- B003 的 O 与 WI 都是 0.0，OI 为 0.5；删除另一局总分反而让 3 个格恢复，提示跨局比分干扰。样本仅 18 格，不能当作稳定结论。
- B004 目标两格 7/12（58.3%），但整表 25/129（19.4%），说明目标格饱和会掩盖整表损失。
- B007/B009 的困难根全文目标格 0%，与“文本没有明确总分句”的可答性缺口一致，不是单纯格式失败。

## 9. 问题与边界

- B011 未跑完（3 个 queued），当前实验结论只基于 B001–B010。
- B006 的 WI/OI 变体不可用，实际只生成 O 的 3 个请求；candidates 表记录了 variant_unavailable。
- 人工盲审 0/40；证据索引 96 条仍 pending_human_review，未并入自动结论。
- 15 分钟状态由“阈值 + 每次批次转移即写”共同保证；小时快照阈值由隔离测试验证，生产运行未连续等待 60 分钟，21:48:50 / 21:49:48 为显式快照。
- decisions.batch_id 统一记为 genesis，批次链条靠 next_batch_id 与 created_at 还原；不影响选择，但后续可改为上一批 id。
- B011 的批次状态仍为 running、任务为 queued，这是为 resume 保留的中断态。

## 10. 下一批任务（B011）

| 根 | 局 | 模型 | 条件 | 字段 |
|---|---:|---|---|---|
| match_0015 | 2 | qwen2.5:7b-instruct-q4_K_M | O | inn2.total_runs, inn2.total_wickets |
| match_0015 | 2 | llama3.1:8b | O | inn2.total_runs, inn2.total_wickets |
| match_0015 | 2 | gemma2:9b | O | inn2.total_runs, inn2.total_wickets |

## 11. 复现命令

    cd "D:/Download/VETT_Cricket_Complete_Delivery_R19_20261017/VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117"
    PY="/c/Users/PC/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/python.exe"

    "$PY" vettctl.py start
    "$PY" vettctl.py status --md
    "$PY" vettctl.py pause
    "$PY" vettctl.py resume
    "$PY" vettctl.py stop
    "$PY" vettctl.py snapshot
    "$PY" vettctl.py report

## 12. 证据索引

- 验收日志：ACCEPTANCE.md
- 架构说明：README.md
- 操作命令：COMMANDS.md
- 最终状态：reports/STATUS.md
- 研究记忆：reports/RESEARCH_MEMORY.md
- 机器可读验收数据：reports/ACCEPTANCE_DATA.json
- 覆盖缺口：reports/COVERAGE_GAP.md
- 批次原始结果：runs/B001.jsonl … runs/B011.jsonl
- 批次评分：reports/B001_SCORE.json … reports/B010_SCORE.json
- 决策与事件：state/workflow.db 的 decisions、events 表
- 计时器测试：tests/test_timers.py
