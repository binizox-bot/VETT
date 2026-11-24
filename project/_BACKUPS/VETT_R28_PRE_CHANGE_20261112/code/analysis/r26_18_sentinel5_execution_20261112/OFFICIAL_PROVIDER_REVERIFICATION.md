# R26.18 Sentinel5官方条件复核

复核日期：2026-11-12（Asia/Shanghai）

## 结论

冻结合同中的模型身份、价格、上下文和接口字段与当前官方资料一致，可以进入本地临门门禁；这不替代用户授权、候选哈希、测试、预检或配置diff。

## 官方证据

- SiliconFlow模型广场当前列出`zai-org/GLM-5.3-Flash`，标注支持1M上下文：[模型广场](https://cloud.siliconflow.cn/open/models?types=chat)。
- SiliconFlow官方上新公告给出的价格为：缓存0.23元/M tokens、输入0.8元/M tokens、输出2.8元/M tokens，并说明支持1M上下文：[GLM-5.3-Flash公告](https://www.siliconflow.cn/news/ok5ja7brf921kgf1644yyedz)。
- 官方Chat Completions文档仍支持`response_format.type=json_schema`、`enable_thinking`和`thinking_budget`：[Chat Completions API](https://docs.siliconflow.cn/docs/api/chat-completions-post)。
- 官方快速上手继续使用OpenAI兼容的`https://api.siliconflow.cn/v1`：[快速上手](https://docs.siliconflow.cn/docs/userguide/quickstart)。

## 与冻结配置对照

| 项目 | 冻结配置 | 官方复核 | 结果 |
| --- | --- | --- | --- |
| 模型 | `zai-org/GLM-5.3-Flash` | 同名可用 | 一致 |
| 上下文 | 1,048,576 tokens | 1M | 一致 |
| 缓存价格 | 0.23元/M | 0.23元/M | 一致 |
| 输入价格 | 0.8元/M | 0.8元/M | 一致 |
| 输出价格 | 2.8元/M | 2.8元/M | 一致 |
| API根 | `https://api.siliconflow.cn/v1` | 官方OpenAI兼容根 | 一致 |
| 结构化输出 | `json_schema` | 官方支持 | 一致 |
| 推理参数 | thinking=true, budget=2048 | 官方字段支持 | 一致 |

## 边界

官方文档可能随时变化；本记录只绑定本次一次性执行尝试。任何后续run、重试或Pilot20都必须重新复核并重新授权。

