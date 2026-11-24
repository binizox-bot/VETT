"""R28 generator: constants, paths and frozen identifiers.

This package is new code for the R28 build (task t5).  It never writes inside the
R26.15 candidate tree and imports the frozen R25 solver read-only.
"""

from __future__ import annotations

import pathlib

# Byte-code writes are disabled so that importing the frozen reference solver can
# never add files under the protected ``src/`` tree.
import sys

sys.dont_write_bytecode = True

ROOT = pathlib.Path(__file__).resolve().parents[2]  # VETT_R28_DIFFICULTY_20261112
WS = ROOT.parent  # workspace root
PROJ = WS / "VETT_Cricket_v0.22_R16_Multisource_Dilemmas"
SRC = PROJ / "src"
BUILD = ROOT / "03_build"
BACKUP = WS / "_BACKUPS" / "VETT_R28_PRE_CHANGE_20261112"

DATASET_VERSION = "VETT-Cricket-v0.37-R28-diagnostic-pair-20261112"
DESIGN_ID = "R28-DOSE-DIAGNOSTIC-PAIR"
CONTRACT_ID = "VETT-R28-CONTRACT-20261112-v1"
CONTRACT_VERSION = "1.1.0"
PREREG_ID = "VETT-R28-PREREG-20261112-v1"
PREREG_VERSION = "1.1.0"

SEED = 20261112
N_PUBLISHED = 320

# ---------------------------------------------------------------------------
# Record schema (frozen by the contract; field names must not change).
# ---------------------------------------------------------------------------
RECORD_FIELDS = (
    "delivery_status",
    "counts_in_over",
    "dismissal",
    "total_runs",
    "batter_runs",
    "bowler_runs",
    "ledger.BATTER",
    "ledger.NO_BALL_EXTRA",
    "ledger.WIDE_EXTRA",
    "ledger.BYE",
    "ledger.LEG_BYE",
    "ledger.PENALTY",
)
LEDGER_ORDER = ("BATTER", "NO_BALL_EXTRA", "WIDE_EXTRA", "BYE", "LEG_BYE", "PENALTY")
LEDGER_FIELDS = ("ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY")

# Main-endpoint set frozen by the pre-registration: the nine informative fields of
# R26.15 (all twelve fields except the three that were constant there).  R28 makes
# the other three non-constant as well; they stay outside the main denominator.
INFORMATIVE_FIELDS = (
    "delivery_status",
    "counts_in_over",
    "dismissal",
    "total_runs",
    "batter_runs",
    "bowler_runs",
    "ledger.BATTER",
    "ledger.NO_BALL_EXTRA",
    "ledger.WIDE_EXTRA",
)

STATUSES = ("LEGAL", "NO_BALL", "WIDE", "DEAD_REBALL")
DISMISSALS = (
    "NONE",
    "BOWLED",
    "LBW",
    "CAUGHT",
    "RUN_OUT",
    "STUMPED",
    "OBSTRUCTING_FIELD",
    "HIT_BALL_TWICE",
)
# Legal (delivery-completed) dismissals are capped by the record space (CEIL-2).
LEGAL_DISMISSALS = ("BOWLED", "LBW", "CAUGHT", "STUMPED")

LEDGER_MASKS = ("000", "001", "010", "011", "100", "101")
MASK_FIELDS = LEDGER_FIELDS  # bit order = (BYE, LEG_BYE, PENALTY)

# ---------------------------------------------------------------------------
# Dose semantics frozen by the contract (all UNTESTED).
# ---------------------------------------------------------------------------
DOSE_IDS = ("D1", "D2", "D3", "D4")
DOSE_PARAMETER = {
    "D1": "alias_hops",
    "D2": "temporal_joins",
    "D3": "scope_decisions",
    "D4": "isomorphic_distractors",
}
DOSE_LEVELS = {
    "D1": (0, 1, 2),
    "D2": (0, 1, 2),
    "D3": (0, 1, 2),  # 2 means ">= 2"
    "D4": (0, 1, 2),  # 2 means ">= 2"
}

# Prompt budget (RISK-4 / HA15).
MAX_PROMPT_TOKENS = 7000
MAX_DOCUMENTS = 12
MAX_SPANS = 80
CHARS_PER_TOKEN = 4

# Record-space safety rule (contract section 6).
HELD_OUT_N = 40
SAFETY_FACTOR = 0.10

DERIVATION_OPERATOR_VERSION = "r28-derivation-pipeline-v1"
CERTIFICATE_SCHEMA = "vett.r28.certificate.v1"
PUBLIC_SCHEMA = "vett.r28.public_instance.v1"
GOLD_SCHEMA = "vett.r28.private_gold.v1"


def relative(path: pathlib.Path) -> str:
    """Project-relative POSIX path (used in manifests and witnesses)."""

    resolved = path.resolve()
    for base in (WS, ROOT):
        try:
            return resolved.relative_to(base.resolve()).as_posix()
        except ValueError:
            continue
    return resolved.as_posix()
