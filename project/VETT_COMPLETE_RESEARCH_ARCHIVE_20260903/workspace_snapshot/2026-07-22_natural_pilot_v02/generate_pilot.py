"""Generate natural-checkpoint pilot v0.2 from the validated v0.1 generator.

The innings and table schema stay unchanged. This version increases only the
number of OCR-conflicted deliveries from 20 to 24 and selects natural
checkpoint equations whose coefficient matrix has full column rank.
"""

from pathlib import Path


here = Path(__file__).resolve().parent
source_path = here.parent / "2026-07-22_natural_pilot_v01" / "generate_pilot.py"
source = source_path.read_text(encoding="utf-8")

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
source = source.replace("pilot_case.txt", "pilot_v02_case.txt")
source = source.replace("pilot_gold.json", "pilot_v02_gold.json")
source = source.replace("pilot_manifest.json", "pilot_v02_manifest.json")

start_marker = "# Every checkpoint statistic is additive across deliveries."
end_marker = "\ndef describe_reading(reading):"
start = source.index(start_marker)
end = source.index(end_marker)

rank_block = '''# Every checkpoint statistic is additive across deliveries. Precompute
# its all-feed-one value and every clip's feed-two-minus-feed-one delta.
left_features = checkpoint_features(materialize([0] * len(ambiguous)))
feature_deltas = {key: [0] * len(ambiguous) for key in pool_keys}
for index in range(len(ambiguous)):
    bits = [0] * len(ambiguous)
    bits[index] = 1
    one_right = checkpoint_features(materialize(bits))
    for key in pool_keys:
        feature_deltas[key][index] = one_right.get(key, 0) - left_features.get(key, 0)

# Select natural checkpoint rows that increase matrix rank. Full column rank
# guarantees that the public linear equations have exactly one real solution,
# and therefore exactly one binary solution.
selected_keys = []
rows = []
current_rank = 0
for key in pool_keys:
    row = feature_deltas[key]
    proposed = rows + [row]
    proposed_rank = int(np.linalg.matrix_rank(np.asarray(proposed, dtype=float)))
    if proposed_rank > current_rank:
        selected_keys.append(key)
        rows.append(row)
        current_rank = proposed_rank
    if current_rank == len(ambiguous):
        break

if current_rank != len(ambiguous):
    raise RuntimeError(
        f"Natural checkpoint pool rank {current_rank} does not identify "
        f"{len(ambiguous)} conflicted clips"
    )

true_mask = sum(bit << index for index, bit in enumerate(true_bits))
candidates = [true_mask]
'''

source = source[:start] + rank_block + source[end:]
exec(compile(source, str(here / "pilot_v02_expanded.py"), "exec"), {"__file__": str(here / "pilot_v02_expanded.py")})
