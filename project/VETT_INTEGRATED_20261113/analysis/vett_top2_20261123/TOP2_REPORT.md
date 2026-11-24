# Top-2 中性任务报告

## 1. 排序规则与可答性（冻结）

- 规则：wickets 降序，runs conceded 升序，姓名升序；先评成员集合，行序单列。
- 可接受名单：标准全名（名+姓，空格归一、大小写不敏感）；不接受只写姓或只写名。
- 可答性按“文本是否给出 top-2 与第一竞争者的 wicket 数字”审计，4/8 根保守可答；不可答根仍运行，但单列。

## 2. 总体（成员集合 / 行序）

| 通知 | 成员对 | 行序对 | 总数 |
|---|---:|---:|---:|
| T2_N0 | 18 | 16 | 24 |
| T2_N1 | 14 | 11 | 24 |
| T2_N2 | 15 | 10 | 24 |

## 3. 分模型

| 模型 | 通知 | 成员对 | 行序对 | 总数 |
|---|---|---:|---:|---:|
| Qwen | T2_N0 | 6 | 6 | 8 |
| Qwen | T2_N1 | 3 | 2 | 8 |
| Qwen | T2_N2 | 5 | 3 | 8 |
| Llama | T2_N0 | 4 | 3 | 8 |
| Llama | T2_N1 | 4 | 3 | 8 |
| Llama | T2_N2 | 4 | 3 | 8 |
| Gemma | T2_N0 | 8 | 7 | 8 |
| Gemma | T2_N1 | 7 | 6 | 8 |
| Gemma | T2_N2 | 6 | 4 | 8 |

### 2b 按可答性拆分

| 可答性 | 通知 | 成员对 | 行序对 | 总数 |
|---|---|---:|---:|---:|
| answerable | T2_N0 | 7 | 6 | 12 |
| answerable | T2_N1 | 5 | 5 | 12 |
| answerable | T2_N2 | 4 | 2 | 12 |
| not_answerable | T2_N0 | 11 | 10 | 12 |
| not_answerable | T2_N1 | 9 | 6 | 12 |
| not_answerable | T2_N2 | 11 | 8 | 12 |

## 4. 普通唯一排名 / 排名退出 / 同分

| 比赛 | 旧 top-2 | 改判后 top-2 | 排名退出 | 同分 |
|---|---|---|---|---|
| match_0003 | Evan Clarke, Connor Reed | Evan Clarke, Connor Reed | - | False |
| match_0008 | Luke Barrett, Ryan Frost | Ryan Frost, Evan Reed | Luke Barrett | False |
| match_0010 | Ryan Foster, Evan Turner | Evan Turner, Luke Barrett | Ryan Foster | True |
| match_0012 | Caleb Brooks, Lucas Vale | Lucas Vale, Caleb Brooks | - | False |
| match_0015 | Noah Grant, Caleb Rourke | Caleb Rourke, Noah Grant | - | False |
| match_0017 | Miles Carter, Liam Brooks | Miles Carter, Liam Brooks | - | False |
| match_0026 | Dylan Cole, Ben Carter | Dylan Cole, Ben Carter | - | False |
| match_0030 | Logan Vale, Owen Price | Owen Price, Logan Vale | - | False |

### 4b 按排名类别拆分

| 类别 | 通知 | 成员对 | 行序对 | 总数 |
|---|---|---:|---:|---:|
| unique | T2_N0 | 15 | 14 | 18 |
| unique | T2_N1 | 13 | 10 | 18 |
| unique | T2_N2 | 15 | 10 | 18 |
| rank_exit | T2_N0 | 1 | 0 | 3 |
| rank_exit | T2_N1 | 0 | 0 | 3 |
| rank_exit | T2_N2 | 0 | 0 | 3 |
| rank_exit_and_tie | T2_N0 | 2 | 2 | 3 |
| rank_exit_and_tie | T2_N1 | 1 | 1 | 3 |
| rank_exit_and_tie | T2_N2 | 0 | 0 | 3 |
| tie | T2_N0 | 0 | 0 | 0 |
| tie | T2_N1 | 0 | 0 | 0 |
| tie | T2_N2 | 0 | 0 | 0 |

## 5. match_0003：三种任务对照（Qwen / Llama）

| 模型 | 通知 | 中性 top-2 | 具名短问 5 字段 | 整表目标两格+total |
|---|---|---|---|---|
| Qwen | N0 | 成员对/行序对 | 1 | False |
| Qwen | N1 | 成员对/行序对 | 1 | False |
| Qwen | N2 | 成员对/行序对 | 1 | False |
| Llama | N0 | 成员错/行序错 | 1 | True |
| Llama | N1 | 成员错/行序错 | 1 | True |
| Llama | N2 | 成员错/行序错 | 0 | False |

- 首场 match_0003 的 9 个位置全部返回恰好两个人名（格式 9/9 通过），再扩到其余 7 根。
- Qwen：中性 top-2 三个通知都成员/行序全对；具名短问也全对；但 43 字段整表目标两格+total 全错（维持/无通知把 Connor Reed 写成 2，改判写 0）。
- Llama：中性 top-2 三个通知都错，且把第二人写成 Isaac Wells（另一局投手）；具名短问全对，整表维持/无通知目标两格+total 正确、改判错。
- 这说明“点名式短问”可以正确，但无目标提示的 top-2 需要自己绑定局别与行序，Llama 在这一步绑到另一局；Qwen 相反，点名能对，整表行映射错。


### 5b 全部 8 根的三任务连接（同场/同通知/同模型）

| 比赛 | 模型 | N0 top-2/短问/整表 | N1 top-2/短问/整表 | N2 top-2/短问/整表 |
|---|---|---|---|---|
| match_0003 | Qwen | M/O; 1; False | M/O; 1; False | M/O; 1; False |
| match_0003 | Llama | -; 1; True | -; 1; True | -; 0; False |
| match_0003 | Gemma | M/O; 1; False | M/O; 1; False | M/O; 1; False |
| match_0008 | Qwen | -; 1; False | -; 0; False | -; 0; False |
| match_0008 | Llama | -; 0; False | -; 0; False | -; 0; False |
| match_0008 | Gemma | M; 1; False | -; 1; False | -; 1; False |
| match_0010 | Qwen | M/O; 1; False | -; 1; False | -; 0; False |
| match_0010 | Llama | -; 0; False | -; 0; False | -; 0; False |
| match_0010 | Gemma | M/O; 1; False | M/O; 1; False | -; 0; False |
| match_0012 | Qwen | M/O; 1; False | -; 1; False | M/O; 0; False |
| match_0012 | Llama | M/O; 1; False | M/O; 1; False | M; 0; False |
| match_0012 | Gemma | M/O; 1; False | M/O; 1; False | M; 0; False |
| match_0015 | Qwen | M/O; 1; False | M; 0; False | M/O; 0; False |
| match_0015 | Llama | M; 0; False | M; 0; False | M/O; 0; False |
| match_0015 | Gemma | M/O; 1; True | M; 1; False | M/O; 1; False |
| match_0017 | Qwen | M/O; 1; False | M/O; 1; False | M; 0; False |
| match_0017 | Llama | M/O; 0; True | M/O; 0; True | M/O; 0; False |
| match_0017 | Gemma | M/O; 1; False | M/O; 1; False | M/O; 0; False |
| match_0026 | Qwen | M/O; 1; True | -; 1; True | M; 1; False |
| match_0026 | Llama | M/O; 1; False | M/O; 1; False | M/O; 0; False |
| match_0026 | Gemma | M/O; 1; False | M/O; 1; False | M/O; 1; False |
| match_0030 | Qwen | -; 1; False | -; 1; False | -; 1; False |
| match_0030 | Llama | -; 0; False | -; 0; False | -; 0; False |
| match_0030 | Gemma | M/O; 1; False | M/O; 1; False | M; 0; False |

- M=成员对，/O=行序对；短问为 5 字段 task_correct；整表为目标两格+total 全对。


## 6. 逐条输出

| 比赛 | 模型 | 通知 | 预测 | 金标 | 成员 | 行序 |
|---|---|---|---|---|---|---|
| match_0003 | Gemma | T2_N0 | ["Evan Clarke", "Connor Reed"] | ["Evan Clarke", "Connor Reed"] | True | True |
| match_0003 | Gemma | T2_N1 | ["Evan Clarke", "Connor Reed"] | ["Evan Clarke", "Connor Reed"] | True | True |
| match_0003 | Gemma | T2_N2 | ["Evan Clarke", "Connor Reed"] | ["Evan Clarke", "Connor Reed"] | True | True |
| match_0003 | Llama | T2_N0 | ["Evan Clarke", "Isaac Wells"] | ["Evan Clarke", "Connor Reed"] | False | False |
| match_0003 | Llama | T2_N1 | ["Evan Clarke", "Isaac Wells"] | ["Evan Clarke", "Connor Reed"] | False | False |
| match_0003 | Llama | T2_N2 | ["Evan Clarke", "Isaac Wells"] | ["Evan Clarke", "Connor Reed"] | False | False |
| match_0003 | Qwen | T2_N0 | ["Evan Clarke", "Connor Reed"] | ["Evan Clarke", "Connor Reed"] | True | True |
| match_0003 | Qwen | T2_N1 | ["Evan Clarke", "Connor Reed"] | ["Evan Clarke", "Connor Reed"] | True | True |
| match_0003 | Qwen | T2_N2 | ["Evan Clarke", "Connor Reed"] | ["Evan Clarke", "Connor Reed"] | True | True |
| match_0008 | Gemma | T2_N0 | ["Ryan Frost", "Luke Barrett"] | ["Luke Barrett", "Ryan Frost"] | True | False |
| match_0008 | Gemma | T2_N1 | ["Dylan Price", "Aaron Wells"] | ["Luke Barrett", "Ryan Frost"] | False | False |
| match_0008 | Gemma | T2_N2 | ["Ryan Frost", "Luke Barrett"] | ["Ryan Frost", "Evan Reed"] | False | False |
| match_0008 | Llama | T2_N0 | ["Dylan Price", "Aaron Wells"] | ["Luke Barrett", "Ryan Frost"] | False | False |
| match_0008 | Llama | T2_N1 | ["Dylan Price", "Aaron Wells"] | ["Luke Barrett", "Ryan Frost"] | False | False |
| match_0008 | Llama | T2_N2 | ["Dylan Price", "Aaron Wells"] | ["Ryan Frost", "Evan Reed"] | False | False |
| match_0008 | Qwen | T2_N0 | ["Dylan Price", "Aaron Wells"] | ["Luke Barrett", "Ryan Frost"] | False | False |
| match_0008 | Qwen | T2_N1 | ["Dylan Price", "Aaron Wells"] | ["Luke Barrett", "Ryan Frost"] | False | False |
| match_0008 | Qwen | T2_N2 | ["Dylan Price", "Aaron Wells"] | ["Ryan Frost", "Evan Reed"] | False | False |
| match_0010 | Gemma | T2_N0 | ["Ryan Foster", "Evan Turner"] | ["Ryan Foster", "Evan Turner"] | True | True |
| match_0010 | Gemma | T2_N1 | ["Ryan Foster", "Evan Turner"] | ["Ryan Foster", "Evan Turner"] | True | True |
| match_0010 | Gemma | T2_N2 | ["Aaron Vale", "Ryan Foster"] | ["Evan Turner", "Luke Barrett"] | False | False |
| match_0010 | Llama | T2_N0 | ["Ryan Foster", "Luke Barrett"] | ["Ryan Foster", "Evan Turner"] | False | False |
| match_0010 | Llama | T2_N1 | ["Ryan Foster", "Luke Barrett"] | ["Ryan Foster", "Evan Turner"] | False | False |
| match_0010 | Llama | T2_N2 | ["Aaron Vale", "Ryan Foster"] | ["Evan Turner", "Luke Barrett"] | False | False |
| match_0010 | Qwen | T2_N0 | ["Ryan Foster", "Evan Turner"] | ["Ryan Foster", "Evan Turner"] | True | True |
| match_0010 | Qwen | T2_N1 | ["Ryan Foster", "Mason Hart"] | ["Ryan Foster", "Evan Turner"] | False | False |
| match_0010 | Qwen | T2_N2 | ["Evan Turner", "Ryan Foster"] | ["Evan Turner", "Luke Barrett"] | False | False |
| match_0012 | Gemma | T2_N0 | ["Caleb Brooks", "Lucas Vale"] | ["Caleb Brooks", "Lucas Vale"] | True | True |
| match_0012 | Gemma | T2_N1 | ["Caleb Brooks", "Lucas Vale"] | ["Caleb Brooks", "Lucas Vale"] | True | True |
| match_0012 | Gemma | T2_N2 | ["Caleb Brooks", "Lucas Vale"] | ["Lucas Vale", "Caleb Brooks"] | True | False |
| match_0012 | Llama | T2_N0 | ["Caleb Brooks", "Lucas Vale"] | ["Caleb Brooks", "Lucas Vale"] | True | True |
| match_0012 | Llama | T2_N1 | ["Caleb Brooks", "Lucas Vale"] | ["Caleb Brooks", "Lucas Vale"] | True | True |
| match_0012 | Llama | T2_N2 | ["Caleb Brooks", "Lucas Vale"] | ["Lucas Vale", "Caleb Brooks"] | True | False |
| match_0012 | Qwen | T2_N0 | ["Caleb Brooks", "Lucas Vale"] | ["Caleb Brooks", "Lucas Vale"] | True | True |
| match_0012 | Qwen | T2_N1 | ["Liam Frost", "Caleb Brooks"] | ["Caleb Brooks", "Lucas Vale"] | False | False |
| match_0012 | Qwen | T2_N2 | ["Lucas Vale", "Caleb Brooks"] | ["Lucas Vale", "Caleb Brooks"] | True | True |
| match_0015 | Gemma | T2_N0 | ["Noah Grant", "Caleb Rourke"] | ["Noah Grant", "Caleb Rourke"] | True | True |
| match_0015 | Gemma | T2_N1 | ["Caleb Rourke", "Noah Grant"] | ["Noah Grant", "Caleb Rourke"] | True | False |
| match_0015 | Gemma | T2_N2 | ["Caleb Rourke", "Noah Grant"] | ["Caleb Rourke", "Noah Grant"] | True | True |
| match_0015 | Llama | T2_N0 | ["Caleb Rourke", "Noah Grant"] | ["Noah Grant", "Caleb Rourke"] | True | False |
| match_0015 | Llama | T2_N1 | ["Caleb Rourke", "Noah Grant"] | ["Noah Grant", "Caleb Rourke"] | True | False |
| match_0015 | Llama | T2_N2 | ["Caleb Rourke", "Noah Grant"] | ["Caleb Rourke", "Noah Grant"] | True | True |
| match_0015 | Qwen | T2_N0 | ["Noah Grant", "Caleb Rourke"] | ["Noah Grant", "Caleb Rourke"] | True | True |
| match_0015 | Qwen | T2_N1 | ["Caleb Rourke", "Noah Grant"] | ["Noah Grant", "Caleb Rourke"] | True | False |
| match_0015 | Qwen | T2_N2 | ["Caleb Rourke", "Noah Grant"] | ["Caleb Rourke", "Noah Grant"] | True | True |
| match_0017 | Gemma | T2_N0 | ["Miles Carter", "Liam Brooks"] | ["Miles Carter", "Liam Brooks"] | True | True |
| match_0017 | Gemma | T2_N1 | ["Miles Carter", "Liam Brooks"] | ["Miles Carter", "Liam Brooks"] | True | True |
| match_0017 | Gemma | T2_N2 | ["Miles Carter", "Liam Brooks"] | ["Miles Carter", "Liam Brooks"] | True | True |
| match_0017 | Llama | T2_N0 | ["Miles Carter", "Liam Brooks"] | ["Miles Carter", "Liam Brooks"] | True | True |
| match_0017 | Llama | T2_N1 | ["Miles Carter", "Liam Brooks"] | ["Miles Carter", "Liam Brooks"] | True | True |
| match_0017 | Llama | T2_N2 | ["Miles Carter", "Liam Brooks"] | ["Miles Carter", "Liam Brooks"] | True | True |
| match_0017 | Qwen | T2_N0 | ["Miles Carter", "Liam Brooks"] | ["Miles Carter", "Liam Brooks"] | True | True |
| match_0017 | Qwen | T2_N1 | ["Miles Carter", "Liam Brooks"] | ["Miles Carter", "Liam Brooks"] | True | True |
| match_0017 | Qwen | T2_N2 | ["Liam Brooks", "Miles Carter"] | ["Miles Carter", "Liam Brooks"] | True | False |
| match_0026 | Gemma | T2_N0 | ["Dylan Cole", "Ben Carter"] | ["Dylan Cole", "Ben Carter"] | True | True |
| match_0026 | Gemma | T2_N1 | ["Dylan Cole", "Ben Carter"] | ["Dylan Cole", "Ben Carter"] | True | True |
| match_0026 | Gemma | T2_N2 | ["Dylan Cole", "Ben Carter"] | ["Dylan Cole", "Ben Carter"] | True | True |
| match_0026 | Llama | T2_N0 | ["Dylan Cole", "Ben Carter"] | ["Dylan Cole", "Ben Carter"] | True | True |
| match_0026 | Llama | T2_N1 | ["Dylan Cole", "Ben Carter"] | ["Dylan Cole", "Ben Carter"] | True | True |
| match_0026 | Llama | T2_N2 | ["Dylan Cole", "Ben Carter"] | ["Dylan Cole", "Ben Carter"] | True | True |
| match_0026 | Qwen | T2_N0 | ["Dylan Cole", "Ben Carter"] | ["Dylan Cole", "Ben Carter"] | True | True |
| match_0026 | Qwen | T2_N1 | ["Nathan Wells", "Leo Marsh"] | ["Dylan Cole", "Ben Carter"] | False | False |
| match_0026 | Qwen | T2_N2 | ["Ben Carter", "Dylan Cole"] | ["Dylan Cole", "Ben Carter"] | True | False |
| match_0030 | Gemma | T2_N0 | ["Logan Vale", "Owen Price"] | ["Logan Vale", "Owen Price"] | True | True |
| match_0030 | Gemma | T2_N1 | ["Logan Vale", "Owen Price"] | ["Logan Vale", "Owen Price"] | True | True |
| match_0030 | Gemma | T2_N2 | ["Logan Vale", "Owen Price"] | ["Owen Price", "Logan Vale"] | True | False |
| match_0030 | Llama | T2_N0 | ["Connor Blake", "Logan Vale"] | ["Logan Vale", "Owen Price"] | False | False |
| match_0030 | Llama | T2_N1 | ["Connor Blake", "Logan Vale"] | ["Logan Vale", "Owen Price"] | False | False |
| match_0030 | Llama | T2_N2 | ["Logan Vale", "Connor Blake"] | ["Owen Price", "Logan Vale"] | False | False |
| match_0030 | Qwen | T2_N0 | ["Connor Blake", "Logan Vale"] | ["Logan Vale", "Owen Price"] | False | False |
| match_0030 | Qwen | T2_N1 | ["Connor Blake", "Logan Vale"] | ["Logan Vale", "Owen Price"] | False | False |
| match_0030 | Qwen | T2_N2 | ["Connor Blake", "Logan Vale"] | ["Owen Price", "Logan Vale"] | False | False |