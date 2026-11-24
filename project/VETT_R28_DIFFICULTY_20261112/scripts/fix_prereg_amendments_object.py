#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_prereg_amendments_object.py — 恢复 amendments 策略对象并把 AMEND-001 放进 executed。"""
import json
import pathlib

p = pathlib.Path(__file__).resolve().parents[1] / "preregistration.json"
d = json.loads(p.read_text(encoding="utf-8"))
executed = d.get("amendments")
if isinstance(executed, dict):
    print("already fixed")
else:
    d["amendments"] = {
        "frozen": True,
        "policy": [
            {"id": "AM1",
             "rule": "允许：错别字、格式、补充出处链接、不改变含义的措辞澄清。此类改动必须写入 prereg_amendments.jsonl（append-only），并重新生成 prereg_freeze.json。"},
            {"id": "AM2",
             "rule": "禁止（必须人工批准 + 版本号升级 + t8 告警）：修改主端点定义、次要端点清单或定义、判定阈值（含 10pp、25pp、40%、90%、100%、32%、52.89%、54.22%、73.33%）、停止规则、零结果契约、多重比较方案、有效 n 规则、Brier/边指标口径。"},
            {"id": "AM3",
             "rule": "在看到任何 R28 结果之后，端点与判定规则不得再改；任何事后分析只能标注为 EXPLORATORY，且不得替换主端点。"},
            {"id": "AM4",
             "rule": "t8 一致性检查：重算 preregistration.json 与 PREREGISTRATION.md 的 sha256、endpoint_registry_sha256，与 prereg_freeze.json 比对；任一不符 → FAIL 并输出 diff。"},
            {"id": "AM5",
             "rule": "人工门：预注册冻结后的任何端点修改必须由 captain 上报用户批准；批准前不得执行对应分析。"},
        ],
        "log_path": "VETT_R28_DIFFICULTY_20261112/prereg_amendments.jsonl",
        "current_log_entries": 1,
        "executed": executed,
    }
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("fixed amendments object; executed entries:", len(executed))
