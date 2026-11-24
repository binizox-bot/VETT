# VETT-Cricket 完整交付包（R19，2026-10-17）

本目录是可独立保存的完整工作交付，包含当前 R16–R19 工程、各版本数据与审计产物、2026-09-03 全量研究归档、220 场原始压缩包，以及 220 场解压工作副本。

## 从这里开始

1. 阅读 `VETT_Cricket_v0.22_R16_Multisource_Dilemmas/README.md`。
2. 最新数据位于 `VETT_Cricket_v0.22_R16_Multisource_Dilemmas/release_r19/`。
3. 只可把 `release_r19/public/` 交给待测模型；`private/`、`audit/`、发布报告和本包其他材料都可能泄漏答案或审计逻辑。
4. 自动复核流程见 `VETT_Cricket_v0.22_R16_Multisource_Dilemmas/docs/DATA_AND_AUDIT_GUIDE.md`。
5. 历史研究入口见 `VETT_COMPLETE_RESEARCH_ARCHIVE_20260903/README_START_HERE.md`。

## 目录内容

| 路径 | 说明 |
| --- | --- |
| `VETT_Cricket_v0.22_R16_Multisource_Dilemmas/` | 当前 Git 工作树内容（R16–R19 源码、测试、文档、发布数据及历史发布备份） |
| `VETT_COMPLETE_RESEARCH_ARCHIVE_20260903/` | 原样保留的全量研究归档，含历史快照、清单、复核和维护材料 |
| `Self-cricket-clean_text_scorecard_v1_220_matches.zip` | 用户最初提供的 220 场数据压缩包 |
| `Self-cricket-clean_text_scorecard_v1_220_matches_extracted/` | 当前解压工作副本，含 220 场数据和配套分析材料 |
| `VERIFICATION_RESULTS.json` | 本次打包前自动测试与各版本审计结论 |
| `PACKAGE_MANIFEST.json` | 载荷文件路径、字节数和 SHA-256 清单 |
| `PACKAGE_SHA256SUMS.txt` | 包内所有非自身文件的 SHA-256 |

## 完整性边界

全量研究归档目录按原有字节复制。当前工程和 220 场解压工作副本仅排除了 `.git`、`__pycache__`、`.pytest_cache` 和 `*.pyc`；这些是版本库元数据或可再生缓存，不属于数据、源码、文档或发布产物。历史备份没有删减。

压缩包生成后会逐条读取 ZIP 成员，并按 `PACKAGE_MANIFEST.json` 重新计算载荷 SHA-256。外部同名 `.sha256` 文件用于验证整个 ZIP。

## 当前机器结论

打包前 52/52 项测试通过；R16、R17、R18、R19 的独立语义审计和发布清单审计全部 PASS。R19 的已登记全局/逐目标最新修订捷径为 0/84，固定修订序位攻击的最高准确率为 6/84（7.14%）。

这些结论不包含人工自然度审计，也不包含外部语言模型盲测，不能据此宣称所有语言模型均无法求解。
