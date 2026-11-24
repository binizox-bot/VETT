# VETT 晚间简报（2026-11-19）

绝对路径：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117

## 当前状态

- workflow: running；batch: running
- supervisor 15312 / worker 14024；worker heartbeat 15.8 秒
- 结果 3618；queue {"claimed": 1, "done": 3618, "queued": 35}
- 两次快照结果增量：34（3584 → 3618）

## 本次新增与配对

- 恢复后新增结果：116
- P 三元组：552/552 完整；缺 0
- B151 llama P320 试验：3 条，parse 2/3，correct 2/3

## 每模型吞吐与加载（恢复后）

- gemma2:9b: n=38，load_avg=986.3 ms，inference_avg=953.6 ms，load>1s=4，load<100ms=34
- llama3.1:8b: n=41，load_avg=1663.7 ms，inference_avg=643.0 ms，load>1s=5，load<100ms=36
- qwen2.5:7b-instruct-q4_K_M: n=37，load_avg=1504.2 ms，inference_avg=317.3 ms，load>1s=4，load<100ms=33

## GPU / CPU

- RTX 3070 8192 MiB；/api/ps 中 qwen size_vram=5,148,633,988，context=8192；单模型全量 VRAM，无 CPU 拆分。
- 派发已改为同模型连续：每个模型每批只加载一次，块内 load≈5ms。

## 失败与恢复

- 09:10:15 主机重启终止旧进程；15:42 用 auto_recover 恢复，非代码异常。
- uncertain attempts：5；主机重启与受控 stop 的未确认请求已保留
- llama probe_wickets 在 num_predict=200 有 10 条 length；B151 改 320 后 2/3 parse，match_0027 仍 length。
- gemma2 B004 43 字段 JSON 不合法，done_reason=stop，非截断。

## 余额与续航

- probe_cursor 188/360；剩余 unit 约 172，每 unit 最多 9 任务。
- 按新分组吞吐（约 600–700 条/小时）估算 2–3 小时；按旧 240 条/小时估算 6–7 小时。
- 当前运行批次：B154 P_field_sweep；后续任务可继续领取。

## 案例卡

- 发布版关联（含直接发布文本链接）：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\reports\CASE_CARD_PUBLICATION.md
- 反例：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117\reports\CASE_CARD_COUNTEREXAMPLE.md
