"""Generate a larger instance from the Level-5 blind generator.

The source transformation changes only scale, participant lists and output
filenames. It deliberately preserves the same data model and audit mechanism,
so Level 6 tests capacity rather than introducing a new task.
"""

from pathlib import Path


root = Path(__file__).resolve().parent
source = (root / "level5_generate.py").read_text(encoding="utf-8")

replacements = {
    'batters = ["Aaron", "Connor", "Dylan", "Ethan", "Gavin"]':
        'batters = ["Aaron", "Connor", "Dylan", "Ethan", "Gavin", "Julian", "Cameron"]',
    'bowlers = ["Frost", "Pike", "Stone", "Rowe", "Shaw", "Hart", "Cross"]':
        'bowlers = ["Frost", "Pike", "Stone", "Rowe", "Shaw", "Hart", '
        '"Cross", "Blake", "Grant", "Wells", "Price", "Cole"]',
    'wicket_positions = [10, 24, 36]':
        'wicket_positions = [10, 24, 36, 50, 64]',
    'for legal_position in range(1, 43):':
        'for legal_position in range(1, 73):',
    'rng.sample(eligible, 14)':
        'rng.sample(eligible, 24)',
    'for over in range(1, 8):':
        'for over in range(1, 13):',
    'level5_case.txt':
        'level6_case.txt',
    'level5_gold.json':
        'level6_gold.json',
}

for old, new in replacements.items():
    if old not in source:
        raise RuntimeError(f"Expected generator fragment not found: {old}")
    source = source.replace(old, new)

exec(compile(source, str(root / "level6_expanded.py"), "exec"), {"__file__": str(root / "level6_expanded.py")})
