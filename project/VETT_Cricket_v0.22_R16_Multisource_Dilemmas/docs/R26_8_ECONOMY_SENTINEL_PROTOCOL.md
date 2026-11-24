# R26.8 五场多模型经济哨兵协议

## 目标

本协议只校准当前 `r26_authority_binding_pilot/`，不修改题目、事实答案或难度结构。五个固定比赛为 `match_0066`、`match_0067`、`match_0021`、`match_0162` 和 `match_0220`，每场五题保持在一个请求中，避免为逐题调用重复发送同一长上下文。

配置文件：`eval_configs/r26_8_siliconflow_economy_sentinel5.json`。

模型顺序如下：

1. `Qwen/Qwen3.5-4B`：免费协议与弱基线；
2. `Qwen/Qwen3.5-35B-A3B`：低价主基线；
3. `stepfun-ai/Step-3.5-Flash`：异构长上下文基线；
4. `zai-org/GLM-5.3-Flash`：带 2K 思考预算的经济强模型锚点。

## Token 与故障安全契约

- 每场五题合并为一个请求，`target_batch_size=5`。
- `max_tokens=12288`；按每题 1500 token 估计，非思考模型保留约 1.60 倍输出余量，GLM 思考配置保留约 1.26 倍余量。
- 正证据、排除证据和类型边分别限制为最多 32、8、48 项，并要求数组内唯一。
- 输出必须恰好包含五个问题；解释不超过 480 字符。
- `max_retries=0`，无效 JSON、截断、超时、HTTP 错误均不自动重试。
- 第一场出现任何非 `OK` 批次时，停止该模型余下四场；其他模型仍可独立运行。
- 每个请求使用 SHA-256 checkpoint。成功结果和终止失败都可恢复，重复启动不会重新提交。
- 请求提交前原子创建 `.inflight.json`。若进程在等待服务商时退出，后续启动会将其判定为“提交状态不确定”并拒绝重发。
- 只有修改协议并使用新 `run_id`，才允许重新请求一个已经形成终止收据的批次。

这些措施不能保证外部服务永不超时，但能保证超时、截断、格式失败或进程中断不会触发自动重复消耗。

## 预算

当前零缓存保守估计：

| 模型 | 五场估计上限 |
|---|---:|
| Qwen3.5-4B | ¥0.0000 |
| Qwen3.5-35B-A3B | ¥1.9715 |
| Step-3.5-Flash | ¥0.7278 |
| GLM-5.3-Flash | ¥0.8758 |
| 合计 | ¥3.5751 |

Qwen3.5-35B-A3B 使用超过 128K 档位的最高价格做保守估算；实际低于 128K 时费用会更低。配置总预算门为 ¥3.80，任一模型也有独立预算门。

## 运行顺序

先执行只读预估：

```powershell
$env:PYTHONPATH = 'src'
python -m vett_eval.cli estimate --config eval_configs/r26_8_siliconflow_economy_sentinel5.json
```

确认预估后才运行：

```powershell
$env:PYTHONPATH = 'src'
python -m vett_eval.cli run --config eval_configs/r26_8_siliconflow_economy_sentinel5.json
```

中断后使用同一命令恢复。不得删除 `.inflight.json` 后盲目重跑；应先检查同批次的 `raw/`、checkpoint 和服务商账单。若确认请求从未到达服务商，再由人工建立新 `run_id`。

运行完成或部分完成后生成协议感知的多模型报告：

```powershell
$env:PYTHONPATH = 'src'
python -m vett_eval.cli analyze-r26-panel --config eval_configs/r26_8_siliconflow_economy_sentinel5.json
```

该命令只读取本地结果，不请求模型。输出为 `PANEL_ANALYSIS.json` 和 `PANEL_ANALYSIS.md`。

## 结果判定

分别报告：有效响应率、截断率、格式有效率、事实字段宏准确率、事实整行准确率、正证据 F1、排除证据 F1、类型边 F1、完整证据链 exact、事实加完整链 joint exact，以及 L1--L5 分级结果。协议失败不计为事实错误；无法评分的模型不得进入难度均值。
