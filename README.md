# VETT 完整项目归档

这是 `VETT_Cricket_Complete_Delivery_R19_20261017` 在 2026-11-24 的私有完整归档仓库。

仓库保存项目打包报告、逐文件清单以及完整 ZIP 的 Git LFS 分卷。完整 ZIP 内保留项目当时的隐藏文件、数据、实验结果、依赖环境、缓存和 `DeepTutor/.git`，因此 DeepTutor 的原始 Git 历史没有被扁平化或丢弃。

## 归档摘要

| 项 | 数值 |
|---|---:|
| 项目普通文件 | 151,381 |
| 项目逻辑大小 | 12.036 GiB |
| ZIP 大小 | 2,653,059,762 字节（约 2.47 GiB） |
| ZIP SHA-256 | `3dcccf27eb1327c461925cc3e42b735db4820b349af6f51f04e7b3da3bb94ce4` |
| ZIP CRC/流式解压 | PASS |
| LFS 分卷 | 2 |

## 文件说明

- `project/`：本地项目的展开文件树；按用户要求排除 `DeepTutor/`，并出于凭据安全排除 `.secrets/siliconflow.env`；其余 35,247 个本地文件均纳入版本控制。
- `PROJECT_PACKAGING_REPORT_20261124.md`：项目结构、现有基础、研究结论、风险和打包边界。
- `PROJECT_FILE_INVENTORY_20261124.csv`：151,380 条打包前文件元数据记录；不包含清单自身。
- `archive/*.part001`、`archive/*.part002`：完整 ZIP 的二进制分卷，由 Git LFS 管理。
- `archive/ARCHIVE_PARTS.sha256`：两个分卷的 SHA-256。
- `archive/SOURCE_ARCHIVE.sha256`：重建后完整 ZIP 的 SHA-256。
- `Verify-ArchiveParts.ps1`：不落盘合并文件，直接验证分卷和拼接后的整体哈希。
- `Restore-VETTArchive.ps1`：按顺序合并分卷、验证 SHA-256，并可选择解压。

## 下载与恢复

克隆后先取得 LFS 对象：

```powershell
git lfs pull
```

验证分卷和整体归档：

```powershell
powershell -ExecutionPolicy Bypass -File .\Verify-ArchiveParts.ps1
```

重建 ZIP：

```powershell
powershell -ExecutionPolicy Bypass -File .\Restore-VETTArchive.ps1
```

重建并解压：

```powershell
powershell -ExecutionPolicy Bypass -File .\Restore-VETTArchive.ps1 -Extract
```

默认输出文件名为 `VETT_Cricket_Complete_Delivery_R19_20261017_FULL_20261124.zip`。输出 ZIP 被 `.gitignore` 排除，避免误提交第二份完整归档。

## Git 历史说明

本仓库本身记录“归档发布”的 Git 历史。原项目根目录在打包时不是 Git 仓库；唯一的嵌套仓库是 `DeepTutor/.git`，其 HEAD 为：

```text
60fb3bdfddb30b7740c7ce3bd9b28d908f2af6db
release: v1.7.2
origin: https://github.com/HKUDS/DeepTutor.git
```

该 `.git` 目录完整包含在 ZIP 内。解压后可在 `DeepTutor` 中运行 `git status`、`git log` 和 `git remote -v` 查看原历史。

展开上传阶段按用户后续要求不提交 `project/DeepTutor/`。同时，疑似有效凭据 `.secrets/siliconflow.env` 不写入永久 Git 历史。因此，GitHub 文件树中的 `project/` 是“原项目减 DeepTutor 与一个凭据文件”的可浏览快照；先前上传的全量归档 ZIP 仍保留最初打包边界。

## 安全边界

本归档包含 public、private、audit、金标、评分器、聊天数据库、日志、本地依赖和历史备份，只适合作为受控的私有全量归档。不要把整个仓库转为公开，也不要把完整归档直接提供给待测模型。完整 ZIP 在排除决定之前生成，可能仍包含 `.secrets/siliconflow.env`；如该凭据有效，应立即轮换，并考虑重建无凭据归档。

## 许可证

仓库根目录的 `LICENSE` 是创建仓库时选择的 Apache-2.0 文本。归档内包含多个来源和组件，它们可能有各自的许可证、数据许可或访问限制；根许可证不会覆盖或替代归档内已有的第三方许可证。
