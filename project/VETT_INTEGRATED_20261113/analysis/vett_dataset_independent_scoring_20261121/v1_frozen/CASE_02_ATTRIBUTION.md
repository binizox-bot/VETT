# 案例 2：归属改判记账

- 稳定 ID：`vett-dev-v1-0002`
- 比赛根：`match_0003`，第一局，Brandon Hale 的出局归属；8 个既有归属事件之一。
- 用途：开发；不在方法保留根 `match_0121`–`match_0160`。
- 抽样类型：历史错例。历史 `C_change` 中 Qwen 保留旧值，Llama/Gemma 正确；用于复查“通知到最终 figures 的传播”。
- 原始格：Evan Clarke bowling 行 `R=28, W=4`；Connor Reed bowling 行 `R=28, W=1`；第一局 Total `164/8`；Brandon Hale dismissal 行原记为 `b Evan Clarke`。
- 旧值时点：pre-revision scorecard snapshot。
- 三臂固定同一事件、同一旧值：
  - `c10` 正式改判：Evan wickets `4→3`，Connor wickets `1→2`。
  - `c11` 维持：保持 `4`、`1`。
  - `c12` 无通知：保持 `4`、`1`。
- 应保持字段：Evan runs `28`、Connor runs `28`、innings total wickets `8`。
- 题目实际考查：最终改判值没有直接写出。`c10` 需要跨句读取旧值，再应用一次 A−1/B+1；旧值句与通知句之间没有其他相关事件。旧 runs 恰好相等（28/28），可检测人物/字段错位。
- 来源分类：旧值与原始归属来自 scorecard；三臂通知是局部受控编辑。不是发布版原文，不是重渲染，也不是仅比赛根映射。
- 后半段矛盾检查：三个模型输入在通知后直接结束，没有残留旧 figures 的最终汇总。
- 审核状态：字段、算术和输入逐字检查通过；通知语义仍标 `pending_human_review`。
