#!/usr/bin/env python3
"""Audit the 220-match cricket text-to-table collection.

The script deliberately separates:
1. file/package integrity,
2. scorecard-internal cricket arithmetic,
3. text-to-scorecard recoverability,
4. duplication and construction artifacts.

It never edits source matches.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


INNINGS_RE = re.compile(
    r"^## (?P<team>.+?) - (?P<runs>\d+)(?:/(?P<wickets>\d+))? "
    r"\((?P<overs>\d+\.\d+) Overs\)$"
)
FOW_RE = re.compile(r"^(?P<score>\d+)/(?P<wicket>\d+)\((?P<over>\d+\.\d+)\)$")


@dataclass
class Innings:
    team: str
    runs: int
    wickets: int | None
    overs: str
    summary: dict[str, str] = field(default_factory=dict)
    tables: dict[str, list[dict[str, str]]] = field(default_factory=dict)


@dataclass
class MatchAudit:
    match_id: str
    file_complete: bool
    innings_count: int
    commentary_chars: int
    commentary_words: int
    commentary_paragraphs: int
    commentary_digit_tokens: int
    scorecard_chars: int
    evidence_chars: int
    construction_marker_count: int
    construction_markers: str
    commentary_construction_leak: bool
    evidence_uses_target_table: bool
    player_name_coverage: float | None
    batter_run_local_coverage: float | None
    exact_duplicate_group: str
    checks_total: int
    checks_failed: int
    strong_checks_failed: int
    failure_rate: float
    issue_codes: str
    recommended_action: str


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def to_balls(overs: str, balls_per_over: int = 6) -> int:
    overs = str(overs).strip()
    if "." not in overs:
        return int(overs) * balls_per_over
    whole, ball = overs.split(".", 1)
    remainder = int(ball)
    if remainder >= balls_per_over:
        raise ValueError(f"invalid over notation: {overs}")
    return int(whole) * balls_per_over + remainder


def parse_markdown_table(lines: list[str], start: int) -> tuple[list[dict[str, str]], int]:
    headers = [x.strip() for x in lines[start].strip().strip("|").split("|")]
    i = start + 2
    rows: list[dict[str, str]] = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        values = [x.strip() for x in lines[i].strip().strip("|").split("|")]
        if len(values) == len(headers):
            rows.append(dict(zip(headers, values)))
        i += 1
    return rows, i


def parse_scorecard(text: str) -> tuple[dict[str, str], list[Innings]]:
    lines = text.splitlines()
    match_meta: dict[str, str] = {}
    innings: list[Innings] = []
    current: Innings | None = None
    current_section = ""
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = INNINGS_RE.match(line)
        if m:
            current = Innings(
                team=m.group("team"),
                runs=int(m.group("runs")),
                wickets=int(m.group("wickets")) if m.group("wickets") else None,
                overs=m.group("overs"),
            )
            innings.append(current)
            current_section = "Summary"
            i += 1
            continue
        if line.startswith("## "):
            current = None
            current_section = ""
            i += 1
            continue
        if line.startswith("### "):
            current_section = line[4:].strip()
            i += 1
            continue
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|\s*---", lines[i + 1].strip()):
            rows, next_i = parse_markdown_table(lines, i)
            if current is None:
                if rows and set(rows[0]) == {"Field", "Value"}:
                    match_meta.update({r["Field"]: r["Value"] for r in rows})
            else:
                if rows and set(rows[0]) == {"Field", "Value"} and current_section == "Summary":
                    current.summary.update({r["Field"]: r["Value"] for r in rows})
                elif current_section:
                    current.tables[current_section] = rows
            i = next_i
            continue
        i += 1
    return match_meta, innings


def num(value: str | None) -> int | None:
    if value is None:
        return None
    value = value.strip()
    return int(value) if re.fullmatch(r"-?\d+", value) else None


def flt(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def close(a: float, b: float, tolerance: float = 0.011) -> bool:
    return abs(a - b) <= tolerance


def dismissal_is_out(text: str) -> bool:
    x = text.strip().lower()
    return bool(x) and x not in {"not out", "retired hurt", "absent hurt"}


def dismissal_bowler(text: str) -> str | None:
    x = text.strip()
    low = x.lower()
    if not x or "run out" in low or "retired" in low or "obstruct" in low:
        return None
    if low.startswith("lbw "):
        bowler = x[4:].strip()
        return re.sub(r"^b\s+", "", bowler, flags=re.I)
    m = re.search(r"\bb\s+(.+)$", x, flags=re.I)
    return m.group(1).strip() if m else None


def normalize_name(name: str) -> str:
    return re.sub(r"\s+\((?:c|wk|c/wk|wk/c)\)\s*$", "", name.strip(), flags=re.I)


def names_from_innings(innings: list[Innings]) -> set[str]:
    names: set[str] = set()
    for inn in innings:
        for row in inn.tables.get("Batting", []):
            if row.get("Batter"):
                names.add(normalize_name(row["Batter"]))
        for row in inn.tables.get("Bowling", []):
            if row.get("Bowler"):
                names.add(normalize_name(row["Bowler"]))
    return {n for n in names if n}


SMALL_NUMBERS = {
    0: ("zero", "nought", "duck"),
    1: ("one",),
    2: ("two",),
    3: ("three",),
    4: ("four",),
    5: ("five",),
    6: ("six",),
    7: ("seven",),
    8: ("eight",),
    9: ("nine",),
    10: ("ten",),
    11: ("eleven",),
    12: ("twelve",),
    13: ("thirteen",),
    14: ("fourteen",),
    15: ("fifteen",),
    16: ("sixteen",),
    17: ("seventeen",),
    18: ("eighteen",),
    19: ("nineteen",),
    20: ("twenty",),
    30: ("thirty",),
    40: ("forty",),
    50: ("fifty",),
    60: ("sixty",),
    70: ("seventy",),
    80: ("eighty",),
    90: ("ninety",),
}


def number_forms(n: int) -> set[str]:
    forms = {str(n)}
    if n in SMALL_NUMBERS:
        forms.update(SMALL_NUMBERS[n])
    elif 20 < n < 100:
        tens = (n // 10) * 10
        unit = n % 10
        if tens in SMALL_NUMBERS and unit in SMALL_NUMBERS:
            for t in SMALL_NUMBERS[tens][:1]:
                for u in SMALL_NUMBERS[unit][:1]:
                    forms.update({f"{t}-{u}", f"{t} {u}"})
    elif 100 <= n < 1000:
        h, rem = divmod(n, 100)
        for hword in SMALL_NUMBERS.get(h, (str(h),))[:1]:
            if rem == 0:
                forms.add(f"{hword} hundred")
            else:
                for r in number_forms(rem):
                    if not r.isdigit():
                        forms.update({f"{hword} hundred {r}", f"{hword} hundred and {r}"})
    return forms


def local_batter_run_supported(commentary: str, batter: str, runs: int) -> bool:
    low = commentary.lower()
    pos = low.find(batter.lower())
    if pos < 0:
        return False
    # Search all occurrences and a generous local context. This is an optimistic proxy.
    positions = [m.start() for m in re.finditer(re.escape(batter.lower()), low)]
    forms = number_forms(runs)
    for p in positions:
        context = low[max(0, p - 180) : min(len(low), p + len(batter) + 180)]
        for form in forms:
            if re.search(rf"(?<![\w]){re.escape(form)}(?![\w])", context):
                return True
    return False


def add_check(checks: list[tuple[str, bool, str]], code: str, passed: bool, detail: str) -> None:
    checks.append((code, bool(passed), detail))


def audit_innings(inn: Innings) -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    batting = inn.tables.get("Batting", [])
    bowling = inn.tables.get("Bowling", [])
    partnerships = inn.tables.get("Partnerships", [])
    fow = inn.tables.get("Fall of Wickets", [])
    extras = num(inn.summary.get("Total Extras"))
    byes = num(inn.summary.get("Byes"))
    leg_byes = num(inn.summary.get("Leg Byes"))
    no_balls = num(inn.summary.get("No Balls"))
    wides = num(inn.summary.get("Wides"))

    if batting and extras is not None:
        batter_runs = [num(r.get("R")) for r in batting]
        if all(x is not None for x in batter_runs):
            total = sum(x for x in batter_runs if x is not None) + extras
            add_check(checks, "BAT_PLUS_EXTRAS", total == inn.runs, f"{total} vs {inn.runs}")

    if extras is not None and None not in {byes, leg_byes, no_balls, wides}:
        parts = int(byes) + int(leg_byes) + int(no_balls) + int(wides)
        add_check(checks, "EXTRAS_BREAKDOWN", parts == extras, f"{parts} vs {extras}")

    if inn.summary.get("Total"):
        expected = f"{inn.runs}"
        add_check(
            checks,
            "HEADER_SUMMARY_TOTAL",
            inn.summary["Total"].startswith(expected),
            f"{inn.summary['Total']} vs header {inn.runs}",
        )

    if batting:
        outs = sum(dismissal_is_out(r.get("Dismissal", "")) for r in batting)
        expected_wkts = inn.wickets if inn.wickets is not None else 10
        add_check(checks, "DISMISSAL_WICKETS", outs == expected_wkts, f"{outs} vs {expected_wkts}")

        legal_balls = to_balls(inn.overs)
        batter_balls = [num(r.get("B")) for r in batting]
        if all(x is not None for x in batter_balls):
            faced = sum(x for x in batter_balls if x is not None)
            # Providers differ on whether a No ball is included in batter balls faced.
            # Accept both common conventions; anything else is still inconsistent.
            accepted = {legal_balls}
            if no_balls is not None:
                accepted.add(legal_balls + no_balls)
            add_check(checks, "BATTER_BALLS", faced in accepted, f"{faced} vs accepted {sorted(accepted)}")

        sr_bad = []
        for row in batting:
            r, b, sr = num(row.get("R")), num(row.get("B")), row.get("SR", "")
            if r is None or b is None:
                continue
            if b == 0:
                ok = sr in {"-", "", "0", "0.00"}
            else:
                val = flt(sr)
                ok = val is not None and close(val, round(100 * r / b, 2))
            if not ok:
                sr_bad.append(row.get("Batter", "?"))
        add_check(checks, "STRIKE_RATE", not sr_bad, ", ".join(sr_bad[:5]))

    if bowling:
        bowler_balls = []
        invalid_overs = []
        for row in bowling:
            try:
                bowler_balls.append(to_balls(row.get("O", "0.0")))
            except ValueError:
                invalid_overs.append(row.get("Bowler", "?"))
        add_check(checks, "BOWLING_OVER_NOTATION", not invalid_overs, ", ".join(invalid_overs))
        if not invalid_overs:
            actual = sum(bowler_balls)
            expected = to_balls(inn.overs)
            add_check(checks, "BOWLER_BALLS", actual == expected, f"{actual} vs {expected}")

        if byes is not None and leg_byes is not None:
            conceded = sum(num(r.get("R")) or 0 for r in bowling)
            expected = inn.runs - byes - leg_byes
            add_check(checks, "BOWLING_RUNS", conceded == expected, f"{conceded} vs {expected}")

        econ_bad = []
        for row in bowling:
            balls = to_balls(row.get("O", "0.0"))
            runs = num(row.get("R"))
            econ = flt(row.get("Econ"))
            if runs is None or econ is None or balls == 0:
                continue
            expected = round(runs * 6 / balls, 2)
            if not close(econ, expected):
                econ_bad.append(row.get("Bowler", "?"))
        add_check(checks, "ECONOMY", not econ_bad, ", ".join(econ_bad[:5]))

        credited = Counter()
        for row in batting:
            b = dismissal_bowler(row.get("Dismissal", ""))
            if b:
                credited[normalize_name(b)] += 1
        listed = {normalize_name(r.get("Bowler", "")): num(r.get("W")) or 0 for r in bowling}
        mismatches = []
        for bowler in set(credited) | set(listed):
            if credited.get(bowler, 0) != listed.get(bowler, 0):
                mismatches.append(f"{bowler}:{credited.get(bowler, 0)}/{listed.get(bowler, 0)}")
        add_check(checks, "BOWLER_WICKETS", not mismatches, ", ".join(mismatches[:6]))

    rr = flt(inn.summary.get("Run Rate"))
    if rr is not None:
        expected = round(inn.runs * 6 / to_balls(inn.overs), 2)
        add_check(checks, "RUN_RATE", close(rr, expected), f"{rr} vs {expected}")

    if partnerships:
        part_runs = [num(r.get("Runs")) for r in partnerships]
        if all(x is not None for x in part_runs):
            total = sum(x for x in part_runs if x is not None)
            add_check(checks, "PARTNERSHIP_TOTAL", total == inn.runs, f"{total} vs {inn.runs}")
            max_part = num(inn.summary.get("Max Partnership"))
            if max_part is not None:
                add_check(checks, "MAX_PARTNERSHIP", max(part_runs) == max_part, f"{max(part_runs)} vs {max_part}")
        component_bad = []
        for idx, row in enumerate(partnerships, 1):
            pr = num(row.get("Runs"))
            ex = num(row.get("Extras"))
            vals = []
            for col in ("Striker", "Non-striker"):
                m = re.match(r"^(\d+)\(", row.get(col, ""))
                vals.append(int(m.group(1)) if m else None)
            if pr is not None and ex is not None and all(v is not None for v in vals):
                if sum(v for v in vals if v is not None) + ex != pr:
                    component_bad.append(str(idx))
        add_check(checks, "PARTNERSHIP_COMPONENTS", not component_bad, ",".join(component_bad))

    if fow:
        parsed = []
        invalid = []
        for row in fow:
            m = FOW_RE.match(row.get("At", ""))
            if m:
                parsed.append((int(m.group("score")), int(m.group("wicket")), m.group("over")))
            elif not (inn.wickets == 0 and row.get("At", "") == "0"):
                invalid.append(row.get("At", ""))
        add_check(checks, "FOW_FORMAT", not invalid, ", ".join(invalid[:3]))
        if parsed:
            monotonic = all(
                parsed[i][0] >= parsed[i - 1][0] and parsed[i][1] == i + 1
                for i in range(1, len(parsed))
            ) and parsed[0][1] == 1
            add_check(checks, "FOW_MONOTONIC", monotonic, str(parsed[:3]))
            if partnerships:
                running = 0
                bad = []
                for i, row in enumerate(partnerships):
                    pr = num(row.get("Runs"))
                    if pr is None:
                        continue
                    running += pr
                    if i < len(parsed) and running != parsed[i][0]:
                        bad.append(f"{i+1}:{running}/{parsed[i][0]}")
                add_check(checks, "PARTNERSHIP_FOW", not bad, ", ".join(bad[:5]))

    return checks


def audit_match(meta: dict[str, str], innings: list[Innings]) -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    result = meta.get("Result", "").strip()
    names = names_from_innings(innings)
    pom = normalize_name(meta.get("Player of the Match", ""))
    pom = re.sub(r"\s+\([^)]*\)\s*$", "", pom).strip()
    if pom and pom.lower() not in {"not awarded", "none", "n/a"}:
        add_check(checks, "POM_IN_SCORECARD", pom in names, pom)

    is_adjusted = bool(re.search(r"\bD/?L(?:S)?\b|Duckworth", result, flags=re.I))
    if len(innings) >= 2 and not is_adjusted:
        m_runs = re.search(r"won by (\d+) runs?", result, flags=re.I)
        m_wkts = re.search(r"won by (\d+) wickets?", result, flags=re.I)
        m_innings = re.search(r"innings and (\d+) runs?", result, flags=re.I)
        if m_runs and len(innings) == 2:
            stated = int(m_runs.group(1))
            actual = innings[0].runs - innings[1].runs
            add_check(checks, "RESULT_RUN_MARGIN", stated == actual, f"{stated} vs {actual}")
        elif m_wkts and len(innings) == 2:
            stated = int(m_wkts.group(1))
            chase_wickets = innings[1].wickets
            actual = 10 - chase_wickets if chase_wickets is not None else None
            add_check(checks, "RESULT_WICKET_MARGIN", actual is not None and stated == actual, f"{stated} vs {actual}")
        elif m_innings and len(innings) == 3:
            stated = int(m_innings.group(1))
            actual = innings[1].runs - innings[0].runs - innings[2].runs
            add_check(checks, "RESULT_INNINGS_MARGIN", stated == actual, f"{stated} vs {actual}")
    return checks


def percentile(values: list[float], p: float) -> float:
    if not values:
        return math.nan
    values = sorted(values)
    k = (len(values) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - k) + values[hi] * (k - lo)


def write_csv(path: Path, rows: Iterable[dict]) -> None:
    rows = list(rows)
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    match_dirs = sorted(p for p in args.input.glob("match_*") if p.is_dir())
    required = {"commentary.txt", "scorecard.md", "evidence_chain.md", "meta.json"}
    records = []
    detail_rows = []
    issue_examples: dict[str, list[str]] = defaultdict(list)
    normalized_hash_groups: dict[str, list[str]] = defaultdict(list)
    raw_commentaries: dict[str, str] = {}
    parsed_cache: dict[str, tuple[dict[str, str], list[Innings]]] = {}

    for d in match_dirs:
        match_id = d.name
        files = {p.name for p in d.iterdir() if p.is_file()}
        complete = required <= files
        commentary = (d / "commentary.txt").read_text(encoding="utf-8") if (d / "commentary.txt").exists() else ""
        scorecard = (d / "scorecard.md").read_text(encoding="utf-8") if (d / "scorecard.md").exists() else ""
        evidence = (d / "evidence_chain.md").read_text(encoding="utf-8") if (d / "evidence_chain.md").exists() else ""
        raw_commentaries[match_id] = commentary
        meta, innings = parse_scorecard(scorecard)
        parsed_cache[match_id] = (meta, innings)
        normalized_scorecard = re.sub(r"^# match_\d+\s*", "# MATCH_ID\n", scorecard)
        normalized_hash_groups[sha256_text(normalized_scorecard)].append(match_id)

    duplicate_ids = {}
    duplicate_groups = []
    for group in normalized_hash_groups.values():
        if len(group) > 1:
            label = "+".join(group)
            duplicate_groups.append(group)
            for match_id in group:
                duplicate_ids[match_id] = label

    construction_terms = [
        "anonym",
        "rekey",
        "fingerprint",
        "original",
        "redesign",
        "synchron",
        "hidden evidence",
    ]

    all_check_rows = []
    for d in match_dirs:
        match_id = d.name
        files = {p.name for p in d.iterdir() if p.is_file()}
        commentary = raw_commentaries[match_id]
        scorecard = (d / "scorecard.md").read_text(encoding="utf-8")
        evidence = (d / "evidence_chain.md").read_text(encoding="utf-8")
        match_meta, innings = parsed_cache[match_id]
        checks = []
        for code, passed, detail in audit_match(match_meta, innings):
            checks.append((f"M_{code}", passed, detail))
            all_check_rows.append(
                {
                    "match_id": match_id,
                    "innings": 0,
                    "team": "",
                    "check": code,
                    "passed": int(passed),
                    "detail": detail,
                }
            )
            if not passed and len(issue_examples[code]) < 8:
                issue_examples[code].append(f"{match_id}: {detail}")
        for idx, inn in enumerate(innings, 1):
            for code, passed, detail in audit_innings(inn):
                checks.append((f"I{idx}_{code}", passed, detail))
                all_check_rows.append(
                    {
                        "match_id": match_id,
                        "innings": idx,
                        "team": inn.team,
                        "check": code,
                        "passed": int(passed),
                        "detail": detail,
                    }
                )
                if not passed and len(issue_examples[code]) < 8:
                    issue_examples[code].append(f"{match_id}/I{idx}: {detail}")

        names = names_from_innings(innings)
        name_hits = sum(bool(re.search(rf"\b{re.escape(n)}\b", commentary, flags=re.I)) for n in names)
        name_coverage = name_hits / len(names) if names else None

        batter_cells = []
        for inn in innings:
            for row in inn.tables.get("Batting", []):
                batter = normalize_name(row.get("Batter", ""))
                runs = num(row.get("R"))
                if batter and runs is not None and num(row.get("B")) != 0:
                    batter_cells.append(local_batter_run_supported(commentary, batter, runs))
        run_coverage = sum(batter_cells) / len(batter_cells) if batter_cells else None

        hit_terms = [t for t in construction_terms if t in evidence.lower()]
        failures = [code for code, passed, _ in checks if not passed]
        strong_failures = [code for code in failures if not code.endswith("_BATTER_BALLS")]
        commentary_leak = bool(
            re.search(r"\banonymized\b|\bsource game\b|\bscorecard fingerprint\b", commentary, flags=re.I)
        )
        evidence_uses_target = bool(
            re.search(
                r"direct[^\n|]*table|batting table|bowling table|partnership table",
                evidence,
                flags=re.I,
            )
        )
        duplicate_group = duplicate_ids.get(match_id, "")
        duplicate_members = duplicate_group.split("+") if duplicate_group else []
        if duplicate_members and match_id != sorted(duplicate_members)[0]:
            recommended_action = "EXCLUDE_DUPLICATE"
        elif commentary_leak:
            recommended_action = "REWRITE_INPUT_CONSTRUCTION_LEAK"
        elif strong_failures:
            recommended_action = "REPAIR_SCORECARD"
        elif failures:
            recommended_action = "REVIEW_BALL_ACCOUNTING"
        else:
            recommended_action = "AUTO_PASS_NEEDS_SUPPORT_AUDIT"
        paragraphs = [x for x in re.split(r"\n\s*\n", commentary.strip()) if x.strip()]
        records.append(
            MatchAudit(
                match_id=match_id,
                file_complete=required <= files,
                innings_count=len(innings),
                commentary_chars=len(commentary),
                commentary_words=len(re.findall(r"\b[\w'-]+\b", commentary)),
                commentary_paragraphs=len(paragraphs),
                commentary_digit_tokens=len(re.findall(r"\b\d+(?:\.\d+)?\b", commentary)),
                scorecard_chars=len(scorecard),
                evidence_chars=len(evidence),
                construction_marker_count=len(hit_terms),
                construction_markers=";".join(hit_terms),
                commentary_construction_leak=commentary_leak,
                evidence_uses_target_table=evidence_uses_target,
                player_name_coverage=round(name_coverage, 4) if name_coverage is not None else None,
                batter_run_local_coverage=round(run_coverage, 4) if run_coverage is not None else None,
                exact_duplicate_group=duplicate_group,
                checks_total=len(checks),
                checks_failed=len(failures),
                strong_checks_failed=len(strong_failures),
                failure_rate=round(len(failures) / len(checks), 4) if checks else 0.0,
                issue_codes=";".join(failures),
                recommended_action=recommended_action,
            )
        )

    # Lexical similarity is a diagnostic of near-duplication/template reuse.
    similarity_pairs = []
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        ids = [r.match_id for r in records]
        docs = [raw_commentaries[i] for i in ids]
        matrix = TfidfVectorizer(lowercase=True, ngram_range=(2, 3), min_df=1).fit_transform(docs)
        sim = cosine_similarity(matrix)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                if sim[i, j] >= 0.45:
                    similarity_pairs.append(
                        {"match_a": ids[i], "match_b": ids[j], "tfidf_bigram_trigram_cosine": round(float(sim[i, j]), 4)}
                    )
        similarity_pairs.sort(key=lambda x: x["tfidf_bigram_trigram_cosine"], reverse=True)
    except Exception as exc:  # pragma: no cover - diagnostic fallback
        similarity_pairs = [{"error": str(exc)}]

    rows = [asdict(r) for r in records]
    write_csv(args.output / "per_match_audit.csv", rows)
    write_csv(args.output / "check_details.csv", all_check_rows)
    if similarity_pairs:
        write_csv(args.output / "high_similarity_pairs.csv", similarity_pairs)

    checks_by_code = defaultdict(list)
    for row in all_check_rows:
        checks_by_code[row["check"]].append(bool(row["passed"]))
    check_summary = {
        code: {
            "n": len(vals),
            "failed": len(vals) - sum(vals),
            "failure_rate": round((len(vals) - sum(vals)) / len(vals), 4),
            "examples": issue_examples.get(code, []),
        }
        for code, vals in sorted(checks_by_code.items())
    }
    failure_rates = [r.failure_rate for r in records]
    name_cov = [r.player_name_coverage for r in records if r.player_name_coverage is not None]
    run_cov = [r.batter_run_local_coverage for r in records if r.batter_run_local_coverage is not None]
    paragraphs = Counter(r.commentary_paragraphs for r in records)
    report = {
        "collection": {
            "match_directories": len(match_dirs),
            "complete_match_packages": sum(r.file_complete for r in records),
            "parsed_innings": sum(r.innings_count for r in records),
            "unique_scorecards_after_id_normalization": len(normalized_hash_groups),
            "exact_duplicate_groups": duplicate_groups,
            "matches_with_construction_markers": sum(r.construction_marker_count > 0 for r in records),
            "commentaries_with_explicit_construction_leak": sum(r.commentary_construction_leak for r in records),
            "evidence_files_using_target_tables_as_evidence": sum(r.evidence_uses_target_table for r in records),
            "recommended_action_counts": dict(Counter(r.recommended_action for r in records)),
        },
        "commentary": {
            "chars": {
                "min": min(r.commentary_chars for r in records),
                "median": statistics.median(r.commentary_chars for r in records),
                "mean": round(statistics.mean(r.commentary_chars for r in records), 2),
                "max": max(r.commentary_chars for r in records),
            },
            "words": {
                "min": min(r.commentary_words for r in records),
                "median": statistics.median(r.commentary_words for r in records),
                "mean": round(statistics.mean(r.commentary_words for r in records), 2),
                "max": max(r.commentary_words for r in records),
            },
            "paragraph_count_distribution": dict(sorted(paragraphs.items())),
            "digit_tokens_median": statistics.median(r.commentary_digit_tokens for r in records),
        },
        "recoverability_proxies": {
            "player_name_coverage_mean": round(statistics.mean(name_cov), 4),
            "player_name_coverage_median": round(statistics.median(name_cov), 4),
            "batter_run_local_coverage_mean": round(statistics.mean(run_cov), 4),
            "batter_run_local_coverage_median": round(statistics.median(run_cov), 4),
            "note": "Optimistic local lexical proxies; they do not prove semantic entailment.",
        },
        "scorecard_checks": {
            "total_checks": sum(r.checks_total for r in records),
            "failed_checks": sum(r.checks_failed for r in records),
            "overall_failure_rate": round(sum(r.checks_failed for r in records) / sum(r.checks_total for r in records), 4),
            "matches_with_any_failure": sum(r.checks_failed > 0 for r in records),
            "per_match_failure_rate": {
                "median": round(statistics.median(failure_rates), 4),
                "p90": round(percentile(failure_rates, 0.9), 4),
                "max": round(max(failure_rates), 4),
            },
            "by_check": check_summary,
        },
        "similarity": {
            "pairs_at_or_above_0_45": len([x for x in similarity_pairs if "match_a" in x]),
            "top_pairs": [x for x in similarity_pairs[:20] if "match_a" in x],
            "method": "TF-IDF word bigram/trigram cosine on raw commentary.",
        },
    }
    (args.output / "audit_summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
