# 结果证据登记与可引用表

这里只集中展示有冻结预测档案的R10/R12关键矩阵。全部其他结果、消融、失败与机械检查见本页末尾的结果文件全集索引及原始JSON。

历史文件声明的模型平台为GPT-5.5；本次检查可验证文件与评分一致性，不重新认证历史服务端模型身份或上下文隔离。

## R10六方法冻结预测

| 方法 | 严格正确/336 | 严格错误率 | 核心标量错误/232 |
| --- | ---: | ---: | ---: |
| direct_no_cot | 234/336 | 30.36% | 18/232 |
| direct_cot | 253/336 | 24.70% | 0/232 |
| t3_paper_direct_integration_variant | 224/336 | 33.33% | 27/232 |
| t3_provenance_enhanced | 251/336 | 25.30% | 0/232 |
| mapmake_paper_style | 253/336 | 24.70% | 0/232 |
| mapmake_scope_version_enhanced | 253/336 | 24.70% | 0/232 |

来源：[完整成绩](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.15_mainstream_method_check/GPT55_R10_RESULTS.json)；[误差分解](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.15_mainstream_method_check/GPT55_R10_ERROR_DECOMPOSITION.json)。严格错误受复合字段和无证据Referee影响。

## R12四方法冻结预测

| 方法 | 规范值正确/317 | 规范值错误率 | 事实内容错误率（原报告） |
| --- | ---: | ---: | ---: |
| direct | 315/317 | 0.63% | 0.00% |
| cot | 317/317 | 0.00% | 0.00% |
| t3_provenance_enhanced | 317/317 | 0.00% | 0.00% |
| mapmake_scope_version_enhanced | 264/317 | 16.72% | 16.72% |

来源：[完整成绩](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.17_r12_naturalized_multiroot/GPT55_R12_RESULTS.json)；[最终报告与Direct限制说明](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.17_r12_naturalized_multiroot/GPT55_R12_FINAL_REPORT.md)。

## 其余结果文件全集

这个索引按文件名检索出结果、评分、自测、消融、审计、决策与冻结资料，保留目录上下文。文件名含方法名并不自动获得模型实测资格。

- [v0.10_r6_single_root_strict/R6_CANDIDATE_SOLVER_AUDIT.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.10_r6_single_root_strict/R6_CANDIDATE_SOLVER_AUDIT.json)
- [v0.10_r6_single_root_strict/R6_SINGLE_DECISION.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.10_r6_single_root_strict/R6_SINGLE_DECISION.md)
- [v0.10_r6_single_root_strict/R6_SINGLE_SELFTEST.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.10_r6_single_root_strict/R6_SINGLE_SELFTEST.json)
- [v0.10_r6_single_root_strict/R6_SINGLE_SELFTEST.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.10_r6_single_root_strict/R6_SINGLE_SELFTEST.md)
- [v0.10_r6_single_root_strict/R6_SINGLE_SELFTEST_REGRESSION.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.10_r6_single_root_strict/R6_SINGLE_SELFTEST_REGRESSION.json)
- [v0.10_r6_single_root_strict/R6_SINGLE_SELFTEST_pre_naturalization.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.10_r6_single_root_strict/R6_SINGLE_SELFTEST_pre_naturalization.json)
- [v0.10_r6_single_root_strict/R6_SOURCE_EVENT_FEASIBILITY_AUDIT.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.10_r6_single_root_strict/R6_SOURCE_EVENT_FEASIBILITY_AUDIT.json)
- [v0.11_r7_second_root_hard/R7_ADVANCEMENT_DECISION.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.11_r7_second_root_hard/R7_ADVANCEMENT_DECISION.md)
- [v0.11_r7_second_root_hard/R7_ITERATION_HISTORY.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.11_r7_second_root_hard/R7_ITERATION_HISTORY.md)
- [v0.11_r7_second_root_hard/R7_ROOT_ADMISSION_AUDIT.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.11_r7_second_root_hard/R7_ROOT_ADMISSION_AUDIT.json)
- [v0.11_r7_second_root_hard/R7_SECOND_ROOT_SELFTEST.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.11_r7_second_root_hard/R7_SECOND_ROOT_SELFTEST.json)
- [v0.11_r7_second_root_hard/R7_SECOND_ROOT_SELFTEST_attempt1_fail.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.11_r7_second_root_hard/R7_SECOND_ROOT_SELFTEST_attempt1_fail.json)
- [v0.11_r7_second_root_hard/R7_SECOND_ROOT_SELFTEST_attempt2_fail.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.11_r7_second_root_hard/R7_SECOND_ROOT_SELFTEST_attempt2_fail.json)
- [v0.11_r7_second_root_hard/R7_SECOND_ROOT_SELFTEST_attempt3_fail.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.11_r7_second_root_hard/R7_SECOND_ROOT_SELFTEST_attempt3_fail.json)
- [v0.11_r7_second_root_hard/R7_SECOND_ROOT_SELFTEST_attempt4_pass_pre_naturalization.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.11_r7_second_root_hard/R7_SECOND_ROOT_SELFTEST_attempt4_pass_pre_naturalization.json)
- [v0.11_r7_second_root_hard/R7_SECOND_SELFTEST.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.11_r7_second_root_hard/R7_SECOND_SELFTEST.md)
- [v0.12_r8_third_root_nonperiodic/R8_ADVANCEMENT_DECISION.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.12_r8_third_root_nonperiodic/R8_ADVANCEMENT_DECISION.md)
- [v0.12_r8_third_root_nonperiodic/R8_ITERATION_HISTORY.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.12_r8_third_root_nonperiodic/R8_ITERATION_HISTORY.md)
- [v0.12_r8_third_root_nonperiodic/R8_ROOT_CURATION_AUDIT.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.12_r8_third_root_nonperiodic/R8_ROOT_CURATION_AUDIT.json)
- [v0.12_r8_third_root_nonperiodic/R8_THIRD_SELFTEST.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.12_r8_third_root_nonperiodic/R8_THIRD_SELFTEST.md)
- [v0.12_r8_third_root_nonperiodic/selftest/r8_selftest.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.12_r8_third_root_nonperiodic/selftest/r8_selftest.json)
- [v0.13_r9_split_authority/R8_R9_ATTACK_AUDIT.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.13_r9_split_authority/R8_R9_ATTACK_AUDIT.md)
- [v0.13_r9_split_authority/R9_DECISION.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.13_r9_split_authority/R9_DECISION.md)
- [v0.13_r9_split_authority/R9_ITERATION_HISTORY.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.13_r9_split_authority/R9_ITERATION_HISTORY.md)
- [v0.13_r9_split_authority/R9_MECHANICAL_AUDIT.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.13_r9_split_authority/R9_MECHANICAL_AUDIT.json)
- [v0.13_r9_split_authority/R9_SELFTEST.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.13_r9_split_authority/R9_SELFTEST.json)
- [v0.13_r9_split_authority/R9_SELFTEST.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.13_r9_split_authority/R9_SELFTEST.md)
- [v0.14_r10_fourth_root_implicit/R10_DECISION.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.14_r10_fourth_root_implicit/R10_DECISION.md)
- [v0.14_r10_fourth_root_implicit/R10_ITERATION_HISTORY.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.14_r10_fourth_root_implicit/R10_ITERATION_HISTORY.md)
- [v0.14_r10_fourth_root_implicit/R10_MECHANICAL_AUDIT.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.14_r10_fourth_root_implicit/R10_MECHANICAL_AUDIT.json)
- [v0.14_r10_fourth_root_implicit/R10_SELFTEST.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.14_r10_fourth_root_implicit/R10_SELFTEST.json)
- [v0.14_r10_fourth_root_implicit/R10_SELFTEST.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.14_r10_fourth_root_implicit/R10_SELFTEST.md)
- [v0.15_mainstream_method_check/GPT55_PREDICTION_FREEZE.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.15_mainstream_method_check/GPT55_PREDICTION_FREEZE.json)
- [v0.15_mainstream_method_check/GPT55_R10_RESULTS.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.15_mainstream_method_check/GPT55_R10_RESULTS.json)
- [v0.15_mainstream_method_check/GPT55_R10_RESULTS.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.15_mainstream_method_check/GPT55_R10_RESULTS.md)
- [v0.15_mainstream_method_check/scores_gpt55/direct_cot.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.15_mainstream_method_check/scores_gpt55/direct_cot.score.json)
- [v0.15_mainstream_method_check/scores_gpt55/direct_no_cot.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.15_mainstream_method_check/scores_gpt55/direct_no_cot.score.json)
- [v0.15_mainstream_method_check/scores_gpt55/mapmake_paper_style.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.15_mainstream_method_check/scores_gpt55/mapmake_paper_style.score.json)
- [v0.15_mainstream_method_check/scores_gpt55/mapmake_scope_version_enhanced.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.15_mainstream_method_check/scores_gpt55/mapmake_scope_version_enhanced.score.json)
- [v0.15_mainstream_method_check/scores_gpt55/t3_paper_direct_integration_variant.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.15_mainstream_method_check/scores_gpt55/t3_paper_direct_integration_variant.score.json)
- [v0.15_mainstream_method_check/scores_gpt55/t3_provenance_enhanced.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.15_mainstream_method_check/scores_gpt55/t3_provenance_enhanced.score.json)
- [v0.15_mainstream_method_check/selftest/blank_score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.15_mainstream_method_check/selftest/blank_score.json)
- [v0.15_mainstream_method_check/selftest/mutation_score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.15_mainstream_method_check/selftest/mutation_score.json)
- [v0.15_mainstream_method_check/selftest/oracle_score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.15_mainstream_method_check/selftest/oracle_score.json)
- [v0.16_r11_hallucination_chains/selftest_report.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.16_r11_hallucination_chains/selftest_report.json)
- [v0.17_r12_naturalized_multiroot/GPT55_R12_DIRECT_FREEZE.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.17_r12_naturalized_multiroot/GPT55_R12_DIRECT_FREEZE.json)
- [v0.17_r12_naturalized_multiroot/GPT55_R12_DIRECT_SCORE.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.17_r12_naturalized_multiroot/GPT55_R12_DIRECT_SCORE.json)
- [v0.17_r12_naturalized_multiroot/GPT55_R12_DIRECT_SCORE_NORMALIZED_DIAGNOSTIC.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.17_r12_naturalized_multiroot/GPT55_R12_DIRECT_SCORE_NORMALIZED_DIAGNOSTIC.json)
- [v0.17_r12_naturalized_multiroot/GPT55_R12_PREDICTION_FREEZE.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.17_r12_naturalized_multiroot/GPT55_R12_PREDICTION_FREEZE.json)
- [v0.17_r12_naturalized_multiroot/GPT55_R12_RESULTS.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.17_r12_naturalized_multiroot/GPT55_R12_RESULTS.json)
- [v0.17_r12_naturalized_multiroot/R12_SELFTEST.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.17_r12_naturalized_multiroot/R12_SELFTEST.json)
- [v0.18_r13_spiral_constraints/R13_SCORER_SELFTEST.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.18_r13_spiral_constraints/R13_SCORER_SELFTEST.json)
- [v0.18_r13_spiral_constraints/R13_SPIRAL_SELFTEST.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.18_r13_spiral_constraints/R13_SPIRAL_SELFTEST.json)
- [v0.18_r13_spiral_constraints/attempt_a_local_controls/audit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.18_r13_spiral_constraints/attempt_a_local_controls/audit.json)
- [v0.18_r13_spiral_constraints/attempt_b_cross_batch/audit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.18_r13_spiral_constraints/attempt_b_cross_batch/audit.json)
- [v0.18_r13_spiral_constraints/blind/R13_BLIND_AUDIT.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.18_r13_spiral_constraints/blind/R13_BLIND_AUDIT.json)
- [v0.19_r13c_cricket_conservation/CANONICAL_CONSERVATION_AUDIT.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.19_r13c_cricket_conservation/CANONICAL_CONSERVATION_AUDIT.json)
- [v0.19_r13c_cricket_conservation/R13C_ITERATION_HISTORY.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.19_r13c_cricket_conservation/R13C_ITERATION_HISTORY.md)
- [v0.19_r13c_cricket_conservation/R13C_SCORER_SELFTEST.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.19_r13c_cricket_conservation/R13C_SCORER_SELFTEST.json)
- [v0.19_r13c_cricket_conservation/R13C_SELFTEST.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.19_r13c_cricket_conservation/R13C_SELFTEST.json)
- [v0.19_r13c_cricket_conservation/attempt_a_signed_rows/audit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.19_r13c_cricket_conservation/attempt_a_signed_rows/audit.json)
- [v0.19_r13c_cricket_conservation/attempt_b_cricket_conservation/audit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.19_r13c_cricket_conservation/attempt_b_cricket_conservation/audit.json)
- [v0.20_r14_field_independent/R14_ATTEMPT_A_RETAINED_FAILURE.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.20_r14_field_independent/R14_ATTEMPT_A_RETAINED_FAILURE.json)
- [v0.20_r14_field_independent/R14_ITERATION_HISTORY.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.20_r14_field_independent/R14_ITERATION_HISTORY.md)
- [v0.20_r14_field_independent/R14_SCORER_SELFTEST.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.20_r14_field_independent/R14_SCORER_SELFTEST.json)
- [v0.20_r14_field_independent/R14_SELFTEST.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.20_r14_field_independent/R14_SELFTEST.json)
- [v0.21_r15_synthetic_dualworld/R15_FAILURES.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.21_r15_synthetic_dualworld/R15_FAILURES.json)
- [v0.21_r15_synthetic_dualworld/R15_ITERATION_HISTORY.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.21_r15_synthetic_dualworld/R15_ITERATION_HISTORY.md)
- [v0.21_r15_synthetic_dualworld/R15_SCORER_SELFTEST.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.21_r15_synthetic_dualworld/R15_SCORER_SELFTEST.json)
- [v0.21_r15_synthetic_dualworld/R15_SELFTEST.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.21_r15_synthetic_dualworld/R15_SELFTEST.json)
- [v0.3_dev_baseline/ISOLATED_PROBE_RESULTS.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.3_dev_baseline/ISOLATED_PROBE_RESULTS.md)
- [v0.3_dev_baseline/NEXT_DIFFICULTY_ITERATION.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.3_dev_baseline/NEXT_DIFFICULTY_ITERATION.md)
- [v0.4_sdc_probe/SDC_PROBE_RESULTS.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.4_sdc_probe/SDC_PROBE_RESULTS.json)
- [v0.4_sdc_probe/SDC_PROBE_RESULTS.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.4_sdc_probe/SDC_PROBE_RESULTS.md)
- [v0.4_sdc_probe/package/all_prediction_audit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.4_sdc_probe/package/all_prediction_audit.json)
- [v0.4_sdc_probe/package/prediction_freeze_manifest.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.4_sdc_probe/package/prediction_freeze_manifest.json)
- [v0.4_sdc_probe/package/sdc_package_audit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.4_sdc_probe/package/sdc_package_audit.json)
- [v0.4_sdc_probe/package/sdc_redaction_audit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.4_sdc_probe/package/sdc_redaction_audit.json)
- [v0.4_sdc_probe/package/semantic_oracle.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.4_sdc_probe/package/semantic_oracle.score.json)
- [v0.4_sdc_probe/package/wave1_prediction_audit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.4_sdc_probe/package/wave1_prediction_audit.json)
- [v0.4_sdc_probe/scoring/direct_cot.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.4_sdc_probe/scoring/direct_cot.score.json)
- [v0.4_sdc_probe/scoring/direct_no_cot.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.4_sdc_probe/scoring/direct_no_cot.score.json)
- [v0.4_sdc_probe/scoring/mapmake_paper_style.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.4_sdc_probe/scoring/mapmake_paper_style.score.json)
- [v0.4_sdc_probe/scoring/mapmake_scope_version_enhanced.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.4_sdc_probe/scoring/mapmake_scope_version_enhanced.score.json)
- [v0.4_sdc_probe/scoring/query_guided_direct.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.4_sdc_probe/scoring/query_guided_direct.score.json)
- [v0.4_sdc_probe/scoring/t3_paper_direct_integration_variant.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.4_sdc_probe/scoring/t3_paper_direct_integration_variant.score.json)
- [v0.4_sdc_probe/scoring/t3_provenance_enhanced.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.4_sdc_probe/scoring/t3_provenance_enhanced.score.json)
- [v0.5_r2_probe/R2_CRITICAL_SELF_AUDIT.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/R2_CRITICAL_SELF_AUDIT.md)
- [v0.5_r2_probe/R2_SIX_METHOD_RESULTS.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/R2_SIX_METHOD_RESULTS.json)
- [v0.5_r2_probe/R2_SIX_METHOD_RESULTS.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/R2_SIX_METHOD_RESULTS.md)
- [v0.5_r2_probe/SHORTCUT_AUDIT.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/SHORTCUT_AUDIT.md)
- [v0.5_r2_probe/SHORTCUT_REAUDIT.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/SHORTCUT_REAUDIT.md)
- [v0.5_r2_probe/package/r2_audit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/package/r2_audit.json)
- [v0.5_r2_probe/package/r2_prediction_audit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/package/r2_prediction_audit.json)
- [v0.5_r2_probe/package/r2_prediction_freeze.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/package/r2_prediction_freeze.json)
- [v0.5_r2_probe/package/r2_six_method_prediction_audit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/package/r2_six_method_prediction_audit.json)
- [v0.5_r2_probe/package/r2_six_method_prediction_freeze.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/package/r2_six_method_prediction_freeze.json)
- [v0.5_r2_probe/package/semantic_oracle.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/package/semantic_oracle.score.json)
- [v0.5_r2_probe/scoring/direct_cot.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/scoring/direct_cot.score.json)
- [v0.5_r2_probe/scoring/direct_no_cot.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/scoring/direct_no_cot.score.json)
- [v0.5_r2_probe/scoring/mapmake_paper_style.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/scoring/mapmake_paper_style.score.json)
- [v0.5_r2_probe/scoring/mapmake_scope_version_enhanced.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/scoring/mapmake_scope_version_enhanced.score.json)
- [v0.5_r2_probe/scoring/r2_query_guided_strong.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/scoring/r2_query_guided_strong.score.json)
- [v0.5_r2_probe/scoring/t3_paper_direct_integration_variant.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/scoring/t3_paper_direct_integration_variant.score.json)
- [v0.5_r2_probe/scoring/t3_provenance_enhanced.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/scoring/t3_provenance_enhanced.score.json)
- [v0.5_r2_probe/shortcut_audit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/shortcut_audit.json)
- [v0.5_r2_probe/shortcut_reaudit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.5_r2_probe/shortcut_reaudit.json)
- [v0.6_r3_probe/R3_SELF_TEST_RESULTS.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.6_r3_probe/R3_SELF_TEST_RESULTS.json)
- [v0.6_r3_probe/R3_SELF_TEST_RESULTS.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.6_r3_probe/R3_SELF_TEST_RESULTS.md)
- [v0.6_r3_probe/SHORTCUT_AUDIT_ROUND1.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.6_r3_probe/SHORTCUT_AUDIT_ROUND1.md)
- [v0.6_r3_probe/SHORTCUT_AUDIT_ROUND2.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.6_r3_probe/SHORTCUT_AUDIT_ROUND2.md)
- [v0.6_r3_probe/package/r3_audit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.6_r3_probe/package/r3_audit.json)
- [v0.6_r3_probe/package/r3_final_prediction_audit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.6_r3_probe/package/r3_final_prediction_audit.json)
- [v0.6_r3_probe/package/r3_final_prediction_freeze.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.6_r3_probe/package/r3_final_prediction_freeze.json)
- [v0.6_r3_probe/package/semantic_oracle.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.6_r3_probe/package/semantic_oracle.score.json)
- [v0.6_r3_probe/scoring/r3_final_strong.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.6_r3_probe/scoring/r3_final_strong.score.json)
- [v0.6_r3_probe/shortcut_audit_round1.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.6_r3_probe/shortcut_audit_round1.json)
- [v0.6_r3_probe/shortcut_audit_round2.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.6_r3_probe/shortcut_audit_round2.json)
- [v0.7_r4_probe/R4_INTERNAL_SELF_TEST_RESULTS.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.7_r4_probe/R4_INTERNAL_SELF_TEST_RESULTS.json)
- [v0.7_r4_probe/R4_INTERNAL_SELF_TEST_RESULTS.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.7_r4_probe/R4_INTERNAL_SELF_TEST_RESULTS.md)
- [v0.7_r4_probe/ablations/block_a_unresolved.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.7_r4_probe/ablations/block_a_unresolved.score.json)
- [v0.7_r4_probe/ablations/block_b_unresolved.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.7_r4_probe/ablations/block_b_unresolved.score.json)
- [v0.7_r4_probe/ablations/both_blocks_unresolved.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.7_r4_probe/ablations/both_blocks_unresolved.score.json)
- [v0.7_r4_probe/package/r4_audit.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.7_r4_probe/package/r4_audit.json)
- [v0.7_r4_probe/package/semantic_oracle.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.7_r4_probe/package/semantic_oracle.score.json)
- [v0.8_r5_redesign/R4_RED_TEAM_SHORTCUT_AUDIT.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.8_r5_redesign/R4_RED_TEAM_SHORTCUT_AUDIT.json)
- [v0.8_r5_stage_a/R5_STAGE_A_SELFTEST.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.8_r5_stage_a/R5_STAGE_A_SELFTEST.json)
- [v0.8_r5_stage_a/R5_STAGE_A_SELFTEST.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.8_r5_stage_a/R5_STAGE_A_SELFTEST.md)
- [v0.8_r5_stage_a/package/semantic_oracle.score.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.8_r5_stage_a/package/semantic_oracle.score.json)
- [v0.9_r6_single_root/R6_SINGLE_DECISION.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.9_r6_single_root/R6_SINGLE_DECISION.md)
- [v0.9_r6_single_root/R6_SINGLE_SELFTEST.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.9_r6_single_root/R6_SINGLE_SELFTEST.json)
- [v0.9_r6_single_root/R6_SINGLE_SELFTEST.md](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.9_r6_single_root/R6_SINGLE_SELFTEST.md)
- [v0.9_r6_single_root/R6_SOURCE_EVENT_FEASIBILITY_AUDIT.json](../workspace_snapshot/vett_cricket_pilot_v1/experiments/v0.9_r6_single_root/R6_SOURCE_EVENT_FEASIBILITY_AUDIT.json)
