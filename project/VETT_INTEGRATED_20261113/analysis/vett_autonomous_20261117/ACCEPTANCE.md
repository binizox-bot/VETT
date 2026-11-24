
# VETT 本地自治实验工作流验收日志

验收日期：2026-11-17 21:40–21:50（Asia/Shanghai）。
最终状态：stopped（可 resume）。外部 API：0。

## 0. 结论

部署完成并通过验收：

- 无人工介入连续完成 10 个已评分批次（B001–B010），批次在根、条件、字段范围、模型负载上明确不同。
- 11 条决策记录把上一批结果与下一批选择绑定，理由落库。
- 模拟一次 worker 被杀的可恢复中断，任务重跑且只保留一条结果。
- 启动终端退出后 supervisor 继续运行并落盘新响应。
- 用户 stop 同时停止派发、worker 和 supervisor 自动重启，12 秒内无新结果。
- 只有一个 GPU 推理 worker；外部 API 调用 0；保留根零越界。

## 1. 环境检查（真实入口，不猜测）

实际执行：

    dsh --version
    0.2.2-rc.1

    dsh --help
    Usage: dsh [--profile] <name> [options] [app-args...]
    dsh web
    dsh headless "run the tests"
    dsh tui --resume <session>
    dsh plugin --profile tui add <package>

会话内也有 schedule_create / schedule_edit 定时任务工具。

判断：

- DSH 有 CLI、一次性 headless、TUI 会话恢复和定时任务入口。
- 但 headless 与聊天入口会驱动外部模型，无法满足“外部 API 0”。
- 因此实验执行器采用独立本地 Python 进程，直接调用 127.0.0.1 的 Ollama；DSH 只保留交互与恢复入口。
- Python 使用 C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe（3.12.14）。系统 python 是 WindowsApps 占位，未使用。
- Ollama 0.40.16；三个模型均本地存在，digest 写入每条结果。

## 2. 实际进程

    supervisor 24948 / worker 24696   21:40:02–21:43:40
    supervisor 22104 / worker 16724   21:43:41–21:44:20
    supervisor 20772 / worker 23852   21:44:42–21:47:23
    supervisor 22676 / worker  7876   21:47:23–21:47:53
    supervisor 22984 / worker 14808   21:48:49–21:49:05
    supervisor  2872 / worker 22440   21:49:22–21:49:32

每次 stop 后均验证 pid 不再存活；最终 supervisor_pid 与 worker_pid 为空。

## 3. 验收清单

| 验收项 | 结果 | 证据 |
|---|---|---|
| 无人工介入完成≥3批差异实验 | PASS | 10 批已评分，见第 4 节 |
| 上一批结果触发下一批并保存理由 | PASS | 11 条 decisions，见第 5 节 |
| 模拟可恢复中断并续跑 | PASS | 21:40:42 worker 24696 被杀，任务恢复后完成，见第 6 节 |
| 关闭启动终端仍有响应落盘 | PASS | 21:40:02 启动，调用返回后 21:40:26 已 3 条完成，见第 7 节 |
| stop 同时停派发与监督器重启 | PASS | 三次 stop，最终 21:49:32，12 秒无新结果，见第 8 节 |
| 单 GPU worker | PASS | PowerShell 计数 1/1；领取 pid 串行，见第 9 节 |
| 15 分钟状态 / 小时快照 | PASS | 阈值测试 7/7；状态在每次转移即写；快照后推理继续，见第 10 节 |
| 外部 API 0 | PASS | meta.external_api_calls=0；请求 URL 全部 127.0.0.1 |
| 保留根隔离 | PASS | 使用 14 根，0121–0160 越界 0 |
| 唯一键、工作锁、恢复记录 | PASS | 57/57 唯一键；claimed_by/attempts/recoveries |
| 43 字段整表复用 | PASS | B004 129 格，字段来自 full_table.py 的 43 字段定义 |
| 研究记忆与原始结果路径 | PASS | RESEARCH_MEMORY.json/md、runs/B0xx.jsonl |

## 4. 批次与差异

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

差异点：

- B001/B008/B010 是开发根原文基线；B002/B005 是困难根短摘录；B003/B006 是删除对照；B004 是单根 43 字段整表；B007/B009/B011 是无 E 可用时的困难根全文回退。
- B004 的 129 格来自 3 个模型 × 43 字段，目标两格只有 7/12，而整表只有 19.4%，说明目标格饱和会掩盖整表损失。
- B006 的候选表记录 WI/OI variant_unavailable，实际只生成 O 的 3 个请求；没有伪造对照。

## 5. 决策链

| 时间 | 规则 | 选择 | 下一批 | 理由摘要 |
|---|---|---|---|---|
| 21:40:02 | R0 | T1 | B001 | 初始基线 |
| 21:40:38 | R1 | T2 | B002 | 基线 1.0 饱和，转困难根短摘录 |
| 21:41:06 | R4 | T3 | B003 | 摘录仍 0.833，转配对删除 |
| 21:41:48 | R5 | T4 | B004 | WI 0.0 < OI 0.5，删除特异，转整表 |
| 21:42:40 | R6 | T2 | B005 | 整表完成，扩下一组困难根 |
| 21:42:54 | R4 | T3 | B006 | 摘录仍 0.833，转配对删除 |
| 21:43:41 | R8 | T5 | B007 | 无剩余困难根支持 E，转全文回退 |
| 21:44:09 | R9 | T1 | B008 | 困难全文完成，扩剩余开发根 |
| 21:47:23 | R1F | T5 | B009 | 基线 0.917 本应 T2，但 T2 无合格任务，回退 T5 |
| 21:47:51 | R9 | T1 | B010 | 困难全文完成，扩剩余开发根 |
| 21:49:32 | R1F | T5 | B011 | 基线 1.0 本应 T2，但 T2 无合格任务，回退 T5 |

理由原文与 observation 在 decisions 表与 reports/RESEARCH_MEMORY.md。

## 6. 可恢复中断

- B002 第一任务 bc556ad3（qwen，cond E）被领取后，手工 taskkill /F PID 24696。
- 21:40:42 事件：worker_died 24696；task_recovered bc556ad3 previous_owner=24696 recoveries=1 attempts=1；worker_spawned 9872；worker_started 9872。
- 恢复后该任务 attempts=2、recoveries=1、status=done；results 中该 task_key 只有 1 行。
- B002 最终 6 请求、10/12 格、0.8333，无重复计分。
- 另有 recovered_with_existing_result 路径用于“结果已落盘但领取状态未清”的情况。

## 7. 脱离终端

- 21:40:02 在一个 Bash 调用中执行 vettctl.py start，返回 supervisor 24948、worker 24696。
- 该 Bash 调用随后结束（启动终端关闭）。
- 21:40:26 新调用读取状态：B001 已完成 3 条、queue claimed=1。
- 21:40:38 B001 评分 1.0，自动选择并冻结 B002。
- 说明新响应在启动终端结束后继续落盘。

## 8. 用户停止

三次完整停止验证：

- 21:44:20：supervisor 22104、worker 16724；requeued_claimed=1；12 秒后 results 48=48，pids 清空。
- 21:47:23：supervisor 20772、worker 23852；requeued_claimed=0；10 秒后无新结果。
- 21:49:32：supervisor 2872、worker 22440；requeued_claimed=0；8 秒后 results 54=54。

停止后：

- state=stopped，supervisor_pid 与 worker_pid 为空，claimed=0。
- worker_restarts 不再增加，说明 supervisor 重启职责同时停止。
- B011 的 3 个任务退回 queued，可在下次 start 继续。

## 9. 单 GPU worker

- 21:44:47 PowerShell 统计：worker_count=1（pid 23852），supervisor_count=1（pid 20772）。
- DB 中领取 pid 依次为 24696(6)、9872(24)、16724(8)、23852(4)、7876(6)、22440；同一时刻只有一个 worker 存活。
- 工作锁使用 BEGIN IMMEDIATE + 条件更新；领取记录写入 claimed_by、claimed_at、attempts。
- worker 启动时若发现已有存活 worker 会拒绝重复启动（worker_refused_duplicate）。

## 10. 计时器与快照

- 配置：status_interval_seconds=900，snapshot_interval_seconds=3600，claim_timeout_seconds=300。
- 状态除 15 分钟阈值外，在每次冻结/评分/决策时立即写；运行期间 STATUS.md 多次更新。
- 21:48:50 在推理进行中强制写快照；21:48:50 结果数 48，21:49:05 已到 52，证明快照后推理继续。
- 隔离测试 tests/test_timers.py 全部通过：

    status_due_at_901s true
    snapshot_due_at_3601s true
    status_file true
    status_not_due_after_write true
    snapshot_file true
    snapshot_not_due_after_write true
    status_not_due_at_10s true

说明：小时快照的 3600 秒阈值由隔离测试验证；生产运行未连续等待 60 分钟，21:48:50 与 21:49:48 的快照是显式调用，使用同一写入函数。

## 11. 外部 API、隔离、唯一键

- external_api_calls=0；所有 request_json.url 均为 http://127.0.0.1:11434/api/generate。
- 使用 14 个根：0002,0003,0008,0009,0010,0011,0013,0015,0021,0066,0085,0087,0096,0165。
- 保留根 0121–0160 越界 0。
- 任务 57 行、唯一键 57 个；结果 54 行；批次 11。
- 金标来自 scorecard.md；43 字段与历史 full_table.py 一致；证据索引 96 条仍 pending_human_review，人工确认 0。

## 12. 下一批任务（B011，已冻结）

| 根 | 局 | 模型 | 条件 | 字段 |
|---|---:|---|---|---|
| match_0015 | 2 | qwen2.5:7b-instruct-q4_K_M | O | inn2.total_runs, inn2.total_wickets |
| match_0015 | 2 | llama3.1:8b | O | inn2.total_runs, inn2.total_wickets |
| match_0015 | 2 | gemma2:9b | O | inn2.total_runs, inn2.total_wickets |

执行 resume 后从这 3 个 queued 任务继续；B011 评分后按 R9/R1F 规则决定下一批。

## 13. 现有结果样例

B001 match_0066 inn1 qwen 原文：

    {"inn1.total_runs": 64, "inn1.total_wickets": 5}

- 两格均对；耗时 2875 ms；prompt_eval_count 1475；digest 845dbda0…；options temperature=0, seed=42, num_ctx=8192, num_predict=300。

B003 match_0002 inn2 qwen 原文：

    {"inn2.total_runs": 252, "inn2.total_wickets": 8}

- B003 该条件 0/6 格，属于实际模型错误，不是格式失败。

## 14. 残余与边界

- B011 未跑完（3 个 queued），所以当前实验结论只基于 B001–B010。
- 人工盲审 0/40；证据索引 96 条仍待审，未并入结论。
- B006 的 WI/OI 变体不可用，实际只跑了 O；candidates 表有记录。
- B002/B005 的 83.3% 样本很小（12 格 / 6 格），不能单独外推。
- B009/B007 的 0% 说明这些根的目标格在文本中没有明确总分句，属于可答性缺口，不是单纯长上下文问题。
- 小时快照阈值是配置与隔离测试验证，未在生产等待满 60 分钟。

## 15. 证据文件

- 状态：[STATUS.md](reports/STATUS.md)
- 最新快照：[SNAPSHOT_20261117_214948.md](reports/SNAPSHOT_20261117_214948.md)
- 快照后继续推理：[SNAPSHOT_20261117_214850.md](reports/SNAPSHOT_20261117_214850.md)
- 研究记忆：[RESEARCH_MEMORY.md](reports/RESEARCH_MEMORY.md)
- 验收数据：[ACCEPTANCE_DATA.json](reports/ACCEPTANCE_DATA.json)
- 覆盖缺口：[COVERAGE_GAP.md](reports/COVERAGE_GAP.md)
- 批次原始结果：runs/B001.jsonl … runs/B011.jsonl
- 批次评分：reports/B001_SCORE.json … reports/B010_SCORE.json
- 决策与事件：state/workflow.db 的 decisions、events 表
- 操作命令：[COMMANDS.md](COMMANDS.md)
- 架构说明：[README.md](README.md)
