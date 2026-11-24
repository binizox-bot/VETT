# Codex 交换进度（2026-11-21T12:45:14+08:00）

| 批次 | 内容 | 计划位置 | Codex 已冻结 | DSH 已运行 | 收到响应 | 可评分 | 完整配对 | Codex 已复算 | 待人工审 |
|---|---|---:|---|---|---:|---:|---:|---|---:|
| B019+B022 | 8 个改判事件 × 3 条件 × 3 模型 | 8 场 | 历史已封存 | 72/72 | 72 | 72 | 24 组事件×模型 | 待 | 0/72 |
| B209Z | 2 场 pilot：定位 + 记账 × 3 模型 | 2 场 | 提案 v1（21 新 + 3 复用） | 21/21 | 21 | 21 | 3 定位 + 18 记账 | 待 | 0/21 |
| B211 | P_OI_probe 既有缓冲队列 | 多场 | 不适用 | 运行中 | - | - | - | - | - |

## 运行健康

- workflow: running；supervisor 21336 / worker 19052；worker restarts 30
- 队列: [{'status': 'claimed', 'n': 1}, {'status': 'done', 'n': 7660}, {'status': 'failed', 'n': 8}, {'status': 'queued', 'n': 335}]
- 外部 API: 0

## 协议核查（B209Z）

- prompt_sha 重算：21/21 一致；请求内 prompt_sha：21/21 一致。
- model digest 与 response meta：21/21 一致；响应 model 名：21/21 一致。
- 截断：最大 prompt 5,171 字符（约 1.3k token），num_ctx 8192，21/21 done_reason=stop，无截断。
- 发现并修复：声明 top_p=1.0 未随请求发送（worker 旧代码只发 temperature/seed/num_ctx/num_predict）；B209Z 21 条受影响，12:44 修复，之后请求带 top_p=1.0。temperature=0 下 argmax 不变，但声明与实际必须一致。
