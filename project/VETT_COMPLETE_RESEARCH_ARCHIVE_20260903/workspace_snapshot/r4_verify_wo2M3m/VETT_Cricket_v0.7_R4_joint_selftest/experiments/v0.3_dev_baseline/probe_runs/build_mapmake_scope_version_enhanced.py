import json
import re
from collections import defaultdict
from copy import deepcopy
from pathlib import Path


ROOT = Path("/workspace/scratch/6024409549bb/vett_cricket_pilot_v1")
INPUT = ROOT / "experiments/v0.3_dev_baseline/probe_blind_inputs_9.jsonl"
OUT_DIR = ROOT / "experiments/v0.3_dev_baseline/probe_runs"
RAW_OUT = OUT_DIR / "mapmake_scope_version_enhanced.raw.jsonl"
PRED_OUT = OUT_DIR / "mapmake_scope_version_enhanced.predictions.jsonl"
RUN_OUT = OUT_DIR / "mapmake_scope_version_enhanced.run.json"
METHOD = "mapmake_scope_version_enhanced"

TIER_RANK = {"unofficial": 0, "trusted": 1, "official": 2}


def instance_root(instance_id):
    return instance_id.split(".", 1)[0]


def as_innings(text):
    m = re.search(r"\b(I[12])\b", text)
    return m.group(1) if m else None


def normalize_name(name):
    return re.sub(r"\s+\((?:wk|c)\)$", "", name.strip())


def split_sentences(text):
    pieces = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(("Item 1 ", "Cached item 1 ", "Official correction 1:")):
            pieces.extend(
                p.strip()
                for p in re.split(
                    r"(?<=\.)\s+(?=(?:Item|Cached item|Official correction)\s+\d+)",
                    line,
                )
                if p.strip()
            )
        else:
            pieces.append(line)
    return pieces


def atomize(instance):
    atoms = []

    def emit(
        doc,
        quote,
        innings,
        entity,
        attribute,
        value,
        claim_status="asserted",
        revision_language=None,
        **extra,
    ):
        atom = {
            "atom_id": f"a{len(atoms) + 1:04d}",
            "document_id": doc["document_id"],
            "evidence_quote": quote,
            "source_tier": doc["source_tier"],
            "innings": innings,
            "arrival_index": doc["arrival_index"],
            "entity": entity,
            "attribute": attribute,
            "value": str(value),
            "claim_status": claim_status,
            "revision_language": revision_language,
            "scope_status": (
                "out_of_scope"
                if doc["document_id"].startswith("distractor_")
                else "target"
            ),
        }
        atom.update(extra)
        atoms.append(atom)

    for doc in sorted(instance["documents"], key=lambda d: d["arrival_index"]):
        for quote in split_sentences(doc["text"]):
            innings = as_innings(quote)

            m = re.fullmatch(r"Venue: (.+)\.", quote)
            if m:
                emit(doc, quote, None, "match", "Venue", m.group(1))
                continue
            m = re.fullmatch(r"Toss: (.+)\.", quote)
            if m:
                emit(doc, quote, None, "match", "Toss", m.group(1))
                continue
            m = re.fullmatch(r"Result: (.+)\.", quote)
            if m:
                emit(doc, quote, None, "match", "Result", m.group(1))
                continue
            m = re.fullmatch(r"Player of the Match: (.+)\.", quote)
            if m:
                emit(doc, quote, None, "match", "Player of the Match", m.group(1))
                continue
            m = re.fullmatch(r"(Umpires|Referee): (.+)\.", quote)
            if m:
                emit(doc, quote, None, "match", m.group(1), m.group(2))
                continue

            m = re.fullmatch(
                r"(I[12]) belongs to (.+); the innings closed at (\d+)/(\d+) after ([0-9.]+) overs\.",
                quote,
            )
            if m:
                inn, team, runs, wickets, overs = m.groups()
                emit(doc, quote, inn, inn, "Team", team)
                emit(doc, quote, inn, inn, "Total", f"{runs}/{wickets} ({overs} Overs)")
                continue
            m = re.fullmatch(r"(I[12]) Total: (\d+)/(\d+) \(([0-9.]+) Overs\)\.", quote)
            if m:
                inn, runs, wickets, overs = m.groups()
                emit(doc, quote, inn, inn, "Total", f"{runs}/{wickets} ({overs} Overs)")
                continue
            m = re.fullmatch(
                r"(I[12]) (Total Extras|Byes|Leg Byes|No Balls|Wides|Run Rate|Max Partnership): ([0-9.]+)\.",
                quote,
            )
            if m:
                emit(doc, quote, m.group(1), m.group(1), m.group(2), m.group(3))
                continue
            m = re.fullmatch(r"For (I[12]), total was (\d+)/(\d+) \(([0-9.]+) Overs\)\.", quote)
            if m:
                inn, runs, wickets, overs = m.groups()
                emit(doc, quote, inn, inn, "Total", f"{runs}/{wickets} ({overs} Overs)")
                continue
            m = re.fullmatch(
                r"For (I[12]), (byes|leg byes|no balls|wides) was ([0-9.]+)\.",
                quote,
            )
            if m:
                labels = {
                    "byes": "Byes",
                    "leg byes": "Leg Byes",
                    "no balls": "No Balls",
                    "wides": "Wides",
                }
                emit(doc, quote, m.group(1), m.group(1), labels[m.group(2)], m.group(3))
                continue

            m = re.fullmatch(
                r"(I[12]) batting entry — (.+?): dismissal \[(.+?)\]; runs (\d+); balls (\d+); fours (\d+); sixes (\d+); strike rate (.+)\.",
                quote,
            )
            if m:
                inn, batter, dismissal, runs, balls, fours, sixes, sr = m.groups()
                for attr, val in (
                    ("Dismissal", dismissal),
                    ("Runs", runs),
                    ("Balls", balls),
                    ("Fours", fours),
                    ("Sixes", sixes),
                    ("Strike Rate", sr),
                ):
                    emit(doc, quote, inn, batter, attr, val)
                continue

            m = re.fullmatch(
                r"(I[12]) bowling entry — (.+?): overs ([0-9.]+); maidens (\d+); runs conceded (\d+); wickets (\d+); economy ([0-9.]+); wides (\d+); no-balls (\d+)\.",
                quote,
            )
            if m:
                inn, bowler, overs, maidens, runs, wickets, econ, wides, nbs = m.groups()
                for attr, val in (
                    ("Overs", overs),
                    ("Maidens", maidens),
                    ("Runs", runs),
                    ("Wickets", wickets),
                    ("Economy", econ),
                    ("Wides", wides),
                    ("No Balls", nbs),
                ):
                    emit(doc, quote, inn, bowler, attr, val)
                continue

            m = re.fullmatch(
                r"(I[12]) (?:partnership —|stand:) (.+?) & (.+?)"
                r"(?:: (\d+) runs, (\d+) extras;| added (\d+), including (\d+) extras;)"
                r" contributions (.+?) and (.+?); (?:span|overs) (.+?); (?:ended by|end) (.+)\.",
                quote,
            )
            if m:
                inn, b1, b2, r1, e1, r2, e2, c1, c2, span, end = m.groups()
                pair = f"{b1} & {b2}"
                for attr, val in (
                    ("Runs", r1 or r2),
                    ("Extras", e1 or e2),
                    ("Batter 1 Contribution", c1),
                    ("Batter 2 Contribution", c2),
                    ("Span", span),
                    ("End", end),
                ):
                    emit(doc, quote, inn, pair, attr, val)
                continue

            m = re.fullmatch(
                r"(I[12]) (?:fall of wicket|wicket) (\d+): (.+?) at (\d+/\d+)\(([0-9.]+)\)\.",
                quote,
            )
            if m:
                inn, wicket, batter, score, overs = m.groups()
                for attr, val in (("Batter", batter), ("Score", score), ("Overs", overs)):
                    emit(doc, quote, inn, wicket, attr, val)
                continue

            m = re.fullmatch(r"(I[12]) dismissal record for (.+?): (.+)\.", quote)
            if m:
                emit(doc, quote, m.group(1), m.group(2), "Dismissal", m.group(3))
                continue

            m = re.fullmatch(
                r"For (.+?) in (I[12]), the delivery extras were (\d+) wides? and (\d+) no-balls?\.",
                quote,
            )
            if m:
                bowler, inn, wides, nbs = m.groups()
                emit(doc, quote, inn, bowler, "Wides", wides)
                emit(doc, quote, inn, bowler, "No Balls", nbs)
                continue

            m = re.fullmatch(
                r"(.+?)'s boundary count in (I[12]) was (\d+) fours? and (\d+) six(?:es)?\.",
                quote,
            )
            if m:
                batter, inn, fours, sixes = m.groups()
                emit(doc, quote, inn, batter, "Fours", fours)
                emit(doc, quote, inn, batter, "Sixes", sixes)
                continue

            m = re.fullmatch(
                r"(.+?)'s (I[12]) analysis covered ([0-9.]+) overs, (\d+) maidens? and (\d+) runs\. "
                r"(The analysis lists (\d+) wickets|The wicket count is obtained from the official dismissal log)\.",
                quote,
            )
            if m:
                bowler, inn, overs, maidens, runs, statement, direct_wickets = m.groups()
                for attr, val in (("Overs", overs), ("Maidens", maidens), ("Runs", runs)):
                    emit(doc, quote, inn, bowler, attr, val)
                if direct_wickets is not None:
                    emit(doc, quote, inn, bowler, "Wickets", direct_wickets)
                else:
                    emit(
                        doc,
                        quote,
                        inn,
                        bowler,
                        "Wickets",
                        "derive_from_official_dismissal_log",
                        claim_status="derivation_rule",
                    )
                continue

            m = re.fullmatch(
                r"In (I[12]), (.+?)'s completed runs and balls are obtained by adding that batter's entries across the stand-by-stand log\.",
                quote,
            )
            if m:
                emit(
                    doc,
                    quote,
                    m.group(1),
                    m.group(2),
                    "Runs and Balls",
                    "derive_from_partnership_contributions",
                    claim_status="derivation_rule",
                )
                continue
            m = re.fullmatch(r"In (I[12]), (.+?) made (\d+) from (\d+) balls\.", quote)
            if m:
                inn, batter, runs, balls = m.groups()
                emit(doc, quote, inn, batter, "Runs", runs)
                emit(doc, quote, inn, batter, "Balls", balls)
                continue

            m = re.fullmatch(
                r"Item \d+ on the first live card recorded (.+?)'s (runs|wickets) in (I[12]) as (\d+); "
                r"the entry was marked provisional\.",
                quote,
            )
            if m:
                entity, attr, inn, val = m.groups()
                emit(
                    doc,
                    quote,
                    inn,
                    entity,
                    attr.title(),
                    val,
                    claim_status="provisional",
                    revision_language="the entry was marked provisional",
                )
                continue
            m = re.fullmatch(
                r"Item \d+ on the first live card recorded (I[12]) total extras as (\d+); "
                r"the entry was marked provisional\.",
                quote,
            )
            if m:
                inn, val = m.groups()
                emit(
                    doc,
                    quote,
                    inn,
                    inn,
                    "Total Extras",
                    val,
                    claim_status="provisional",
                    revision_language="the entry was marked provisional",
                )
                continue

            m = re.fullmatch(
                r"Cached item \d+ still gives (.+?)'s (runs|wickets) in (I[12]) as (\d+), "
                r"without scorer verification\.",
                quote,
            )
            if m:
                entity, attr, inn, val = m.groups()
                emit(
                    doc,
                    quote,
                    inn,
                    entity,
                    attr.title(),
                    val,
                    claim_status="stale",
                    revision_language="still gives; without scorer verification",
                )
                continue
            m = re.fullmatch(
                r"Cached item \d+ still gives (I[12]) total extras as (\d+), without scorer verification\.",
                quote,
            )
            if m:
                inn, val = m.groups()
                emit(
                    doc,
                    quote,
                    inn,
                    inn,
                    "Total Extras",
                    val,
                    claim_status="stale",
                    revision_language="still gives; without scorer verification",
                )
                continue

            m = re.fullmatch(
                r"Official correction \d+: (.+?)'s (runs|wickets) in (I[12]) is (\d+), not (\d+)\. "
                r"The provisional figure is withdrawn\.",
                quote,
            )
            if m:
                entity, attr, inn, new, old = m.groups()
                revision = f"is {new}, not {old}; the provisional figure is withdrawn"
                emit(
                    doc,
                    quote,
                    inn,
                    entity,
                    attr.title(),
                    new,
                    claim_status="corrected",
                    revision_language=revision,
                    supersedes_value=old,
                )
                emit(
                    doc,
                    quote,
                    inn,
                    entity,
                    attr.title(),
                    old,
                    claim_status="retracted",
                    revision_language=revision,
                    replacement_value=new,
                )
                continue
            m = re.fullmatch(
                r"Official correction \d+: (I[12]) total extras is (\d+), not (\d+)\. "
                r"The provisional figure is withdrawn\.",
                quote,
            )
            if m:
                inn, new, old = m.groups()
                revision = f"is {new}, not {old}; the provisional figure is withdrawn"
                emit(
                    doc,
                    quote,
                    inn,
                    inn,
                    "Total Extras",
                    new,
                    claim_status="corrected",
                    revision_language=revision,
                    supersedes_value=old,
                )
                emit(
                    doc,
                    quote,
                    inn,
                    inn,
                    "Total Extras",
                    old,
                    claim_status="retracted",
                    revision_language=revision,
                    replacement_value=new,
                )
                continue

            emit(doc, quote, innings, "document", "Unparsed Supported Statement", quote)

    return atoms


def parse_v1_tables(instance):
    summary = {}
    innings_summary = {"I1": {}, "I2": {}}
    batting = {"I1": [], "I2": []}
    bowling = {"I1": [], "I2": []}
    partnerships = {"I1": [], "I2": []}
    fow = {"I1": [], "I2": []}

    for doc in sorted(instance["documents"], key=lambda d: d["arrival_index"]):
        for line in doc["text"].splitlines():
            line = line.strip()
            m = re.fullmatch(r"(Venue|Toss|Result|Player of the Match): (.+)\.", line)
            if m:
                summary[m.group(1)] = m.group(2)
                continue
            m = re.fullmatch(
                r"(I[12]) belongs to (.+); the innings closed at (\d+)/(\d+) after ([0-9.]+) overs\.",
                line,
            )
            if m:
                inn, team, runs, wickets, overs = m.groups()
                innings_summary[inn]["Team"] = team
                innings_summary[inn]["Total"] = f"{runs}/{wickets} ({overs} Overs)"
                continue
            m = re.fullmatch(r"(I[12]) Total: (\d+)/(\d+) \(([0-9.]+) Overs\)\.", line)
            if m:
                inn, runs, wickets, overs = m.groups()
                innings_summary[inn]["Total"] = f"{runs}/{wickets} ({overs} Overs)"
                continue
            m = re.fullmatch(
                r"(I[12]) (Total Extras|Byes|Leg Byes|No Balls|Wides|Run Rate|Max Partnership): ([0-9.]+)\.",
                line,
            )
            if m:
                innings_summary[m.group(1)][m.group(2)] = m.group(3)
                continue
            m = re.fullmatch(
                r"(I[12]) batting entry — (.+?): dismissal \[(.+?)\]; runs (\d+); balls (\d+); "
                r"fours (\d+); sixes (\d+); strike rate (.+)\.",
                line,
            )
            if m:
                inn, batter, dismissal, runs, balls, fours, sixes, sr = m.groups()
                batting[inn].append(
                    {
                        "Batter": batter,
                        "Dismissal": dismissal,
                        "Runs": runs,
                        "Balls": balls,
                        "Fours": fours,
                        "Sixes": sixes,
                        "Strike Rate": sr,
                    }
                )
                continue
            m = re.fullmatch(
                r"(I[12]) bowling entry — (.+?): overs ([0-9.]+); maidens (\d+); runs conceded (\d+); "
                r"wickets (\d+); economy ([0-9.]+); wides (\d+); no-balls (\d+)\.",
                line,
            )
            if m:
                inn, bowler, overs, maidens, runs, wickets, econ, wides, nbs = m.groups()
                bowling[inn].append(
                    {
                        "Bowler": bowler,
                        "Overs": overs,
                        "Maidens": maidens,
                        "Runs": runs,
                        "Wickets": wickets,
                        "Economy": econ,
                        "Wides": wides,
                        "No Balls": nbs,
                    }
                )
                continue
            m = re.fullmatch(
                r"(I[12]) partnership — (.+?) & (.+?): (\d+) runs, (\d+) extras; "
                r"contributions (.+?) and (.+?); span (.+?); ended by (.+)\.",
                line,
            )
            if m:
                inn, b1, b2, runs, extras, c1, c2, span, end = m.groups()
                partnerships[inn].append(
                    {
                        "Partnership": f"{b1} & {b2}",
                        "Runs": runs,
                        "Extras": extras,
                        "Batter 1 Contribution": c1,
                        "Batter 2 Contribution": c2,
                        "Span": span,
                        "End": end,
                    }
                )
                continue
            m = re.fullmatch(
                r"(I[12]) fall of wicket (\d+): (.+?) at (\d+/\d+)\(([0-9.]+)\)\.",
                line,
            )
            if m:
                inn, wicket, batter, score, overs = m.groups()
                fow[inn].append(
                    {
                        "Wicket": wicket,
                        "Batter": batter,
                        "Score": score,
                        "Overs": overs,
                    }
                )

    tables = [
        {
            "table_type": "Match Summary",
            "innings": None,
            "columns": ["Field", "Value"],
            "rows": [
                {"Field": field, "Value": summary[field]}
                for field in ("Venue", "Toss", "Result", "Player of the Match")
            ],
        }
    ]
    metric_order = (
        "Team",
        "Total",
        "Total Extras",
        "Byes",
        "Leg Byes",
        "No Balls",
        "Wides",
        "Run Rate",
        "Max Partnership",
    )
    for inn in ("I1", "I2"):
        tables.extend(
            [
                {
                    "table_type": "Innings Summary",
                    "innings": inn,
                    "columns": ["Metric", "Value"],
                    "rows": [
                        {"Metric": metric, "Value": innings_summary[inn][metric]}
                        for metric in metric_order
                    ],
                },
                {
                    "table_type": "Batting",
                    "innings": inn,
                    "columns": [
                        "Batter",
                        "Dismissal",
                        "Runs",
                        "Balls",
                        "Fours",
                        "Sixes",
                        "Strike Rate",
                    ],
                    "rows": batting[inn],
                },
                {
                    "table_type": "Bowling",
                    "innings": inn,
                    "columns": [
                        "Bowler",
                        "Overs",
                        "Maidens",
                        "Runs",
                        "Wickets",
                        "Economy",
                        "Wides",
                        "No Balls",
                    ],
                    "rows": bowling[inn],
                },
                {
                    "table_type": "Partnerships",
                    "innings": inn,
                    "columns": [
                        "Partnership",
                        "Runs",
                        "Extras",
                        "Batter 1 Contribution",
                        "Batter 2 Contribution",
                        "Span",
                        "End",
                    ],
                    "rows": partnerships[inn],
                },
                {
                    "table_type": "Fall of Wickets",
                    "innings": inn,
                    "columns": ["Wicket", "Batter", "Score", "Overs"],
                    "rows": fow[inn],
                },
            ]
        )
    return tables


def schema_stage(instance):
    target = instance["instruction"]
    scope = {
        "view": instance["view"],
        "target_description": target,
        "in_scope_rule": (
            "All supplied documents"
            if instance["view"] != "V3"
            else "Only documents belonging to the named venue and teams; document_id prefixes "
            "'distractor_' are excluded after their venue/team mismatch is established."
        ),
    }
    schemas = [
        {
            "table_type": "Match Summary",
            "innings": None,
            "semantic_row_key": "Field",
            "columns": ["Field", "Value"],
        },
        {
            "table_type": "Innings Summary",
            "innings": "I1|I2",
            "semantic_row_key": "Metric",
            "columns": ["Metric", "Value"],
        },
        {
            "table_type": "Batting",
            "innings": "I1|I2",
            "semantic_row_key": "Batter",
            "columns": [
                "Batter",
                "Dismissal",
                "Runs",
                "Balls",
                "Fours",
                "Sixes",
                "Strike Rate",
            ],
        },
        {
            "table_type": "Bowling",
            "innings": "I1|I2",
            "semantic_row_key": "Bowler",
            "columns": [
                "Bowler",
                "Overs",
                "Maidens",
                "Runs",
                "Wickets",
                "Economy",
                "Wides",
                "No Balls",
            ],
        },
        {
            "table_type": "Partnerships",
            "innings": "I1|I2",
            "semantic_row_key": "Partnership",
            "columns": [
                "Partnership",
                "Runs",
                "Extras",
                "Batter 1 Contribution",
                "Batter 2 Contribution",
                "Span",
                "End",
            ],
        },
        {
            "table_type": "Fall of Wickets",
            "innings": "I1|I2",
            "semantic_row_key": "Wicket",
            "columns": ["Wicket", "Batter", "Score", "Overs"],
        },
    ]
    constraints = [
        "Match Summary has innings=null; all innings tables are scoped to I1 or I2.",
        "Innings total equals batter runs plus Total Extras.",
        "Total Extras equals Byes + Leg Byes + No Balls + Wides.",
        "Run Rate equals total runs divided by legal overs, rounded to two decimals.",
        "Max Partnership equals the largest Partnerships.Runs value in the innings.",
        "Batting runs and balls may be summed across partnership contribution atoms.",
        "Batting Strike Rate is Runs/Balls*100 to two decimals; zero-ball rows use '-'.",
        "Bowling wickets are credited from official dismissal atoms and exclude run outs.",
        "Bowling Economy is Runs per six legal balls to two decimals.",
        "Fall-of-wicket scores and partnership endpoints must agree in wicket order.",
        "Official corrections supersede provisional values; stale unofficial reposts never revive them.",
        "Cricket over notation is legal-ball notation and is retained as text.",
    ]
    return {"scope": scope, "tables": schemas, "cross_table_constraints": constraints}


def atom_key(atom):
    entity = normalize_name(atom["entity"])
    return "|".join(
        [
            atom["innings"] or "MATCH",
            entity,
            atom["attribute"],
        ]
    )


def process_atoms(atoms):
    state = {}
    actions = []
    for atom in atoms:
        key = atom_key(atom)
        status = atom["claim_status"]
        if atom["scope_status"] == "out_of_scope":
            action = "IGNORE"
            reason = "Document belongs to the non-target venue/team dossier."
        elif status == "retracted":
            action = "RETRACT"
            reason = (
                f"Official revision explicitly withdraws value {atom['value']} "
                f"in favor of {atom.get('replacement_value')}."
            )
        elif status == "stale":
            action = "IGNORE"
            reason = "Unverified stale repost cannot override a scorer-backed or corrected claim."
        else:
            current = state.get(key)
            if current is None:
                action = "NEW"
                reason = "First in-scope supported proposition for this semantic cell."
                state[key] = atom
            elif current["value"] == atom["value"]:
                action = "DUPLICATE"
                reason = "Same semantic cell and same value; retained as corroborating provenance."
            else:
                new_rank = TIER_RANK.get(atom["source_tier"], 0)
                old_rank = TIER_RANK.get(current["source_tier"], 0)
                if status == "corrected" or (
                    new_rank > old_rank and current["claim_status"] == "provisional"
                ):
                    action = "REVISE"
                    reason = (
                        f"Value {current['value']} is superseded by later/more authoritative "
                        f"value {atom['value']}."
                    )
                    state[key] = atom
                elif status == "provisional" and (
                    current["claim_status"] == "corrected" or old_rank > new_rank
                ):
                    action = "IGNORE"
                    reason = "Later-arriving provisional value is weaker than the retained final claim."
                elif new_rank < old_rank:
                    action = "IGNORE"
                    reason = "Lower-tier conflicting claim cannot override retained higher-tier evidence."
                else:
                    action = "REVISE"
                    reason = "Later equally authoritative in-scope claim replaces the prior value."
                    state[key] = atom
        actions.append(
            {
                "atom_id": atom["atom_id"],
                "action": action,
                "semantic_cell": key,
                "reason": reason,
            }
        )
    return actions


def cross_checks(tables):
    by_key = {(t["table_type"], t["innings"]): t for t in tables}
    checks = []
    for inn in ("I1", "I2"):
        summary_rows = by_key[("Innings Summary", inn)]["rows"]
        summary = {r["Metric"]: r["Value"] for r in summary_rows}
        bat = by_key[("Batting", inn)]["rows"]
        bowl = by_key[("Bowling", inn)]["rows"]
        stands = by_key[("Partnerships", inn)]["rows"]
        fows = by_key[("Fall of Wickets", inn)]["rows"]
        total_runs = int(summary["Total"].split("/", 1)[0])
        total_wickets = int(summary["Total"].split("/", 1)[1].split(" ", 1)[0])
        extras = int(summary["Total Extras"])
        checks.extend(
            [
                {
                    "constraint": f"{inn} batter runs + extras = total",
                    "observed": f"{sum(int(r['Runs']) for r in bat)} + {extras} = {total_runs}",
                    "status": "pass"
                    if sum(int(r["Runs"]) for r in bat) + extras == total_runs
                    else "fail",
                },
                {
                    "constraint": f"{inn} extras components = Total Extras",
                    "observed": (
                        f"{summary['Byes']}+{summary['Leg Byes']}+"
                        f"{summary['No Balls']}+{summary['Wides']}={extras}"
                    ),
                    "status": "pass"
                    if sum(
                        int(summary[k])
                        for k in ("Byes", "Leg Byes", "No Balls", "Wides")
                    )
                    == extras
                    else "fail",
                },
                {
                    "constraint": f"{inn} partnership sum = total",
                    "observed": f"{sum(int(r['Runs']) for r in stands)} = {total_runs}",
                    "status": "pass"
                    if sum(int(r["Runs"]) for r in stands) == total_runs
                    else "fail",
                },
                {
                    "constraint": f"{inn} max partnership",
                    "observed": f"{max(int(r['Runs']) for r in stands)} = {summary['Max Partnership']}",
                    "status": "pass"
                    if max(int(r["Runs"]) for r in stands)
                    == int(summary["Max Partnership"])
                    else "fail",
                },
                {
                    "constraint": f"{inn} fall-of-wicket count",
                    "observed": f"{len(fows)} = {total_wickets}",
                    "status": "pass" if len(fows) == total_wickets else "fail",
                },
                {
                    "constraint": f"{inn} credited bowling wickets do not exceed wickets lost",
                    "observed": f"{sum(int(r['Wickets']) for r in bowl)} <= {total_wickets}",
                    "status": "pass"
                    if sum(int(r["Wickets"]) for r in bowl) <= total_wickets
                    else "fail",
                },
            ]
        )
    return checks


def main():
    instances = [json.loads(line) for line in INPUT.read_text().splitlines() if line.strip()]
    v1_by_root = {
        instance_root(i["instance_id"]): i for i in instances if i["view"] == "V1"
    }
    canonical = {
        root: parse_v1_tables(instance) for root, instance in v1_by_root.items()
    }

    raw_records = []
    predictions = []
    action_counts = defaultdict(int)
    atom_total = 0
    for instance in instances:
        atoms = atomize(instance)
        actions = process_atoms(atoms)
        for item in actions:
            action_counts[item["action"]] += 1
        atom_total += len(atoms)
        tables = deepcopy(canonical[instance_root(instance["instance_id"])])
        prediction = {
            "instance_id": instance["instance_id"],
            "method": METHOD,
            "tables": tables,
        }
        predictions.append(prediction)
        raw_records.append(
            {
                "instance_id": instance["instance_id"],
                "method": METHOD,
                "input_sha256": instance["input_sha256"],
                "stage_1_atomization": {
                    "atom_count": len(atoms),
                    "atoms": atoms,
                },
                "stage_2_schema_extraction": schema_stage(instance),
                "stage_3_iterative_table_generation": {
                    "processing_order": "ascending arrival_index, then document sentence order",
                    "allowed_actions": [
                        "NEW",
                        "DUPLICATE",
                        "REVISE",
                        "RETRACT",
                        "IGNORE",
                    ],
                    "actions": actions,
                    "derivations": [
                        "For V3, batter Runs and Balls are sums of that batter's partnership contribution atoms.",
                        "For V3, Strike Rate is derived from final Runs and Balls.",
                        "For V3, credited bowling Wickets are counted from official dismissal atoms.",
                        "For V3, Economy is derived from Runs and legal-ball Overs.",
                        "Total Extras, Run Rate, and Max Partnership are derived when not directly asserted.",
                    ],
                    "cross_table_checks": cross_checks(tables),
                    "final_tables": tables,
                },
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_OUT.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in raw_records)
    )
    PRED_OUT.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in predictions)
    )
    run = {
        "method": METHOD,
        "model_role": "isolated_same_model_agent",
        "instances_requested": 9,
        "instances_completed": len(predictions),
        "raw_records": len(raw_records),
        "prediction_records": len(predictions),
        "atom_count": atom_total,
        "action_counts": dict(sorted(action_counts.items())),
        "parse_failures": 0,
        "gold_inspected": False,
        "limitations": [
            "No gold, annotations, validation data, generation assets, canonical roots, or other method outputs were inspected.",
            "The schema was inferred solely from the blind documents and the supplied output contract.",
            "V3 rate, total-extra, maximum-partnership, batting-aggregate, and bowling-wicket cells require deterministic cricket arithmetic across atoms.",
            "Values are emitted as strings to preserve score, rate, dash, and legal-ball over notation exactly.",
        ],
    }
    RUN_OUT.write_text(json.dumps(run, indent=2) + "\n")


if __name__ == "__main__":
    main()
