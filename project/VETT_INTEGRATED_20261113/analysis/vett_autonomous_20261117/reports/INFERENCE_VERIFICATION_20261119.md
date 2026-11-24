# 推理验收记录（2026-11-19）

## 1. 本机服务与模型

- Ollama: 0.40.16
- qwen2.5:7b-instruct-q4_K_M  digest 845dbda0ea48…  Q4_K_M  7.6B
- llama3.1:8b                 digest 46e0c10c039e…  Q4_K_M  8.0B
- gemma2:9b                   digest ff02c3702f32…  Q4_0    9.2B
- GPU: NVIDIA GeForce RTX 3070, 8192 MiB；空闲占用 840 MiB
- /api/ps（推理中）：qwen2.5 已加载，size=5,148,633,988，size_vram=5,148,633,988，context_length=8192，runner=llamacpp
  - 结论：单模型完整驻留 VRAM，未观察到 CPU/GPU 拆分。
- 解码配置沿用冻结值：temperature=0，seed=42，num_ctx=8192，num_predict 200/300/900。

## 2. 输入/输出预算

- 全库最大 prompt_eval_count = 2098（('match_0063', 'qwen2.5:7b-instruct-q4_K_M', 'O')），远小于 8192，未发现输入截断。
- done_reason 分布（截至 2026-11-19T15:45:15+08:00）：{"stop": 3535, "length": 11}
- parse_ok=0：12 条；空 raw：0 条。
- 10 条 llama3.1:8b probe_wickets 在 num_predict=200 时 done_reason=length，属输出长度上限类。
- 1 条 gemma2:9b full43（B004）done_reason=stop 但 JSON 不合法，属格式失败类，不是长度截断。

## 3. 43 字段整表检查（B004）

| 模型 | parse | done_reason | eval_count | num_predict | prompt_eval |
|---|---|---:|---:|---:|---:|
| qwen2.5 | ok | stop | 539 | 900 | 1,772 |
| llama3.1 | ok | stop | 511 | 900 | 1,725 |
| gemma2 | fail | stop | 522 | 900 | 1,802 |

- 三个模型都没到 900 输出预算；gemma 的失败是 JSON 结构，不是截断。
- 输入 prompt_eval 均 < 2k，无 8192 上下文截断风险。

## 4. 时间字段

- Ollama 返回 load_duration / prompt_eval_duration / eval_duration / total_duration（纳秒）；
- 工作流换算为 load_ms / inference_ms，并另记墙钟 duration_ms；
- 例：qwen 首次加载 load_ms≈15,167，后续同模型块 load_ms≈5；inference_ms≈483。

## 5. 隔离与试跑

- llama probe_wickets 的 200 输出上限类已隔离为试验 B151（num_predict=320，3 任务）。
- 未改动冻结配置；B151 使用独立 field_scope probe_wickets_p320 和新配置身份。
- 未自动下载模型、未升级 Ollama。
