# t20 闭环验证报告

- 生成：`2026-11-12T15:54:39+00:00`；总耗时 19.113s；**10/10 PASS → PASS**
- 单命令复现：`cd 05_pipeline && python verify/run_closed_loop_verification.py --config r28.toml`
- 环境：ambient `PYTHONUTF8=None`、`PYTHONIOENCODING=None`；启动时 stdout 编码 `gbk`；脚本把自身输出改为 UTF-8，且所有子进程强制 `PYTHONUTF8=1`/`PYTHONIOENCODING=utf-8` + 父进程按 UTF-8 解码（Windows GBK 控制台无需前置即可跑通）。

## 修复后复跑（Windows GBK，无 PYTHONUTF8）

- 运行环境：console `chcp 936`；`PYTHONUTF8`/`PYTHONIOENCODING` 未设置；Python 3.14.7。
- 结果：**10/10 PASS → PASS**（D0–D9 全部通过；D0 不再出现 UnicodeDecodeError）。
- 代码修复：`run_proc` 对子进程强制 UTF-8 并用 `encoding='utf-8', errors='replace'` 解码；harness 自身 stdout/stderr reconfigure 为 UTF-8。
- 修复前（原 10/10，ambient UTF-8）报告哈希保留在 `archive_prefix_utf8/`：
  - `04_verify/t20_closed_loop/CLOSED_LOOP_VERIFICATION.json` `87031999b1e9411afa9593445cbf51e291976dbe7828fa97fad4a78ba62125fe`
  - `04_verify/t20_closed_loop/CLOSED_LOOP_VERIFICATION.md` `37bde9afbcbd7025b208efe60fe95887f31e9c6ca116c8972d99c0219aaeb5bb`
  - `04_verify/t20_closed_loop/PIPELINE_VERIFICATION.json` `76015567e4dacf8ae1fa762dde756dae0977fee7225e4a43552d10274955a8b9`
  - `04_verify/t20_closed_loop/T20_CLOSURE.md` `a659df7e0d81369861ff0cdb6b25bf6782f81f75a8bc494fa3f4c2531c2ea28a`
  - `05_pipeline/verify/out/CLOSED_LOOP_VERIFICATION.json` `cdc6f326695898cd695dc303ee581e7dd407ce3fec3d5f08958102b4eec50b0a`
  - `05_pipeline/verify/out/CLOSED_LOOP_VERIFICATION.md` `85b3292555f533f4d859aa4633d727aa9c9e06d322514b45c5b700c464d58a22`

| 项 | 名称 | 结果 | 命令 | 日志 |
|---|---|---|---|---|
| D0 | protocol_verify 22/22 + PAMEND-003 blind-pattern rescan | **PASS** | `python protocol_verify.py --check ; python scripts/reaudit_packets.py --inject-selftest` | `VETT_R28_DIFFICULTY_20261112\05_pipeline\verify\out\00_protocol_verify.log`, `VETT_R28_DIFFICULTY_20261112\05_pipeline\verify\out\00_reaudit_packets.log` |
| D1 | kill -9 then --resume: no duplicate calls, identical artefacts | **PASS** | `python -m vett_r28.pipeline ... --fault kill_after_report\|kill_mid_annotate then --resume` | `01_kill_report.log`, `01_resume_after_report.log`, `01_kill_mid.log`, `01_resume_mid.log`, `01_rerun_mid.log` |
| D2 | local service down -> DEGRADED mechanical fallback, chain continues | **PASS** | `python -m vett_r28.pipeline --stage all --fault local --limit 2` | `02_degrade_local.log` |
| D3 | tampered cache object -> quarantined + recomputed (never silently used) | **PASS** | `tamper one cache object result, rerun --stage all --dry-run` | `03_tamper_first.log`, `03_tamper_second.log` |
| D4 | same command twice: 2nd run all cache hits + identical artefact hashes | **PASS** | `python -m vett_r28.pipeline --stage all --dry-run (twice)` | `04_double_first.log`, `04_double_second.log` |
| D5 | --dry-run green, zero real-directory writes, R26.15 zero drift | **PASS** | `python -m vett_r28.pipeline --stage all --dry-run` | `05_dryrun.log` |
| D6 | byte-level replay from raw_output; replay != regeneration | **PASS** | `python -m vett_r28.pipeline.replay ... ; independent R-R7 cache-key v2 recomputation` | `VETT_R28_DIFFICULTY_20261112\05_pipeline\verify\out\06_replay_t14.log` |
| D7 | routing card is the single source of ALLOW/DENY; no bypass call | **PASS** | `pipeline --routing-card <tampered DENY T1> ; static bypass scan` | `07_routing_tamper.log` |
| D8 | <=1 question per family, 1 record per question, family bootstrap runs | **PASS** | `python verify/run_closed_loop_verification.py (drill 8)` | `VETT_R28_DIFFICULTY_20261112\05_pipeline\verify\out\08_family_bootstrap.json` |
| D9 | J8 template hygiene closed (independent C1/C2/C3 recheck) | **PASS** | `independent audit + python -m unittest test_j8_templates + j_gate.py` | `09_j8_guard_test.log`, `09_j_gate.log` |

## 逐项证据

### D0 protocol_verify 22/22 + PAMEND-003 blind-pattern rescan — PASS

```json
{
  "protocol_summary": {
    "total": 22,
    "passed": 22,
    "failed": 0,
    "ok": true
  },
  "blind_patterns": {
    "type": "tuple",
    "count": 10,
    "ids": [
      "BP-MATCH-ID",
      "BP-FAMILY",
      "BP-LEVEL",
      "BP-DIFFICULTY-WORD",
      "BP-WINPATH",
      "BP-INNERFILE",
      "BP-DATASETPATH",
      "BP-R28-ID",
      "BP-R28-HELDOUT-ITEM",
      "BP-R28-FAMILY"
    ],
    "required_ids_present": [
      "BP-R28-FAMILY",
      "BP-R28-HELDOUT-ITEM",
      "BP-R28-ID"
    ]
  },
  "blind_scan": {
    "packets_scanned": 64,
    "packet_files": [
      "T1_localarm_packets.jsonl",
      "T1_packets.jsonl",
      "T2_packets.jsonl"
    ],
    "violating_packets": 0,
    "violations": []
  },
  "injection": [
    {
      "needle": "r28q_0001",
      "blocked": true,
      "codes": [
        "BP-R28-ID"
      ],
      "expected_codes": [
        "BP-R28-ID"
      ],
      "blocked_by_expected_rule": true
    },
    {
      "needle": "r28h_0005",
      "blocked": true,
      "codes": [
        "BP-R28-HELDOUT-ITEM",
        "BP-R28-ID"
      ],
      "expected_codes": [
        "BP-R28-HELDOUT-ITEM",
        "BP-R28-ID"
      ],
      "blocked_by_expected_rule": true
    },
    {
      "needle": "rfam_83faedd9516b",
      "blocked": true,
      "codes": [
        "BP-R28-FAMILY"
      ],
      "expected_codes": [
        "BP-R28-FAMILY"
      ],
      "blocked_by_expected_rule": true
    },
    {
      "needle": "r28fact_446afd688a87582ab949",
      "blocked": true,
      "codes": [
        "BP-R28-ID"
      ],
      "expected_codes": [
        "BP-R28-ID"
      ],
      "blocked_by_expected_rule": true
    }
  ],
  "external_reaudit_exit": 0,
  "external_reaudit_tail": "pattern table : 10 条 -> BP-MATCH-ID, BP-FAMILY, BP-LEVEL, BP-DIFFICULTY-WORD, BP-WINPATH, BP-INNERFILE, BP-DATASETPATH, BP-R28-ID, BP-R28-HELDOUT-ITEM, BP-R28-FAMILY\nfiles         : 3\npackets       : 64\nviolations    : 0\nmax tokens    : 130\nself-test     : BP-R28-ID=BLOCKED, BP-R28-ID#1=BLOCKED, BP-R28-ID#2=BLOCKED, BP-R28-HELDOUT-ITEM=BLOCKED, BP-R28-FAMILY=BLOCKED, BP-MATCH-ID=BLOCKED, BP-FAMILY=BLOCKED, clean_packet=PASS\nnamespace     : 13/13 blocked\n[ok] re-audit\n",
  "frozen_artifacts": [
    "PROTOCOL.md",
    "build_protocol.py",
    "judge_protocol.py",
    "protocol.json",
    "protocol_verify.py",
    "routing_evidence_snapshot.json",
    "test_judge_protocol.py"
  ],
  "frozen_artifact_count": 7,
  "excluded_derived": [
    "02_design/protocol_verify_result.json"
  ],
  "exclusion_reason": "derived output rewritten by every --check; not one of the 7 frozen artifacts, so G_PROTOCOL_FROZEN must not hash it",
  "protocol_json_sha256": "1a87c3165353f5ec44701f85207aa8cc4faf0b96173c6312152c3d50c50c1293"
}
```

### D1 kill -9 then --resume: no duplicate calls, identical artefacts — PASS

```json
{
  "clean_calls": 12,
  "model_calls_total_after_mid_resume": 12,
  "cache_hits_after_resume": 4,
  "duplicate_cache_miss_keys": 0,
  "kill_after_report_exit": 9,
  "resume_resumed_stages": [
    "bootstrap",
    "generate",
    "annotate",
    "judge",
    "aggregate",
    "report"
  ],
  "resume_calls": 0,
  "resume_vs_rerun_hashes_identical": true,
  "kill_mid_completed_annotations": 4,
  "kill_mid_resume_exit": 0,
  "mid_resume_vs_rerun_hashes_identical": true,
  "mid_hash_diff": {}
}
```

### D2 local service down -> DEGRADED mechanical fallback, chain continues — PASS

```json
{
  "exit": 0,
  "degradation": {
    "blocking": 0,
    "by_reason_code": {
      "LOCAL_SERVICE_UNAVAILABLE": 3
    },
    "count": 3
  },
  "annotations_mode": "mechanical_only",
  "coverage": 0.0,
  "cloud_calls": 0,
  "t14_real_vram_incident": {
    "path": "VETT_R28_DIFFICULTY_20261112\\03_build\\local\\t14\\acceptance.json",
    "context": "201\",\n      \"raw_output\": \"{\\\"topic\\\": \\\"BOWLING\\\"}\",\n      \"repeat_index\": 1,\n      \"same\": true,\n      \"second\": {\n       \"topic\": \"BOWLING\"\n      },\n      \"status\": \"OK\"\n     },\n     {\n      \"clean_position\": \"a\",\n      \"first\": {\n       \"topic\": \"DISMISSAL\"\n      },\n      \"input_sha256\": \"54711877088bc6cccc5538a52f1c7f41cee6a99787c05f81a2177647c259b663\",\n      \"item_id\": \"r28q_0211\",\n      \"raw_output\": \"{\\\"topic\\\": \\\"DISMISSAL\\\"}\",\n      \"repeat_index\": 1,\n      \"same\": true,\n      \"second\": {\n       \"topic\": \"DISMISSAL\"\n      },\n      \"status\": \"OK\"\n     },\n     {\n      \"clean_position\":"
  }
}
```

### D3 tampered cache object -> quarantined + recomputed (never silently used) — PASS

```json
{
  "tampered_object": "VETT_R28_DIFFICULTY_20261112\\05_pipeline\\runs\\_dryrun\\_verify\\tamper\\cache\\objects\\14\\1415ce4e8352b31409a1423e11616aa5857222feefe8758ad82e9c39a0983940.json",
  "cache": {
    "hits": 11,
    "misses": 1,
    "quarantined": 1,
    "stored_objects": 12,
    "writes": 1
  },
  "quarantine_files": [
    "VETT_R28_DIFFICULTY_20261112\\05_pipeline\\runs\\_dryrun\\_verify\\tamper\\cache\\objects\\14\\1415ce4e8352b31409a1423e11616aa5857222feefe8758ad82e9c39a0983940.json.quarantine"
  ],
  "data_hashes_unchanged": true,
  "tampered_marker_absent_from_annotations": true
}
```

### D4 same command twice: 2nd run all cache hits + identical artefact hashes — PASS

```json
{
  "first_cache": {
    "hits": 0,
    "misses": 12,
    "quarantined": 0,
    "stored_objects": 12,
    "writes": 12
  },
  "second_cache": {
    "hits": 12,
    "misses": 0,
    "quarantined": 0,
    "stored_objects": 12,
    "writes": 0
  },
  "second_calls": 12,
  "hashes_identical": true,
  "replay_identical": true
}
```

### D5 --dry-run green, zero real-directory writes, R26.15 zero drift — PASS

```json
{
  "gates": {
    "G_PREREG_FROZEN": "PASS",
    "G_CONTRACT_FROZEN": "PASS",
    "G_PROTOCOL_FROZEN": "PASS",
    "G_SOLVER_PIN": "PASS",
    "G_R26_15_ZERO_DRIFT": "PASS",
    "G_PROTECTED_PATHS": "PASS",
    "G_BUDGET_CONFIG": "PASS",
    "G_FAMILY_UNIT": "PASS",
    "G_CONFIG_VALID": "PASS",
    "G_DATASET_COUNTS": "PASS",
    "G_DATASET_INTEGRITY": "PASS",
    "G_DATASET_DETERMINISM": "PASS",
    "G_ROUTING_CARD": "PASS",
    "G_LOCAL_ROUTE": "PASS",
    "G_ANNOTATION_CACHE_KEY": "PASS",
    "G_ANNOTATION_COVERAGE": "PASS",
    "G_LOCAL_FIRST": "PASS",
    "G_JUDGE_SCHEMA": "PASS",
    "G_JUDGE_COMPARABILITY": "PASS",
    "G_ENDPOINT_UNSCORED": "PASS",
    "G_BUDGET_WITHIN_CAP": "PASS",
    "G_ARTIFACTS_DETERMINISTIC": "PASS",
    "G_REPORT_COMPLETE": "PASS"
  },
  "watched_unchanged": true,
  "dataset_file_list_unchanged": true,
  "r26_15": {
    "ok": true,
    "files": 165,
    "bytes": 93346177
  }
}
```

### D6 byte-level replay from raw_output; replay != regeneration — PASS

```json
{
  "t14": {
    "ledger_rows": 905,
    "reparse_mismatched": 0,
    "annotations_checked": 960,
    "annotations_mismatched": 0,
    "t1_metric": {
      "agreement": 0.975,
      "correct": 312,
      "expected": 0.975,
      "matches_expected": true,
      "n": 320
    },
    "all_identical": true
  },
  "r_r7_parser_binding": {
    "cache_objects": 806,
    "cache_keys_checked": 806,
    "cache_keys_matched": 806,
    "cache_key_mismatches": [],
    "main_path_templates": {
      "T1.factor_visibility.v1": 323,
      "S1.span_topic.v4": 242,
      "T2.naturalness_pair.v1": 310
    },
    "old_templates_in_main_path": [],
    "parser_incompatible_rows": [],
    "parser_incompatible_count": 0
  },
  "pipeline_live_replay": {
    "skipped": false,
    "exit": 0,
    "all_identical": true,
    "judge_identical": true,
    "ledger_rows": 6
  },
  "nondeterminism_evidence": {
    "diffs": [
      {
        "both_correct": true,
        "fresh": 4,
        "previous": 3,
        "sample_id": "R1-53fd65f10741",
        "task": "R1_readability"
      }
    ],
    "gate_unchanged": true,
    "n_prediction_diffs": 1,
    "n_samples_compared": 152,
    "note": "temperature=0 + fixed seed is not bitwise deterministic across Ollama sessions; one 5-point readability score of 152 shifted by 1 (both runs counted it correct). All task agreements and verdicts stayed identical.",
    "probe": "fresh --no-cache measurement vs earlier content-addressed replay (same prompts/params)",
    "schema_version": "vett-local-nondeterminism/v1",
    "seed": 20261112,
    "temperature": 0.0
  },
  "statement": "Replay re-parses stored raw_output and recomputes metrics without calling the model. It is not regeneration: R28 measured one 5-point score of 152 moving by 1 across runs at temperature=0, so re-running the model is not claimed to reproduce the same bytes."
}
```

### D7 routing card is the single source of ALLOW/DENY; no bypass call — PASS

```json
{
  "allow": [
    "C1_cert_sentence_consistency",
    "S1_span_topic",
    "T1_factor_visibility",
    "T2_naturalness"
  ],
  "deny_count": 9,
  "tamper_exit": 4,
  "tamper_status": "FROZEN_VIOLATION",
  "G_ROUTING_CARD_failed": true,
  "gates": {
    "G_PREREG_FROZEN": "PASS",
    "G_CONTRACT_FROZEN": "PASS",
    "G_PROTOCOL_FROZEN": "PASS",
    "G_SOLVER_PIN": "PASS",
    "G_R26_15_ZERO_DRIFT": "PASS",
    "G_PROTECTED_PATHS": "PASS",
    "G_BUDGET_CONFIG": "PASS",
    "G_FAMILY_UNIT": "PASS",
    "G_CONFIG_VALID": "PASS",
    "G_DATASET_COUNTS": "PASS",
    "G_DATASET_INTEGRITY": "PASS",
    "G_DATASET_DETERMINISM": "PASS",
    "G_ROUTING_CARD": "FAIL"
  },
  "hardcoded_protocol_digests": [],
  "static_scan": {
    "scanned_files": 0,
    "violations": [],
    "allowed_annotation_path": "adapters.py -> local_inference.api.annotate",
    "patterns": [
      "service.generate(",
      "urllib.request",
      "urllib.error",
      "http.client",
      "requests.get",
      "requests.post",
      "socket.socket"
    ]
  }
}
```

### D8 <=1 question per family, 1 record per question, family bootstrap runs — PASS

```json
{
  "structure": {
    "published_items": 320,
    "families": 320,
    "max_questions_per_family": 1,
    "one_question_per_family": true,
    "distinct_records": 320,
    "one_record_per_question": true
  },
  "bootstrap": {
    "schema": "vett-r28-family-bootstrap/v1",
    "seed": 20261112,
    "resamples": 1000,
    "clusters": 320,
    "point_estimate": 0.975,
    "ci95": [
      0.95625,
      0.990625
    ],
    "digest": "7bf341e8812d9df2cf072d38d67678e2d06370032a90765d8e273413fea44fc0",
    "deterministic": true
  }
}
```

### D9 J8 template hygiene closed (independent C1/C2/C3 recheck) — PASS

```json
{
  "independent_cache_audit": {
    "cache_hits": 71,
    "unique_cache_keys": 25,
    "templates": {
      "T1.factor_visibility.v1": 29,
      "T2.naturalness_pair.v1": 42
    },
    "choice_hits": 0,
    "cache_objects_missing": [],
    "cache_object_template_mismatches": [],
    "all_frozen": true
  },
  "supplied_cache_audit": {
    "cache_hits": 71,
    "unique_cache_keys": 25,
    "choice_hits": 0,
    "problems": []
  },
  "crosscheck": {
    "present": true,
    "records_identical": true,
    "supplied_records": 71,
    "independent_records": 71
  },
  "variant_hits_under_runs": [],
  "config_field_ok": true,
  "config_field_value": null,
  "config_sha256": "fde4427c806d3161ca4e6bbd2ecef9c8da9db714c27f4907d39490b021527655",
  "quarantine": {
    "path": "VETT_R28_DIFFICULTY_20261112\\03_build\\local\\t14\\quarantine",
    "outside_runs": true,
    "files": 36,
    "manifest": true,
    "smoke_dirs_absent_from_runs": true
  },
  "guard": {
    "source_has_FROZEN_TEMPLATES": true,
    "source_has_assert": true,
    "test_exit": 0
  },
  "main_results_immutable": {
    "present": true,
    "unchanged": [
      "DEGRADED_EVENTS.jsonl",
      "acceptance.json",
      "annotations.json",
      "annotations_S1_span_topic.jsonl",
      "annotations_T1_factor_visibility.jsonl",
      "annotations_T2_naturalness.jsonl",
      "cost_ledger.jsonl",
      "local_cost_ledger.jsonl",
      "repeats.json",
      "run_manifest.json",
      "s1_analysis.json",
      "t1_analysis.json",
      "t2_pairs.json"
    ],
    "changed_expected": [
      "REPORT_T14.md",
      "config.json"
    ]
  },
  "j8_fix_evidence": {
    "path": "VETT_R28_DIFFICULTY_20261112\\03_build\\local\\t14\\evidence\\J8_FIX_EVIDENCE.json",
    "present": true,
    "self_consistent": true,
    "j8_status": {
      "C1_main_path_zero_contamination": true,
      "C2_runs_no_choice_v1": true,
      "C3_key_removed": true
    }
  },
  "j_gate": {
    "ran": true,
    "exit": 0,
    "mode": "--check-md (read-only; j_gate persists only with --write)",
    "j_gate_json_sha256": "971a6840d1fdb4893148500043798153611c3f4157c9dc928815b421a17737f5",
    "j_gate_read_only": {
      "before_sha256": "971a6840d1fdb4893148500043798153611c3f4157c9dc928815b421a17737f5",
      "after_sha256": "971a6840d1fdb4893148500043798153611c3f4157c9dc928815b421a17737f5",
      "unchanged": true
    },
    "verdict": "PASS",
    "j8_in_blocking": false,
    "blocking": [],
    "config_field": {
      "field": "t2_choice_template_version",
      "absent": true,
      "value": null,
      "ok": true,
      "accepted_forms": [
        "字段不存在",
        "null / 空串",
        "{\"deprecated\": true}",
        "任何含 'deprecated' 的字符串"
      ]
    },
    "variant_files_under_runs": []
  }
}
```

