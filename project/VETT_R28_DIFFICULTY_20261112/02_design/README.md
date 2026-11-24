# 02_design — 评测协议（t12）

本目录是 R28 的**评测协议**冻结产物：谁可以判什么、能看什么、怎么记账、什么才算数。
协议本身不含任何新的测量结论；所有实测数字都从 t18 的 `routing_card.json` /
`capability_matrix.json` 与 t2 的 `BASELINES.json` 原样派生并逐文件绑定 sha256。

| 文件 | 作用 |
|---|---|
| [`PROTOCOL.md`](PROTOCOL.md) | 人类可读的冻结协议（14 节 + 2 附录，50 条规则） |
| [`protocol.json`](protocol.json) | 机器可读镜像（派生自权威文件，`--check` 会重建比对） |
| [`protocol_freeze.json`](protocol_freeze.json) | 冻结指纹（逐文件 sha256 + 9 个语义摘要） |
| [`PROTOCOL.sha256`](PROTOCOL.sha256) | `sha256sum -c` 可用的指纹清单 |
| [`protocol_verify_result.json`](protocol_verify_result.json) | V1–V22 逐项结果与证据 |
| [`protocol_amendments.jsonl`](protocol_amendments.jsonl) | append-only 修订日志（当前为空） |
| [`scripts/judge_protocol.py`](scripts/judge_protocol.py) | 可执行协议引擎（断言 / 盲包 / 缓存 / 底线 / DEGRADED） |
| [`scripts/build_protocol.py`](scripts/build_protocol.py) | 从权威文件派生 `protocol.json` + 证据快照 |
| [`scripts/protocol_verify.py`](scripts/protocol_verify.py) | 校验器（`--freeze` / `--check`，exit 0/4） |
| [`tests/test_judge_protocol.py`](tests/test_judge_protocol.py) | 离线单测（77 项，无网络 / 无模型） |
| [`evidence/routing_evidence_snapshot.json`](evidence/routing_evidence_snapshot.json) | 13 条路由与实测证据的可审计桥 |

## 复现

```powershell
cd VETT_R28_DIFFICULTY_20261112\02_design
D:\Conda\python.exe scripts\build_protocol.py            # 派生 protocol.json（幂等）
D:\Conda\python.exe scripts\protocol_verify.py --freeze   # 冻结指纹
D:\Conda\python.exe scripts\protocol_verify.py --check    # V1–V22（22/22 PASS, exit 0）
D:\Conda\python.exe -m unittest discover -s tests -v      # 77 tests OK
```

## 下游接入

```python
import sys; sys.path.insert(0, r"...\VETT_R28_DIFFICULTY_20261112\02_design\scripts")
import judge_protocol as jp

jp.assert_local_allowed("T1_factor_visibility", prompt=text)       # DENY/超限直接抛
packet = jp.build_blind_packet(item, "T1_factor_visibility", salt) # 越权直接抛
key = jp.cache_key(task, text, params, template_version, jp.MODEL_DIGEST)
report = jp.require_baseline_trio(accuracy_report)                 # 缺三基线直接抛
jp.make_degraded(task=..., reason_code=..., fallback_used=..., affected_items=[...])
```

## 边界

- 只读 R26.15：`--check` 的 V22 每轮重算 165 文件 / 93,346,177 字节 / 聚合 `343afde4…51bd`。
- 零付费 API、零联网、零第三方包；本地推理只在 `03_build/local` 侧发生，本目录不触发推理。
- 协议与预注册冲突时以预注册 v1.1.0 为准；改协议必须重新 `--freeze` 并在
  `protocol_amendments.jsonl` 登记，否则 V22 的冻结摘要校验会失败。
