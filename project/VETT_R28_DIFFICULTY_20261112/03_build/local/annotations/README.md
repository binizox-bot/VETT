# 03_build/local/annotations — 云端深度标注（t16，annotator_alpha）

本目录是 t16 的**唯一写入区**：云端独立标注员的盲判日志、盲包、私密索引、裁定与对照。

| 文件 | 作用 |
|---|---|
| [`cloud_alpha.jsonl`](cloud_alpha.jsonl) | **append-only 判定日志**，76 行，schema `vett-annotation-record/v1` |
| [`DISAGREEMENTS.md`](DISAGREEMENTS.md) | 与本地模型的对照 + **T1 逐条分歧清单** + T3 裁定摘要 + 诚实边界 |
| [`crosscheck_alpha_vs_local.json`](crosscheck_alpha_vs_local.json) | 机器可读对照（T1 逐条 / T2 分布 / t14 状态） |
| [`VERIFICATION.json`](VERIFICATION.json) | 独立校验输出（覆盖率 / schema / 盲包审计 / token 预算），exit 0 |
| [`packets/`](packets) | 盲包（T1 24 + T1 对照臂 24 + T2 16）、T3 裁定输入 12、私密索引、`SALT.json` |
| [`alpha_labels/`](alpha_labels) | 人工撰写的标签源（按批 8 条落盘），由 assemble 脚本转成 jsonl |
| [`tools/`](tools) | 建包 / 组装 / 校验 / 对照 四个脚本 + 冻结的 `judge_config.json` |

## 三段标注（共 76 次，硬顶 80）

| 段 | 条数 | 说明 |
|---|---:|---|
| `T1_factor_visibility`（R28 分层） | 24 | 三类真值各 8：revision 取代 / provenance 硬负 / 普通 fact；机制 D1–D4+FACTOR 均 ≥2 |
| `T1_factor_visibility`（同刺激对照臂） | 24 | 从 t18 冻结矩阵 30 条 prompt 中**只取 passage** 重新封包，与本地逐条对照 |
| `T2_naturalness` | 16 | R28 fact span × 4 种机械损坏各 4 条，clean_position 由哈希决定 |
| `T3_adjudication` | 12 | 整份公开卷宗 + 一条**弱提交**（naive drafter），判 fields/span/edge/abstain/conformance |

## 复现

```powershell
cd VETT_R28_DIFFICULTY_20261112\03_build\local\annotations
D:\Conda\python.exe tools\build_t1t2_packets.py      # 建 R28 T1/T2 盲包（重跑会换 salt）
D:\Conda\python.exe tools\build_t1_local_arm.py      # 建同刺激对照臂盲包（只读 t18 冻结矩阵）
D:\Conda\python.exe tools\build_t3_submissions.py    # 建 12 条 T3 裁定输入（弱提交者，只读公开卷宗）
D:\Conda\python.exe tools\assemble_cloud_alpha.py    # 把 alpha_labels/*.json 追加成 cloud_alpha.jsonl（幂等）
D:\Conda\python.exe tools\verify_annotation.py       # 覆盖率 / schema / 盲包 / 预算，exit 0
D:\Conda\python.exe tools\compare_with_local.py      # 与本地对照；t14 落盘后重跑即可
```

## 边界

- 只读 `dataset_r28/public/`、`02_design/protocol.json`（+`judge_protocol.py`）、t18 冻结矩阵；**未读** `private/`。
- 未改任何 packet / 数据集 / 协议 / 合同；R26.15 未触碰。
- 0 网络、0 付费 API；云端 = 本会话模型。
- `T3` 输入不含 gold：`verify_annotation.py` 会扫描 `private_gold / decision_record_flat / 路径 / r28q_ 编号`。
