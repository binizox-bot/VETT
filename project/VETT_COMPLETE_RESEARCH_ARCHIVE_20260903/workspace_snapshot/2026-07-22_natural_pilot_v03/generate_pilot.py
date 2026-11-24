"""Natural dense-reconciliation pilot.

This version keeps the same 12-over innings and 24 conflicted clips as v0.2,
but replaces nearly triangular time checkpoints with dense, domain-framed
reconciliation totals over multiple overs, batters and bowlers.
"""

from pathlib import Path


here = Path(__file__).resolve().parent
source_path = here.parent / "2026-07-22_natural_pilot_v01" / "generate_pilot.py"
source = source_path.read_text(encoding="utf-8")

source = source.replace("20260722", "20260724")
source = source.replace(
    "import random\nfrom pathlib import Path",
    "import random\nfrom pathlib import Path\n\nimport numpy as np",
)
source = source.replace(
    "rng.sample([event for event in events if not event.get(\"wicket\")], 20)",
    "rng.sample([event for event in events if not event.get(\"wicket\")], 24)",
)
source = source.replace(
    'event["packet"] = f"clip-{chr(64 + index)}"',
    'event["packet"] = f"clip-{index:02d}"',
)
source = source.replace("pilot_case.txt", "pilot_v03_case.txt")
source = source.replace("pilot_gold.json", "pilot_v03_gold.json")
source = source.replace("pilot_manifest.json", "pilot_v03_manifest.json")

feature_start = source.index("def checkpoint_features(candidate_events):")
feature_end = source.index("# Every checkpoint statistic is additive across deliveries.")

dense_feature_block = '''def make_dense_keys():
    keys = set()
    while len(keys) < 800:
        kind = rng.choice([
            "team", "batters", "bowlers", "leg_byes",
            "team_segments", "batter_segments",
            "marked_deliveries", "batter_marked",
        ])
        over_count = rng.randrange(3, 8)
        overs = tuple(sorted(rng.sample(range(1, 13), over_count)))
        if kind == "team":
            keys.add((kind, overs))
        elif kind == "leg_byes":
            keys.add((kind, overs))
        elif kind == "team_segments":
            segments = tuple(sorted(rng.sample(
                [(over, half) for over in range(1, 13) for half in (1, 2)],
                rng.randrange(4, 10),
            )))
            keys.add((kind, segments))
        elif kind == "batter_segments":
            players = tuple(sorted(rng.sample(batters, rng.randrange(2, 5))))
            segments = tuple(sorted(rng.sample(
                [(over, half) for over in range(1, 13) for half in (1, 2)],
                rng.randrange(4, 10),
            )))
            keys.add((kind, players, segments))
        elif kind == "marked_deliveries":
            positions = tuple(sorted(rng.sample(range(1, 73), rng.randrange(8, 22))))
            keys.add((kind, positions))
        elif kind == "batter_marked":
            players = tuple(sorted(rng.sample(batters, rng.randrange(2, 5))))
            positions = tuple(sorted(rng.sample(range(1, 73), rng.randrange(8, 22))))
            keys.add((kind, players, positions))
        elif kind == "batters":
            players = tuple(sorted(rng.sample(batters, rng.randrange(2, 5))))
            keys.add((kind, players, overs))
        else:
            players = tuple(sorted(rng.sample(bowlers, rng.randrange(2, 5))))
            keys.add((kind, players, overs))
    return list(keys)


pool_keys = make_dense_keys()
rng.shuffle(pool_keys)


def dense_features(candidate_events):
    output = {}
    for key in pool_keys:
        kind = key[0]
        players = None
        overs = None
        segments = None
        positions = None
        if kind in ("team", "leg_byes"):
            overs = set(key[1])
            players = None
            segments = None
        elif kind == "team_segments":
            segments = set(key[1])
            players = None
            overs = None
        elif kind == "batter_segments":
            players = set(key[1])
            segments = set(key[2])
            overs = None
            positions = None
        elif kind == "marked_deliveries":
            positions = set(key[1])
            players = None
            overs = None
            segments = None
        elif kind == "batter_marked":
            players = set(key[1])
            positions = set(key[2])
            overs = None
            segments = None
        else:
            players = set(key[1])
            overs = set(key[2])
            segments = None
            positions = None
        value = 0
        for event in candidate_events:
            if positions is not None:
                if event["position"] not in positions:
                    continue
            elif segments is not None:
                event_segment = (event["over"], 1 if event["ball"] <= 3 else 2)
                if event_segment not in segments:
                    continue
            elif event["over"] not in overs:
                continue
            if kind == "team":
                value += event.get("bat", 0) + event.get("leg_byes", 0)
            elif kind == "leg_byes":
                value += event.get("leg_byes", 0)
            elif kind == "batters" and event["batter"] in players:
                value += event.get("bat", 0)
            elif kind == "bowlers" and event["bowler"] in players:
                value += event.get("bat", 0)
            elif kind == "team_segments":
                value += event.get("bat", 0) + event.get("leg_byes", 0)
            elif kind == "batter_segments" and event["batter"] in players:
                value += event.get("bat", 0)
            elif kind == "marked_deliveries":
                value += event.get("bat", 0) + event.get("leg_byes", 0)
            elif kind == "batter_marked" and event["batter"] in players:
                value += event.get("bat", 0)
        output[key] = value
    return output


true_features = dense_features(events)

# Precompute each clip's feed-two-minus-feed-one coefficient for every natural
# reconciliation equation.
left_features = dense_features(materialize([0] * len(ambiguous)))
feature_deltas = {key: [0] * len(ambiguous) for key in pool_keys}
for index in range(len(ambiguous)):
    bits = [0] * len(ambiguous)
    bits[index] = 1
    one_right = dense_features(materialize(bits))
    for key in pool_keys:
        feature_deltas[key][index] = one_right[key] - left_features[key]

# Select dense natural equations that increase rank. Full rank proves the
# public evidence has one real solution and therefore one binary solution.
selected_keys = []
rows = []
current_rank = 0
for key in pool_keys:
    row = feature_deltas[key]
    proposed_rank = int(np.linalg.matrix_rank(np.asarray(rows + [row], dtype=float)))
    if proposed_rank > current_rank:
        selected_keys.append(key)
        rows.append(row)
        current_rank = proposed_rank
    if current_rank == len(ambiguous):
        break

if current_rank != len(ambiguous):
    raise RuntimeError(
        f"Dense natural evidence rank {current_rank} does not identify "
        f"{len(ambiguous)} conflicted clips"
    )

true_mask = sum(bit << index for index, bit in enumerate(true_bits))
candidates = [true_mask]

'''
source = source[:feature_start] + dense_feature_block + source[feature_end:]

# Remove the old additive precomputation and exhaustive candidate filtering,
# which sits between the retained marker and describe_reading.
old_start = source.index("# Every checkpoint statistic is additive across deliveries.")
old_end = source.index("\ndef describe_reading(reading):")
source = source[:old_start] + source[old_end:]

old_evidence_start = source.index(
    'lines.extend(["", "OFFICIAL SCORER CHECKPOINTS"])'
)
old_evidence_end = source.index(
    'lines.append(\n    "These official checkpoints, taken together, admit exactly one reading of every conflicted clip."\n)'
) + len(
    'lines.append(\n    "These official checkpoints, taken together, admit exactly one reading of every conflicted clip."\n)'
)

evidence_block = '''lines.extend(["", "OFFICIAL SCORER RECONCILIATION SHEETS"])
for number, key in enumerate(selected_keys, 1):
    value = true_features[key]
    kind = key[0]
    if kind == "team":
        overs = ", ".join(map(str, key[1]))
        text = (
            f"Reconciliation {number}: the combined team runs produced in overs "
            f"[{overs}] were {value}."
        )
    elif kind == "leg_byes":
        overs = ", ".join(map(str, key[1]))
        text = (
            f"Reconciliation {number}: the combined leg-byes recorded in overs "
            f"[{overs}] were {value}."
        )
    elif kind == "batters":
        players = ", ".join(key[1])
        overs = ", ".join(map(str, key[2]))
        text = (
            f"Reconciliation {number}: across overs [{overs}], the combined bat "
            f"runs of [{players}] were {value}."
        )
    elif kind == "team_segments":
        segments = ", ".join(
            f"over {over} {'first' if half == 1 else 'second'} half"
            for over, half in key[1]
        )
        text = (
            f"Reconciliation {number}: across [{segments}], the combined team "
            f"runs were {value}."
        )
    elif kind == "batter_segments":
        players = ", ".join(key[1])
        segments = ", ".join(
            f"over {over} {'first' if half == 1 else 'second'} half"
            for over, half in key[2]
        )
        text = (
            f"Reconciliation {number}: across [{segments}], the combined bat "
            f"runs of [{players}] were {value}."
        )
    elif kind == "marked_deliveries":
        deliveries = ", ".join(
            f"{(position - 1) // 6 + 1}.{(position - 1) % 6 + 1}"
            for position in key[1]
        )
        text = (
            f"Reconciliation {number}: the marked delivery cells [{deliveries}] "
            f"contained {value} combined team runs."
        )
    elif kind == "batter_marked":
        players = ", ".join(key[1])
        deliveries = ", ".join(
            f"{(position - 1) // 6 + 1}.{(position - 1) % 6 + 1}"
            for position in key[2]
        )
        text = (
            f"Reconciliation {number}: in marked cells [{deliveries}], the "
            f"combined bat runs of [{players}] were {value}."
        )
    else:
        players = ", ".join(key[1])
        overs = ", ".join(map(str, key[2]))
        text = (
            f"Reconciliation {number}: across overs [{overs}], the combined "
            f"chargeable runs conceded by [{players}] were {value}."
        )
    lines.append(text)
lines.append(
    "The reconciliation sheets are jointly full-rank: exactly one reading of "
    "every conflicted clip satisfies all of them."
)'''

source = source[:old_evidence_start] + evidence_block + source[old_evidence_end:]
exec(compile(source, str(here / "pilot_v03_expanded.py"), "exec"), {"__file__": str(here / "pilot_v03_expanded.py")})
