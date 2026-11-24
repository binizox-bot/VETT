# Held-out 提交协议（40 题）

## 1. 范围

- R28 held-out = **40 题**，位于 `03_build/dataset_r28/held_out/`，**不进入公开包**（公开包 roots 仅 `public/` 与 `variants/`）。
- held-out 每题独立 `scene_id`（`r28scene_held_###`），与公开 64 场不重叠。
- 公开发布物不得包含：held-out 的 `public_instance.json`、`private_gold.json`、`certificate.json`、`audit/*`、任何 `r28h_####` 题号或 held-out 文本片段。

## 2. 评分方（server-side）

服务端持有：

```
03_build/dataset_r28/held_out/<item_id>/private_gold.json
03_build/dataset_r28/held_out/<item_id>/certificate.json
03_build/dataset_r28/build_index.json
```

服务端用本包 `held_out_score.py` 评分；脚本只读 `held_out/`，不读取 `private/`，不需要网络。

```powershell
D:\Conda\python.exe held_out_score.py `
  --predictions submissions/team_x.jsonl `
  --dataset ..\..\03_build\dataset_r28 `
  --out scores/team_x.json
```

## 3. 提交格式（submission contract）

`predictions.jsonl`，每行一个 JSON 对象，**恰好 40 行**，每行：

```json
{"item_id":"r28h_XXXX","record":{"batter_runs":0,"bowler_runs":0,"counts_in_over":true,"delivery_status":"LEGAL","dismissal":"NONE","ledger.BATTER":0,"ledger.BYE":0,"ledger.LEG_BYE":0,"ledger.NO_BALL_EXTRA":0,"ledger.PENALTY":0,"ledger.WIDE_EXTRA":0,"total_runs":0}}
```

硬性规则：

- `item_id` 必须与 held-out 的 40 个 ID 一一对应；缺/多/重复/未知 ID → 整份提交 invalid（exit 2）。
- `record` 必须含 12 个字段，类型与取值符合 solver schema；缺字段 → invalid。
- 不接受 `gold`、`certificate`、`private`、路径或任何辅助字段作为输入；不允许把公开集答案映射到 held-out。
- 提交方不得获得 held-out 的 gold/证书；服务端不回传逐题 gold，只回传聚合指标与（可选的）逐题 0/1 错误掩码。

## 4. 指标（与主实验一致）

- **informative field accuracy**：9 个信息字段（不含 `ledger.BYE/LEG_BYE/PENALTY`）的 cell 准确率；主指标。
- **all-field accuracy**：12 字段 cell 准确率；报告但不作主指标。
- **record-exact**：整条 12 字段完全一致的比例；R28 主实验为 5/638=0.78%，held-out 上同样只作描述。
- 不计算“难度提升”：R28 的难度主张已撤回（见数据卡 B4），held-out 只用于泛化/误差诊断，不用于“比 R26.15 难”的结论。
- 统计不确定度：n=40 很小，报告 Wilson 95% CI，不做强推断。

## 5. 服务端约定

1. 接收提交后先做 schema/ID/hash 校验，再评分；invalid 不进入排行榜。
2. 每个团队最多 5 次提交；保留每次提交的 sha256。
3. 服务端记录 `dataset build_index.sha256 = dd6de16a…`、`held_out` 文件哈希、评分脚本哈希；评分脚本版本变化必须重跑全部历史提交。
4. 不向提交方暴露 held-out gold、证书 span、`r28h_` 文本；只返回聚合指标与错误掩码。
5. 评审复现：服务端运行 `held_out_score.py --self-check`（只校验 40 题 gold 结构，不打印内容），再用同一脚本评分。

## 6. 公开包检查

提交/发布前运行：

```powershell
D:\Conda\python.exe reproduce.py --check
D:\Conda\python.exe held_out_score.py --self-check --dataset ..\..\03_build\dataset_r28
```

并检查公开包中不存在 `r28h_` 或 `held_out/` 路径；本包不包含 held-out 内容。
