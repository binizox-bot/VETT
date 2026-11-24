# 本机开发环境与磁盘审计（2026-11-09）

## 结论

- C 盘：199.21 GB，最初可用 38.66 GB；完成缓存清理与 Conda 迁移后可用 43.12 GB。
- D 盘：731.22 GB，最初可用 63.13 GB；接收四个 Conda 环境及新包缓存后可用 59.38 GB。
- 本轮已释放约 3.30 GB，来源为 pip、npm、Conda 与 pnpm 的工具缓存。
- 最大的项目相关可疑冗余是 `D:\DockerData\DockerDesktopWSL\disk\docker_data.vhdx`，占 85.47 GB。
- Docker 当前设置明确指向 `C:\Users\PC\AppData\Local\Docker\wsl`；启动 Docker Desktop 后，C 盘现用数据盘更新为约 5.67 GB，而 D 盘 85.47 GB 文件的时间戳仍停留在 2026-10-13。当前 Docker 只有一个 Stirling PDF 镜像（3.82 GB）、一个容器（约 113 MB）、无命名卷、无构建缓存。对旧 VHDX 的只读解析显示约 60.35 GB 为 `desktop-containerd` 镜像 blob 与 overlayfs 快照（约 198 万文件，包含 Milvus、PyTorch、Chromium 层）；旧盘的 `docker\volumes` 只有极小元数据，`docker\containers` 为空。因此它是旧镜像/快照盘，不是当前 Docker 数据，也未发现需要保留的命名卷数据。
- `D:\pagefile.sys` 占 32 GB，是系统分页文件，不按项目垃圾处理。

## 已执行的安全清理

| 项目 | 结果 |
|---|---:|
| pip 下载缓存 | 释放约 1.09 GB |
| pnpm 无引用包与元数据 | 释放约 0.39 GB |
| Conda 未使用包、tarball、索引 | 已清理 |
| npm 缓存 | 已清理 |
| 迁移后旧用户 Conda 包缓存 | 释放约 0.99 GB |
| 已清理缓存合计 | 约 4.29 GB |

清理后已复测 Python、Node、npm、pnpm、Git 与 Conda，命令均可用，Conda 环境列表正常。

## 开发环境现状

| 组件 | 当前状态 | 位置/备注 |
|---|---|---|
| Python | 3.14.7 | `D:\Conda\python.exe` |
| pip | 26.2.1 | `D:\Conda\Scripts\pip.exe` |
| Conda base | 激活 | `D:\Conda` |
| Node.js | 24.21.0 | `D:\Download\node.exe` |
| npm | 11.19.0 | `D:\Download\npm.cmd` |
| pnpm | 11.25.0 | 当前命令来自 Codex runtime fallback；store 在 `D:\.pnpm-store\v11` |
| Git | 2.55.0 | 主命令在 `D:\Download\Git\cmd\git.exe`，Codex runtime 另带一份 |
| .NET SDK | 3.1.101 | 仅有旧 SDK；运行时另有 3.1.1 与 6.0.31 |
| Docker | 29.7.2 | Docker Desktop 当前未运行；WSL2 中只有 `docker-desktop` |
| VS Code | 命令报告 1.135.0 | 目录同时保留 1.135.0、1.138.0、1.139.0、1.139.1；更新标记指向 1.139.1，属于未完成/异常更新状态，暂不直接删除版本目录 |
| Java / Yarn / `py` launcher | 未检测到 | 如项目不需要，无需补装 |

环境整理建议：将 pnpm 固定为独立全局安装或 Corepack 管理，避免依赖 Codex runtime 的临时 fallback；确认兼容性后升级或卸载已过时的 .NET 3.1/6；修复或重装 VS Code 后再清理旧版本目录。

## Conda 与项目环境

| 环境 | 占用 |
|---|---:|
| `D:\CondaData\envs\binizox-dev` | 2.45 GB |
| `D:\CondaData\envs\railway-telemetry` | 0.71 GB |
| `D:\CondaData\envs\binizox-parser` | 0.26 GB |
| `D:\CondaData\envs\paddleocr-workspace` | 1.17 GB |
| Conda base `D:\Conda` | 0.94 GB |

四个环境已通过完整包集合对比和 Python 运行验证，旧源环境已由 Conda 正常移除。未来环境与包缓存已分别固定到 `D:\CondaData\envs` 和 `D:\CondaData\pkgs`。PaddleOCR 的 `run_all.ps1` 已切换到新解释器，并通过 PaddlePaddle 3.2.0、PaddleOCR、OpenCV 导入测试。

## D 盘结构

与项目无关的大头：Steam 228.48 GB、永劫无间 108.39 GB、守望先锋 68.29 GB、WeGameApps 40.27 GB。它们应通过各自启动器迁移或卸载，不与项目缓存混清。

项目/工具相关大项：

| 路径 | 占用 | 判断 |
|---|---:|---|
| `D:\DockerData` | 85.47 GB | 已确认是未被当前 Docker 使用的旧镜像/快照盘；没有命名卷数据，删除风险较低，但仍需明确确认 |
| `D:\Download` | 46.65 GB | 项目、安装包、便携软件混放 |
| `D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017` | 11.74 GB | 当前交付包 |
| `D:\Fast-whisper` | 5.37 GB | 独立项目/运行环境，确认不用后再删 |
| `D:\.pnpm-store` | 0.60 GB | 已执行 prune，剩余为在用内容 |
| `D:\Conda` | 0.94 GB | 当前 Python/Conda base，不可删除 |

其他非项目大项：`D:\Reviews` 6.76 GB 为游戏录屏；`D:\qycache` 6.08 GB 为爱奇艺缓存；`D:\xwechat_files` 5.52 GB 为微信数据。

## 当前 VETT 交付包

| 内容 | 占用 | 处理建议 |
|---|---:|---|
| `VETT_Cricket_v0.22_R16_Multisource_Dilemmas` | 5.99 GB | 主交付内容，保留 |
| `DeepTutor` | 4.87 GB | 含可重建环境与构建缓存 |
| `VETT_COMPLETE_RESEARCH_ARCHIVE_20260903` | 0.86 GB | 研究快照/证据归档，按交付需要决定 |
| 外层 ZIP | 0.26 GB | 与解压目录并存；体积不大，可作为完整备份保留 |

`DeepTutor` 内部：

| 内容 | 占用 | 处理建议 |
|---|---:|---|
| `web\.next\cache` | 1.19 GB | 可重建 |
| `web\.next-deeptutor\cache` | 1.19 GB | 可重建 |
| `web\node_modules` | 0.90 GB | 可由 lockfile 重装；需要离线运行则保留 |
| `.venv` | 0.91 GB | 可由 requirements/pyproject 重建；需要即开即用则保留 |
| `.git` | 0.25 GB | 如交付不需要历史可另做精简副本，原仓库建议保留 |

## 尚未执行、但可回收的项目

低风险、可自动重建的直接缓存（因当前执行策略阻止递归目录删除，本轮未动）：

| 路径 | 可回收 |
|---|---:|
| 百度网盘 `.accelerate` | 8.86 GB |
| NVIDIA `DXCache` | 6.56 GB |
| uv cache | 1.84 GB |
| Windows 用户 Temp | 0.82 GB |
| CrashDumps | 0.46 GB |
| VETT 两套 Next.js cache | 2.38 GB |
| 合计 | 20.92 GB |

需要明确确认的高收益项：

1. 删除旧 Docker 数据盘：85.47 GB。
2. 清空上述可重建缓存：约 20.92 GB。
3. 删除明确不用的安装包：CUDA 安装包 3.01 GB、旧 NVIDIA 驱动安装包 0.91 GB、Codex MSIX/ZIP 约 1.62 GB。
4. 处理旧项目依赖：`Binizox\web\node_modules` 1.84 GB、VETT `DeepTutor\web\node_modules` 0.90 GB、VETT `.venv` 0.91 GB。

若只执行第 1、2 项，理论上还可释放约 106 GB；按当前状态估算，D 盘可用空间可从约 59.4 GB 增至约 147 GB，C 盘可用空间可从约 43.1 GB 增至约 61 GB（实际值会受文件占用、稀疏文件与系统活动影响）。
