from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from .auditor import audit_instance
from .generator import VERSION, build_instance, load_canonical_roots


PILOT_MATCH_IDS = [
    "match_0003",
    "match_0007",
    "match_0009",
    "match_0025",
    "match_0026",
    "match_0030",
]


def _public_minute(document: dict[str, Any]) -> int:
    match = re.fullmatch(r"T\+(\d+)m", str(document.get("published_at", "")))
    return int(match.group(1)) if match else -1


def _normalized_opening(text: str) -> str:
    text = re.sub(r"K[0-9A-F]{8}-(?:M|I1|I2)", "<DOCKET>", text)
    text = re.sub(r"packet_[0-9a-f]+", "<PACKET>", text)
    text = re.sub(r"\b\d+\b", "<N>", text)
    return " ".join(text.lower().split()[:5])


def _cross_instance_language_metrics(
    public_instances: list[dict[str, Any]],
) -> dict[str, Any]:
    openings = [
        _normalized_opening(span.get("text", ""))
        for public in public_instances
        for document in public.get("documents", [])
        for span in document.get("spans", [])
        if span.get("text", "").strip()
    ]
    counts = Counter(openings)
    total = len(openings)
    unique_ratio = len(counts) / total if total else 0.0
    maximum_ratio = counts.most_common(1)[0][1] / total if counts and total else 1.0
    passed = bool(total) and unique_ratio >= 0.70 and maximum_ratio <= 0.08
    return {
        "status": "PASS" if passed else "FAIL",
        "span_count": total,
        "normalized_unique_openings": len(counts),
        "normalized_unique_ratio": round(unique_ratio, 6),
        "normalized_maximum_ratio": round(maximum_ratio, 6),
    }


def _selected_document_ids(
    public: dict[str, Any], selector: Callable[[dict[str, Any]], bool]
) -> set[str]:
    return {
        str(document["document_id"])
        for document in public.get("documents", [])
        if selector(document)
    }


def _latest_amendment_ids(public: dict[str, Any]) -> set[str]:
    candidates = [
        document
        for document in public.get("documents", [])
        if re.search(r"\bamends\s+K[0-9A-F]{8}-(?:M|I1|I2)\b", document.get("text", ""))
    ]
    if not candidates:
        return set()
    latest = max(candidates, key=_public_minute)
    return {str(latest["document_id"])}


def _shortcut_metrics(
    bundles: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]]
) -> dict[str, dict[str, Any]]:
    selectors: dict[str, Callable[[dict[str, Any]], set[str]]] = {
        "sealed_genre_or_text": lambda public: _selected_document_ids(
            public,
            lambda document: bool(
                re.search(
                    r"sealed scorer bulletin|closes the ledger",
                    f"{document.get('genre', '')} {document.get('text', '')}",
                    flags=re.IGNORECASE,
                )
            ),
        ),
        "fixed_t32": lambda public: _selected_document_ids(
            public, lambda document: document.get("published_at") == "T+32m"
        ),
        "latest_amendment": _latest_amendment_ids,
        "single_span_amendment": lambda public: _selected_document_ids(
            public,
            lambda document: len(document.get("spans", [])) == 1
            and bool(
                re.search(
                    r"\bamends\s+K[0-9A-F]{8}-(?:M|I1|I2)\b",
                    document.get("text", ""),
                )
            ),
        ),
        "amendment_template_family": lambda public: _selected_document_ids(
            public,
            lambda document: bool(
                re.search(
                    r"\b(?:Ledger update|Operations entry|After reconciliation, note|"
                    r"Packet note|For the [^.;]+ alone, entry)\b",
                    document.get("text", ""),
                    flags=re.IGNORECASE,
                )
            ),
        ),
        "terminal_lexicon": lambda public: _selected_document_ids(
            public,
            lambda document: bool(
                re.search(
                    r"\b(?:final|official|settled entry|terminal notice)\b",
                    f"{document.get('genre', '')} {document.get('text', '')}",
                    flags=re.IGNORECASE,
                )
            ),
        ),
    }
    metrics: dict[str, dict[str, Any]] = {}
    for name, selector in selectors.items():
        correct = 0
        total = 0
        selected_documents = 0
        for public, gold, evidence in bundles:
            selected = selector(public)
            selected_documents += len(selected)
            claims = evidence.get("claims", [])
            schema_by_id = {
                raw.get("target_id"): raw for raw in public.get("target_schema", [])
            }
            for target in gold.get("targets", []):
                if not target.get("decisive_support"):
                    continue
                total += 1
                schema = schema_by_id.get(target.get("target_id"), {})
                predictions = {
                    claim.get("value")
                    for claim in claims
                    if claim.get("document_id") in selected
                    and claim.get("status", "asserted") == "asserted"
                    and claim.get("innings") == schema.get("innings")
                    and claim.get("field") == schema.get("field")
                }
                prediction = next(iter(predictions)) if len(predictions) == 1 else None
                correct += int(prediction == target.get("value"))
        metrics[name] = {
            "correct": correct,
            "total": total,
            "accuracy": round(correct / total, 6) if total else 0.0,
            "selected_documents": selected_documents,
        }
    return metrics


def _decisive_support_metrics(
    bundles: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]]
) -> dict[str, Any]:
    instance_shares: dict[str, float] = {}
    document_counts: dict[str, int] = {}
    for public, gold, evidence in bundles:
        claims = {claim["claim_id"]: claim for claim in evidence.get("claims", [])}
        documents = [
            claims[target["decisive_support"][0]]["document_id"]
            for target in gold.get("targets", [])
            if target.get("decisive_support")
        ]
        counts = Counter(documents)
        share = max(counts.values()) / len(documents) if documents else 1.0
        instance_id = str(public.get("instance_id"))
        instance_shares[instance_id] = round(share, 6)
        document_counts[instance_id] = len(counts)
    maximum_share = max(instance_shares.values()) if instance_shares else 1.0
    return {
        "status": "PASS" if maximum_share <= 0.25 else "FAIL",
        "maximum_document_share": round(maximum_share, 6),
        "document_counts": document_counts,
        "instance_shares": instance_shares,
    }


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_record(root: Path, path: Path) -> dict[str, Any]:
    content = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def _release_report(summary: dict[str, Any]) -> str:
    shortcut_rows = "\n".join(
        f"| {name} | {item['correct']}/{item['total']} | {item['accuracy']:.2%} |"
        for name, item in summary["public_shortcuts"].items()
    )
    return f"""# VETT-Cricket R18 Adversarial Hardening Pilot

## Release decision

**{summary['status']}** — {summary['passed_instances']}/{summary['instances']} instances passed every machine gate.

## Hardening results

- Direct answers are distributed across at least five documents per instance.
- Maximum direct-answer concentration in one document: {summary['decisive_support']['maximum_document_share']:.2%}
- Identifier-normalized unique five-word openings: {summary['cross_instance_language']['normalized_unique_ratio']:.2%}
- Most common normalized opening: {summary['cross_instance_language']['normalized_maximum_ratio']:.2%}
- Claim values must be stated in their hashed public span.
- Quoted or negated edge phrases are rejected.

| Public-only shortcut | Correct | Accuracy |
| --- | ---: | ---: |
{shortcut_rows}

These deterministic attacks are release gates, not proof that a language model cannot solve the task. No external blind model run or human naturalness audit was performed.
"""


def _dataset_card(summary: dict[str, Any]) -> str:
    return f"""# Dataset Card: {summary['dataset_version']}

R18 is a controlled semi-synthetic adversarial pilot for reconstructing scoped cricket records from affirmative amendments, withdrawals, and copy ancestry. Genre, timestamp, array position, quoted phrases, and negated phrases are not authority signals.

Use only `public/` as model input. Keep `private/` and `audit/` outside the solving context. Exposing the complete release invalidates evaluation.

Machine release status: **{summary['status']}**. Blind language-model performance and human naturalness remain unverified.
"""


def build_release(
    roots_path: Path,
    output_dir: Path,
    selected_ids: list[str] | None = None,
    *,
    seed: int = 18031,
) -> dict[str, Any]:
    selected = selected_ids or PILOT_MATCH_IDS
    if len(set(selected)) != len(selected):
        raise ValueError("selected match IDs must be unique")
    output_dir.mkdir(parents=True, exist_ok=True)
    if any(path.is_file() for path in output_dir.rglob("*")):
        raise FileExistsError(f"release directory is not empty: {output_dir}")

    roots = load_canonical_roots(roots_path, set(selected))
    roots_by_id = {root["root_id"]: root for root in roots}
    audits: list[dict[str, Any]] = []
    bundles: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    for match_id in selected:
        bundle = build_instance(roots_by_id[match_id], seed=seed)
        audit = audit_instance(bundle.public, bundle.gold, bundle.evidence)
        _write_json(output_dir / "public" / match_id / "public_instance.json", bundle.public)
        _write_json(output_dir / "private" / match_id / "private_gold.json", bundle.gold)
        _write_json(
            output_dir / "private" / match_id / "private_evidence.json",
            bundle.evidence,
        )
        _write_json(output_dir / "audit" / f"{match_id}.audit.json", audit)
        audits.append(audit)
        bundles.append((bundle.public, bundle.gold, bundle.evidence))

    baseline_names = (
        "first_mention",
        "last_array_mention",
        "latest_timestamp",
        "majority_vote",
    )
    baselines: dict[str, dict[str, Any]] = {}
    for name in baseline_names:
        correct = sum(audit["baselines"][name]["correct"] for audit in audits)
        total = sum(audit["baselines"][name]["total"] for audit in audits)
        baselines[name] = {
            "correct": correct,
            "total": total,
            "accuracy": round(correct / total, 6) if total else 0.0,
        }

    language = _cross_instance_language_metrics([bundle[0] for bundle in bundles])
    shortcuts = _shortcut_metrics(bundles)
    decisive_support = _decisive_support_metrics(bundles)
    release_passed = (
        all(audit["status"] == "PASS" for audit in audits)
        and language["status"] == "PASS"
        and decisive_support["status"] == "PASS"
        and all(item["accuracy"] <= 0.25 for item in shortcuts.values())
    )
    summary = {
        "dataset_version": VERSION,
        "status": "PASS" if release_passed else "FAIL",
        "seed": seed,
        "instances": len(audits),
        "passed_instances": sum(audit["status"] == "PASS" for audit in audits),
        "match_ids": selected,
        "documents": sum(audit["summary"]["documents"] for audit in audits),
        "claims": sum(audit["summary"]["claims"] for audit in audits),
        "direct_targets": sum(audit["summary"]["direct_targets"] for audit in audits),
        "derived_targets": sum(audit["summary"]["derived_targets"] for audit in audits),
        "counterfactuals": sum(len(audit["counterfactuals"]) for audit in audits),
        "edge_ablations": sum(len(audit["edge_ablations"]) for audit in audits),
        "baselines": baselines,
        "public_shortcuts": shortcuts,
        "decisive_support": decisive_support,
        "cross_instance_language": language,
    }
    _write_json(output_dir / "RELEASE_SUMMARY.json", summary)
    (output_dir / "RELEASE_REPORT.md").write_text(
        _release_report(summary), encoding="utf-8"
    )
    (output_dir / "DATASET_CARD.md").write_text(
        _dataset_card(summary), encoding="utf-8"
    )
    manifest_files = [
        _file_record(output_dir, path)
        for path in sorted(output_dir.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.json"
    ]
    _write_json(
        output_dir / "MANIFEST.json",
        {
            "dataset_version": VERSION,
            "seed": seed,
            "file_count_excluding_manifest": len(manifest_files),
            "files": manifest_files,
        },
    )
    return summary


def audit_release(release_dir: Path) -> dict[str, Any]:
    manifest_errors: list[str] = []
    try:
        manifest = json.loads((release_dir / "MANIFEST.json").read_text(encoding="utf-8"))
        records = manifest.get("files", [])
    except (OSError, json.JSONDecodeError, AttributeError) as exc:
        manifest = {}
        records = []
        manifest_errors.append(f"manifest unreadable: {exc}")
    records_by_path = {
        record.get("path"): record
        for record in records
        if isinstance(record, dict) and isinstance(record.get("path"), str)
    }
    if manifest.get("file_count_excluding_manifest") != len(records):
        manifest_errors.append("manifest file count does not match its records")
    if len(records_by_path) != len(records):
        manifest_errors.append("manifest contains a duplicate or invalid path")
    actual_files = {
        path.relative_to(release_dir).as_posix(): path
        for path in sorted(release_dir.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.json"
    }
    if set(records_by_path) != set(actual_files):
        manifest_errors.append("manifest file set differs from release file set")
    for relative_path in sorted(set(records_by_path) & set(actual_files)):
        actual = _file_record(release_dir, actual_files[relative_path])
        expected = records_by_path[relative_path]
        if expected.get("bytes") != actual["bytes"]:
            manifest_errors.append(f"byte-count mismatch: {relative_path}")
        if expected.get("sha256") != actual["sha256"]:
            manifest_errors.append(f"sha256 mismatch: {relative_path}")

    semantic_errors: list[str] = []
    audits: list[dict[str, Any]] = []
    bundles: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    public_paths = sorted((release_dir / "public").glob("*/public_instance.json"))
    discovered_ids = [path.parent.name for path in public_paths]
    try:
        summary = json.loads(
            (release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8")
        )
        if summary.get("dataset_version") != VERSION:
            semantic_errors.append("release summary has an unexpected dataset version")
        if summary.get("match_ids") != discovered_ids:
            semantic_errors.append("release summary match IDs differ from public files")
    except (OSError, json.JSONDecodeError, AttributeError) as exc:
        semantic_errors.append(f"summary unreadable: {exc}")
    for public_path in public_paths:
        match_id = public_path.parent.name
        try:
            public = json.loads(public_path.read_text(encoding="utf-8"))
            gold = json.loads(
                (release_dir / "private" / match_id / "private_gold.json").read_text(
                    encoding="utf-8"
                )
            )
            evidence = json.loads(
                (release_dir / "private" / match_id / "private_evidence.json").read_text(
                    encoding="utf-8"
                )
            )
            audits.append(audit_instance(public, gold, evidence))
            bundles.append((public, gold, evidence))
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            semantic_errors.append(f"{match_id}: {exc}")

    language = _cross_instance_language_metrics([bundle[0] for bundle in bundles])
    shortcuts = _shortcut_metrics(bundles)
    support = _decisive_support_metrics(bundles)
    semantic_passed = (
        bool(audits)
        and not semantic_errors
        and all(audit["status"] == "PASS" for audit in audits)
        and language["status"] == "PASS"
        and support["status"] == "PASS"
        and all(item["accuracy"] <= 0.25 for item in shortcuts.values())
    )
    manifest_passed = not manifest_errors
    return {
        "status": "PASS" if manifest_passed and semantic_passed else "FAIL",
        "manifest_status": "PASS" if manifest_passed else "FAIL",
        "manifest_errors": manifest_errors,
        "semantic_errors": semantic_errors,
        "instances": len(audits),
        "passed_instances": sum(audit["status"] == "PASS" for audit in audits),
        "cross_instance_language": language,
        "public_shortcuts": shortcuts,
        "decisive_support": support,
    }


__all__ = ["PILOT_MATCH_IDS", "audit_release", "build_release"]
