"""Pre-registered repair actions (bounded: at most 2 repairs per gate).

Every repair is deterministic, side-effect-scoped to the run directory and
returns ``{repair_id, gate, action, ok}``.  There is no unbounded retry and no
repair is allowed to weaken a predicate: a repair may rebuild an artefact from
authoritative inputs, re-probe a service, or recompute a hash - never change a
threshold.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Any, Callable

from .canonical import sha256_file


@dataclass(frozen=True)
class RepairSpec:
    repair_id: str
    gate_id: str
    description: str
    fn: Callable[[Any], dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "repair_id": self.repair_id,
            "gate_id": self.gate_id,
            "description": self.description,
            "action": f"{self.fn.__module__}.{self.fn.__name__}",
        }


REPAIRS: dict[str, RepairSpec] = {}


def repair(repair_id: str, gate_id: str, description: str):
    def decorator(fn: Callable[[Any], dict[str, Any]]):
        if repair_id in REPAIRS:
            raise RuntimeError(f"duplicate repair id {repair_id}")
        REPAIRS[repair_id] = RepairSpec(repair_id=repair_id, gate_id=gate_id,
                                        description=description, fn=fn)
        return fn

    return decorator


@repair("rebuild_dataset", "G_DATASET_DETERMINISM",
        "rebuild the deterministic sample from the frozen generator and re-derive digests")
def rebuild_dataset(ctx) -> dict[str, Any]:
    from . import stages

    result = stages.generate_stage(ctx, rebuild=True)
    return {"repair_id": "rebuild_dataset", "gate": "G_DATASET_DETERMINISM",
            "action": "regenerate dataset sample", "ok": bool(result.get("determinism", {}).get("ok")),
            "evidence": result.get("determinism")}


@repair("retry_annotation", "G_ANNOTATION_COVERAGE",
        "re-probe the local judge; retry once if it is now available, else stay degraded")
def retry_annotation(ctx) -> dict[str, Any]:
    from . import stages

    probe = stages.probe_local(ctx)
    if not probe.get("available"):
        ctx.degrade.emit(stage="annotate", reason_code="LOCAL_STILL_UNAVAILABLE",
                         fallback="mechanical_only", evidence=probe, source="repair")
        return {"repair_id": "retry_annotation", "gate": "G_ANNOTATION_COVERAGE",
                "action": "re-probe local judge", "ok": False, "evidence": probe}
    result = stages.annotate_stage(ctx, retry=True)
    return {"repair_id": "retry_annotation", "gate": "G_ANNOTATION_COVERAGE",
            "action": "retry annotations", "ok": result.get("metrics", {}).get("ok", 0) > 0,
            "evidence": result.get("metrics")}


@repair("rescore_judge", "G_JUDGE_COMPARABILITY",
        "recompute judge metrics from the stored annotations and mechanical references")
def rescore_judge(ctx) -> dict[str, Any]:
    from . import stages

    result = stages.judge_stage(ctx)
    return {"repair_id": "rescore_judge", "gate": "G_JUDGE_COMPARABILITY",
            "action": "rescore from cached annotations", "ok": bool(result.get("ok")),
            "evidence": result.get("tasks")}


@repair("rebuild_report", "G_REPORT_COMPLETE",
        "regenerate REPORT.md from the current run artefacts")
def rebuild_report(ctx) -> dict[str, Any]:
    from . import stages

    result = stages.report_stage(ctx)
    return {"repair_id": "rebuild_report", "gate": "G_REPORT_COMPLETE",
            "action": "regenerate report", "ok": bool(result.get("report_sha256")),
            "evidence": {"report_sha256": result.get("report_sha256")}}


@repair("rewrite_artifact_hashes", "G_ARTIFACTS_DETERMINISTIC",
        "recompute ARTIFACT_HASHES.json from the artefact files on disk")
def rewrite_artifact_hashes(ctx) -> dict[str, Any]:
    from . import stages

    hashes = stages.write_artifact_hashes(ctx)
    return {"repair_id": "rewrite_artifact_hashes", "gate": "G_ARTIFACTS_DETERMINISTIC",
            "action": "recompute artefact hashes", "ok": True, "evidence": hashes}


def registry_snapshot() -> dict[str, Any]:
    return {
        "schema": "vett-r28-pipeline-repair-registry/v1",
        "repair_count": len(REPAIRS),
        "max_rounds": 2,
        "repairs": [REPAIRS[key].as_dict() for key in sorted(REPAIRS)],
    }


def repair_ids() -> set[str]:
    return set(REPAIRS)


__all__ = ["RepairSpec", "REPAIRS", "repair", "registry_snapshot", "repair_ids"]
