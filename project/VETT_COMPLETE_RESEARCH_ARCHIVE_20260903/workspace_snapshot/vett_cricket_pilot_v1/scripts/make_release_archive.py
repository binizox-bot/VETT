#!/usr/bin/env python3
"""Create a checksummed VETT-Cricket candidate archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


def included(path: Path) -> bool:
    return (
        path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
        and path.name != "CHECKSUMS.sha256"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--archive-root", default="VETT_Cricket_Candidate_v0.3_high_audit")
    args = parser.parse_args()

    files = sorted(path for path in args.source.rglob("*") if included(path))
    checksums = []
    for path in files:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        checksums.append(f"{digest}  {path.relative_to(args.source).as_posix()}")
    checksum_path = args.source / "CHECKSUMS.sha256"
    checksum_path.write_text("\n".join(checksums) + "\n", encoding="utf-8")
    files.append(checksum_path)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files):
            arcname = f"{args.archive_root}/{path.relative_to(args.source).as_posix()}"
            archive.write(path, arcname)

    with zipfile.ZipFile(args.output) as archive:
        bad_member = archive.testzip()
        members = len(archive.infolist())
    result = {
        "archive": str(args.output),
        "files": members,
        "bytes": args.output.stat().st_size,
        "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "zip_crc_status": "PASS" if bad_member is None else f"FAIL:{bad_member}",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
