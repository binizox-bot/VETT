# R26.18 阶段0冻结基线复验报告

## 结论

阶段0复验通过，状态为：

`PASS_NO_DRIFT_EXTERNAL_EXECUTION_BLOCKED`

R26.15候选在复验前后逐文件聚合SHA-256一致；新生成的零请求预检和本地准入工件与冻结工件逐字节一致。当前仍未授权外部执行或数据变更。

## 范围与边界

- 工作对象：`r26_15_content_dependency_candidate_v3`
- 评测协议：R26.18 `canonical_set_v2`
- 仅运行本地哈希、回归测试、零请求预检和本地准入
- 未读取`.secrets/`或任何API密钥
- 未调用provider，未产生费用
- 未修改R26.15候选、金标、题目或评测合同
- 原项目没有`.git`元数据，因此以逐文件SHA-256清单代替Git提交状态证明

## 基线清单

| 范围 | 文件数 | 字节数 | 聚合SHA-256 |
| --- | ---: | ---: | --- |
| R26.15候选 | 165 | 93,346,177 | `2cb1ea2c62d1b8d57b6c20bbc3c22ed7ad0440ca73f68946d24fcbf0ebab9417` |
| `src/vett_eval` | 10 | 241,599 | `7c279887b90eb88e7f0b7d2e51aa5c932e11d3fedb14defcb4e8445bd4b26ed1` |
| `src/vett_r26` | 57 | 738,236 | `580b05bcf9d733ff342039578e5fb14c5c215791fba889e477d4d278534af076` |
| `tests` | 31 | 273,243 | `b18ad0a262c6f5f56c490d6335627aaa2740eb2953cae76be16460b8b337b12e` |

Python缓存文件和`__pycache__`不计入代码聚合哈希。完整逐文件记录见`BASELINE_MANIFEST.json`。

## 回归测试

使用Python 3.12.14运行：

```text
Ran 202 tests in 100.508s
OK
```

测试日志SHA-256：

`cb8d4ca64b7906538a8fb76d5e680f32dc988e47e17959ddf1e26b8dadb69707`

## 零请求预检

| 项目 | 结果 |
| --- | --- |
| 状态 | `REQUEST_READY_BLOCKED_BY_AUTHORIZATION` |
| 场次 / 题目 | 5 / 25 |
| 全部门 | 通过 |
| 错误数 | 0 |
| provider请求 | 0 |
| `execution_authorized` | `false` |
| 零缓存保守费用估算 | 1.0074元 |
| 最大上下文利用率上界 | 26.4562% |
| 最小Oracle输出余量 | 1.551163倍 |

新旧预检SHA-256均为：

`538b25f91fdc1bcbdea6379323f056f9238b5f8e29db195f2ed1e6c7698d0f81`

因此两份预检逐字节一致。

## 本地准入

| 项目 | 结果 |
| --- | --- |
| 状态 | `LOCAL_PROTOCOL_PASS_EXTERNAL_EXECUTION_BLOCKED` |
| 全部准入门 | 通过 |
| R26.18 provider请求 | 0 |
| 外部执行授权 | `false` |
| 数据变更授权 | `false` |
| 数据候选 | `r26_15_content_dependency_candidate_v3` |

新旧准入SHA-256均为：

`ad3bf09453b262a90214b9287faeefcf84ba9f8591ae5dbb41d3e4088bef340c`

因此两份准入工件逐字节一致。

## 数据未漂移证明

R26.15候选在复验前后的聚合SHA-256均为：

`2cb1ea2c62d1b8d57b6c20bbc3c22ed7ad0440ca73f68946d24fcbf0ebab9417`

复验过程没有改变165个候选文件。

## 下一决策点

本地协议工作保持完成状态。若没有新的明确费用授权，应停留在当前阻断状态。若继续阶段1，需要针对冻结的R26.18五场Sentinel5单独授权；该授权不能自动覆盖重试、Pilot20、第二模型或220场物化。
