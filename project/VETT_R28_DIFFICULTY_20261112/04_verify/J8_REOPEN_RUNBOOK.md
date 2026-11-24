# J8 修复判据与重开命令（给 t20 pipeline_engineer / t8 verifier）

| | |
|---|---|
| **门** | J8 模板卫生（`VETT-R28-GATE-J-20261112` 唯一阻塞项） |
| **当前判定** | **FAIL** —— `T2.naturalness_pair.choice.v1` 残留在非生产运行与配置里 |
| **判定出处** | [`J_GATE.json`](J_GATE.json) → `items.J8_template_hygiene`；说明见 [`J_GATE.md`](J_GATE.md) §9 |
| **重开入口** | `python 04_verify\scripts\j_gate.py` |
| **盲包复扫入口** | `python 04_verify\scripts\reaudit_packets.py --inject-selftest` |
| **协议依据** | `02_design/protocol.json`（`4d9fb8c0`→现 `a07463aa…02ff7a`，PAMEND-003 后）：T2 只报序判定、模板必须是 `T2.naturalness_pair.v1`；变体进缓存键/账本即 FAIL |

---

## 1. 修复判据（三条，全部机器可判；缺一不可）

J8 的 PASS 条件写在 `j_gate.py::j8_template_hygiene` 里，`ok = 三条同时成立`：

| # | 判据 | 机器检查 | 当前实测 |
|---|---|---|---|
| **C1** | **主路径零污染**：生产账本与生产标注里没有任何变体条目 | 905 条 `local_cost_ledger.jsonl` 与 320 条 `annotations_T2_naturalness.jsonl` 全为 `T2.naturalness_pair.v1` | 已满足（0 / 0） |
| **C0** | **J8 的 PASS 依据顺序**：C1 + C3 + C4 + C5 为结构证据，C2 为辅助 | 见 `J_GATE.md` §9.1（F4 修复记录） | 已确立 |
| **C2** | **`t14/runs/**` 下无变体痕迹** | raw-bytes 扫 `choice.v1` **+** 结构扫描（`.json` 整文件解析、`.jsonl` 逐行；解析失败记 `unauditable`，生产目录内不可解析即 FAIL） | 已满足（raw 0 / 结构 0 / unauditable 0） |
| **C3** | **config 字段消失或显式废弃** | `t14/runs/t14_main/config.json` 的 `t2_choice_template_version` 满足下列任一形态 | **未满足**：值为 `"T2.naturalness_pair.choice.v1"` |

C3 接受的形态（任一即可）：字段不存在 / `null` / 空串 / `{"deprecated": true}` / 任何含 `deprecated` 的字符串。

> C2 的含义：**只搬走账本、留下 cache objects 不算修复**；C3 的含义：**加一句注释但保留字段也不算修复**。
> 两者由同一次配置改写一起关闭，所以预期 C2、C3 同时变绿。

---

## 2. 隔离目录清单（C2 的修复动作）

需要移出 `03_build/local/t14/runs/` 的目录（当前 10 个命中文件全在这两个目录 + 两个 config）：

| 目录 | 说明 | 处理 |
|---|---|---|
| `03_build/local/t14/runs/t14_smoke/` | 修复前预检运行（含变体 ledger + cache objects） | 整体移入隔离区 |
| `03_build/local/t14/runs/t14_dry/` | dry-run（`config.json` 含变体） | 整体移入隔离区 |
| `03_build/local/t14/runs/t14_main/config.json` | 生产 config，但**声明了**变体字段 | 就地修复（删字段/标 deprecated），**不要**移走整个 `t14_main` |
| `03_build/local/t14/runs/t14_main/local_cost_ledger.jsonl` | 生产账本（干净） | 保留，只复算 |
| `03_build/local/t14/runs/t14_main/annotations_T2_naturalness.jsonl` | 生产标注（干净） | 保留，只复算 |

**建议隔离位置**（必须在 `t14/runs/` **之外**，否则 C2 永远不过）：

```
03_build/local/quarantine/t14_pre_fix_20261112/
├── QUARANTINE.json          # {"reason": "...", "moved_from": [...], "moved_at_utc": ...,
│                            #  "rule": "任何统计/报告/门不得读取本目录"}
├── t14_smoke/
└── t14_dry/
```

`QUARANTINE.json` 里请写死：**本目录只作审计留存，禁止被 t19/t21/t11/t8 任何统计读取**。

---

## 3. 修复后的复算步骤（t20 执行，t8 复核）

```powershell
cd VETT_R28_DIFFICULTY_20261112\03_build\local\t14\runs\t14_main

# C1：生产账本与生产标注必须 100% 是冻结模板
D:\Conda\python.exe -c "import json,collections,pathlib; \
 c=collections.Counter(json.loads(l)['prompt_template_version'] for l in \
 pathlib.Path('local_cost_ledger.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()); print('ledger',dict(c))"
# 期望：{"T1.factor_visibility.v1": 323, "S1.span_topic.v4": 242, "T2.naturalness_pair.v1": 340}

D:\Conda\python.exe -c "import json,collections,pathlib; \
 c=collections.Counter(json.loads(l)['prompt_template_version'] for l in \
 pathlib.Path('annotations_T2_naturalness.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()); print('ann',dict(c))"
# 期望：{"T2.naturalness_pair.v1": 320}

# C2：runs/ 下不应再出现 choice.v1
D:\Conda\python.exe -c "import pathlib; \
 h=[str(p) for p in pathlib.Path('..').rglob('*') if p.is_file() and p.suffix in ('.json','.jsonl') \
 and 'choice.v1' in p.read_text(encoding='utf-8',errors='ignore')]; print('hits',len(h),h[:5])"
# 期望：hits 0 []
```

然后重开 J8：

```powershell
cd VETT_R28_DIFFICULTY_20261112\04_verify
D:\Conda\python.exe scripts\j_gate.py                       # 重算全门（约 2 s）
D:\Conda\python.exe scripts\j_gate.py --json-only --check-md # 文档/结果一致性，期望 20/20
```

**期望输出**
- `items.J8_template_hygiene.verdict == "PASS"`，且
  `config_field.ok == true`、`variant_files_under_runs == []`；
- `ruling.blocking == []`（J8 是唯一阻塞项，清空即无阻塞）；
- 其余 J 项判定不变（T1 PASS 0.9750、T2 PASS 0.9905、S1/C1 INSUFFICIENT、T3 DESCRIPTIVE_ONLY、kappa NOT_ESTIMATED、J5 NOT_RUN）。

---

## 4. 盲包复扫（与 J8 无关，但发布前必跑）

PAMEND-003 把 R28 自身 id 形态补进了禁用模式表（11 条）。任何新增/重建的盲包都要用**当前协议**复扫：

```powershell
cd VETT_R28_DIFFICULTY_20261112\04_verify
D:\Conda\python.exe scripts\reaudit_packets.py --inject-selftest
# 默认扫 t16 的 T1_packets / T1_localarm_packets / T2_packets（64 包）
# 期望：violations 0，self-test 六条注入全部 BLOCKED、clean_packet PASS，exit 0

# 换目录/换文件集：
D:\Conda\python.exe scripts\reaudit_packets.py --root <packets_dir> --glob "**/*packets*.jsonl"
# 机器可读：--json
```

`--inject-selftest` 会逐条断言**点名的模式**被触发（不是"随便报了个违规"）：
`BP-R28-ITEM` / `BP-R28-HELDOUT-ITEM` / `BP-R28-FAMILY` / `BP-R28-SPAN` / `BP-MATCH-ID` / `BP-FAMILY`。
这条自检的意义：captain 原给的 `r28q_[0-9a-f]{12}` 与真实题号（`r28q_0001`）不匹配，若照抄会得到一条
**永不触发的空规则**——扫描全绿但仍是洞。自检就是防这种"补了等于没补"。

---

## 5. 什么**不算**修复（反面清单，t8 可直接据此判 FAIL）

1. 只移走 `local_cost_ledger.jsonl`、留下 `cache/objects/`（C2 仍红）；
2. 在 `config.json` 里加注释说明该字段已废弃，但字段仍在（C3 仍红）；
3. 把变体字符串改名成 `T2.naturalness_pair.choice.v2`（仍命中 `choice.v1` 前缀族？不——但属于换名绕过，
   按 R-BL/R-Q3 视为未修复；t8 应检查模板版本集合只含冻结值）；
4. 删掉 `t14_smoke` 而不是隔离（丢审计痕迹；不可接受——t8 需要能复查"当时发生了什么"）；
5. 只跑 `j_gate.py` 看 PASS 而不复算 C1/C2（数字可能是被改过的工作区给的）。

---

## 6. 关闭 J8 之后仍**不等于** T2 可发布

J8 只回答"模板卫生"。T2 进发布链路还要满足：

- 预注册 v1.2.0 的三基线门槛（G1/G1r，`52.89 / 54.22 / 73.33 + exact 32`，双阈值取小、严格小于）；
- 有效 n（EN1–EN6：320/320/320；与 R26.15 比较按族 n_eff≤25 + 按族 bootstrap）；
- t19 主端点 `paired_accuracy_drop`（预注册冻结，不得改）；
- T2 **只报序判定**（0.9905 口径），绝对分只作描述；
- 任何 T1 结论必须带上 J1c 的限制：**T1 是覆盖词表匹配，不是"读懂证据支持"**；`authority_policy` 子组 0.7500。

---

## 7. 责任人 / 时序

| 步骤 | 责任 | 触发点 |
|---|---|---|
| 隔离 `t14_smoke` / `t14_dry` + `QUARANTINE.json` | local_operator | t14_main / t21 跑完后 |
| 修 `t14_main/config.json`（与 `t14_dry` 一并） | local_operator | 同上 |
| 复算 C1/C2 + 跑 `j_gate.py` 重开 J8 | pipeline_engineer (t20) | 修复提交后 |
| 独立复核（不得复用上面的脚本结论，需自己复算三判据 + 跑 `reaudit_packets.py`） | verifier (t8) | t20 关闭后 |

> 回归测试：`04_verify/tests/test_j_gate.py`（14 项，含 verifier 的 pretty-JSON 复现样本 `test_pretty_printed_variant_is_detected`）。
> 备注：`j_gate.py` 与 `reaudit_packets.py` 都是只读、纯标准库、零网络；`j_gate.py` 用
> `--generated-at` 钉住时间戳后两次构建逐字节相同（当前 digest 稳定性已由 `--determinism-check` 证明）。
