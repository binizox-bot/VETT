# q4 单因素对照：中和 N2 更新祈使句

## 0. 首页结论

- 原版全文 q4 可恢复数值口径 **20 条完全新值**；严格键名口径 19 条（有 1 条把空格写成下划线，数值可恢复）。
- 中和后，这 20 条里回到完全旧值 **4** 条；仍完全新值 9，单边混合 7，其他 0，格式失败 0。

### 各模型全文—窗口差距（完全旧值，/8）

| 模型 | 原版全文 | 原版窗口 | 原版差 | 中和全文 | 中和窗口 | 中和差 |
|---|---:|---:|---:|---:|---:|---:|
| Qwen | 0/8 | 2/8 | -2 | 1/8 | 5/8 | -4 |
| Llama | 0/8 | 0/8 | 0 | 6/8 | 1/8 | 5 |
| Gemma | 0/8 | 8/8 | -8 | 0/8 | 8/8 | -8 |

## 1. 冻结文本差异

- 16 条差异（8 场 × 全文/窗口），只删除 “Update both bowlers' figures; ”，保留 “runs and innings total do not change.”；逐条位置见 NEUTRAL_DIFFS.md/json。

## 2. 原版分类（q4 旧值问题，N2）

| 输入 | 完全旧值 | 完全新值 | 只有原投手−1 | 只有新投手+1 | 其他 | 格式失败 | 总数 |
|---|---:|---:|---:|---:|---:|---:|---:|
| N2_F | 0 | 20 | 2 | 2 | 0 | 0 | 24 |
| N2_W | 10 | 7 | 0 | 5 | 2 | 0 | 24 |

- 两表分类均以可恢复数值为准；严格键名失败：原版 4/48、中和 4/48（均为下划线代替空格），数值全部可恢复。


## 3. 中和后分类

| 输入 | 完全旧值 | 完全新值 | 只有原投手−1 | 只有新投手+1 | 其他 | 格式失败 | 总数 |
|---|---:|---:|---:|---:|---:|---:|---:|
| N2_F | 7 | 9 | 0 | 8 | 0 | 0 | 24 |
| N2_W | 14 | 5 | 0 | 3 | 2 | 0 | 24 |

- 严格键名通过 44/48；严格失败但可恢复 4 条；数值仍不可恢复 0 条。
  - strict_fail match_0015 Llama N2_F keys={'Caleb_Rourke_wickets', 'Noah_Grant_wickets'} recovered=(4, 2)
  - strict_fail match_0030 Llama N2_F keys={'Owen_Price_wickets', 'Logan_Vale_wickets'} recovered=(4, 2)
  - strict_fail match_0030 Llama N2_W keys={'Owen_Price_wickets', 'Logan_Vale_wickets'} recovered=(3, 3)
  - strict_fail match_0012 Qwen N2_F keys={'Lucas_Vale_wickets', 'Caleb_Brooks_wickets'} recovered=(3, 3)

## 4. 原版完全新值 → 中和后

| 比赛 | 模型 | 中和后类别 |
|---|---|---|
| match_0003 | Gemma | fully_new |
| match_0003 | Llama | fully_old |
| match_0003 | Qwen | fully_new |
| match_0008 | Gemma | fully_new |
| match_0008 | Llama | fully_old |
| match_0008 | Qwen | only_new_plus1 |
| match_0010 | Gemma | only_new_plus1 |
| match_0010 | Qwen | only_new_plus1 |
| match_0012 | Gemma | fully_new |
| match_0012 | Llama | fully_new |
| match_0012 | Qwen | fully_new |
| match_0015 | Gemma | only_new_plus1 |
| match_0015 | Llama | fully_old |
| match_0015 | Qwen | only_new_plus1 |
| match_0017 | Gemma | fully_new |
| match_0017 | Llama | fully_old |
| match_0026 | Gemma | fully_new |
| match_0026 | Qwen | only_new_plus1 |
| match_0030 | Gemma | fully_new |
| match_0030 | Qwen | only_new_plus1 |