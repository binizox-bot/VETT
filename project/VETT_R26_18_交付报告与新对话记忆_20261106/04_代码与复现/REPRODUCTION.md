# 本地复现说明

## 0. 进入原项目

```powershell
Set-Location 'D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_Cricket_v0.22_R16_Multisource_Dilemmas'
$env:PYTHONPATH='src'
```

先确认`python --version`能够返回真实版本。如果系统`python.exe`只是Windows商店占位
程序，应改用Codex工作区依赖报告给出的实际Python可执行文件。例如本次复验使用：

```powershell
$vettPython='C:\Users\PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $vettPython --version
```

后文的`python`都可以替换为`& $vettPython`。以下流程全部可以在不读取API密钥、
不产生费用的情况下运行。

## 1. 回归测试

```powershell
python -m unittest discover -s tests
```

冻结时预期：`Ran 202 tests`，结果`OK`。

2026-11-06交付复验使用实际工作区Python运行，结果为`Ran 202 tests in 190.710s`、
`OK`。一次对Windows商店占位`python.exe`的调用在进入测试框架前退出，不属于测试失败。

## 2. R26.17保存响应的非官方回放

```powershell
python -m vett_r26.canonical_set_replay `
  --config eval_configs/r26_18_glm53_canonical_set_sentinel5_blocked.json `
  --output-dir analysis/r26_18_canonical_set_replay_match0021
```

预期工件：

- `analysis/r26_18_canonical_set_replay_match0021/CANONICAL_SET_REPLAY.json`
- 状态必须保留为非官方后验回放；不得把旧R26.17结果改成正式通过。
- 去重前后集合语义评分字典应逐项一致。

## 3. 五场零请求预检

```powershell
python -m vett_r26.sentinel_preflight `
  --config eval_configs/r26_18_glm53_canonical_set_sentinel5_blocked.json `
  --output-dir analysis/r26_18_canonical_set
```

预期至少满足：

- 5场、25题完整；
- Oracle、未知合法引用和重复故障注入通过；
- provider请求数为0；
- `execution_authorized=false`；
- 估算费用不超过1.4元硬上限。

## 4. 本地准入

```powershell
python -m vett_r26.canonical_set_admission `
  --config eval_configs/r26_18_glm53_canonical_set_sentinel5_blocked.json `
  --output-dir analysis/r26_18_canonical_set
```

预期状态：

```text
LOCAL_PROTOCOL_PASS_EXTERNAL_EXECUTION_BLOCKED
```

## 5. 外部请求边界

本文不提供可直接复制执行的付费命令。需要外测时应当：

1. 由用户在新对话中重新明确授权；
2. 复制冻结配置，只允许变更授权字段和新的空输出目录；
3. 再跑一次零请求预检并保存差异；
4. 确认费用硬上限1.4元、零重试、首个硬失败停止；
5. 确认不会重发已经有终态的请求。

没有新授权时，读取`.secrets/`、调用provider或创建付费重试都不属于复现步骤。
