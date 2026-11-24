from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from .answer_blind_release import build_answer_blind_shadow


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_answer_blind_determinism(
    parent_release: Path,
    candidate_release: Path,
    output_path: Path | None = None,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="vett_r26_14_rebuild_") as directory:
        rebuild = Path(directory) / "candidate"
        build_answer_blind_shadow(parent_release, rebuild)
        candidate_files = {
            path.relative_to(candidate_release).as_posix(): path
            for path in candidate_release.rglob("*")
            if path.is_file()
        }
        rebuild_files = {
            path.relative_to(rebuild).as_posix(): path
            for path in rebuild.rglob("*")
            if path.is_file()
        }
        shared = sorted(set(candidate_files) & set(rebuild_files))
        mismatches = [
            name
            for name in shared
            if candidate_files[name].read_bytes() != rebuild_files[name].read_bytes()
        ]
        missing = sorted(set(candidate_files) - set(rebuild_files))
        extra = sorted(set(rebuild_files) - set(candidate_files))
        candidate_manifest = candidate_release / "MANIFEST.json"
        rebuild_manifest = rebuild / "MANIFEST.json"
        report = {
            "protocol_version": "VETT-R26.14-BYTE-REBUILD-1",
            "status": "PASS" if not (mismatches or missing or extra) else "FAIL",
            "candidate_files": len(candidate_files),
            "rebuild_files": len(rebuild_files),
            "shared_files": len(shared),
            "byte_mismatch_count": len(mismatches),
            "missing_file_count": len(missing),
            "extra_file_count": len(extra),
            "mismatch_examples": mismatches[:20],
            "missing_examples": missing[:20],
            "extra_examples": extra[:20],
            "candidate_manifest_sha256": _sha256(candidate_manifest),
            "rebuild_manifest_sha256": _sha256(rebuild_manifest),
            "manifest_byte_identical": candidate_manifest.read_bytes()
            == rebuild_manifest.read_bytes(),
            "provider_requests_made": 0,
            "claim_boundary": (
                "A fresh temporary build is byte-compared against the candidate. "
                "This verifies deterministic construction, not empirical difficulty."
            ),
        }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-answer-blind-determinism")
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(
        verify_answer_blind_determinism(
            args.parent, args.candidate, args.output
        ),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()


__all__ = ["verify_answer_blind_determinism"]
