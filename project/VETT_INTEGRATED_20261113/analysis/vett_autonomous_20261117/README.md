
# VETT 本地自治实验工作流

日期：2026-11-17 部署；2026-11-18 升级 v2 并持续运行。外部 API：0。

## v2 可靠性层（2026-11-18）

- 任务身份：model_digest + decode_json + input_version + prompt_version + replicate_id + prompt_sha；旧键到新键写入 task_key_map，不整体重跑。
- attempts 表：每次领取独立 attempt_id，记录 claimed/sent/responded/persisted/accepted/failed/uncertain；不宣称 exactly-once。
- 心跳独立于长请求：worker 每 5 秒写心跳；只有心跳超过 300 秒才判死，不因单次请求超过 150 秒杀进程。
- 评分与推理分离：results.scoring_version；vettctl.py rescore 只用现有 raw_output 离线复算。
- 决策：source_batch_id、source_result_ids、rule_version、trigger_metrics_json、next_batch_id。
- 状态：workflow_state / batch_state / task_state 分开；stopped 时显示 interrupted_batch，不显示 running。
- 分支：A_field_probe、B_cross_innings、S_coverage_sweep、C_adjudication、P_field_sweep（覆盖组字段探针）。
- 报告：每小时 HOURLY_<stamp>.md；08:00 STAGE_<date>_0800.md；都不停止推理。

## 0. 当前结果

- 已评分 10 批（B001–B010），第 11 批 B011 已冻结并有 3 个待跑任务。
- 本地请求 54 次，结果行 54，任务行 57，任务键 57/57 唯一。
- 使用 14 个比赛根；保留根 0121–0160 零越界。
- 研究记忆、状态、快照、原始结果均在 reports/ 与 runs/。

## 1. 环境结论

实际检查到的入口：

- DSH CLI 0.2.2-rc.1：dsh web、dsh headless "task"、dsh tui --resume <session>、dsh plugin。
- 会话内定时任务工具可用（schedule_create / schedule_edit）。
- 但 DSH headless 与聊天入口都会驱动外部模型，不能满足本实验“外部 API 0”。
- 因此实验驱动使用本地 Python 进程，直接调用 127.0.0.1:11434 的 Ollama；DSH 仅保留交互与恢复入口。
- Python：C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe（3.12.14，sqlite 3.53.1）。
- Ollama 0.40.16；qwen2.5:7b-instruct-q4_K_M、llama3.1:8b、gemma2:9b 均在本地，digest 已写入每条结果。
- 系统：Windows 10.0.26200，MSYS Bash。

这一选择使工作流不依赖聊天会话存活，也不需要 DSH 进程常驻。

## 2. 架构

    vettctl.py  start/status/pause/resume/stop/snapshot/report/coverage
        |
        | DETACHED_PROCESS + CREATE_NEW_PROCESS_GROUP + CREATE_BREAKAWAY_FROM_JOB
        v
    supervisor.py  (单实例；PID 文件 + DB meta)
        |- planner.py     选择模板、检查资格、冻结清单、写决策
        |- scorer.py      批次评分、配对、反例、研究记忆
        |- reporting.py   15 分钟状态、小时快照、覆盖审计
        |- worker.py      唯一 GPU 推理进程，一次只领取一个任务
                              |
                              v
                         Ollama 127.0.0.1:11434

- supervisor 负责调度、恢复、状态、快照、评分、决策；这些都在 CPU 上完成。
- worker 是唯一推理进程；启动时检查 meta.worker_pid，若已有存活 worker 则拒绝重复启动。
- 快照与状态写入由 supervisor 完成，worker 继续推理，互不阻塞。

## 3. 每轮循环

1. 读取研究目标、历史结果、证据索引、覆盖缺口和待办：config/research_scope.json、reports/RESEARCH_MEMORY.json、reports/COVERAGE_GAP.md、state/workflow.db。
2. 为下一批写明假设、比赛与字段、对照条件、评分、来源、预计成本：planner 的 T1–T5 模板和批次 DESIGN.md。
3. 检查样本与变体资格并冻结：held-out 拒绝、根/局重复检查、变体可用性检查、提示哈希去重；不合格候选写入 candidates 表并继续下一个候选。
4. 调用本机模型并保存真实请求、原始响应、digest、参数、耗时、状态：tasks.prompt、results.request_json、results.response_meta_json、results.raw_output、runs/<batch>.jsonl。
5. 批次完成后自动评分：reports/<batch>_SCORE.json、_PAIRED.json、_COUNTEREXAMPLES.md。
6. 按决策规则自动扩样、追加对照或整表验证，再冻结下一批：decisions 表 + reports/RESEARCH_MEMORY.md。

## 4. 状态库

state/workflow.db（SQLite，WAL）：

- meta：state、paused、stop_requested、supervisor_pid、worker_pid、worker_restarts、batch_seq、last_status_at、last_snapshot_at、external_api_calls。
- batches：批次、模板、假设、理由、design_json、清单路径与 sha256、状态、准确率、成本。
- tasks：task_key 主键、batch_id、match、innings、model、cond、字段范围、prompt、prompt_sha、text_sha、num_predict、status、attempts、claimed_by、claimed_at、recoveries、error。
- results：task_key 主键、raw_output、parsed_json、parse_ok、score_json、correct、duration_ms、request_json、response_meta_json。
- decisions：observation、rule_id、action、next_batch_id、rationale。
- events：启动、冻结、领取、完成、恢复、停止、快照、覆盖审计。
- candidates：不合格候选及原因。

## 5. 唯一键、工作锁与恢复

- task_key = sha256(match | innings | model | cond | field_scope | prompt_sha256)。
- 领取使用 BEGIN IMMEDIATE 事务，条件更新 status='queued'；同一任务只会被一个 worker 领取。
- 领取记录：claimed_by、claimed_at、attempts；被中断后 recoveries+1，attempts 继续累加。
- 恢复规则：worker 死亡或心跳超过 150 秒，supervisor 终止旧进程并把 claimed 任务退回 queued；若结果已落盘则直接标记 done 并记录 recovered_with_existing_result，避免重复推理。
- 停止规则：stop 先写 stop_requested，再终止 supervisor 与 worker 进程树，最后把 claimed 任务退回 queued；stop_requested 清零。
- 幂等：results.task_key 主键；worker 处理前再查一次，已有结果则记 duplicate_result_ignored。

## 6. 模板与决策

模板：

- T1_baseline_o：开发根，原文，目标两格（total_runs、total_wickets），3 模型。
- T2_hard_excerpt：困难根，三句证据摘录 E，目标两格。
- T3_matched_deletion：同一根 O / 删同局局中比分 WI / 删另一局总分 OI，配对对照。
- T4_full_table：单根 43 字段整表，复用 attribution_update_and_full_table/full_table.py 的 43 字段定义。
- T5_hard_fulltext：当困难根没有明确总分句、E 不可用时，用原文 O 在未用困难根上继续。

规则：

- R0 初始基线；R1 基线≥0.90 转 T2；R2 基线<0.90 转 T3。
- R3 摘录≥0.90 转 T4；R4 摘录<0.90 转 T3。
- R5 WI<OI 转 T4；R6 无特异性转 T2。
- R8 无可用 E 根转 T5；R9 转回 T1 扩开发根。
- 模板产不出合格任务时按 T2/T3/T4→T5→T1 回退，并记录 R*F 规则与回退理由。

## 7. 隔离与金标

- 方法开发只用 pools.dev 与 pools.hard；保留根 0121–0160 被 planner 一律拒绝。
- 金标来自 scorecard.md，经 pilot_lib.parse_scorecard_full 解析；43 字段与历史 full_table.py 一致。
- 证据索引 96 条仍为 pending_human_review；人工确认 0，未把待审当已确认。
- 220 场原始数据、scorecard、R28、旧报告均只读；新产物全部在本目录。

## 8. 目录

- config/research_scope.json：目标、模型、池、规则、计时器、覆盖基线。
- batches/：冻结清单 B0xx.json 与可读设计 B0xx_DESIGN.md。
- runs/：每批真实请求的原始结果 JSONL。
- reports/：STATUS、SNAPSHOT、RESEARCH_MEMORY、SCORE、PAIRED、COUNTEREXAMPLES、COVERAGE_GAP、ACCEPTANCE_DATA。
- logs/：supervisor.log、worker.log、supervisor_errors.log。
- state/：workflow.db、supervisor.pid、heartbeat。
- tests/test_timers.py：隔离数据库的计时器阈值测试。

## 9. 计时器

- 状态：每 900 秒到期检查；另外每次冻结、评分、决策都会立即写状态，因此实际更新频率高于 15 分钟。
- 快照：每 3600 秒；快照写入在 supervisor 内完成，worker 继续推理。
- 计时器阈值在隔离数据库用 2 秒级测试验证，见 ACCEPTANCE.md。

## 10. 边界

- external_api_calls 全程 0；所有请求 URL 均为 http://127.0.0.1:11434/api/generate。
- 不使用付费 API；不写入 220 场源数据；不修改 R28 历史结论。
- 人工盲审尚未完成的部分继续标注 pending，不并入自动结论。
