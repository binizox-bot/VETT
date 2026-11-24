# E4 supplemental (V+/V-/V0 triplets)

- `supplemental_to_t19: true` · generated 2026-11-12T15:24:04Z
- items: 40 · calls: 120 · variants: {'v_plus': 40, 'v_minus': 40, 'v_order': 40}
- num_predict actual: [640] (planned 640)
- conformance: {'stop': 120}

| column | n used | stable | rate | 95% CI | parse fail | gate |
|---|---:|---:|---:|---|---:|---|
| V- substitution (primary) | 32 | 16 | 0.500 | [0.336, 0.664] | 0 | >=80%: False |
| V- introduced (separate) | 8 | 1 | 0.125 | [0.022, 0.471] | 0 | not merged |
| V0 order permutation | 40 | 5 | 0.125 | [0.055, 0.261] | 0 | >=90%: False |

- flip+ (V+): 21/40 = 0.525; random floor (V0 flip) = 0.875; >=2x random: False
- blind_flip = flip+: 0.525; flip to V+ gold exact9 = 1, >=7/9 = 9
- V- availability: substitution 271/320, introduced 49/320, none 0/320 (mechanical, pre-model).
- **S12 trigger: True** — S12 触发：order permutation 使 87.5% 的作答改变（stability0=12.5%），非决定性事实变更使 50% 的作答改变（stability-=50%）；模型的 9 字段答案对与金标无关的呈现变化高度敏感。E1 的 0.56pp 配对差远低于该 order-noise floor(87.5%)，因此 E1 的 '呈现难度' 差异不能与模型自身的呈现噪声分离。

## t11 framing (captain-mandated)
- Q1 closing: E1 的 0.557pp 不是'数据集没变难'，而是'这个模型压根没在解题'：V0=0.125 意味着仅打乱文档顺序，87.5% 的情况下答案就变了；如果模型本来就不读证据，把证据呈现得更难当然不会让它更糟。
- Unifying mechanism: 唯一能同时解释 E1（无难度效应）、E2（非单调）、E3（无机制归因）、E4（三条门全败）、record-exact 0.78% 的机制是：输出由位置与噪声驱动。
- Refutes prereg §6: 原计划 §6 假设 E4 能证明'模型读文档还是在猜'；答案是在猜、接近随机，但不是均匀随机——V0 切换率 0.875 远高于 0.5，属于位置敏感噪声。
- Flip below floor: flip+=0.525 < 随机地板 0.875：跟着决定性事实变的比例还不如只换顺序带来的变化多 → 没有证据锚定。

Completed t19 files (`analysis.json`, `analysis_e1/e2/e3.json`, `e1_raw.jsonl`) were not modified.
