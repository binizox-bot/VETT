from pathlib import Path
R=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
t=(R/"START_RECEIPT.md").read_text(encoding="utf-8")
t+="\n## 08:00 验收\n\n- MORNING_ACCEPTANCE.md 已生成（08:01，Asia/Shanghai），覆盖三张总表、失败/成功案例、480 条诊断、513 条整表审计、部分表/窗口表、24 行表与运行账本。\n- 夜间共 2,151 条结果；队列 04:47 耗尽，08:00 后无新任务。\n- 单字段分支 B251/B252 因输出 schema 错误被排除（INCIDENT_FIELD_PROMPT.md）。\n"
(R/"START_RECEIPT.md").write_text(t,encoding="utf-8")
print("ok")
