from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


SAMPLE_MATCH_IDS = (
    "match_0021",
    "match_0066",
    "match_0067",
    "match_0162",
    "match_0220",
)

DEGENERATE_PATTERNS = {
    "entry_inside_entry": re.compile(r"\bThe entry in the [^.]{0,80}\bentry\b", re.I),
    "account_headed_notes": re.compile(r"\bThe account headed [^.]{0,100}\bnotes for\b", re.I),
    "missing_quotation_after_wording": re.compile(r"\bmaps the wording\s+(?!\")", re.I),
    "opaque_internal_identifier": re.compile(
        r"\b(?:r25fact|r25rule|r25shadow|r26bridge|r26authority|r26conflict)[A-Za-z0-9_:-]*\b",
        re.I,
    ),
    "machine_case_marker": re.compile(r"\b(?:CASE|OBS|PKT)-[A-Za-z0-9_-]+\b", re.I),
    "repeated_word": re.compile(r"\b([A-Za-z]{3,})\s+\1\b", re.I),
    "same_surname_delivery_label": re.compile(
        r"\bthe ([A-Z][A-Za-z'-]+)-\1 delivery\b"
    ),
}


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def audit_language_surface(
    release_dir: Path,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    findings: dict[str, list[dict[str, str]]] = {
        name: [] for name in DEGENERATE_PATTERNS
    }
    generated_texts: list[str] = []
    generated_nonrule_texts: list[str] = []
    generated_rule_texts: list[str] = []
    question_texts: list[str] = []
    missing_terminal_punctuation: list[str] = []
    unbalanced_quotes: list[str] = []
    samples: list[dict[str, Any]] = []
    role_counts: Counter[str] = Counter()
    for match_id in map(str, summary["match_ids"]):
        public = _read(release_dir / "public" / match_id / "public_instance.json")
        gold = _read(release_dir / "private" / match_id / "private_gold.json")
        evidence = _read(
            release_dir / "private" / match_id / "private_evidence.json"
        )
        text_by_id = {
            str(span["span_id"]): str(span["text"])
            for document in public["documents"]
            for span in document["spans"]
        }
        touched_ids = {
            str(patch.get("span_id", patch.get("inserted_span_id")))
            for patch in evidence.get("r26_text_patches", [])
        }
        claims = list(evidence.get("r25_evidence_claims", [])) + list(
            evidence.get("r26_evidence_claims", [])
        )
        claim_by_id = {
            str(claim.get("inserted_span_id")): claim for claim in claims
        }
        for span_id in sorted(touched_ids):
            text = text_by_id.get(span_id, "")
            if not text:
                continue
            generated_texts.append(text)
            role = str(claim_by_id.get(span_id, {}).get("role", "unregistered"))
            role_counts[role] += 1
            if role == "rule":
                generated_rule_texts.append(text)
            else:
                generated_nonrule_texts.append(text)
            if text[-1:] not in {".", "?", "!", '"', "'"}:
                missing_terminal_punctuation.append(f"{match_id}:{span_id}")
            if text.count('"') % 2:
                unbalanced_quotes.append(f"{match_id}:{span_id}")
            for name, pattern in DEGENERATE_PATTERNS.items():
                if pattern.search(text):
                    findings[name].append(
                        {"match_id": match_id, "span_id": span_id, "text": text}
                    )
        questions = {
            str(item["question_id"]): str(item["question"])
            for item in public["decision_question_schema"]
        }
        question_texts.extend(questions.values())
        for qid, text in questions.items():
            for name, pattern in DEGENERATE_PATTERNS.items():
                if pattern.search(text):
                    findings[name].append(
                        {"match_id": match_id, "span_id": qid, "text": text}
                    )
        if match_id in SAMPLE_MATCH_IDS:
            for answer in gold["decision_answers"]:
                qid = str(answer["question_id"])
                evidence_rows = []
                selected_ids = list(map(str, answer["minimum_evidence_spans"]))
                selected_ids.extend(map(str, answer.get("rejected_evidence_spans", [])))
                for span_id in selected_ids:
                    claim = claim_by_id.get(span_id, {})
                    role = str(claim.get("role", "unregistered"))
                    if span_id in set(map(str, answer.get("rejected_evidence_spans", []))):
                        role = "rejected_conflict"
                    evidence_rows.append(
                        {
                            "span_id": span_id,
                            "role": role,
                            "text": text_by_id.get(span_id, "<missing>"),
                        }
                    )
                samples.append(
                    {
                        "match_id": match_id,
                        "question_id": qid,
                        "level": str(answer["level"]),
                        "question": questions[qid],
                        "evidence": evidence_rows,
                    }
                )

    exact_generated_duplicates = len(generated_texts) - len(set(generated_texts))
    exact_nonrule_duplicates = len(generated_nonrule_texts) - len(
        set(generated_nonrule_texts)
    )
    exact_rule_duplicates = len(generated_rule_texts) - len(
        set(generated_rule_texts)
    )
    exact_question_duplicates = len(question_texts) - len(set(question_texts))
    gates = {
        "no_known_degenerate_frames": not any(findings.values()),
        "no_missing_terminal_punctuation": not missing_terminal_punctuation,
        "balanced_double_quotes": not unbalanced_quotes,
        "no_exact_question_duplicates": exact_question_duplicates == 0,
        # Governing law statements are intentionally shared premises and are
        # excluded from the no-template shortcut gate.  Identity, authority,
        # accepted-fact and conflict prose must remain unique.
        "no_exact_generated_nonrule_text_duplicates": exact_nonrule_duplicates == 0,
        "stratified_sample_has_five_matches_x_five_levels": len(samples) == 25
        and Counter(item["level"] for item in samples)
        == Counter({f"L{level}": 5 for level in range(1, 6)}),
    }
    report = {
        "protocol_version": "VETT-R26.13-LANGUAGE-SURFACE-AUDIT-1",
        "status": "AUTOMATED_PASS_HUMAN_REVIEW_REQUIRED"
        if all(gates.values())
        else "FAIL",
        "gates": gates,
        "matches": len(summary["match_ids"]),
        "questions": len(question_texts),
        "generated_spans": len(generated_texts),
        "generated_role_counts": dict(sorted(role_counts.items())),
        "exact_generated_text_duplicates": exact_generated_duplicates,
        "exact_generated_nonrule_text_duplicates": exact_nonrule_duplicates,
        "exact_generated_rule_text_duplicates": exact_rule_duplicates,
        "exact_question_duplicates": exact_question_duplicates,
        "known_degenerate_frame_counts": {
            name: len(rows) for name, rows in findings.items()
        },
        "diagnostic_examples": {
            name: rows[:5] for name, rows in findings.items() if rows
        },
        "sample_matches": list(SAMPLE_MATCH_IDS),
        "sample_questions": len(samples),
        "human_review_status": "NOT_RUN",
        "provider_requests_made": 0,
        "claim_boundary": (
            "Automated language checks detect known degeneration, punctuation and "
            "duplication. They do not establish human-perceived naturalness; the "
            "private stratified sample must be reviewed separately."
        ),
    }
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "LANGUAGE_SURFACE_AUDIT.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (output_dir / "PRIVATE_NATURALNESS_SAMPLE.json").write_text(
            json.dumps(samples, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        lines = [
            "# Private R26.13 naturalness sample",
            "",
            "This file contains private levels and evidence roles. Never provide it to a model under evaluation.",
            "",
        ]
        for sample in samples:
            lines.extend(
                [
                    f"## {sample['match_id']} · {sample['level']} · {sample['question_id']}",
                    "",
                    sample["question"],
                    "",
                ]
            )
            for row in sample["evidence"]:
                lines.append(f"- **{row['role']}** `{row['span_id']}` — {row['text']}")
            lines.append("")
        (output_dir / "PRIVATE_NATURALNESS_SAMPLE.md").write_text(
            "\n".join(lines), encoding="utf-8"
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-language-surface-audit")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_language_surface(args.release, args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["audit_language_surface"]
