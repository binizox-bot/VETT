# 可复现清单（离线、单命令、重放=重算评分）

## 1. 环境锁

| 项 | 值 |
|---|---|
| Python | 3.14.7（`D:\Conda\python.exe`；任何 Python ≥3.10 标准库均可运行本包脚本） |
| 第三方依赖 | **无**（`reproduce.py` / `held_out_score.py` 只 import 标准库） |
| OS（实测） | Windows-11-10.0.26200-SP0 |
| 网络 | **0**（脚本不打开 socket；不调用任何模型/云端 API） |
| 模型 | **0**（复现包不跑模型；只读既有分析产物） |
| 数据根 | 交付根目录下的 `VETT_R28_DIFFICULTY_20261112`（脚本按相对路径定位） |

环境记录：`environment.json`；无 requirements/lock 文件，因为不依赖第三方包。

## 2. 单命令

```powershell
cd VETT_R28_DIFFICULTY_20261112\05_release\academic_package
python reproduce.py --check
```

预期最后一行：`[ok] all metrics match metrics_expected.json`，退出码 0。

不带 `--check` 时打印全部指标 JSON；`--json` 为机器可读输出。

## 3. 输入 / 输出 sha256

### 3.1 输入（只读）

| 输入 | sha256 |
|---|---|
| `03_build/dataset_r28/build_index.json` | `dd6de16a4001d414aa3503126f9447c93d571ce64524df9dc38c24f00c9ac0ee` |
| `03_build/dataset_r28/MANIFEST.json` | `a0a3284e19976a7c03a18a2926381093db8a2db8ab1c794d55ae7df7c4c27060` |
| `03_build/dataset_r28/derivation_depth_witness.json` | 见 `metrics_expected.json.hashes` |
| `eval_runs/t19_e1e5_20261112/analysis.json` | 见 `metrics_expected.json.hashes` |
| `eval_runs/t19_e1e5_20261112/e1_raw.jsonl` | 见 `metrics_expected.json.hashes` |
| `eval_runs/t19_e1e5_20261112/analysis_e4_supplemental.json` | 见 `metrics_expected.json.hashes` |
| `03_build/local/t14/runs/t14_main/annotations_T1_factor_visibility.jsonl` | 见 `metrics_expected.json.hashes` |

> `metrics_expected.json.hashes` 是脚本运行时重新计算的值；若输入变了，`--check` 会同时报 metric mismatch 与 hash 变化。

### 3.2 输出（本包）

| 输出 | 说明 |
|---|---|
| `metrics_expected.json` | 全部数据卡数字的机器可读值；`reproduce.py --check` 的对照基准 |
| `held_out_score.py` 输出 | 每个提交的聚合指标 + 提交 sha256；不含 gold |

## 4. 代码哈希（发布前以 `MANIFEST.sha256` 为准）

`MANIFEST.sha256` 在包构建完成后由 `Get-FileHash` 等价规则生成，覆盖：

- `reproduce.py`（复现器）
- `held_out_score.py`（held-out 评分器）
- `metrics_expected.json`（预期值）
- 数据卡、许可、协议、边界文档

本包脚本的源码同时受 MIT 许可；数据受 CC BY 4.0。

## 5. 重放语义（必须绑定解析器版本 R-R7）

“重放”= **重算评分**，不是“重跑模型得到逐位相同输出”：

- R-R7：806/806 个 cache key 按 `v2` 重算；旧模板 **0**；解析器不兼容 **0**（t20 D6 / t14 证据）。
- 152 个样本中 **1 个 5 分制分数跨运行移动 1 分**；答案判定不变。不得把 `temperature=0` 写成逐位可复现。
- 重放绑定到 `judge_protocol.py` + parser 版本；解析器变动后必须重跑全部历史提交，否则评分不可比。
- 单命令闭环（t20）：

```powershell
cd 05_pipeline
python verify/run_closed_loop_verification.py --config r28.toml
```

  **修复后（现行）**：vanilla Windows GBK 控制台、**不设** `PYTHONUTF8`/`PYTHONIOENCODING`/`PYTHONLEGACYWINDOWSSTDIO`，`chcp 936`，**10/10 PASS、exit 0、约 19s**；t20 的 D0 不再出现 `UnicodeDecodeError`。修复前曾 9/10（D0 解码错误），pre 归档在 `04_verify/t20_closed_loop/archive_prefix_utf8/`；本轮 t8 增量复核已 append-only 记录（见 `04_verify/INDEPENDENT_VERIFICATION.md` 补充节）。若使用更早的 t20 代码，必须设 `PYTHONUTF8=1`，否则 D0 失败。

## 6. 复现验收

1. 从干净目录打开交付根，执行第 2 节单命令，退出 0。
2. 核对 `metrics_expected.json.hashes` 与磁盘文件；若不一致，不要继续引用数据卡数字。
3. held-out 评分自检：

```powershell
python held_out_score.py --self-check --dataset ..\..\03_build\dataset_r28
```

预期 `{"ok": true, "n": 40, ...}`。

4. 验收人不读 `private/` 的 gold 也能复现数据卡所有数字；评分方读 held-out gold 只走 `held_out_score.py`，不向提交方暴露。

## 7. 明确不可复现的内容

- 模型输出逐字节（temperature=0 也不保证）；只能重算评分。
- 220 场源素材的原始采集过程（半合成；见 B1）。
- MCC 规则文本的授权状态（见 B7）。
- 人工双标一致性（尚未执行；见 B6）。
