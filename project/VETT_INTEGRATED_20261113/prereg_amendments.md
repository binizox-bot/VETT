# Prereg amendments

## 2026-11-13 — 新增 revision_inline 变体（在跑该变体之前声明）

- 原因：预注册的主要终点覆盖依赖传播（closure），但没有覆盖“版本化”本身。
  RQ3 主张的是 Versioned Event Ledger，需要一个“旧值仍在文本中、后文正式更正”的场景。
- 变更：pilot10 每场新增第 7 个变体 revision_inline：
  正文末尾加入一条“Scorers' correction”，把 match.pom 从原值改为另一名球员；
  gold 只改 match.pom，其余字段不变；changed_fields=["match.pom"]。
- 影响：不改变已冻结的 6 个变体与 49 字段；不改变已有 eval 行的文本。
- 判定（新增次要终点）：revision_inline 的 pom 正确率与 direct 的旧值残留率。
## 2026-11-13（第二次）— 评测限 28 个 core 字段

- 原因：49 字段输出约 900–1100 tokens，单次调用约 25–30 s，540 次调用需 4 h+；
  与 23× 输出瓶颈一致。pilot 是探索性验证，不需要全字段。
- 变更：eval 默认 --field-set core，只评分 28 个核心字段
  （4 比赛级 + 每局 total_runs/wickets/extras/wides/byes/leg_byes/no_balls/bat_sum/bowl_charged/max_partnership
  + 每局最佳击球 runs + 每局最佳投球 figures）。
- 不改数据文件；49 字段仍完整保留，后续可 --field-set full 复跑。
