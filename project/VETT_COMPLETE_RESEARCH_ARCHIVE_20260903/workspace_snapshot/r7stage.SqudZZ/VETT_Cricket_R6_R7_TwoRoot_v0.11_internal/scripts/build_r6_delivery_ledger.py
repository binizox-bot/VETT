#!/usr/bin/env python3
"""Synthesize a delivery ledger that exactly aggregates to one canonical scorecard.

R6 starts with a single short-format root. The ledger is synthetic and private;
its purpose is to support event-level text generation without verbalizing table
rows. The MILP enforces batting, bowling, extras, partnerships and wicket states.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix


DEFAULT_ROOT_ID = "match_0095"
RUN_TOKENS = [
    ("dot", 0, 0, 0),
    ("one", 1, 0, 0),
    ("two", 2, 0, 0),
    ("three", 3, 0, 0),
    ("four", 4, 1, 0),
    ("five", 5, 0, 0),
    ("six", 6, 0, 1),
    ("seven", 7, 0, 0),
    # Some source cards contain eight credited runs from a one-ball, one-six
    # component. Preserve the source as a six plus completed overthrows.
    ("six_plus_two", 8, 0, 1),
]


def canon(name: str) -> str:
    value = re.sub(r"\s*\((?:c|wk|c\)\(wk|C Sub|Sub)\)\s*", " ", name, flags=re.I)
    value = value.replace("(c)(wk)", "").replace("(wk)", "").replace("(c)", "")
    return re.sub(r"\s+", " ", value).strip()


def table_of(root: dict[str, Any], iid: str, table_type: str) -> dict[str, Any]:
    return next(t for t in root["tables"] if t.get("innings_id") == iid and t["table_type"] == table_type)


def parse_component(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(-?\d+)\((\d+)\)\s*", str(value))
    if not match:
        raise ValueError(f"Bad partnership component: {value!r}")
    return int(match.group(1)), int(match.group(2))


def ball_index(notation: str) -> int:
    over, ball = notation.split(".")
    return int(over) * 6 + int(ball)


def notation(index: int) -> str:
    return f"{(index - 1) // 6}.{(index - 1) % 6 + 1}"


def credited_bowler(dismissal: str) -> str | None:
    lower = dismissal.lower().strip()
    if not lower or lower == "not out" or lower.startswith("run out"):
        return None
    if " b " in dismissal:
        return dismissal.rsplit(" b ", 1)[1].strip()
    if lower.startswith("b "):
        return dismissal[2:].strip()
    if lower.startswith("lbw "):
        return dismissal[4:].strip()
    raise ValueError(f"Cannot identify credited bowler: {dismissal}")


def partnership_specs(root: dict[str, Any], iid: str) -> list[dict[str, Any]]:
    partnerships = table_of(root, iid, "Partnerships")
    specs = []
    for pos, row in enumerate(partnerships["rows"]):
        first, second = [canon(x) for x in row["Partnership"].split(" & ", 1)]
        first_runs, first_balls = parse_component(row["Striker"])
        second_runs, second_balls = parse_component(row["Non-striker"])
        start, end = row["Overs"].split("-")
        start_index, end_index = ball_index(start), ball_index(end)
        if end_index - start_index + 1 != first_balls + second_balls:
            raise ValueError(f"Partnership ball mismatch {iid}/{row['Partnership']}")
        if first_runs + second_runs + int(row["Extras"]) != int(row["Runs"]):
            raise ValueError(f"Partnership run mismatch {iid}/{row['Partnership']}")
        specs.append({
            "partnership_id": f"{iid}.P{pos+1:02d}",
            "row": row,
            "first": first,
            "second": second,
            "first_runs": first_runs,
            "first_balls": first_balls,
            "second_runs": second_runs,
            "second_balls": second_balls,
            "start": start_index,
            "end": end_index,
            "extras": int(row["Extras"]),
            "runs": int(row["Runs"]),
        })
    return specs


def fow_specs(root: dict[str, Any], iid: str) -> list[dict[str, Any]]:
    batting = table_of(root, iid, "Batting")
    batting_by_name = {canon(row["Batter"]): row for row in batting["rows"]}
    fow = table_of(root, iid, "Fall of Wickets")
    result = []
    for row in fow["rows"]:
        match = re.fullmatch(r"(\d+)/(\d+)\((\d+\.\d+)\)", row["At"])
        if not match:
            raise ValueError(f"Bad FOW: {row['At']}")
        batter = canon(row["Batter"])
        batting_row = batting_by_name[batter]
        result.append({
            "wicket": int(row["Wkt"]),
            "score": int(match.group(1)),
            "slot": ball_index(match.group(3)),
            "batter": batter,
            "dismissal": batting_row["Dismissal"],
            "credited_bowler": credited_bowler(batting_row["Dismissal"]),
        })
    return result


def feasible_schedules(root: dict[str, Any], iid: str) -> Iterable[dict[int, str]]:
    innings = next(x for x in root["innings"] if x["innings_id"] == iid)
    n_overs = math.ceil(innings["legal_balls"] / 6)
    bowling = table_of(root, iid, "Bowling")
    counts = {}
    partial_owners = []
    for row in bowling["rows"]:
        value = str(row["O"])
        if "." in value:
            overs, balls = value.split(".", 1)
            legal_balls = int(overs) * 6 + int(balls)
        else:
            legal_balls = int(value) * 6
        counts[row["Bowler"]] = math.ceil(legal_balls / 6)
        if legal_balls % 6:
            partial_owners.append((row["Bowler"], legal_balls % 6))
    if sum(
        (int(str(row["O"]).split(".")[0]) * 6 + int(str(row["O"]).split(".")[1]))
        if "." in str(row["O"]) else int(row["O"]) * 6
        for row in bowling["rows"]
    ) != innings["legal_balls"]:
        raise ValueError(f"Bowler balls do not sum to innings balls for {iid}")
    expected_remainder = innings["legal_balls"] % 6
    if expected_remainder:
        if len(partial_owners) != 1 or partial_owners[0][1] != expected_remainder:
            raise ValueError(f"Invalid partial spell ownership for {iid}: {partial_owners}")
    elif partial_owners:
        raise ValueError(f"Unexpected partial spell in complete innings {iid}: {partial_owners}")
    fixed: dict[int, str] = {}
    for wicket in fow_specs(root, iid):
        bowler = wicket["credited_bowler"]
        if bowler is None:
            continue
        over = (wicket["slot"] - 1) // 6
        if over in fixed and fixed[over] != bowler:
            raise ValueError(f"Conflicting wicket owners in over {over}: {fixed[over]} vs {bowler}")
        fixed[over] = bowler
    if expected_remainder:
        partial_bowler = partial_owners[0][0]
        final_over = n_overs - 1
        if final_over in fixed and fixed[final_over] != partial_bowler:
            raise ValueError(f"Final partial over owner conflicts with wicket owner in {iid}")
        fixed[final_over] = partial_bowler
    remaining = Counter(counts)
    for bowler in fixed.values():
        remaining[bowler] -= 1
    if any(v < 0 for v in remaining.values()):
        raise ValueError(f"Fixed wicket overs exceed spell: {remaining}")
    for over in range(n_overs - 1):
        if fixed.get(over) is not None and fixed.get(over) == fixed.get(over + 1):
            raise ValueError(f"Source requires consecutive overs by {fixed[over]} at {over}/{over+1}")

    schedule: dict[int, str] = dict(fixed)
    open_overs = [over for over in range(n_overs) if over not in fixed]

    def rec(pos: int) -> Iterable[dict[int, str]]:
        if pos == len(open_overs):
            if all(v == 0 for v in remaining.values()):
                yield dict(schedule)
            return
        over = open_overs[pos]
        for bowler in sorted(remaining):
            if remaining[bowler] <= 0:
                continue
            # Standard-over realism: avoid consecutive overs by one bowler.
            if schedule.get(over - 1) == bowler or fixed.get(over + 1) == bowler:
                continue
            remaining[bowler] -= 1
            schedule[over] = bowler
            yield from rec(pos + 1)
            del schedule[over]
            remaining[bowler] += 1

    yield from rec(0)


class Model:
    def __init__(self) -> None:
        self.keys: list[tuple[Any, ...]] = []
        self.index: dict[tuple[Any, ...], int] = {}
        self.lb: list[float] = []
        self.ub: list[float] = []
        self.integrality: list[int] = []
        self.rows: list[dict[int, float]] = []
        self.lower: list[float] = []
        self.upper: list[float] = []

    def var(self, key: tuple[Any, ...], lb: float = 0, ub: float = 1, integer: bool = True) -> int:
        idx = len(self.keys)
        self.keys.append(key)
        self.index[key] = idx
        self.lb.append(lb)
        self.ub.append(ub)
        self.integrality.append(1 if integer else 0)
        return idx

    def add(self, coeffs: dict[int, float], lower: float, upper: float) -> None:
        self.rows.append(coeffs)
        self.lower.append(lower)
        self.upper.append(upper)

    def solve(self) -> np.ndarray | None:
        data, row_idx, col_idx = [], [], []
        for r, coeffs in enumerate(self.rows):
            for c, value in coeffs.items():
                if value:
                    row_idx.append(r)
                    col_idx.append(c)
                    data.append(value)
        matrix = coo_matrix((data, (row_idx, col_idx)), shape=(len(self.rows), len(self.keys))).tocsr()
        # A tiny deterministic objective avoids unnecessarily placing all scoring
        # at one edge of a partnership while preserving feasibility priorities.
        objective = np.array([(i % 17) * 1e-6 for i in range(len(self.keys))], dtype=float)
        result = milp(
            c=objective,
            integrality=np.array(self.integrality),
            bounds=Bounds(np.array(self.lb), np.array(self.ub)),
            constraints=LinearConstraint(matrix, np.array(self.lower), np.array(self.upper)),
            options={"time_limit": 20},
        )
        if not result.success:
            return None
        return result.x


def solve_innings(root: dict[str, Any], iid: str, schedule: dict[int, str]) -> dict[str, Any] | None:
    innings = next(x for x in root["innings"] if x["innings_id"] == iid)
    batting = table_of(root, iid, "Batting")
    bowling = table_of(root, iid, "Bowling")
    summaries = {r["Field"]: r["Value"] for r in table_of(root, iid, "Innings Summary")["rows"]}
    partnerships = partnership_specs(root, iid)
    wickets = fow_specs(root, iid)
    batting_by_name = {canon(row["Batter"]): row for row in batting["rows"]}
    partnership_by_slot = {
        slot: p for p in partnerships for slot in range(p["start"], p["end"] + 1)
    }
    if set(partnership_by_slot) != set(range(1, innings["legal_balls"] + 1)):
        raise ValueError(f"Partnerships do not cover innings {iid}")

    # Fix the requested number of completed maiden overs before run allocation.
    # Byes and leg-byes may still occur in a maiden; batter runs, wides and
    # no-balls may not. Partial final overs are never selected as maidens.
    maiden_overs: set[int] = set()
    full_over_count = innings["legal_balls"] // 6
    for row in bowling["rows"]:
        wanted = int(row["M"])
        candidates = [
            over for over, owner in sorted(schedule.items())
            if owner == row["Bowler"] and over < full_over_count
        ]
        if wanted > len(candidates):
            raise ValueError(f"Too many maidens requested for {iid}/{row['Bowler']}")
        maiden_overs.update(candidates[:wanted])

    model = Model()
    x_vars: dict[tuple[int, str, str], int] = {}
    token_by_name = {name: (runs, is_four, is_six) for name, runs, is_four, is_six in RUN_TOKENS}
    for slot in range(1, innings["legal_balls"] + 1):
        p = partnership_by_slot[slot]
        for batter in (p["first"], p["second"]):
            for token, _, _, _ in RUN_TOKENS:
                x_vars[(slot, batter, token)] = model.var(("x", slot, batter, token))

    # Each legal delivery has exactly one striker/run token.
    for slot in range(1, innings["legal_balls"] + 1):
        coeffs = {idx: 1 for (s, _, _), idx in x_vars.items() if s == slot}
        model.add(coeffs, 1, 1)

    # Partnership-level batter balls and runs.
    for p in partnerships:
        for batter, balls, runs in (
            (p["first"], p["first_balls"], p["first_runs"]),
            (p["second"], p["second_balls"], p["second_runs"]),
        ):
            relevant = [
                (key, idx) for key, idx in x_vars.items()
                if p["start"] <= key[0] <= p["end"] and key[1] == batter
            ]
            model.add({idx: 1 for _, idx in relevant}, balls, balls)
            model.add({idx: token_by_name[key[2]][0] for key, idx in relevant}, runs, runs)

    # Global batter boundary counts.
    for batter, row in batting_by_name.items():
        if int(row["B"]) == 0:
            continue
        relevant = [(key, idx) for key, idx in x_vars.items() if key[1] == batter]
        model.add({idx: token_by_name[key[2]][1] for key, idx in relevant}, int(row["4s"]), int(row["4s"]))
        model.add({idx: token_by_name[key[2]][2] for key, idx in relevant}, int(row["6s"]), int(row["6s"]))

    # A credited dismissal ends its partnership on a dot delivery by that batter.
    wicket_by_slot = {w["slot"]: w for w in wickets}
    for slot, wicket in wicket_by_slot.items():
        if not wicket["dismissal"].lower().startswith("run out"):
            key = (slot, wicket["batter"], "dot")
            if key not in x_vars:
                raise ValueError(f"Dismissed batter is not in partnership at {iid}/{notation(slot)}")
            model.add({x_vars[key]: 1}, 1, 1)

    # Extras: byes/leg-byes are attached to legal dots; wides/no-balls are
    # separate illegal deliveries owned by a bowler whose over intersects the stand.
    extra_vars: dict[tuple[str, str, str | None], int] = {}
    category_totals = {
        "bye": int(summaries["Byes"]),
        "leg_bye": int(summaries["Leg Byes"]),
        "wide": int(summaries["Wides"]),
        "no_ball": int(summaries["No Balls"]),
    }
    for p in partnerships:
        for category in ("bye", "leg_bye"):
            extra_vars[(p["partnership_id"], category, None)] = model.var(
                ("extra", p["partnership_id"], category, None), 0, p["extras"]
            )
        overlap_bowlers = sorted({
            schedule[(slot - 1) // 6]
            for slot in range(p["start"], p["end"] + 1)
            if (slot - 1) // 6 not in maiden_overs
        })
        for category in ("wide", "no_ball"):
            for bowler in overlap_bowlers:
                extra_vars[(p["partnership_id"], category, bowler)] = model.var(
                    ("extra", p["partnership_id"], category, bowler), 0, p["extras"]
                )
        coeffs = {
            idx: 1 for (pid, _, _), idx in extra_vars.items()
            if pid == p["partnership_id"]
        }
        model.add(coeffs, p["extras"], p["extras"])

        zero_coeffs = {
            idx: 1 for (slot, _, token), idx in x_vars.items()
            if p["start"] <= slot <= p["end"] and token == "dot"
        }
        for category in ("bye", "leg_bye"):
            zero_coeffs[extra_vars[(p["partnership_id"], category, None)]] = -1
        model.add(zero_coeffs, 0, math.inf)

    for category, total in category_totals.items():
        coeffs = {idx: 1 for (_, cat, _), idx in extra_vars.items() if cat == category}
        model.add(coeffs, total, total)

    bowling_by_name = {row["Bowler"]: row for row in bowling["rows"]}
    for bowler, row in bowling_by_name.items():
        for category, column in (("wide", "Wd"), ("no_ball", "Nb")):
            coeffs = {
                idx: 1 for (_, cat, owner), idx in extra_vars.items()
                if cat == category and owner == bowler
            }
            model.add(coeffs, int(row[column]), int(row[column]))

        run_coeffs: dict[int, float] = {}
        for (slot, _, token), idx in x_vars.items():
            if schedule[(slot - 1) // 6] == bowler:
                run_coeffs[idx] = token_by_name[token][0]
        for (_, category, owner), idx in extra_vars.items():
            if owner == bowler and category in ("wide", "no_ball"):
                run_coeffs[idx] = 1
        model.add(run_coeffs, int(row["R"]), int(row["R"]))

    # Match the source maiden column exactly. Non-maiden overs are required to
    # contain at least one batter-conceded run; this sufficient condition keeps
    # the later illegal-extra placement from changing maiden identity.
    for over in range(math.ceil(innings["legal_balls"] / 6)):
        coeffs = {
            idx: token_by_name[token][0]
            for (slot, _, token), idx in x_vars.items()
            if (slot - 1) // 6 == over
        }
        if over in maiden_overs:
            model.add(coeffs, 0, 0)
        else:
            model.add(coeffs, 1, math.inf)

    solution = model.solve()
    if solution is None:
        return None

    selected: dict[int, tuple[str, str]] = {}
    for key, idx in x_vars.items():
        if solution[idx] > 0.5:
            slot, batter, token = key
            selected[slot] = (batter, token)
    extra_allocations = {
        key: int(round(solution[idx])) for key, idx in extra_vars.items()
        if int(round(solution[idx])) > 0
    }

    # Attach legal extras to dot balls and schedule illegal events immediately
    # before an eligible legal delivery inside the same partnership.
    legal_extras: dict[int, tuple[str, int]] = {}
    illegal_before: dict[int, list[tuple[str, str, int]]] = defaultdict(list)
    for p in partnerships:
        dot_slots = [slot for slot in range(p["start"], p["end"] + 1) if selected[slot][1] == "dot"]
        cursor = 0
        for category in ("bye", "leg_bye"):
            amount = extra_allocations.get((p["partnership_id"], category, None), 0)
            for _ in range(amount):
                legal_extras[dot_slots[cursor]] = (category, 1)
                cursor += 1
        for category in ("wide", "no_ball"):
            for bowler in bowling_by_name:
                amount = extra_allocations.get((p["partnership_id"], category, bowler), 0)
                eligible = [
                    slot for slot in range(p["start"], p["end"] + 1)
                    if schedule[(slot - 1) // 6] == bowler
                    and (slot - 1) // 6 not in maiden_overs
                ]
                if amount and not eligible:
                    raise AssertionError("MILP created an ineligible illegal extra")
                for offset in range(amount):
                    illegal_before[eligible[offset % len(eligible)]].append((category, bowler, 1))

    display_names = {canon(row["Batter"]): row["Batter"] for row in batting["rows"]}
    events = []
    team_score = 0
    wicket_count = 0
    event_no = 0
    for slot in range(1, innings["legal_balls"] + 1):
        p = partnership_by_slot[slot]
        striker, token = selected[slot]
        non_striker = p["second"] if striker == p["first"] else p["first"]
        over = (slot - 1) // 6
        ball = (slot - 1) % 6 + 1
        for category, bowler, amount in illegal_before.get(slot, []):
            event_no += 1
            team_score += amount
            events.append({
                "event_id": f"{iid}.E{event_no:03d}",
                "innings_id": iid,
                "delivery_label": f"{over}.{ball}x{len(events)+1}",
                "legal_ball_index": slot - 1,
                "is_legal": False,
                "striker": display_names[striker],
                "non_striker": display_names[non_striker],
                "bowler": bowler,
                "batter_runs": 0,
                "boundary_four": False,
                "boundary_six": False,
                "extras_type": category,
                "extras_runs": amount,
                "dismissal": None,
                "partnership_id": p["partnership_id"],
                "team_score_after": team_score,
                "wickets_after": wicket_count,
                "version": 1,
                "status": "valid",
            })
        event_no += 1
        runs, is_four, is_six = token_by_name[token]
        extra_type, extra_runs = legal_extras.get(slot, (None, 0))
        wicket = wicket_by_slot.get(slot)
        team_score += runs + extra_runs
        if wicket:
            wicket_count += 1
        events.append({
            "event_id": f"{iid}.E{event_no:03d}",
            "innings_id": iid,
            "delivery_label": f"{over}.{ball}",
            "legal_ball_index": slot,
            "is_legal": True,
            "striker": display_names[striker],
            "non_striker": display_names[non_striker],
            "bowler": schedule[over],
            "batter_runs": runs,
            "boundary_four": bool(is_four),
            "boundary_six": bool(is_six),
            "extras_type": extra_type,
            "extras_runs": extra_runs,
            "dismissal": None if not wicket else {
                "batter": display_names[wicket["batter"]],
                "description": wicket["dismissal"],
                "credited_bowler": wicket["credited_bowler"],
            },
            "partnership_id": p["partnership_id"],
            "team_score_after": team_score,
            "wickets_after": wicket_count,
            "version": 1,
            "status": "valid",
        })

    return {
        "innings_id": iid,
        "team": innings["team"],
        "over_schedule": [
            {"over": over, "bowler": schedule[over], "maiden_target": over in maiden_overs}
            for over in sorted(schedule)
        ],
        "partnerships": [{k: v for k, v in p.items() if k != "row"} for p in partnerships],
        "extra_allocations": [
            {"partnership_id": pid, "type": category, "bowler": bowler, "runs": amount}
            for (pid, category, bowler), amount in sorted(extra_allocations.items(), key=str)
        ],
        "events": events,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--root-id", default=DEFAULT_ROOT_ID)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = next(
        json.loads(line) for line in args.canonical.read_text(encoding="utf-8").splitlines()
        if line.strip() and json.loads(line)["root_id"] == args.root_id
    )
    ledger_innings = []
    schedule_attempts = {}
    for innings in root["innings"]:
        iid = innings["innings_id"]
        solved = None
        attempts = 0
        for schedule in feasible_schedules(root, iid):
            attempts += 1
            solved = solve_innings(root, iid, schedule)
            if solved is not None:
                break
            if attempts >= 500:
                break
        if solved is None:
            raise RuntimeError(f"No feasible delivery ledger for {iid} after {attempts} schedules")
        schedule_attempts[iid] = attempts
        ledger_innings.append(solved)
    payload = {
        "ledger_version": "R6.0-single-root",
        "root_id": args.root_id,
        "source_status": root["curation_status"],
        "synthetic_delivery_ledger": True,
        "synthesis_disclosure": "Delivery order is constrained synthetic data derived from the canonical scorecard; it is not an observed ball-by-ball log.",
        "schedule_attempts": schedule_attempts,
        "innings": ledger_innings,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "root_id": args.root_id,
        "schedule_attempts": schedule_attempts,
        "events": {row["innings_id"]: len(row["events"]) for row in ledger_innings},
    }, indent=2))


if __name__ == "__main__":
    main()
