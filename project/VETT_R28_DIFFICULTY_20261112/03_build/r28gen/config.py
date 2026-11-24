"""Build configuration for the R28 generator (frozen JSON, no hardcoded N).

Everything the build needs - N, block/cell sizes, the 67-layer quota table, the
dose semantics, the prompt budget, the fact grid - is read from
``03_build/config/r28_build_config.json``.  The config itself is generated once
from the frozen contract (``scripts/make_config.py``) so that the generator never
re-derives design constants at build time and cannot silently drift from t4.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from typing import Any

from .canonical import canon, sha256_text
from .constants import (
    DOSE_IDS,
    LEDGER_MASKS,
    LEGAL_DISMISSALS,
    MASK_FIELDS,
    MAX_DOCUMENTS,
    MAX_PROMPT_TOKENS,
    MAX_SPANS,
    N_PUBLISHED,
    RECORD_FIELDS,
    SEED,
)
from .record_space import FACT_GRID

CONFIG_PATH = pathlib.Path(__file__).resolve().parents[1] / "config" / "r28_build_config.json"


class ConfigError(ValueError):
    """Raised when the build config is internally inconsistent."""


@dataclass(frozen=True)
class QuotaLayer:
    status: str
    dismissal: str
    mask: str
    quota: int
    n_factor_core: int
    n_dose_ladder: int
    stratum_rank: tuple[int, int, int]

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.status, self.dismissal, self.mask)

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "dismissal": self.dismissal,
            "mask": self.mask,
            "quota": self.quota,
            "n_factor_core": self.n_factor_core,
            "n_dose_ladder": self.n_dose_ladder,
            "stratum_rank": list(self.stratum_rank),
        }


@dataclass(frozen=True)
class BuildConfig:
    raw: dict[str, Any]
    path: pathlib.Path

    # -- identity ---------------------------------------------------------
    @property
    def sha256(self) -> str:
        return sha256_text(canon(self.raw))

    @property
    def dataset_version(self) -> str:
        return str(self.raw["dataset_version"])

    @property
    def design_id(self) -> str:
        return str(self.raw["design_id"])

    @property
    def seed(self) -> int:
        return int(self.raw["seed"])

    @property
    def n_published(self) -> int:
        return int(self.raw["n_published"])

    # -- blocks -----------------------------------------------------------
    @property
    def factor_core(self) -> dict[str, Any]:
        return dict(self.raw["blocks"]["factor_core"])

    @property
    def dose_ladder(self) -> dict[str, Any]:
        return dict(self.raw["blocks"]["dose_ladder"])

    @property
    def factor_n(self) -> int:
        return int(self.factor_core["n"])

    @property
    def dose_n(self) -> int:
        return int(self.dose_ladder["n"])

    @property
    def factor_cells(self) -> int:
        return int(self.factor_core["cells"])

    @property
    def dose_cells(self) -> int:
        return int(self.dose_ladder["cells"])

    @property
    def factor_cell_capacity(self) -> int:
        return int(self.factor_core["cell_capacity"])

    @property
    def dose_cell_capacity(self) -> int:
        return int(self.dose_ladder["cell_capacity"])

    @property
    def scenes(self) -> int:
        return int(self.raw["scenes"]["n"])

    @property
    def items_per_scene(self) -> int:
        return int(self.raw["scenes"]["items_per_scene"])

    # -- quotas -----------------------------------------------------------
    @property
    def quota_layers(self) -> list[QuotaLayer]:
        rows: list[QuotaLayer] = []
        for row in self.raw["quota_layers"]:
            rows.append(
                QuotaLayer(
                    status=str(row["status"]),
                    dismissal=str(row["dismissal"]),
                    mask=str(row["mask"]),
                    quota=int(row["quota"]),
                    n_factor_core=int(row["n_factor_core"]),
                    n_dose_ladder=int(row["n_dose_ladder"]),
                    stratum_rank=tuple(row.get("stratum_rank", [0, 0, 0])),
                )
            )
        return rows

    @property
    def quota_by_key(self) -> dict[tuple[str, str, str], QuotaLayer]:
        return {layer.key: layer for layer in self.quota_layers}

    @property
    def quota_total(self) -> int:
        return sum(layer.quota for layer in self.quota_layers)

    # -- doses ------------------------------------------------------------
    @property
    def dose_table(self) -> dict[str, dict[str, Any]]:
        return {str(item["id"]): dict(item) for item in self.raw["doses"]}

    @property
    def dose_levels(self) -> dict[str, tuple[int, ...]]:
        return {
            dose_id: tuple(int(level) for level in self.dose_table[dose_id]["levels"])
            for dose_id in DOSE_IDS
        }

    # -- misc -------------------------------------------------------------
    @property
    def prompt(self) -> dict[str, Any]:
        return dict(self.raw["prompt"])

    @property
    def output_contract(self) -> dict[str, Any]:
        return dict(self.raw["output_contract"])

    @property
    def assignment(self) -> dict[str, Any]:
        return dict(self.raw["assignment"])

    @property
    def family(self) -> dict[str, Any]:
        return dict(self.raw["family"])

    @property
    def caps(self) -> dict[str, Any]:
        return dict(self.raw["caps"])

    @property
    def required_combinations(self) -> list[str]:
        return list(self.raw["required_combinations"])

    @property
    def held_out(self) -> dict[str, Any]:
        return dict(self.raw["held_out"])

    @property
    def fact_grid(self) -> dict[str, list[Any]]:
        return {str(key): list(values) for key, values in self.raw["fact_grid"].items()}

    @property
    def solver_reference(self) -> dict[str, Any]:
        return dict(self.raw["solver_reference"])

    # -- validation -------------------------------------------------------
    def validate(self) -> list[str]:
        """Return a list of consistency problems (empty == valid)."""

        problems: list[str] = []
        n = self.n_published
        if n % 40 != 0:
            problems.append(f"n_published={n} is not a multiple of 40")
        if self.quota_total != n:
            problems.append(f"quota sum {self.quota_total} != n_published {n}")
        if self.factor_n + self.dose_n != n:
            problems.append(f"block sizes {self.factor_n}+{self.dose_n} != {n}")
        if self.factor_n != 2 * n // 5:
            problems.append(f"factor_core n {self.factor_n} != 2N/5")
        if self.dose_n != 3 * n // 5:
            problems.append(f"dose_ladder n {self.dose_n} != 3N/5")
        if self.factor_cells * self.factor_cell_capacity != self.factor_n:
            problems.append("factor cell capacity does not multiply to the block size")
        if self.dose_cells * self.dose_cell_capacity != self.dose_n:
            problems.append("dose cell capacity does not multiply to the block size")
        if self.factor_cells != 2 ** len(DOSE_IDS):
            problems.append(f"factor_cells {self.factor_cells} != 2^{len(DOSE_IDS)}")
        if self.dose_cells != len(DOSE_IDS) * 3:
            problems.append(f"dose_cells {self.dose_cells} != {len(DOSE_IDS)} mechanisms x 3 doses")
        if self.scenes * self.items_per_scene != n:
            problems.append("scene plan does not multiply to n_published")
        if sum(layer.n_factor_core for layer in self.quota_layers) != self.factor_n:
            problems.append("per-layer factor_core quotas do not sum to the block size")
        if sum(layer.n_dose_ladder for layer in self.quota_layers) != self.dose_n:
            problems.append("per-layer dose_ladder quotas do not sum to the block size")
        seen: set[tuple[str, str, str]] = set()
        allowed_status = {"LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL"}
        allowed_dismissal = {
            "NONE", "BOWLED", "LBW", "CAUGHT", "RUN_OUT", "STUMPED",
            "OBSTRUCTING_FIELD", "HIT_BALL_TWICE",
        }
        for layer in self.quota_layers:
            if layer.key in seen:
                problems.append(f"duplicate quota layer {layer.key}")
            seen.add(layer.key)
            if layer.status not in allowed_status:
                problems.append(f"bad status {layer.status}")
            if layer.dismissal not in allowed_dismissal:
                problems.append(f"bad dismissal {layer.dismissal}")
            if layer.mask not in LEDGER_MASKS:
                problems.append(f"bad ledger mask {layer.mask}")
            if layer.quota < 1:
                problems.append(f"layer {layer.key} has non-positive quota")
            if layer.quota != layer.n_factor_core + layer.n_dose_ladder:
                problems.append(f"layer {layer.key} quota != factor+dose split")
            if layer.mask[0] == "1" and layer.mask[1] == "1":
                problems.append(f"layer {layer.key} has BYE and LEG_BYE both non-zero (CEIL-4)")
            if layer.status == "DEAD_REBALL" and (layer.mask != "000" or layer.dismissal != "NONE"):
                problems.append("DEAD_REBALL layer must be NONE/000 (CEIL-1)")
            if layer.status == "WIDE" and layer.mask[:2] != "00":
                problems.append("WIDE layer cannot have BYE/LEG_BYE (CEIL-3)")
        legal_rows = [
            layer for layer in self.quota_layers if layer.dismissal in LEGAL_DISMISSALS
        ]
        legal_total = sum(layer.quota for layer in legal_rows)
        cap = int(self.caps["legal_dismissal_total"])
        if legal_total > cap:
            problems.append(f"legal dismissal quota {legal_total} exceeds cap {cap} (HA18)")
        dead_rows = [layer for layer in self.quota_layers if layer.status == "DEAD_REBALL"]
        if sum(layer.quota for layer in dead_rows) != 1:
            problems.append("DEAD_REBALL quota must be exactly 1")
        none_share = sum(layer.quota for layer in self.quota_layers if layer.dismissal == "NONE") / n
        if none_share > float(self.caps["none_share_max"]):
            problems.append(f"NONE share {none_share:.4f} exceeds cap")
        prompt = self.prompt
        if int(prompt["max_tokens"]) != MAX_PROMPT_TOKENS:
            problems.append("prompt token cap drifted from the contract")
        if int(prompt["max_documents"]) != MAX_DOCUMENTS:
            problems.append("document cap drifted from the contract")
        if int(prompt["max_spans"]) != MAX_SPANS:
            problems.append("span cap drifted from the contract")
        if set(self.output_contract["decision_record_fields"]) != set(RECORD_FIELDS):
            problems.append("output record fields drifted from the frozen 12-field schema")
        if int(self.raw["seed"]) != SEED:
            problems.append(f"seed {self.raw['seed']} != frozen seed {SEED}")
        if int(self.raw["n_published"]) != N_PUBLISHED:
            problems.append("n_published differs from the frozen AMEND-001 value (allowed only via amendment)")
        if set(self.fact_grid) != set(FACT_GRID):
            problems.append("fact grid fields differ from the enumerated grid")
        if list(MASK_FIELDS) != ["ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY"]:
            problems.append("ledger mask field order drifted")
        held = self.held_out
        if int(held["n"]) != int(self.factor_cells) + 2 * int(self.dose_cells):
            problems.append("held-out plan does not match 16x1 + 12x2")
        return problems

    def quota_layer_digest(self) -> str:
        return sha256_text(canon([layer.as_dict() for layer in self.quota_layers]))


def load(path: pathlib.Path | str | None = None, *, validate: bool = True) -> BuildConfig:
    config_path = pathlib.Path(path) if path is not None else CONFIG_PATH
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    config = BuildConfig(raw=raw, path=config_path)
    if validate:
        problems = config.validate()
        if problems:
            raise ConfigError("invalid R28 build config:\n - " + "\n - ".join(problems))
    return config


__all__ = ["BuildConfig", "CONFIG_PATH", "ConfigError", "QuotaLayer", "load"]
