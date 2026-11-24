"""Configuration constants for the R28 local-inference service (Qwen2.5-7B / Ollama).

Single source of truth for model identity, decoding parameters, hard limits and
artifact paths.  Everything the pipeline needs is exported here; the routing
card generator reads these values so that code and card cannot drift silently.
"""
from __future__ import annotations

import os
from pathlib import Path

# --- paths -----------------------------------------------------------------
PACKAGE_DIR = Path(__file__).resolve().parent
LOCAL_ROOT = Path(os.environ.get("VETT_LOCAL_ROOT", str(PACKAGE_DIR.parent)))
WORKSPACE_ROOT = Path(
    os.environ.get("VETT_WORKSPACE_ROOT", str(PACKAGE_DIR.parents[3]))
)
R26_15_DIR = Path(
    os.environ.get(
        "VETT_R26_15",
        str(
            WORKSPACE_ROOT
            / "VETT_Cricket_v0.22_R16_Multisource_Dilemmas"
            / "r26_15_content_dependency_candidate_v3"
        ),
    )
)

RUNS_DIR = LOCAL_ROOT / "runs"
CACHE_PATH = RUNS_DIR / "cache.jsonl"
RETEST_CACHE_PATH = RUNS_DIR / "retest_cache.jsonl"
COST_LEDGER_PATH = Path(
    os.environ.get("VETT_LOCAL_LEDGER", str(LOCAL_ROOT / "cost_ledger.jsonl"))
)
DEGRADED_PATH = Path(
    os.environ.get("VETT_LOCAL_DEGRADED", str(LOCAL_ROOT / "DEGRADED_EVENTS.jsonl"))
)
MATRIX_PATH = LOCAL_ROOT / "capability_matrix.json"
ROUTING_CARD_PATH = LOCAL_ROOT / "routing_card.json"
SERVICE_SNAPSHOT_PATH = LOCAL_ROOT / "service_snapshot.json"
SELFTEST_DIR = RUNS_DIR / "selftest"

# --- service identity ------------------------------------------------------
OLLAMA_EXE = Path(
    os.environ.get(
        "VETT_OLLAMA_EXE",
        r"C:\Users\PC\AppData\Local\Programs\Ollama\ollama.exe",
    )
)
OLLAMA_URL = os.environ.get("VETT_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
MODEL_TAG = os.environ.get("VETT_LOCAL_MODEL", "qwen2.5:7b-instruct-q4_K_M")

# --- frozen decoding parameters (temperature 0, fixed seed) ----------------
TEMPERATURE = 0.0
SEED = int(os.environ.get("VETT_LOCAL_SEED", "20261112"))
NUM_CTX = 8192                 # hard ceiling: >8K token inputs are DENY
NUM_PREDICT_DEFAULT = 256
KEEP_ALIVE = "30m"
TIMEOUT_S = float(os.environ.get("VETT_LOCAL_TIMEOUT", "180"))
RETRIES = int(os.environ.get("VETT_LOCAL_RETRIES", "2"))   # 1 + 2 attempts
BACKOFF_S = (1.0, 2.0)
MIN_FREE_VRAM_MIB = 1536       # report/abort below 1.5 GB free (RTX 3070 8GB)
GPU_SAMPLE_EVERY = 1           # sample VRAM after every call

# --- capability gate -------------------------------------------------------
GATE_THRESHOLD = 0.85          # agreement with mechanical truth; below = DENY
GATE_METRIC = "agreement_with_mechanical_truth"

# --- prompt template versions (bump = cache invalidation + ledger audit) ---
TEMPLATE_VERSIONS = {
    "T1_factor_visibility": "T1.factor_visibility.v1",
    "T2_naturalness": "T2.naturalness_pair.v1",
    "S1_span_topic": "S1.span_topic.v4",
    "C1_cert_sentence_consistency": "C1.cert_sentence_consistency.v1",
    "R1_readability": "R1.readability.v1",
}

# --- R26.15 identity (read-only source; never modified) -------------------
R26_15_EXPECTED_FILES = 165
R26_15_EXPECTED_BYTES = 93_346_177
R26_15_TREE_AGGREGATE = (
    "343afde4c91d7785f42296074ecea685d5d466260674ab5a8c3bc37323d851bd"
)

# --- deterministic sampling ------------------------------------------------
DEFAULT_SEED = 20261112
DEFAULT_SAMPLE_SIZES = {
    "T1_factor_visibility": 30,
    "T2_naturalness": 30,          # pairs -> 30 calls, 60 scored texts
    "S1_span_topic": 32,
    "C1_cert_sentence_consistency": 30,
    "R1_readability": 30,
}
T2_RETEST_PAIRS = 10               # retest validator for T2 (repeat calls)
R1_AGREEMENT_TOLERANCE = 1         # 5-point ordinal: adjacent counts as agreement
R1_MIN_DISTINCT_SCORES = 3         # anti-degenerate guard for R1
