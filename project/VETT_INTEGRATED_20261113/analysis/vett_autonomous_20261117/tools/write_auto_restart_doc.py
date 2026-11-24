
from pathlib import Path
doc = r"""# 中断自动恢复与 watchdog

## 入口

- 当前用户 Startup：C:\Users\PC\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\VETT_AutoRecover.cmd
- 触发：用户登录（ONLOGON），不是开机服务；计划任务创建被拒绝，未提权。
- 该 cmd 启动 tools/auto_watch.py（pythonw，隐藏窗口）。

## watchdog 行为

- 单实例锁：state/auto_watch.pid；重复启动会记 already running pid=...; exit duplicate。
- 每 60 秒检查一次 supervisor pid。
- 以下情况不重启：stop_reason=user_stop、paused=1、auto_start_disabled=1。
- supervisor 不在时调用 tools/auto_recover.py：等待/启动 Ollama，再 vettctl start。
- 启动失败后 90 秒再试，不覆盖用户 STOP。

## 已验证

- watchdog 已启动：pid 9756。
- 重复执行 Startup 入口：新进程识别锁并退出，仍在运行的 watchdog 只有 1 个。
- 当前 supervisor 16272 / worker 13912 正常，watchdog 不干扰。

## 边界

- 主机重启后需要用户登录才触发；若要开机即启，需要管理员级计划任务/服务。
- 用户显式 stop/pause 后不会自动恢复，符合用户 STOP 语义。
"""
Path("reports/AUTO_RESTART.md").write_text(doc, encoding="utf-8")
print("written")
