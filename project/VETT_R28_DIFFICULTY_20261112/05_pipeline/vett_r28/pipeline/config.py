"""Configuration for the R28 pipeline (TOML, stdlib ``tomllib``).

All paths in ``r28.toml`` are resolved relative to the config file.  The
pipeline refuses to write anywhere except its own ``runs/`` tree and never
writes inside the frozen R26.15 candidate.
"""

from __future__ import annotations

import pathlib
import tomllib
from dataclasses import dataclass, field
from typing import Any

from .canonical import digest, sha256_file


DEFAULTS: dict[str, Any] = {
    "pipeline": {"run_root": "runs", "default_run_id": "r28-main", "version": "1.0.0"},
    "budget": {
        "hard_cap_cny": 100.0,
        "soft_cap_cny": 3.0,
        "cloud_calls_hard_cap": 80,
        "cloud_enabled": False,
        "local_cost_cny_per_1k_tokens": 0.0,
        "cloud_cost_cny_per_1k_tokens": 0.03,
    },
    "annotation": {
        "mode": "local_first",
        "sample_instances": 4,
        "max_calls": 24,
        "min_coverage": 0.95,
        "tasks": [
            "T1_factor_visibility",
            "S1_span_topic",
            "C1_cert_sentence_consistency",
        ],
    },
    "generate": {"limit_instances": 0, "determinism_sample": 3},
    "run": {"allow_human_gate": False, "repair_rounds": 2, "strict": True},
    "dryrun": {"instances": 8},
}

REQUIRED_PATHS = (
    "prereg",
    "prereg_freeze",
    "contract",
    "contract_freeze",
    "protocol",
    "protocol_freeze",
    "build_config",
    "protected_manifest",
    "judge_protocol_scripts",
    "local_inference_root",
    "routing_card",
)


@dataclass
class Config:
    config_path: pathlib.Path
    base: pathlib.Path
    data: dict[str, Any] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)
    _paths: dict[str, pathlib.Path] = field(default_factory=dict)

    # -- access ---------------------------------------------------------
    def get(self, dotted: str, default: Any = None) -> Any:
        node: Any = self.data
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def path(self, key: str) -> pathlib.Path:
        if key not in self._paths:
            raw = self.get(f"paths.{key}")
            if raw is None:
                raise KeyError(f"paths.{key} missing from {self.config_path}")
            candidate = pathlib.Path(str(raw))
            if not candidate.is_absolute():
                candidate = (self.base / candidate).resolve()
            self._paths[key] = candidate
        return self._paths[key]

    @property
    def pipeline_root(self) -> pathlib.Path:
        return self.base

    def run_root(self) -> pathlib.Path:
        root = pathlib.Path(str(self.get("pipeline.run_root", "runs")))
        if not root.is_absolute():
            root = (self.base / root).resolve()
        return root

    @property
    def dataset_version(self) -> str:
        return str(self.get("expected.dataset_version", ""))

    def budget_settings(self) -> dict[str, Any]:
        merged = dict(DEFAULTS["budget"])
        merged.update(self.get("budget", {}) or {})
        return merged

    def annotation_settings(self) -> dict[str, Any]:
        merged = dict(DEFAULTS["annotation"])
        merged.update(self.get("annotation", {}) or {})
        merged["tasks"] = list(merged.get("tasks") or [])
        return merged

    def generate_settings(self) -> dict[str, Any]:
        merged = dict(DEFAULTS["generate"])
        merged.update(self.get("generate", {}) or {})
        return merged

    def run_settings(self) -> dict[str, Any]:
        merged = dict(DEFAULTS["run"])
        merged.update(self.get("run", {}) or {})
        return merged

    # -- identity -------------------------------------------------------
    def digest(self) -> str:
        """Digest of the semantic config (paths included by relative name)."""
        basis = {
            "pipeline": self.get("pipeline", {}),
            "budget": self.budget_settings(),
            "annotation": self.annotation_settings(),
            "generate": self.generate_settings(),
            "run": self.run_settings(),
            "dryrun": self.get("dryrun", {}),
            "expected": self.get("expected", {}),
            "paths": {key: str(self.get(f"paths.{key}")) for key in REQUIRED_PATHS},
        }
        return digest(basis)

    def input_digests(self) -> dict[str, str]:
        """sha256 of every frozen input this run depends on."""
        out = {}
        for key in REQUIRED_PATHS:
            try:
                path = self.path(key)
            except KeyError:
                continue
            if path.is_file():
                out[f"paths.{key}"] = sha256_file(path)
            elif path.is_dir():
                out[f"paths.{key}"] = "dir"
        return out

    # -- validation -----------------------------------------------------
    def validate(self) -> list[str]:
        problems: list[str] = []
        for key in REQUIRED_PATHS:
            if self.get(f"paths.{key}") is None:
                problems.append(f"paths.{key} is required")
                continue
            try:
                path = self.path(key)
            except KeyError:
                continue
            if not path.exists():
                problems.append(f"paths.{key} does not exist: {path}")
        if self.get("budget.hard_cap_cny") is not None:
            try:
                hard = float(self.get("budget.hard_cap_cny"))
                soft = float(self.get("budget.soft_cap_cny", 0.0) or 0.0)
                if hard <= 0:
                    problems.append("budget.hard_cap_cny must be > 0")
                if soft < 0 or soft > hard:
                    problems.append("budget.soft_cap_cny must be within [0, hard_cap_cny]")
            except (TypeError, ValueError):
                problems.append("budget caps must be numbers")
        if int(self.get("budget.cloud_calls_hard_cap", 80)) > 80:
            problems.append("budget.cloud_calls_hard_cap must be <= 80 (t12 protocol)")
        if bool(self.get("budget.cloud_enabled", False)):
            problems.append("budget.cloud_enabled must stay false: R28 forbids paid/cloud APIs")
        mode = str(self.get("annotation.mode", "local_first"))
        if mode not in ("local_first", "mechanical_only"):
            problems.append(f"annotation.mode {mode!r} is not supported")
        tasks = self.annotation_settings()["tasks"]
        unknown = [t for t in tasks if t not in
                   ("T1_factor_visibility", "T2_naturalness", "S1_span_topic",
                    "C1_cert_sentence_consistency")]
        if unknown:
            problems.append(f"annotation.tasks contains non-whitelisted tasks: {unknown}")
        if int(self.get("run.repair_rounds", 2)) != 2:
            problems.append("run.repair_rounds must be exactly 2 (bounded repair contract)")
        # Write confinement: run root must live under the pipeline root.
        try:
            run_root = self.run_root()
            if not str(run_root).startswith(str(self.pipeline_root)):
                problems.append(f"run_root must stay inside {self.pipeline_root}: {run_root}")
        except Exception:  # pragma: no cover - defensive
            problems.append("run_root cannot be resolved")
        # R26.15 must never be a writable target.
        r26 = self.r26_15_root()
        for key in ("run_root",):
            try:
                candidate = self.run_root()
            except Exception:
                continue
            if str(candidate).startswith(str(r26)):
                problems.append("pipeline output must not be inside the R26.15 candidate")
        self.problems = problems
        return problems

    # -- frozen helper paths -------------------------------------------
    def r26_15_root(self) -> pathlib.Path:
        protected = self.path("protected_manifest")
        project_root = protected.parent.parent.parent if protected.name == "PROTECTED_PATHS.json" else None
        if project_root is None:
            return pathlib.Path("__missing__")
        return project_root / "VETT_Cricket_v0.22_R16_Multisource_Dilemmas" / \
            "r26_15_content_dependency_candidate_v3"


def load(path: pathlib.Path | str) -> Config:
    config_path = pathlib.Path(path).resolve()
    if not config_path.is_file():
        raise FileNotFoundError(f"config not found: {config_path}")
    try:
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:  # pragma: no cover - surfaced to CLI
        raise ValueError(f"invalid TOML in {config_path}: {exc}") from exc
    config = Config(config_path=config_path, base=config_path.parent, data=data)
    for section, defaults in DEFAULTS.items():
        merged = dict(defaults)
        merged.update(data.get(section, {}) or {})
        data[section] = merged
    return config


__all__ = ["Config", "load", "DEFAULTS", "REQUIRED_PATHS"]

