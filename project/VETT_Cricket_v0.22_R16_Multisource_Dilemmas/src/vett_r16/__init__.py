"""VETT-Cricket R16 controlled multi-source dilemma builder."""

from .model import AuthorityPolicy, Claim, Resolution, Target
from .resolver import resolve_target

__all__ = ["AuthorityPolicy", "Claim", "Resolution", "Target", "resolve_target"]

