# 展开文件上传范围

- 来源：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017`
- 日期：2026-11-24（Asia/Shanghai）
- 纳入：除 `DeepTutor/` 与 `.secrets/siliconflow.env` 外的全部本地普通文件和目录
- 文件数：35,246（添加本说明及 junction 说明前）
- 逻辑大小：7,979,360,668 字节（约 7.431 GiB）
- 排除：`DeepTutor/`，按用户明确要求不展开上传
- 安全排除：`.secrets/siliconflow.env`（72 字节），检测为疑似有效凭据，不写入永久 Git 历史
- 特殊对象：一个指向项目外部 Codex Node 运行时的 junction 不跟随上传，目标记录在对应 `.JUNCTION.txt` 中
- 空目录：Git 不直接记录空目录；17 个原始空目录通过 `.gitkeep` 说明文件保留目录结构

完整打包报告、原始文件清单、ZIP 分卷与恢复脚本位于仓库根目录。
