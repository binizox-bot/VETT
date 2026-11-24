"""R20 full-corpus repair and long-form benchmark construction."""

from .generator import DATASET_VERSION, build_instance, resolve_from_evidence
from .evaluation import score_predictions
from .repair import DUPLICATE_OF, VERSION, audit_repair_release, build_repair_release
from .release import audit_release, build_release

__all__ = [
    "DATASET_VERSION",
    "DUPLICATE_OF",
    "VERSION",
    "audit_release",
    "audit_repair_release",
    "build_instance",
    "build_release",
    "build_repair_release",
    "resolve_from_evidence",
    "score_predictions",
]
