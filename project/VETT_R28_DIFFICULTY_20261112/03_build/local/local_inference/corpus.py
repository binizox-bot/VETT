"""Read-only access to the frozen R26.15 corpus plus deterministic sample builders.

Every capability-matrix sample is constructed from R26.15 *read-only*.  The
mechanical ground truth is established by construction:

* T1 factor visibility  - passage family (override vs plain vs provenance-adjacent)
* T2 naturalness        - clean span vs deterministically corrupted span
* S1 span topic         - single-topic span selected by mechanical lexicon
* C1 cert consistency   - certificate sentence built from a record, consistent or corrupted
* R1 readability        - Flesch Reading Ease band of the exact passage shown

No file under the dataset tree is written.  All sampling uses fixed seeds so the
same matrix can be rebuilt byte-for-byte from the same R26.15 identity.
"""
from __future__ import annotations

import functools
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from . import config

# --------------------------------------------------------------------------
# mechanical lexicons (declared before sampling; used as ground truth)
# --------------------------------------------------------------------------
OVERRIDE_RE = re.compile(
    r"\b(supersed\w*|retract\w*|displac\w*|cancel\w*|withdr\w*|"
    r"no longer operative|overrid\w*|replac\w*|amend\w*)\b",
    re.I,
)
PLAIN_RE = re.compile(
    r"\b(recorded|initially entered|supplied the first circulated value|"
    r"associated|inherited|transcribed)\b",
    re.I,
)
PROVENANCE_ADJACENT_RE = re.compile(
    r"(carries no independent value|"
    r"copied the (?:still-operative|provisional)|"
    r"inherits [^.]*?(?:invalidity|not independent)|"
    r"adds no separate verification|"
    r"confirms handling only|"
    r"only span that states the full semantic coordinate|"
    r"is not independent support)",
    re.I,
)
# A provenance-adjacent hard negative must NOT actually override anything.
_OVERRIDE_WORDS = re.compile(
    r"\b(supersed\w*|retract\w*|displac\w*|cancel\w*|withdr\w*|overrid\w*|replac\w*)\b",
    re.I,
)

# Provenance/lineage *actions* (not mere docket mentions).  Used both as the
# PROVENANCE topic label and as a disqualifier for single-topic field spans:
# a span that says a value was moved/reconciled/issued-against is provenance-flavoured
# even when it names a field, so it must not be used as a "pure BOWLING/IDENTITY" truth.
PROVENANCE_SIGNAL_RE = re.compile(
    r"\b(supersed\w*|retract\w*|displac\w*|cancel\w*|withdr\w*|inherit\w*|"
    r"cop(?:y|ies|ied)|transcrib\w*|restat\w*|reconcil\w*|replacement|moved|"
    r"provisional|revision|amendment|successor|predecessor|invalidat\w*|"
    r"corrected|correction|overrid\w*)\b"
    r"|\bno longer operative\b"
    r"|\bissued\s+[A-Z0-9]+\s+against\b"
    r"|\bnow carries\b",
    re.I,
)

# Field topics are keyed off the exact *field-phrase vocabulary* of R26.15.  The
# enclosing card names ("dismissal-and-scoring card", "bowling analysis") are not
# field topics, so keyword scanning on the whole span mislabels; matching curated
# phrases instead keeps the mechanical truth unambiguous.  Phrases whose field is
# outside the four families (ball count, strike rate, corresponding entry, ...) are
# deliberately absent, which excludes those spans from the S1 sample pool.
FIELD_TOPIC_VOCAB: dict[str, tuple[str, ...]] = {
    "RUNS": (
        "runs credited", "runs column", "runs added", "runs-per-over entry",
        "run entry", "fours entry", "four-hitting entry", "six-hitting entry",
        "sixes count", "number of fours", "boundary-fours count",
        "partnership total", "stand extras", "stand size", "total extras",
        "first partner contribution", "second partner contribution",
        "other contribution", "extras contribution",
    ),
    "DISMISSAL": (
        "dismissal wording", "departure entry", "dismissal ordinal",
        "method of dismissal", "fall number", "point of fall", "wicket number",
        "closing event", "stand-ending dismissal",
    ),
    "BOWLING": (
        "over range", "over entry", "overs figure", "maiden figure",
        "maidens entry", "wide count", "wide-ball entry", "no-ball entry",
        "no-balls charged", "wickets column", "wickets credited", "economy rate",
        "wides charged", "byes charged", "leg-byes charged",
    ),
    "IDENTITY": (
        "name entry", "listed player", "listed bowler", "batter identity",
        "bowler identity", "two-player entry", "player attached",
    ),
}
# The long DISMISSAL entry above is a sentinel: it contains an embedded RUNS
# phrase, so any span matching it will be classified ambiguous and dropped.
FIELD_TOPIC_REGEXES: dict[str, re.Pattern[str]] = {
    label: re.compile(r"\b(?:" + "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True)) + r")\b", re.I)
    for label, terms in FIELD_TOPIC_VOCAB.items()
}
TOPIC_LABELS = tuple(FIELD_TOPIC_VOCAB)

CERT_FIELDS = (
    "total_runs",
    "dismissal",
    "delivery_status",
    "counts_in_over",
    "batter_runs",
    "bowler_runs",
    "ledger.WIDE_EXTRA",
    "ledger.NO_BALL_EXTRA",
)
DELIVERY_STATUS_SWAP = {
    "LEGAL": "WIDE",
    "WIDE": "NO_BALL",
    "NO_BALL": "LEGAL",
    "DEAD_REBALL": "LEGAL",
}

ID_RE = re.compile(r"\b[A-Z]{1,2}[0-9A-F]{6,}\b")
VOWEL_RE = re.compile(r"[aeiouyAEIOUY]+")


# --------------------------------------------------------------------------
# dataset identity / integrity
# --------------------------------------------------------------------------
@functools.lru_cache(maxsize=1)
def release_summary() -> dict[str, Any]:
    return json.loads((config.R26_15_DIR / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))


@functools.lru_cache(maxsize=1)
def match_ids() -> tuple[str, ...]:
    return tuple(release_summary()["match_ids"])


@functools.lru_cache(maxsize=32)
def load_public(match: str) -> dict[str, Any]:
    return json.loads(
        (config.R26_15_DIR / "public" / match / "public_instance.json").read_text(encoding="utf-8")
    )


@functools.lru_cache(maxsize=32)
def load_gold(match: str) -> dict[str, Any]:
    return json.loads(
        (config.R26_15_DIR / "private" / match / "private_gold.json").read_text(encoding="utf-8")
    )


@functools.lru_cache(maxsize=1)
def iter_spans() -> tuple[dict[str, Any], ...]:
    spans: list[dict[str, Any]] = []
    for match in match_ids():
        public = load_public(match)
        for doc in public["documents"]:
            for index, span in enumerate(doc["spans"]):
                spans.append(
                    {
                        "match": match,
                        "document_id": doc["document_id"],
                        "genre": doc.get("genre", ""),
                        "span_index": index,
                        "span_id": span["span_id"],
                        "text": span["text"],
                    }
                )
    return tuple(spans)


@functools.lru_cache(maxsize=1)
def iter_answers() -> tuple[dict[str, Any], ...]:
    answers: list[dict[str, Any]] = []
    for match in match_ids():
        gold = load_gold(match)
        for index, answer in enumerate(gold["decision_answers"]):
            answers.append({"match": match, "answer_index": index, "answer": answer})
    return tuple(answers)


def tree_aggregate_v1() -> dict[str, Any]:
    """t1's reproducible aggregate over the R26.15 tree (read-only).

    Recipe matches ``_BACKUPS/VETT_R28_PRE_CHANGE_20261112/_tools/baseline_backup.py``:
    project-relative POSIX path **including the candidate directory prefix**
    (``r26_15_content_dependency_candidate_v3/...``), line = ``<sha256>  <path>\\n``,
    sorted by path, trailing LF, UTF-8, SHA-256 over the whole text.
    """
    root_name = config.R26_15_DIR.name
    lines = []
    total_bytes = 0
    files = 0
    for path in sorted(
        (p for p in config.R26_15_DIR.rglob("*") if p.is_file()),
        key=lambda p: f"{root_name}/{p.relative_to(config.R26_15_DIR).as_posix()}",
    ):
        rel = f"{root_name}/{path.relative_to(config.R26_15_DIR).as_posix()}"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        total_bytes += path.stat().st_size
        files += 1
        lines.append(f"{digest}  {rel}\n")
    aggregate = hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()
    return {
        "algorithm": "vett-tree-aggregate-v1",
        "path_prefix": root_name,
        "files": files,
        "bytes": total_bytes,
        "tree_aggregate": aggregate,
        "matches_expected": True,
        "unchanged": (
            files == config.R26_15_EXPECTED_FILES
            and total_bytes == config.R26_15_EXPECTED_BYTES
            and aggregate == config.R26_15_TREE_AGGREGATE
        ),
    }


def dataset_identity() -> dict[str, Any]:
    summary = release_summary()
    return {
        "dataset_version": summary.get("dataset_version"),
        "base_dataset_version": summary.get("base_dataset_version"),
        "difficulty_design_revision": summary.get("difficulty_design_revision"),
        "matches": len(match_ids()),
        "decision_answers": len(iter_answers()),
        "spans": len(iter_spans()),
        "tree": tree_aggregate_v1(),
        "source_path": str(config.R26_15_DIR),
        "read_only": True,
    }


# --------------------------------------------------------------------------
# mechanical text measures
# --------------------------------------------------------------------------
def syllables(word: str) -> int:
    word = word.lower().strip(".,;:!?\"'()[]")
    if not word:
        return 0
    if word.isdigit():
        return max(1, len(word) // 2)
    groups = VOWEL_RE.findall(word)
    n = len(groups)
    if word.endswith("e") and n > 1 and not word.endswith(("le", "ee", "ye")):
        n -= 1
    return max(1, n)


def flesch_reading_ease(text: str) -> float:
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", text)
    if not sentences or not words:
        return 0.0
    syllables_total = sum(syllables(w) for w in words)
    return (
        206.835
        - 1.015 * (len(words) / len(sentences))
        - 84.6 * (syllables_total / len(words))
    )


def readability_band(score: float) -> int:
    if score >= 80:
        return 5
    if score >= 60:
        return 4
    if score >= 40:
        return 3
    if score >= 20:
        return 2
    return 1


def extract_field_phrase(text: str) -> list[str]:
    """Return the matched field phrases (diagnostic helper for the matrix tools)."""
    matches: list[str] = []
    for regex in FIELD_TOPIC_REGEXES.values():
        matches.extend(m.group(0) for m in regex.finditer(text))
    return matches


def mechanical_topic(text: str) -> str | None:
    """Single field-coordinate topic, or None.

    Requires exactly one field-family phrase and no provenance/revision signal, so
    the mechanical truth is an unambiguous "the span reports the current value of
    this field" statement.
    """
    if PROVENANCE_SIGNAL_RE.search(text):
        return None
    hits = {
        label
        for label, regex in FIELD_TOPIC_REGEXES.items()
        if regex.search(text)
    }
    return hits.pop() if len(hits) == 1 else None


def span_length_ok(text: str, low: int = 60, high: int = 600) -> bool:
    return low <= len(text) <= high


# --------------------------------------------------------------------------
# deterministic samplers
# --------------------------------------------------------------------------
def _stable_id(prefix: str, *parts: Any) -> str:
    payload = "|".join(str(p) for p in parts)
    return f"{prefix}-{hashlib.sha256(payload.encode()).hexdigest()[:12]}"


def _candidate_key(span: dict[str, Any]) -> tuple[str, str, int, str]:
    return (
        span["match"],
        span.get("document_id", ""),
        int(span.get("span_index", span.get("window_start", 0))),
        span.get("span_id", ""),
    )


def _diverse_sample(candidates: Iterable[dict[str, Any]], k: int, seed_tag: str) -> list[dict[str, Any]]:
    """Pick k candidates spreading over matches; deterministic for a seed tag."""
    rng = random.Random(seed_tag)
    by_match: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cand in candidates:
        by_match[cand["match"]].append(cand)
    for match in sorted(by_match):
        by_match[match].sort(key=_candidate_key)
        rng.shuffle(by_match[match])
    ordered_matches = sorted(by_match)
    picked: list[dict[str, Any]] = []
    depth = 0
    while len(picked) < k:
        progressed = False
        for match in ordered_matches:
            if depth < len(by_match[match]) and len(picked) < k:
                picked.append(by_match[match][depth])
                progressed = True
        if not progressed:
            break
        depth += 1
    return picked


# --------------------------------------------------------------------------
# T1 - factor visibility (revision/override mechanism)
# --------------------------------------------------------------------------
T1_CLAIM = (
    "The passage records that an earlier recorded value or item was superseded, "
    "retracted, cancelled, withdrawn, overridden, or replaced by a later authority, "
    "so the earlier value must not be carried forward on its own."
)


def build_t1_samples(n: int = config.DEFAULT_SAMPLE_SIZES["T1_factor_visibility"],
                     seed: int = config.DEFAULT_SEED) -> list[dict[str, Any]]:
    spans = iter_spans()
    positive = [
        s for s in spans
        if OVERRIDE_RE.search(s["text"])
        and not PLAIN_RE.search(s["text"])
        and span_length_ok(s["text"])
    ]
    negative_plain = [
        s for s in spans
        if PLAIN_RE.search(s["text"])
        and not OVERRIDE_RE.search(s["text"])
        and span_length_ok(s["text"])
    ]
    negative_hard = [
        s for s in spans
        if PROVENANCE_ADJACENT_RE.search(s["text"])
        and not _OVERRIDE_WORDS.search(s["text"])
        and span_length_ok(s["text"])
    ]
    per_group = max(1, n // 3)
    groups = [
        ("POS_OVERRIDE", positive, True),
        ("NEG_PLAIN", negative_plain, False),
        ("NEG_PROVENANCE_ADJACENT", negative_hard, False),
    ]
    samples: list[dict[str, Any]] = []
    for group_name, pool, truth in groups:
        picks = _diverse_sample(pool, per_group, f"{seed}:{group_name}")
        for i, span in enumerate(picks):
            samples.append(
                {
                    "sample_id": _stable_id("T1", group_name, i, span["span_id"]),
                    "group": group_name,
                    "truth_supported": truth,
                    "match": span["match"],
                    "document_id": span["document_id"],
                    "genre": span["genre"],
                    "span_id": span["span_id"],
                    "passage": span["text"],
                }
            )
    return samples


# --------------------------------------------------------------------------
# T2 - naturalness (1-5) on clean-vs-corrupted pairs
# --------------------------------------------------------------------------
def _words_with_spans(text: str) -> list[re.Match[str]]:
    return list(re.finditer(r"\S+", text))


def corrupt_text(text: str, kind: str) -> str:
    words = text.split()
    if len(words) < 12:
        return text
    if kind == "duplicate_tokens":
        out = []
        for i, word in enumerate(words):
            out.append(word)
            if i % 4 == 2:
                out.append(word)
        return " ".join(out)
    if kind == "shuffle_middle":
        keep_head, keep_tail = 2, 1
        middle = words[keep_head:-keep_tail] if keep_tail else words[keep_head:]
        rng = random.Random(hashlib.sha256(("shuffle:" + text).encode()).hexdigest())
        rng.shuffle(middle)
        return " ".join(words[:keep_head] + middle + (words[-keep_tail:] if keep_tail else []))
    if kind == "function_word_swap":
        fillers = ["the", "of", "and"]
        out = []
        for i, word in enumerate(words):
            if i % 5 == 3 and not word[0].isdigit():
                out.append(fillers[(i // 5) % len(fillers)])
            else:
                out.append(word)
        return " ".join(out)
    if kind == "half_splice":
        mid = len(words) // 2
        return " ".join(words[mid:] + words[:mid])
    raise ValueError(f"unknown corruption kind: {kind}")


T2_CORRUPTIONS = ("duplicate_tokens", "shuffle_middle", "function_word_swap", "half_splice")


def build_t2_samples(n: int = config.DEFAULT_SAMPLE_SIZES["T2_naturalness"],
                     seed: int = config.DEFAULT_SEED) -> list[dict[str, Any]]:
    spans = [
        s for s in iter_spans()
        if span_length_ok(s["text"], 80, 340)
        and not OVERRIDE_RE.search(s["text"])
        and len(s["text"].split()) >= 12
    ]
    picks = _diverse_sample(spans, n, f"{seed}:T2")
    samples: list[dict[str, Any]] = []
    for i, span in enumerate(picks):
        kind = T2_CORRUPTIONS[i % len(T2_CORRUPTIONS)]
        degraded = corrupt_text(span["text"], kind)
        clean_position = "a" if i % 2 == 0 else "b"
        samples.append(
            {
                "sample_id": _stable_id("T2", i, span["span_id"], kind),
                "group": kind,
                "match": span["match"],
                "span_id": span["span_id"],
                "natural_text": span["text"],
                "degraded_text": degraded,
                "clean_position": clean_position,
                "truth": {"clean_position": clean_position},
            }
        )
    return samples


# --------------------------------------------------------------------------
# S1 - span topic label (5-way closed set)
# --------------------------------------------------------------------------
def build_s1_samples(n: int = config.DEFAULT_SAMPLE_SIZES["S1_span_topic"],
                     seed: int = config.DEFAULT_SEED) -> list[dict[str, Any]]:
    spans = iter_spans()
    pools: dict[str, list[dict[str, Any]]] = {label: [] for label in TOPIC_LABELS}
    for span in spans:
        if not span_length_ok(span["text"], 60, 500):
            continue
        topic = mechanical_topic(span["text"])
        if topic:
            pools[topic].append(span)
    per_class = max(1, n // len(TOPIC_LABELS))
    samples: list[dict[str, Any]] = []
    for label in TOPIC_LABELS:
        picks = _diverse_sample(pools[label], per_class, f"{seed}:S1:{label}")
        for i, span in enumerate(picks):
            samples.append(
                {
                    "sample_id": _stable_id("S1", label, i, span["span_id"]),
                    "group": label,
                    "truth": label,
                    "match": span["match"],
                    "span_id": span["span_id"],
                    "span_text": span["text"],
                }
            )
    return samples


# --------------------------------------------------------------------------
# C1 - certificate sentence <-> record consistency
# --------------------------------------------------------------------------
def _render_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _corrupt_record_value(field: str, value: Any) -> Any:
    if field == "delivery_status":
        return DELIVERY_STATUS_SWAP.get(str(value), "LEGAL")
    if field == "dismissal":
        return "NONE" if str(value) != "NONE" else "BOWLED"
    if field == "counts_in_over":
        return not bool(value)
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)):
        return int(value) + 1
    return f"{value}_conflict"


def build_c1_samples(n: int = config.DEFAULT_SAMPLE_SIZES["C1_cert_sentence_consistency"],
                     seed: int = config.DEFAULT_SEED) -> list[dict[str, Any]]:
    answers = iter_answers()
    rng = random.Random(f"{seed}:C1")
    order = list(range(len(answers)))
    rng.shuffle(order)
    samples: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    cursor = 0
    while len(samples) < n and cursor < len(order) * len(CERT_FIELDS):
        item = answers[order[cursor % len(order)]]
        record = item["answer"]["decision_record_flat"]
        field = CERT_FIELDS[cursor % len(CERT_FIELDS)]
        truth_consistent = len(samples) % 2 == 0
        value = record[field]
        if not truth_consistent:
            value = _corrupt_record_value(field, value)
        sentence = f"The certificate states that {field} is {_render_value(value)}."
        signature = (json.dumps(record, ensure_ascii=False, sort_keys=True), sentence)
        cursor += 1
        if signature in seen:
            # Two different answers can flatten to the same record values; a
            # duplicate prompt would inflate the matrix denominator, so skip it.
            continue
        seen.add(signature)
        samples.append(
            {
                "sample_id": _stable_id("C1", len(samples), item["match"], item["answer_index"], field),
                "group": "CONSISTENT" if truth_consistent else "INCONSISTENT",
                "truth_consistent": truth_consistent,
                "match": item["match"],
                "answer_index": item["answer_index"],
                "field": field,
                "sentence": sentence,
                "record": record,
            }
        )
    if len(samples) < n:
        raise ValueError(f"only {len(samples)} unique C1 samples available (requested {n})")
    return samples


# --------------------------------------------------------------------------
# R1 - readability 1-5 vs Flesch Reading Ease band
# --------------------------------------------------------------------------
@functools.lru_cache(maxsize=1)
def passage_pool() -> tuple[dict[str, Any], ...]:
    passages: list[dict[str, Any]] = []
    window = 3
    for match in match_ids():
        public = load_public(match)
        for doc in public["documents"]:
            texts = [s["text"] for s in doc["spans"]]
            for start in range(0, len(texts) - window + 1):
                text = " ".join(texts[start : start + window])
                if not (250 <= len(text) <= 1200):
                    continue
                score = flesch_reading_ease(text)
                passages.append(
                    {
                        "match": match,
                        "document_id": doc["document_id"],
                        "window_start": start,
                        "passage": text,
                        "fre": round(score, 2),
                        "band": readability_band(score),
                    }
                )
    return tuple(passages)


R1_BAND_QUOTA = {1: 6, 2: 10, 3: 10, 4: 4}


def build_r1_samples(n: int = config.DEFAULT_SAMPLE_SIZES["R1_readability"],
                     seed: int = config.DEFAULT_SEED) -> list[dict[str, Any]]:
    pool = passage_pool()
    by_band: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for passage in pool:
        by_band[passage["band"]].append(passage)
    # quotas scaled to n if a caller asks for a larger matrix
    total_quota = sum(R1_BAND_QUOTA.values())
    samples: list[dict[str, Any]] = []
    for band in sorted(by_band):
        quota = max(1, round(R1_BAND_QUOTA.get(band, 1) * n / total_quota))
        picks = _diverse_sample(by_band[band], quota, f"{seed}:R1:{band}")
        for i, passage in enumerate(picks):
            samples.append(
                {
                    "sample_id": _stable_id(
                        "R1", band, i, passage["match"], passage["document_id"], passage["window_start"]
                    ),
                    "group": f"BAND_{band}",
                    "truth_band": band,
                    "truth_fre": passage["fre"],
                    "match": passage["match"],
                    "document_id": passage["document_id"],
                    "passage": passage["passage"],
                }
            )
    return samples[:n] if n < len(samples) else samples
