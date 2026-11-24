# EVIDENCE_AUDIT：证据修复与正控

## 1. 修复项

| 项 | 旧问题 | 本轮 |
|---|---|---|
| match_0014 总出局 | 证据标错局 | 改为 Harbor Peninsula XI closed on 226 for 7 |
| match_0016 总出局 | 证据标错局 | 改为 Crestline XI closed on 138 for 3 |
| 旧汇总状态 | 短版漏 Note | B/C 均含 the bowling figures above are the pre-revision record |
| 字段 | 旧 _runs 歧义 | 统一 wickets_credited / bowling_runs_conceded / innings_wickets_lost |

## 2. 构建检查（6/6 通过）

- B 去掉 [EVIDENCE] 后与 A 逐字一致。
- 六句证据：出局、A 旧汇总、B 旧汇总、正确终局、Note、通知；无重复。
- B 不含更新后的 figures 短语。
- 金标五项与证据一致；0014/0016 的终局分别 7、3。

## 3. 正控

- Lina gemma：original/explicit 五项全对，derivation 旧值 → 题面能区分“抄新值”和“应用改判”。
- Lina qwen：两人 wickets 对，但 total 恒定 9；说明 total 字段仍是弱点。
- scorer 能区分：两人对、只改一人、方向反、两人对但总数错、格式失败。

## 4. 复核

复核者：构建者本人；范围：6 场证据句、总出局、旧值、金标；未做独立第二人复核。  
未解决：C 的 extraction 字段常缺/错，导致 Python 更新无法执行；这是模型输出协议问题，不是证据缺口。
