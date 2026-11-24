
# VETT 工作流操作命令

工作目录：

    cd "D:/Download/VETT_Cricket_Complete_Delivery_R19_20261017/VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117"

解释器（必须用这个，系统 python 是 WindowsApps 占位）：

    PY="/c/Users/PC/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/python.exe"

## 启动（脱离终端）

    "$PY" vettctl.py start

- 以 DETACHED_PROCESS + CREATE_NEW_PROCESS_GROUP + CREATE_BREAKAWAY_FROM_JOB 启动 supervisor。
- 返回 supervisor_pid、worker_pid、队列计数；关闭启动终端后仍继续。
- 单实例：若已有存活 supervisor，会返回 already_running。

## 状态

    "$PY" vettctl.py status          # 完整 JSON
    "$PY" vettctl.py status --md     # 可读摘要
    "$PY" vettctl.py report          # 批次、决策、下一批任务
    "$PY" vettctl.py tick            # 立即写一次状态

状态文件：reports/STATUS.json、reports/STATUS.md。

## 暂停 / 恢复

    "$PY" vettctl.py pause
    "$PY" vettctl.py resume

- pause 只停止派发；当前任务可完成，supervisor 继续心跳与状态。
- resume 清除 paused，继续处理已冻结批次。

## 停止

    "$PY" vettctl.py stop

- 写 stop_requested，终止 supervisor 进程树与 worker，等待退出。
- 把 claimed 任务退回 queued（recoveries+1），把 state 置为 stopped，清空 pid。
- 停止后不会再派发，也不会再自动拉起 worker。

## 快照

    "$PY" vettctl.py snapshot

写 reports/SNAPSHOT_<时间戳>.md 和 SNAPSHOT_LATEST.md；不影响推理。

## 离线复算（不调用模型）

    "$PY" vettctl.py rescore

只用现有 raw_output 重算 results.score_json 与批次准确率，写 scoring_version=score-v1-offline。

## v2 状态字段

status 输出区分：

- workflow_state：running / paused / stopped / idle_no_valid_tasks
- batch_state：running / interrupted / frozen / idle
- task_state：queued / claimed / done / failed
- run：elapsed_hours、load_ms、inference_ms、scoring_ms、plan_ms、waiting_ms_est、attempts、uncertain_attempts

stopped 时 batch_state=interrupted，并显示 interrupted_batch，不再把中断批次写成 running。

## 覆盖审计

    "$PY" vettctl.py coverage --reason "manual audit"

写 reports/COVERAGE_GAP.md / .json，列出已覆盖、未建方向、保留根、未用困难根。

## 重置（危险）

    "$PY" vettctl.py reset --yes

仅在 supervisor 不在运行时使用；删除 state/workflow.db、batches/、runs/、reports/，重建空库。

## 日志

    tail -n 50 logs/supervisor.log
    tail -n 50 logs/worker.log
    tail -n 50 logs/supervisor_errors.log

## 典型检查

    "$PY" - <<'EOF'
    import sqlite3
    c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row
    print([dict(r) for r in c.execute("SELECT batch_id,template,status,accuracy FROM batches ORDER BY seq")])
    print({r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")})
    EOF

## 计时器测试

    "$PY" tests/test_timers.py

使用临时数据库，不触碰生产状态。

## 运行约束

- 只调用 127.0.0.1:11434；不要改 ollama.url 为外网地址。
- 只允许一个 worker；不要手工再启动 worker.py。
- 修改 planner/worker/supervisor 后必须 stop 再 start，运行中的进程不会热加载。
