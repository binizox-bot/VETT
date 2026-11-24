# 夜间 Python 流水线（后台自持）

所有环节均为本地 Python 进程，外部 API 0。

| 文件 | 作用 |
|---|---|
| `vettctl.py`（vett_autonomous_20261117） | 启动/停止单实例 supervisor/worker；keep-awake 与 Ollama watchdog |
| `supervisor.py` / `worker.py` | 领取 SQLite 任务、调用 127.0.0.1:11434、落盘结果 |
| `night_build.py` | 核心 8 事件 × 3 通知 × 2 输入 × 3 模型（B213、B221–B227） |
| `night_more.py` | 整表回投、普通根整表、自然长文后备（`fulltable` / `fallback` / `ft_ordinary`） |
| `night_diag.py` / `night_diag2.py` | 最小诊断：认人、原投手、最终投手、旧值（B243–B245） |
| `night_watch.py` | 守护进程：每 60s 检查队列、ETA<5h 自动补批、每小时写进度、08:00 生成报告 |
| `night_report.py` | 从 workflow.db 生成 MORNING_ACCEPTANCE.md（不调用模型） |
| `start_night.py` | 用 DETACHED_PROCESS + CREATE_BREAKAWAY_FROM_JOB 启动守护进程 |

## 启动 / 状态 / 停止

    PY="/c/Users/PC/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/python.exe"
    cd "D:/Download/VETT_Cricket_Complete_Delivery_R19_20261017/VETT_INTEGRATED_20261113/analysis/vett_night_20261121"
    "$PY" start_night.py            # 启动夜间守护（脱离终端）
    "$PY" night_report.py --morning # 手动补生成报告
    cd ../vett_autonomous_20261117
    "$PY" vettctl.py status
    "$PY" vettctl.py stop

## 输出

- START_RECEIPT.md / NIGHT_PROGRESS.md / NIGHT_HOURLY.md / NIGHT_WATCH.log
- MORNING_ACCEPTANCE.md（08:00 或恢复后补生成）
- INCIDENT_*.md / NEEDS_HUMAN.md

## 跨重启

守护进程未注册开机自启；主机重启后需手动执行 `vettctl.py start` 与 `start_night.py`。这是已知边界，已在启动回执写明。
