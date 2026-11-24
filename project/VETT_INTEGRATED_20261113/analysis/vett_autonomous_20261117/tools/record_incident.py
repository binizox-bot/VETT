
from pathlib import Path
from datetime import datetime
inc = """# Incident: overnight run died at 2026-11-18 19:13

## Symptom

- Last result and last event: 2026-11-18T19:13:30+08:00.
- Supervisor 26932 and worker 28832 were both dead by 2026-11-19 00:23.
- state meta still said running, with stale pids.
- Ollama endpoint 127.0.0.1:11434 was down (connection refused); no ollama.exe process and no Windows service.
- Logs empty (no traceback); host boot time 2026-11-18 09:08, so no reboot.
- Consistent with host idle sleep / Ollama stop, not a code exception.

## Impact

- Continuous segment 2026-11-18 14:50:24 to 19:13:30 = 4h23m, NOT 8h.
- Five hourly reports were produced (14:50, 15:50, 16:50, 17:50, 18:50).
- 8h milestone at 22:50 was NOT reached.
- 08:00 stage report did NOT run.

## Fix applied

1. Supervisor keep-awake thread: SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED) every 60s.
2. Ollama watchdog: supervisor pings /api/tags every 60s and restarts ollama serve if down.
3. Fresh continuous segment clock: segment_started_at set on start; 8h is measured from the new segment.
4. Restarted 2026-11-19 00:24:45 with supervisor 12068 / worker 26892; B083 resumed.
5. New 8h milestone: 2026-11-19 08:24:45; 08:00 stage report falls inside this segment.

## Evidence

- reports/HOURLY_20261118_145024.md ... HOURLY_20261118_185027.md
- state/workflow.db events: max event 2026-11-18T19:13:30
- logs/supervisor.log and logs/worker.log empty at death
- logs/ollama.log
"""
Path("INCIDENT_20261118_1913.md").write_text(inc, encoding="utf-8")
a = Path("ACCEPTANCE_V2.md")
t = a.read_text(encoding="utf-8")
if "## K. 夜间中断与重启" not in t:
    t += """

## K. 夜间中断与重启

- 旧连续段 2026-11-18 14:50:24–19:13:30：4h23m，5 份小时报；**8 小时未达成**。
- 死因：主机空闲休眠导致 supervisor/worker 停止，同时 Ollama 服务停止；日志无异常，主机未重启。
- 修复：SetThreadExecutionState keep-awake；Ollama 每分钟 watchdog；新 segment_started_at。
- 新连续段：2026-11-19 00:24:45 起，supervisor 12068 / worker 26892；8 小时里程碑 **08:24:45**，08:00 阶段报告落在本段内。
"""
    a.write_text(t, encoding="utf-8")
print("incident recorded")
