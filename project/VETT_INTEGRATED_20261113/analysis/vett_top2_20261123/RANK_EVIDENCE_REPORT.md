# 0008 / 0010 排名缺证—最少补证对照

## 1. 协议

- 先查完全匹配：这两场在 uncertainty 协议下的既有任务为 0；B255 的 top-2 题强制两名，不能复用。
- 冻结新版本 V2：两臂同题面、同输出协议，均允许 {"uncertain": true, "missing": ...}；不再强制两名。
- 缺证臂：N2 原文。补证臂：原文末尾加一句。
- 0008 加：Additional evidence: Evan Reed conceded 27 runs.
- 0010 加：Additional evidence: Luke Barrett conceded 38 runs.
- 2 场 ×2 版本 ×3 模型 =12 次本地调用；外部 API 0。

## 2. 金标与所缺信息

| 场 | 改判后 top-2 | 缺证臂应指出 |
|---|---|---|
| match_0008 | Ryan Frost, Evan Reed | Evan Reed 的 27 runs（与 Barrett 30 比较） |
| match_0010 | Evan Turner, Luke Barrett | Luke Barrett 的 38 runs（与 Foster 48 比较） |

## 3. 首页结果

| 指标 | 结果 |
|---|---|
| 缺证时正确指出所缺信息 | 0/6 |
| 补证后给出合法名单（成员集合） | 0/6 |
| 两种条件都答对（主结果） | 0/6 |
| 两次都猜同一名单 | 4/6 |
| 两次都答不确定 | 0/6 |

## 4. 分模型

| 模型 | 缺证正确 | 补证合法 | 两者都对 | 两次同名单 |
|---|---:|---:|---:|---:|
| Qwen | 0/2 | 0/2 | 0/2 | 0/2 |
| Llama | 0/2 | 0/2 | 0/2 | 2/2 |
| Gemma | 0/2 | 0/2 | 0/2 | 2/2 |

## 5. 逐对输出

| 场 | 模型 | 缺证输出 | 补证输出 | 缺证对 | 补证对 |
|---|---|---|---|---|---|
| match_0008 | Qwen | {"bowlers": ["Dylan Price", "Aaron Wells"]} | {"bowlers": ["Ryan Frost", "Dylan Price"]} | False | False |
| match_0008 | Llama | {"bowlers": ["Dylan Price", "Aaron Wells"]} | {"bowlers": ["Dylan Price", "Aaron Wells"]} | False | False |
| match_0008 | Gemma | {"bowlers": ["Ryan Frost", "Luke Barrett"]} | {"bowlers": ["Ryan Frost", "Luke Barrett"]} | False | False |
| match_0010 | Qwen | {"bowlers": ["Aaron Vale", "Ryan Foster"]} | {"bowlers": ["Ryan Foster", "Evan Turner"]} | False | False |
| match_0010 | Llama | {"bowlers": ["Zane Foster", "Lucas Reed"]} | {"bowlers": ["Zane Foster", "Lucas Reed"]} | False | False |
| match_0010 | Gemma | {"bowlers": ["Aaron Vale", "Ryan Foster"]} | {"bowlers": ["Aaron Vale", "Ryan Foster"]} | False | False |

## 6. 解释

- 12 次输出全部给出两名投手，没有一次使用 uncertain 选项；缺证臂没有指出所缺的 runs。
- 补证后也没有产生合法名单：0008 三模型都未选 Evan Reed；0010 只有 Qwen 选到 Evan Turner，但第二人仍是 Ryan Foster。
- 结论：缺证—补证对照为负；模型在缺证时自信猜测，补一条数字不足以纠正成员集合。
