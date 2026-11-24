# 跨重启恢复入口

- schtasks ONLOGON 创建被拒绝（Access is denied），未强行提升权限。
- 改用当前用户 Startup 文件夹：C:\Users\PC\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\VETT_AutoRecover.cmd
- 触发：用户登录（ONLOGON），不是开机服务。
- 目标：tools/auto_recover.py；检查单实例、user_stop、auto_start_disabled，等待/启动 Ollama，再调用 vettctl start。
- 测试：停止时启动成功（supervisor 15312）；运行中再次执行记录 already running pid=15312; skip。
