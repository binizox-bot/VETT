# R28 枚举与配额报告（t5 生成器）

- config sha256：`cc78be40996eaed4f8d5ac49ceec1cf55dd7739d2b81c3f49c47246024e525d6`
- 发布集 / held-out：**320** / **40**
- 需要互异记录：**360**（含 10% 余量 **392**）
- 规范空间（t4 网格复算）：**761** 条互异记录，67 层
- 扩展空间：**4001** 条
- 合并可达：**4001** 条；安全余量 OK
- 与合同逐层 `reachable_cap` 比对：67 层，不一致 **0** 层
- 配额不足层：**0**

## 分布（发布集 320）

- delivery_status：`{'DEAD_REBALL': 1, 'LEGAL': 166, 'NO_BALL': 100, 'WIDE': 53}`
- dismissal：`{'BOWLED': 2, 'CAUGHT': 2, 'HIT_BALL_TWICE': 50, 'LBW': 2, 'NONE': 124, 'OBSTRUCTING_FIELD': 50, 'RUN_OUT': 86, 'STUMPED': 4}`
- 账本 mask：`{'000': 73, '001': 73, '010': 40, '011': 38, '100': 54, '101': 42}`
- 账本非零记录：`{'ledger.BYE': 96, 'ledger.LEG_BYE': 78, 'ledger.PENALTY': 153}`
- 空配对（四剂量全 0）：72 / 期望 72
- 合法 dismissal 合计：11 （上限 11，OK）
- 族数 / 场数：320 / 64

## 5 个未共存组合

- `appeal_made_false_with_lbw` → LEGAL/NONE/000 （record `4f31d15d58b4`）
- `appeal_in_time_false_with_caught` → LEGAL/NONE/000 （record `79eeafc9cafc`）
- `contact_person_with_wide_called` → LEGAL/NONE/010 （record `42c3134f3f09`）
- `dead_before_wicket_with_run_out` → LEGAL/NONE/100 （record `b6633d1498d0`）
- `penalty_five_with_overthrow` → LEGAL/NONE/001 （record `10efb4a21c75`）

## 逐层配额（67 层）

| status | dismissal | mask | quota | F | D | canonical | extended | combined | selected |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LEGAL | NONE | 000 | 12 | 5 | 7 | 12 | 30 | 30 | 12 |
| LEGAL | NONE | 001 | 10 | 4 | 6 | 34 | 220 | 220 | 10 |
| LEGAL | NONE | 010 | 10 | 4 | 6 | 11 | 28 | 28 | 10 |
| LEGAL | NONE | 011 | 10 | 4 | 6 | 33 | 210 | 210 | 10 |
| LEGAL | NONE | 100 | 10 | 4 | 6 | 11 | 28 | 28 | 10 |
| LEGAL | NONE | 101 | 10 | 4 | 6 | 33 | 210 | 210 | 10 |
| LEGAL | RUN_OUT | 000 | 8 | 3 | 5 | 12 | 30 | 30 | 8 |
| LEGAL | RUN_OUT | 001 | 8 | 3 | 5 | 12 | 150 | 150 | 8 |
| LEGAL | RUN_OUT | 010 | 6 | 2 | 4 | 11 | 28 | 28 | 6 |
| LEGAL | RUN_OUT | 011 | 6 | 2 | 4 | 11 | 140 | 140 | 6 |
| LEGAL | RUN_OUT | 100 | 10 | 4 | 6 | 11 | 28 | 28 | 10 |
| LEGAL | RUN_OUT | 101 | 6 | 2 | 4 | 11 | 140 | 140 | 6 |
| LEGAL | OBSTRUCTING_FIELD | 000 | 4 | 2 | 2 | 12 | 30 | 30 | 4 |
| LEGAL | OBSTRUCTING_FIELD | 001 | 4 | 2 | 2 | 12 | 150 | 150 | 4 |
| LEGAL | OBSTRUCTING_FIELD | 010 | 4 | 2 | 2 | 11 | 28 | 28 | 4 |
| LEGAL | OBSTRUCTING_FIELD | 011 | 4 | 2 | 2 | 11 | 140 | 140 | 4 |
| LEGAL | OBSTRUCTING_FIELD | 100 | 6 | 2 | 4 | 11 | 28 | 28 | 6 |
| LEGAL | OBSTRUCTING_FIELD | 101 | 4 | 2 | 2 | 11 | 140 | 140 | 4 |
| LEGAL | HIT_BALL_TWICE | 000 | 4 | 2 | 2 | 12 | 30 | 30 | 4 |
| LEGAL | HIT_BALL_TWICE | 001 | 4 | 2 | 2 | 12 | 150 | 150 | 4 |
| LEGAL | HIT_BALL_TWICE | 010 | 4 | 2 | 2 | 11 | 28 | 28 | 4 |
| LEGAL | HIT_BALL_TWICE | 011 | 4 | 2 | 2 | 11 | 140 | 140 | 4 |
| LEGAL | HIT_BALL_TWICE | 100 | 6 | 2 | 4 | 11 | 28 | 28 | 6 |
| LEGAL | HIT_BALL_TWICE | 101 | 4 | 2 | 2 | 11 | 140 | 140 | 4 |
| LEGAL | BOWLED | 000 | 1 | 0 | 1 | 1 | 2 | 2 | 1 |
| LEGAL | BOWLED | 001 | 1 | 0 | 1 | 1 | 10 | 10 | 1 |
| LEGAL | LBW | 000 | 1 | 0 | 1 | 1 | 2 | 2 | 1 |
| LEGAL | LBW | 001 | 1 | 0 | 1 | 1 | 10 | 10 | 1 |
| LEGAL | CAUGHT | 000 | 1 | 0 | 1 | 1 | 2 | 2 | 1 |
| LEGAL | CAUGHT | 001 | 1 | 0 | 1 | 1 | 10 | 10 | 1 |
| LEGAL | STUMPED | 000 | 1 | 0 | 1 | 1 | 2 | 2 | 1 |
| LEGAL | STUMPED | 001 | 1 | 0 | 1 | 1 | 10 | 10 | 1 |
| NO_BALL | NONE | 000 | 6 | 2 | 4 | 12 | 15 | 15 | 6 |
| NO_BALL | NONE | 001 | 8 | 3 | 5 | 23 | 145 | 145 | 8 |
| NO_BALL | NONE | 010 | 6 | 2 | 4 | 11 | 14 | 14 | 6 |
| NO_BALL | NONE | 011 | 6 | 2 | 4 | 22 | 140 | 140 | 6 |
| NO_BALL | NONE | 100 | 6 | 2 | 4 | 11 | 14 | 14 | 6 |
| NO_BALL | NONE | 101 | 6 | 2 | 4 | 22 | 140 | 140 | 6 |
| NO_BALL | RUN_OUT | 000 | 4 | 2 | 2 | 12 | 15 | 15 | 4 |
| NO_BALL | RUN_OUT | 001 | 4 | 2 | 2 | 12 | 75 | 75 | 4 |
| NO_BALL | RUN_OUT | 010 | 6 | 2 | 4 | 11 | 14 | 14 | 6 |
| NO_BALL | RUN_OUT | 011 | 4 | 2 | 2 | 11 | 70 | 70 | 4 |
| NO_BALL | RUN_OUT | 100 | 8 | 3 | 5 | 11 | 14 | 14 | 8 |
| NO_BALL | RUN_OUT | 101 | 4 | 2 | 2 | 11 | 70 | 70 | 4 |
| NO_BALL | OBSTRUCTING_FIELD | 000 | 2 | 1 | 1 | 12 | 15 | 15 | 2 |
| NO_BALL | OBSTRUCTING_FIELD | 001 | 2 | 1 | 1 | 12 | 75 | 75 | 2 |
| NO_BALL | OBSTRUCTING_FIELD | 010 | 2 | 1 | 1 | 11 | 14 | 14 | 2 |
| NO_BALL | OBSTRUCTING_FIELD | 011 | 2 | 1 | 1 | 11 | 70 | 70 | 2 |
| NO_BALL | OBSTRUCTING_FIELD | 100 | 4 | 2 | 2 | 11 | 14 | 14 | 4 |
| NO_BALL | OBSTRUCTING_FIELD | 101 | 4 | 2 | 2 | 11 | 70 | 70 | 4 |
| NO_BALL | HIT_BALL_TWICE | 000 | 2 | 1 | 1 | 12 | 15 | 15 | 2 |
| NO_BALL | HIT_BALL_TWICE | 001 | 2 | 1 | 1 | 12 | 75 | 75 | 2 |
| NO_BALL | HIT_BALL_TWICE | 010 | 2 | 1 | 1 | 11 | 14 | 14 | 2 |
| NO_BALL | HIT_BALL_TWICE | 011 | 2 | 1 | 1 | 11 | 70 | 70 | 2 |
| NO_BALL | HIT_BALL_TWICE | 100 | 4 | 2 | 2 | 11 | 14 | 14 | 4 |
| NO_BALL | HIT_BALL_TWICE | 101 | 4 | 2 | 2 | 11 | 70 | 70 | 4 |
| WIDE | NONE | 000 | 11 | 4 | 7 | 12 | 15 | 15 | 11 |
| WIDE | NONE | 001 | 12 | 5 | 7 | 23 | 145 | 145 | 12 |
| WIDE | RUN_OUT | 000 | 6 | 2 | 4 | 12 | 15 | 15 | 6 |
| WIDE | RUN_OUT | 001 | 6 | 2 | 4 | 12 | 75 | 75 | 6 |
| WIDE | OBSTRUCTING_FIELD | 000 | 4 | 2 | 2 | 12 | 15 | 15 | 4 |
| WIDE | OBSTRUCTING_FIELD | 001 | 4 | 2 | 2 | 12 | 75 | 75 | 4 |
| WIDE | HIT_BALL_TWICE | 000 | 4 | 2 | 2 | 12 | 15 | 15 | 4 |
| WIDE | HIT_BALL_TWICE | 001 | 4 | 2 | 2 | 12 | 75 | 75 | 4 |
| WIDE | STUMPED | 000 | 1 | 0 | 1 | 1 | 1 | 1 | 1 |
| WIDE | STUMPED | 001 | 1 | 0 | 1 | 1 | 5 | 5 | 1 |
| DEAD_REBALL | NONE | 000 | 1 | 0 | 1 | 1 | 1 | 1 | 1 |

## 格分配

- 因子核 16 格 × 8：`{'0000': 8, '0001': 8, '0010': 8, '0011': 8, '0100': 8, '0101': 8, '0110': 8, '0111': 8, '1000': 8, '1001': 8, '1010': 8, '1011': 8, '1100': 8, '1101': 8, '1110': 8, '1111': 8}`
- 剂量阶梯 12 格 × 16：`{'D1-0': 16, 'D1-1': 16, 'D1-2': 16, 'D2-0': 16, 'D2-1': 16, 'D2-2': 16, 'D3-0': 16, 'D3-1': 16, 'D3-2': 16, 'D4-0': 16, 'D4-1': 16, 'D4-2': 16}`
- 每格 status/dismissal 多样性：全部 ≥2（见 JSON `cell_table`）

