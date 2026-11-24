"""Mechanical validation of T2 corruption pairs.

The captain's constraint: a "corrupted" text is only a valid negative control if a
mechanical proxy shows it actually became less natural.  We use two proxies:

* ``syntax_break_delta`` — count of deterministic syntactic anomalies (text starts
  lowercase; lowercase after sentence punctuation; duplicated adjacent tokens;
  determiner-determiner / preposition-preposition / determiner-preposition pairs;
  punctuation anomalies), degraded minus natural.  This is the primary proxy for
  ``half_splice`` (word-order break) because FRE is invariant to word order.
* ``bigram_delta`` — mean per-token log-probability drop under a bigram model trained
  on the R28 published corpus (add-1 smoothing).  This catches word-salad corruptions.

FRE delta is recorded for completeness but is **not** used as a gate: swapping words
does not change syllable/sentence counts, so FRE cannot detect half_splice.

Pre-declared ineffective rule: ``syntax_break_delta <= 0 and bigram_delta < 0.05``.
An ineffective pair is marked ``INEFFECTIVE_CORRUPTION`` and excluded from the T2
metric denominator; it is never counted as a model failure.
"""
from __future__ import annotations

import collections
import math
import re
from typing import Any, Iterable

from local_inference import corpus

TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-]*")
DET = r"(?:the|a|an)"
PREP = r"(?:of|to|in|on|with|for|from|by|at|as)"
CONJ = r"(?:and|or|but|nor|yet|so)"
BAD_PAIR_RE = re.compile(
    rf"\b(?:{DET})\s+(?:{DET}|{PREP}|{CONJ})\b|"
    rf"\b(?:{PREP})\s+(?:{PREP}|{CONJ})\b|"
    rf"\b(?:{CONJ})\s+(?:{CONJ}|{DET})\b",
    re.I,
)
BAD_PUNCT_RE = re.compile(r"[,;]\s*[,;]")
LOWERCASE_AFTER_PUNCT_RE = re.compile(r"[.!?]\s+([A-Za-z']+)")
LEADING_WORD_RE = re.compile(r"\s*([A-Za-z']+)")


def tokens(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text or "")]


def syntax_break_count(text: str) -> int:
    text = text or ""
    count = 0
    match = LEADING_WORD_RE.match(text)
    if match and match.group(1)[0].islower():
        count += 1
    for match in LOWERCASE_AFTER_PUNCT_RE.finditer(text):
        if match.group(1)[0].islower():
            count += 1
    toks = tokens(text)
    for first, second in zip(toks, toks[1:]):
        if first == second:
            count += 1
    count += len(BAD_PAIR_RE.findall(text))
    count += len(BAD_PUNCT_RE.findall(text))
    return count


class BigramModel:
    def __init__(self, texts: Iterable[str]):
        self.unigram: collections.Counter = collections.Counter()
        self.bigram: collections.Counter = collections.Counter()
        for text in texts:
            toks = tokens(text)
            self.unigram.update(toks)
            self.bigram.update(zip(toks, toks[1:]))
        self.vocab_size = len(self.unigram) + 1  # + <unk>

    def mean_logprob(self, text: str) -> float:
        toks = tokens(text)
        if len(toks) < 2:
            return 0.0
        total = 0.0
        for first, second in zip(toks, toks[1:]):
            total += math.log((self.bigram[(first, second)] + 1.0)
                              / (self.unigram[first] + self.vocab_size))
        return total / (len(toks) - 1)


_MODEL: BigramModel | None = None


def model() -> BigramModel:
    global _MODEL
    if _MODEL is None:
        _MODEL = BigramModel(span["text"] for span in corpus.iter_spans())
    return _MODEL


def assess(natural: str, degraded: str) -> dict[str, Any]:
    natural_break = syntax_break_count(natural)
    degraded_break = syntax_break_count(degraded)
    bigram = model()
    natural_lp = bigram.mean_logprob(natural)
    degraded_lp = bigram.mean_logprob(degraded)
    delta = natural_lp - degraded_lp
    fre_natural = corpus.flesch_reading_ease(natural)
    fre_degraded = corpus.flesch_reading_ease(degraded)
    syntax_delta = degraded_break - natural_break
    ineffective = (degraded == natural) or (syntax_delta <= 0 and delta < 0.05)
    reason = None
    if degraded == natural:
        reason = "identical text"
    elif ineffective:
        reason = "no syntax break and bigram delta < 0.05"
    return {
        "syntax_breaks_natural": natural_break,
        "syntax_breaks_degraded": degraded_break,
        "syntax_break_delta": syntax_delta,
        "bigram_logprob_natural": round(natural_lp, 6),
        "bigram_logprob_degraded": round(degraded_lp, 6),
        "bigram_delta": round(delta, 6),
        "fre_natural": round(fre_natural, 3),
        "fre_degraded": round(fre_degraded, 3),
        "fre_delta": round(fre_natural - fre_degraded, 3),
        "ineffective": bool(ineffective),
        "ineffective_reason": reason,
        "proxies": {
            "primary": "syntax_break_delta",
            "secondary": "bigram_delta",
            "unused": "fre_delta (word-order invariant)",
            "ineffective_rule": "degraded == natural OR (syntax_break_delta <= 0 AND bigram_delta < 0.05)",
        },
    }


__all__ = ["BigramModel", "assess", "model", "syntax_break_count", "tokens"]
