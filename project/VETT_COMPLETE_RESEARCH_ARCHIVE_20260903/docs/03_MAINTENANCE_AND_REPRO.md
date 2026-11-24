# 安装、离线复现与维护

## 先验证，后执行

以下命令在解压后的`VETT_COMPLETE_RESEARCH_ARCHIVE_20260903/`根目录运行。验证器与新编安全测试仅需Python标准库。当前归档验证使用Python 3.12；这不是所有历史实验的依赖锁。

```bash
python tools/verify_archive.py .
python tools/run_safe_smoke_checks.py --workspace workspace_snapshot --output maintenance_runs/local_smoke
```

也可以在解压前验证ZIP：

```bash
python tools/verify_archive.py /path/to/VETT_COMPLETE_RESEARCH_ARCHIVE_20260903.zip
```

Windows PowerShell可用`py -3`替代`python`。请使用短目录，避免部分解压软件的路径长度限制。原始文件名保留，不能为了方便批量改名后再声称哈希未变。

## 安全复核脚本实际做什么

- 校验R10六份预测的冻结哈希，并调用原评分器把结果写到新输出目录；逐份比较原评分JSON。
- 校验R12的公开输入和四份预测的冻结哈希；不调用其冻结程序。
- 调用R13-C与R14评分器自检，并显式传入新输出路径。
- 将R15复制到临时目录，执行评分器和发布验证。
- 在另一个临时目录重新生成R15公开实例、金标、证据、自测、盲包和两个预览；比较七份产物的字节哈希。
- 不调用外部模型、不启动新评测、不读取密钥、不改写历史实验。

本次结果为35/35通过，详见`verification/smoke/SMOKE_TEST_RESULTS.json`。这个结论仅覆盖列明的检查，不代表20个实验的所有生成流程都重跑过。

## 各类依赖

`manifests/STATIC_CODE_AUDIT.json`逐脚本列出import与历史绝对路径；`manifests/ENVIRONMENT_OBSERVED.json`记录本次可观察到的版本。

| 使用范围 | 依赖/注意事项 |
| --- | --- |
| 新归档验证、安全复核、R13-C/R14/R15主要评分 | Python标准库；建议3.12 |
| 部分早期数值与约束合成 | numpy、scipy、scikit-learn；具体以import索引为准 |
| JavaScript基线与JSON Schema验证 | Node.js及对应脚本require的包；不要把Python环境当成充分条件 |
| 论文PDF抽取与旧页面预览 | 原PDF和已抽取文本/图片都在包内；仅重建预览时才需要对应PDF工具 |
| 新真实模型实验 | 正常配置的模型端点、型号、上下文与输出预算；本包不提供密钥和模型权重 |

没有找到可覆盖全部历史阶段的统一锁文件。重新运行旧生成器前，先在隔离环境根据对应脚本建立阶段级依赖文件，并把实际安装版本和命令写进新运行记录。禁止用当前环境信息推定旧实验使用过相同版本。

## 单独运行R14评分器

```bash
python workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.20_r14_field_independent/score_r14_predictions.py \
  --selftest --output maintenance_runs/r14_scorer_selftest.json
```

先创建`maintenance_runs/`。正常预测评分用`--prediction`与`--output`；输入格式见数据契约文档。脚本默认输出可能位于实验目录，因此每次都显式指定新输出路径。

## 单独重建R15

从归档根运行：

```bash
python workspace_snapshot/vett_cricket_pilot_v1/scripts/build_r15_synthetic_dualworld.py \
  --ledger workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.21_r15_synthetic_dualworld/construction/match_0031.synthetic_delivery_ledger.json \
  --output maintenance_runs/r15_rebuilt
```

该命令只重建R15实例产物；完整实验目录中的人工报告、验证脚本和历史失败说明由归档保留，不是此生成器的全部输出。

R15评分命令：

```bash
python workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.21_r15_synthetic_dualworld/score_r15_predictions.py \
  --gold workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.21_r15_synthetic_dualworld/private_gold.json \
  --prediction maintenance_runs/my_prediction.json \
  --output maintenance_runs/my_score.json
```

## 全部旧阶段恢复

`workspace_snapshot/`保持原来的相对布局，上游220场、审核CSV、辅助审计模块均位于主工程旁。旧README中的源码入口仍可定位。检查`STATIC_CODE_AUDIT.json`的绝对路径清单，将新工作副本的参数改为实际路径；不要在只读档案中批量替换路径。

部分构造程序可能读写默认目录，即使传`--help`也应先检查`if __name__`之前的代码。`freeze_and_score_*`和部分`validate_*`会写文件，不能当作纯只读命令批量执行。初次新根逐球求解应设置进程级时间上限并保存stdout/stderr，不做无限等待。

## 维护工作流

1. 保存本ZIP原件及校验文件；解压目录作为只读基线。
2. 复制需要迭代的工程到独立工作目录，初始化或沿用自己的Git仓库。归档本身不提供历史Git提交。
3. 为每轮建新版本目录；选根、提示词、判据、种子与模型运行计划先冻结。
4. 新增测试与变更说明，保留失败文件，防止生成器覆盖失败轮输出。
5. 先复核原子金标和公开支持性，再执行盲测；预测冻结后再评分。
6. 与至少一个旧版本回归对照，把结构变化、分母变化与模型变化分开报告。
7. 更新文件清单与哈希，再交付新归档。新增文件会使原清单验证提示差异，这是预期版本变化。
