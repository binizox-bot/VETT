# 四根小规模复验：直接整表 / 独立选人 / 带自选名单整表

## 1. 方法

- 4 根：match_0170、match_0096、match_0049、match_0180；每根维持+改判 ×3 模型。
- 直接整表 24 次、独立选人 24 次、带自选名单整表 24 次，共 72 次；后者的名单来自同场同模型独立选人。
- 主指标：合法 top-2 两人、各自 wickets/runs、局总 wickets 同时正确。

## 2. 主指标（/12 每通知）

| 通知 | 直接整表 | 独立选人成员对 | 带名单整表 | 直接→带名单救回 | 直接→带名单改坏 |
|---|---:|---:|---:|---:|---:|
| N1 | 5/12 | 9/12 | 6/12 | 1 | 0 |
| N2 | 0/12 | 6/12 | 0/12 | 0 | 0 |

## 3. 分模型

| 模型 | 通知 | 直接整表 | 独立成员 | 带名单整表 |
|---|---|---:|---:|---:|
| Qwen | N1 | 3/4 | 3/4 | 3/4 |
| Qwen | N2 | 0/4 | 2/4 | 0/4 |
| Llama | N1 | 2/4 | 4/4 | 3/4 |
| Llama | N2 | 0/4 | 2/4 | 0/4 |
| Gemma | N1 | 0/4 | 2/4 | 0/4 |
| Gemma | N2 | 0/4 | 2/4 | 0/4 |

## 4. 代价与副作用

- 直接整表：24 次调用；独立选人：24 次；带名单整表：24 次（另复用同批独立名单，不额外调用）。总计 72 次。
- 带名单相对直接：其他有依据字段退步 45 格，改善 30 格。
- 自选名单错误被带入整表：5 例。
  - match_0049 N2 Qwen 名单=["Carter Flynn", "Finn Mercer"]
  - match_0049 N2 Llama 名单=["Carter Flynn", "Finn Mercer"]
  - match_0049 N2 Gemma 名单=["Carter Flynn", "Finn Mercer"]
  - match_0180 N1 Gemma 名单=["Arjun Stone", "Finn Carter"]
  - match_0180 N2 Llama 名单=["Mason Price", "Finn Carter"]

## 5. 逐例配对

| 比赛 | 通知 | 模型 | 独立名单 | 直接 | 带名单 | 其他字段退步 |
|---|---|---|---|---|---|---:|
| match_0170 | N1 | Qwen | ["Carter Flynn", "Ari Blake"] | 对 | 对 | 0 |
| match_0170 | N1 | Llama | ["Carter Flynn", "Ari Blake"] | 错 | 对 | 0 |
| match_0170 | N1 | Gemma | ["Carter Flynn", "Ari Blake"] | 错 | 错 | 0 |
| match_0170 | N2 | Qwen | ["Carter Flynn", "Ari Blake"] | 错 | 错 | 0 |
| match_0170 | N2 | Llama | ["Carter Flynn", "Ari Blake"] | 错 | 错 | 3 |
| match_0170 | N2 | Gemma | ["Carter Flynn", "Ari Blake"] | 错 | 错 | 15 |
| match_0096 | N1 | Qwen | ["Noah Vale", "Ryan North"] | 对 | 对 | 1 |
| match_0096 | N1 | Llama | ["Noah Vale", "Ryan North"] | 错 | 错 | 5 |
| match_0096 | N1 | Gemma | ["Noah Vale", "Ryan North"] | 错 | 错 | 0 |
| match_0096 | N2 | Qwen | ["Ryan North", "Noah Vale"] | 错 | 错 | 1 |
| match_0096 | N2 | Llama | ["Noah Vale", "Ryan North"] | 错 | 错 | 11 |
| match_0096 | N2 | Gemma | ["Noah Vale", "Ryan North"] | 错 | 错 | 0 |
| match_0049 | N1 | Qwen | ["Carter Flynn", "Finn Mercer"] | 对 | 对 | 1 |
| match_0049 | N1 | Llama | ["Finn Mercer", "Carter Flynn"] | 对 | 对 | 0 |
| match_0049 | N1 | Gemma | ["Gavin Cross", "Jasper Reed"] | 错 | 错 | 0 |
| match_0049 | N2 | Qwen | ["Carter Flynn", "Finn Mercer"] | 错 | 错 | 5 |
| match_0049 | N2 | Llama | ["Carter Flynn", "Finn Mercer"] | 错 | 错 | 0 |
| match_0049 | N2 | Gemma | ["Carter Flynn", "Finn Mercer"] | 错 | 错 | 0 |
| match_0180 | N1 | Qwen | ["Arjun Stone", "Ethan Brooks"] | 错 | 错 | 0 |
| match_0180 | N1 | Llama | ["Finn Carter", "Mason Price"] | 对 | 对 | 0 |
| match_0180 | N1 | Gemma | ["Arjun Stone", "Finn Carter"] | 错 | 错 | 0 |
| match_0180 | N2 | Qwen | ["Arjun Stone", "Ethan Brooks"] | 错 | 错 | 3 |
| match_0180 | N2 | Llama | ["Mason Price", "Finn Carter"] | 错 | 错 | 0 |
| match_0180 | N2 | Gemma | ["Arjun Stone", "Mason Price"] | 错 | 错 | 0 |

## 6. 开发案例

match_0003 / N1 的 3 次提示回投：0 次救回，1 次改坏原本正确的 Llama，1 次格式失败；见 DEV_CASE_0003.md。
