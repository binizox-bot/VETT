"""Per-run context: paths, ledgers, writers.

Every write goes through :meth:`PipelineContext.write_json` / ``write_text``,
which refuses any path outside the run directory and consults the human gate
before touching the frozen R26.15 tree.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from typing import Any

from .budget import BudgetLedger
from .cache import ContentAddressedCache
from .canonical import canon_pretty, sha256_file, sha256_text
from .config import Config
from .degrade import DegradationManager
from .errors import ConfigError
from .events import append_jsonl
from .human import HumanGate


@dataclass
class PipelineContext:
    config: Config
    run_dir: pathlib.Path
    dry_run: bool
    resume: bool
    fault: str | None
    allow_human_gate: bool
    run_id: str
    cache: ContentAddressedCache
    budget: BudgetLedger
    degrade: DegradationManager
    human: HumanGate
    gate_ledger: pathlib.Path
    state: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, dict[str, Any]] = field(default_factory=dict)
    previous_artifacts: dict[str, Any] = field(default_factory=dict)
    dataset: dict[str, Any] | None = None
    annotations: dict[str, Any] | None = None
    judged: dict[str, Any] | None = None
    aggregated: dict[str, Any] | None = None
    writes: list[str] = field(default_factory=list)
    gate_results: list[dict[str, Any]] = field(default_factory=list)
    stage_order: list[str] = field(default_factory=list)
    stage_results: dict[str, Any] = field(default_factory=dict)
    exit_status: str = "OK"
    notes: list[str] = field(default_factory=list)

    # -- logging --------------------------------------------------------
    def log(self, message: str) -> None:
        append_jsonl(self.run_dir / "pipeline_log.jsonl", {
            "schema": "vett-r28-pipeline-log/v1",
            "stage": self.state.get("current_stage"),
            "message": message,
        })
        print(f"[pipeline] {message}", flush=True)

    # -- write guards ---------------------------------------------------
    def _resolve(self, name: str) -> pathlib.Path:
        target = (self.run_dir / name).resolve()
        try:
            target.relative_to(self.run_dir.resolve())
        except ValueError as exc:
            raise ConfigError(f"refusing to write outside the run directory: {target}") from exc
        self.human.guard_write(target)
        return target

    def write_json(self, name: str, payload: Any) -> dict[str, Any]:
        target = self._resolve(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        text = canon_pretty(payload)
        with open(target, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        self.writes.append(str(target))
        return {"path": str(target), "sha256": sha256_text(text), "bytes": len(text.encode("utf-8"))}

    def write_text(self, name: str, text: str) -> dict[str, Any]:
        target = self._resolve(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        self.writes.append(str(target))
        return {"path": str(target), "sha256": sha256_text(text),
                "bytes": len(text.encode("utf-8"))}

    def read_json(self, name: str) -> Any:
        target = self.run_dir / name
        if not target.is_file():
            raise FileNotFoundError(f"missing run artefact: {target}")
        return json.loads(target.read_text(encoding="utf-8"))

    # -- artefacts ------------------------------------------------------
    def artifact(self, name: str, payload: Any) -> dict[str, Any]:
        info = self.write_json(name, payload)
        self.artifacts[name] = info
        return info

    def artifact_text(self, name: str, text: str) -> dict[str, Any]:
        info = self.write_text(name, text)
        self.artifacts[name] = info
        return info

    def record_gate(self, gate_id: str, stage: str, verdict: str, evidence: Any,
                    attempt: int, blocked: bool) -> None:
        entry = {
            "schema": "vett-r28-pipeline-gate-ledger/v1",
            "gate": gate_id,
            "stage": stage,
            "verdict": verdict,
            "blocked": bool(blocked),
            "attempt": int(attempt),
            "evidence": evidence,
        }
        append_jsonl(self.gate_ledger, entry)
        self.gate_results.append(entry)

    # -- state ----------------------------------------------------------
    def save_state(self) -> None:
        payload = {
            "schema": "vett-r28-pipeline-state/v1",
            "run_id": self.run_id,
            "config_digest": self.config.digest(),
            "dry_run": self.dry_run,
            "stages": self.stage_results,
            "exit_status": self.exit_status,
            "artifacts": {name: info["sha256"] for name, info in self.artifacts.items()},
        }
        self.write_json("state.json", payload)

    def artifact_hashes(self, names: list[str]) -> dict[str, str]:
        return {name: self.artifacts[name]["sha256"] for name in names
                if name in self.artifacts}


__all__ = ["PipelineContext"]
