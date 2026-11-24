# R26.14 static admission

- Status: `STATIC_CANDIDATE_PASS_EMPIRICAL_BLOCKED`
- Static candidate admitted: `True`
- Empirical difficulty calibrated: `False`
- Full 220 materialization authorized: `False`
- Next authorized experiment: `uniform_sentinel5_one_economic_strong_model_after_explicit_user_authorization`

## Static gates

- release_20_pass: `True`
- integrated_release_audit_pass: `True`
- question_only_answer_shortcut_controlled: `True`
- stronger_question_only_and_scenario_holdout_baselines_pass: `True`
- answer_blind_transform_is_narrow_and_semantics_preserving: `True`
- all_100_proof_certificates_pass: `True`
- automated_language_surface_pass: `True`
- assistant_stratified_language_review_pass: `True`
- semantic_shortcut_audit_pass: `True`
- oracle_companion_metrics_all_one: `True`
- fresh_rebuild_byte_identical: `True`
- streaming_220_preflight_pass: `True`
- streaming_220_has_no_unapproved_question_duplicates: `True`
- streaming_220_has_no_span_id_collisions: `True`
- full_cohort_answer_prior_gates_pass: `True`
- full_cohort_stronger_question_baselines_pass: `True`
- matched_anchor_control_complete: `True`
- protocol_fault_attribution_pass: `True`
- sentinel_request_ready_but_not_authorized: `True`
- diagnostic_escalation_waits_for_explicit_authorization: `True`
- metric_addendum_frozen_before_provider_result: `True`
- zero_provider_requests: `True`

## Remaining blockers

- `INDEPENDENT_HUMAN_NATURALNESS_REVIEW_NOT_RUN`
- `R26_14_SENTINEL5_UNIFORM_NOT_RUN`
- `R26_14_PILOT20_TWO_STRONG_MODEL_FAMILIES_NOT_RUN`
- `STRONG_MODEL_65PCT_AND_ADJACENT_8PPT_TARGETS_UNCALIBRATED`

## Claim boundary

Static admission establishes deterministic construction, factual/proof invariants, shortcut controls, evaluator sensitivity, matched-anchor coverage and request safety. It does not establish strong-model accuracy, empirical adjacent-level gaps, human naturalness or publication readiness.
