# VETT-R28 变更前基线备份与冻结回执

- 生成时间：`2026-11-12T20:10:57.312350+08:00`
- 备份根：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\_BACKUPS\VETT_R28_PRE_CHANGE_20261112`
- 生成器：`_tools\baseline_backup.py`（纯标准库，无网络，未读取 `.secrets`）
- 总体状态：**passed**

## 1. 口径

| 项 | 值 |
| --- | --- |
| 工作区根 | `D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017` |
| 主项目 | `D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_Cricket_v0.22_R16_Multisource_Dilemmas` |
| 数据基线 | `r26_15_content_dependency_candidate_v3` |
| Python | `D:\Conda\python.exe`（3.14.7，纯标准库） |
| 排除项 | `__pycache__`、`*.pyc`、`.secrets`（后者按政策从不读取、从不哈希） |
| 网络 / provider 调用 | 0 |
| 原件修改 | 无（只读遍历 + 复制） |

## 2. 备份内容

| 产物 | 内容 | 规模 |
| --- | --- | --- |
| `frozen\r26_15_content_dependency_candidate_v3\` | R26.15 逐字节冻结副本 | 165 文件 / 93,346,177 字节 |
| `code\` | `src`、`tests`、`design`、`eval_configs`、`analysis`、`eval_runs` + `README.md`、`CHANGELOG.md`、`.gitignore`（排除 `__pycache__`/`*.pyc`） | 1,412 文件 / 32,810,211 字节 |
| `CODE_MANIFEST.json` | `code\` 快照逐文件 sha256（回滚校验用） | 1,412 文件 |
| `FULL_FILE_MANIFEST.json` | 主项目每文件（路径 / 字节 / mtime / sha256） | 14,150 文件 / 6,423,479,279 字节 |
| `PROTECTED_PATHS.json` | 不可变清单（r26_15 + src/vett_r16..vett_r26 + src/vett_eval + 既有 tests） | 338 文件 / 95,265,149 字节 |
| `restore.ps1` | 恢复脚本（安全模式：打印绝对路径 + 交互确认） | - |
| `VERIFICATION.json` | 机器可判校验结果 | - |

## 3. 校验结果

| 检查 | 状态 | 证据 |
| --- | --- | --- |
| C0_r26_15_pre_snapshot | passed | {"files": 165, "bytes": 93346177} |
| C1_frozen_count_bytes | passed | {"files": 165, "bytes": 93346177} |
| C2_frozen_hashes | passed | {"mismatched": [], "mismatched_count": 0, "source_volatile_during_copy": []} |
| C3_frozen_vs_r26_18_stage0 | passed | {"stage0_scope_file_count": 165, "stage0_scope_total_bytes": 93346177, "stage0_scope_legacy_aggregate": "2cb1ea2c62d1b8d57b6c20bbc3c22ed7ad0440ca73f68946d24fcbf0ebab9417", "mismatched": [], "mismatched_count": 0} |
| C3b_frozen_vs_candidate_manifest | passed | {"candidate_manifest_entries": 164, "mismatched": [], "mismatched_count": 0} |
| C4_code_copy_integrity | passed | {"files": 1412, "bytes": 32810211, "mismatched": [], "mismatched_count": 0, "volatile_during_copy": [], "volatile_count": 0} |
| C5_full_manifest_intrinsic | passed | {"file_count": 14150, "total_bytes": 6423479279} |
| C6_manifest_sample20_recompute | passed | {"sampled": [".gitignore", "dataset_r20_220/private/match_0151/private_evidence.json", "dataset_r22_220/private/match_0080/private_gold.json", "dataset_r22_220_pre_retraction_backup/private/match_0010/private_gold.json", "dataset_r24_220... |
| C7_protected_paths | passed | {"total_files": 338, "groups": [{"id": "r26_15_candidate", "files": 165, "bytes": 93346177, "aggregate": "343afde4c91d7785f42296074ecea685d5d466260674ab5a8c3bc37323d851bd"}, {"id": "code_vett_r16_r26", "files": 142, "bytes": 1644679, "ag... |
| C8_r26_15_zero_drift | passed | {"before_files": 165, "before_bytes": 93346177, "after_files": 165, "after_bytes": 93346177, "drifted": []} |
| C9_secrets_never_read | passed | {"leaked_paths": []} |
| C10_writes_confined | passed | {"outside": [], "backup_root": "D:\\Download\\VETT_Cricket_Complete_Delivery_R19_20261017\\_BACKUPS\\VETT_R28_PRE_CHANGE_20261112"} |
| V1_frozen_equals_source | passed | {"source_files": 165, "frozen_files": 165, "mismatched": []} |
| V2_frozen_equals_protected | passed | {"mismatched": [], "mismatched_count": 0, "group_files": 165} |
| V3_aggregate_reproducible | passed | {"aggregate_sha256": "343afde4c91d7785f42296074ecea685d5d466260674ab5a8c3bc37323d851bd", "from_protected": "343afde4c91d7785f42296074ecea685d5d466260674ab5a8c3bc37323d851bd", "from_manifest": "343afde4c91d7785f42296074ecea685d5d466260674... |
| V4_protected_paths_unchanged | passed | {"protected_files": 338, "violations": [], "violation_count": 0} |
| V5_protected_vs_manifest | passed | {"mismatched": [], "mismatched_count": 0} |
| V6_manifest_count | passed | {"manifest_file_count": 14150, "manifest_total_bytes": 6423479279, "live_file_count": 14150, "added_since_build": [], "added_count": 0, "removed_since_build": [], "removed_count": 0} |
| V7_sample20_recompute | passed | {"sampled": [".gitignore", "dataset_r20_220/private/match_0151/private_evidence.json", "dataset_r22_220/private/match_0080/private_gold.json", "dataset_r22_220_pre_retraction_backup/private/match_0010/private_gold.json", "dataset_r24_220... |
| V8_code_snapshot_consistent_with_manifest | passed | {"checked": 1412, "mismatched": [], "mismatched_count": 0} |
| V9_restore_dry_run | passed | {"exit_code": 0, "missing_targets": [], "log": "_BACKUPS\\VETT_R28_PRE_CHANGE_20261112\\RESTORE_DRYRUN.txt", "stdout_head": "=== VETT-R28 baseline restore ===\nBackup root : D:\\Download\\VETT_Cricket_Complete_Delivery_R19_20261017\\_BAC... |
| V10_r26_15_zero_drift_post_verify | passed | {"files": 165, "bytes": 93346177, "drifted": []} |

### 关键判定

- R26.15 冻结副本：**165 文件 / 93,346,177 字节**，逐文件 sha256 与原件一致，且与 R26.18 Stage-0 `BASELINE_MANIFEST.json` 的 165 条记录逐项一致。
- 不可变清单：338 文件（r26_15 165 + 代码 142 + tests 31）。
- 主项目清单：14,150 文件 / 6,423,479,279 字节；抽样 20 条重算一致。
- **R26.15 未被修改**：变更前后 + 校验后三次快照的 165 个 sha256 全部相同。

## 4. 聚合 SHA-256 复算配方

### 4.1 采用口径（vett-tree-aggregate-v1，可复现）

对目标文件集合，按**项目相对 POSIX 路径升序**（字典序、区分大小写，`/` 分隔）逐文件拼接一行：

```text
<sha256>␠␠<相对路径>\n
```

（每行两个空格分隔哈希与路径，LF 结尾，最后一行也带 LF），再对整段 UTF-8 文本取 SHA-256。

一行命令复算（PowerShell）：

```powershell
# $root 为目标目录；相对路径以 / 分隔
$lines = Get-ChildItem $root -Recurse -File | Where-Object { $_.FullName -notmatch '__pycache__' -and $_.Extension -ne '.pyc' } |
  ForEach-Object { '{0}  {1}' -f (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower(), (Resolve-Path $_.FullName -Relative).Substring(2).Replace('\','/') } |
  Sort-Object
$payload = ($lines -join "`n") + "`n"
$bytes = [Text.Encoding]::UTF8.GetBytes($payload)
[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes)).ToLower()
```

本清单记录的聚合值：

| 集合 | 文件数 | 字节 | 聚合 SHA-256 |
| --- | --- | --- | --- |
| r26_15 候选 | 165 | 93,346,177 | `343afde4c91d7785f42296074ecea685d5d466260674ab5a8c3bc37323d851bd` |
| src/vett_r16..vett_r26 + vett_eval | 142 | 1,644,679 | `1b49a6dd5a8e1194263237ef2c5e2a70e7755db26fedb64f6e78afeaaf48e7a6` |
| tests（既有） | 31 | 274,293 | `39677df6d91118974e9488936e9276a7d39232bf484b5529cbcc2572ea38df16` |
| 全部受保护文件 | 338 | 95,265,149 | `66e108d8efbe91c6e2d91b973f5cbac3929518386384d8a8bafa26a97b2a0433` |

### 4.2 历史口径（不可复现，仅作来源记录）

项目历史文档（R26.18 Stage-0 起）使用聚合值 `2cb1ea2c62d1b8d57b6c20bbc3c22ed7ad0440ca73f68946d24fcbf0ebab9417`。

本次**未能复现**该值：原始生成脚本不在交付包内；已尝试 657 种已记录口径变体（路径/哈希字段顺序、`:`/`\t`/两空格/`\0` 分隔、LF/CRLF、尾部换行有/无、正反斜杠路径、JSON（紧凑/缩进/排序）形式、二进制摘要拼接、路径+字节+哈希三元组、以及 R26.18 Stage-0 `BASELINE_MANIFEST.json` 自带顺序），全部不匹配。

替代口径：见 4.1，r26_15 聚合为 `343afde4c91d7785f42296074ecea685d5d466260674ab5a8c3bc37323d851bd`。该值与历史值不可互比；流水线自检**只使用** 4.1 口径，并同时逐文件比对 165 条 sha256（等价强度，且可定位到具体文件）。

## 5. 恢复方法

```powershell
pwsh -NoProfile -File _BACKUPS\VETT_R28_PRE_CHANGE_20261112\restore.ps1 -DryRun
pwsh -NoProfile -File _BACKUPS\VETT_R28_PRE_CHANGE_20261112\restore.ps1 -Scope frozen
pwsh -NoProfile -File _BACKUPS\VETT_R28_PRE_CHANGE_20261112\restore.ps1 -Scope all
```

- `-DryRun`：仅打印将写入的绝对目标路径并校验备份完整性，零写入。
- 正式恢复：先打印目标绝对路径，要求输入 `RESTORE` 确认（默认 N/中止），再逐文件复核 sha256 后覆盖。
- 恢复前会按 `FULL_FILE_MANIFEST.json` / `PROTECTED_PATHS.json` 校验备份自身完整性，不通过即中止。

## 6. 耗时

| 阶段 | 秒 |
| --- | --- |
| build_r26_15_before_snapshot_s | 0.072 |
| build_frozen_copy_verify_s | 1.148 |
| build_code_copy_verify_s | 6.465 |
| build_full_manifest_hash_s | 4.931 |
| build_total_s | 12.803 |
| restore_dryrun_s | 1.711 |
| verify_total_s | 20.965 |

## 7. 结论

- 基线已冻结并做三重复核（原件 / 冻结副本 / R26.18 Stage-0 快照）。
- 不可变清单已生成，可作为流水线每轮自检谓词（违反 => exit 4）。
- **R26.15 未被修改**（文件数、字节数与 165 个 sha256 全部不变）。
- 唯一无法复现的口径是历史聚合 SHA-256 `2cb1ea2c62d1b8d57b6c20bbc3c22ed7ad0440ca73f68946d24fcbf0ebab9417`，已在 4.2 说明并给出替代口径。

