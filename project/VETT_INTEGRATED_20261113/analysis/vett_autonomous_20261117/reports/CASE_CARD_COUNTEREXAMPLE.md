# 案例卡：长度匹配非证据删除反例

- case_id: CASE_B021_0002_NEI_CONTROL
- match_root: match_0002
- source_version: commentary-v1
- source_type: controlled_rewrite
- innings: 2
- entity_ids: match_0002
- field_ids: inn2.total_runs, inn2.total_wickets
- evidence_spans: 目标终局句在 O/WI/OI/NEI 中均保留；NEI_OI 删除 313 字无关句，NEI_WI 删除 251 字无关句
- answerability_status: explicit_total_present_in_all_variants
- diagnostic_variant_ids: O, WI, OI, NEI_OI, NEI_WI
- verification_status: auto_checked_source_diff
- candidate_patch: do_not_claim_OI_specific_effect；保留为未定，扩展匹配对照
- full_task_validation: B021 0/6；B003 O 0/6、OI 3/6

## 配对结果

- O: 0/6
- OI: 3/6
- NEI_OI: 0/6
- NEI_WI: 0/6
- 删除长度：WI 269、OI 364、NEI_OI 313、NEI_WI 251

## 原始回答样例（B021 NEI_OI, qwen2.5:7b-instruct-q4_K_M）

- raw: {
  "inn2.total_runs": 252,
  "inn2.total_wickets": 8
}
- parsed: {"inn2.total_runs": 252, "inn2.total_wickets": 8}

## 结论

- 删除长度匹配的非证据句也会让模型全错；
- B003 的 OI +3 未被 NEI 复现，不能当作“删另一局比分”的特异收益；
- 人工未复核，pending_human_review。
