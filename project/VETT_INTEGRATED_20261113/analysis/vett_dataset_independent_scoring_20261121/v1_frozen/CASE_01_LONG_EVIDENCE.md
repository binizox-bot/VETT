# 案例 1：发布版长文证据定位

- 稳定 ID：`vett-dev-v1-0001`
- 比赛根：`match_0047`，第一局，Ridgefield。
- 用途：开发；不在方法保留根 `match_0121`–`match_0160`。
- 抽样类型：普通开发样本。不是按历史错误挑选；历史 A/B 中三个模型均答对。选择它是因为发布版全文、证据窗、三模型历史输出和记分表字段都齐全。
- 字段格：`inn1.total_runs`、`inn1.total_wickets` → scorecard 第一局 `Total` 行、`Value` 列：`337/8 (50.0 Overs)`。
- 发布版原句：`Hayden Brooks added a brief 11, Isaac Lane stayed unbeaten with 9, Jordan Dale helped finish the last over, and Ridgefield closed on 337 for 8.`
- 源字符范围：`3501:3644`，0-based、end-exclusive。
- 输入：`c00` 为完整发布版原文；`c01` 为从同一原文逐字截取的证据句。不是重渲染，不是仅比赛根映射。
- 题目实际考查：最终答案在正文直接写出；不需要跨句更新。全文中有第一局中间比分和第二局 `222/10` 等竞争比分，因此全文条件仍包含检索干扰。
- 通知/旧值：不适用。
- 后半段矛盾检查：不适用（无通知）；发布版结尾与终局值一致。
- 审核状态：自动逐字与记分表核对通过，人工语义复核仍为 `pending_human_review`。
