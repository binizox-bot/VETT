"""Parse original evidence_chain.md to extract L1/L2 operand requirements."""
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class EvidenceChainItem:
    level: str  # L1, L2, L3
    field: str
    difficulty_logic: str
    evidence_path: str
    operands: Dict[str, int] = field(default_factory=dict)  # name → value
    equation: str = ""  # e.g., "123 + 21 = 144"


def parse_evidence_chain(text: str) -> List[EvidenceChainItem]:
    """Parse the original evidence_chain.md table into structured items."""
    items = []
    lines = text.strip().split("\n")

    # Find table rows (skip header and separator)
    in_table = False
    for line in lines:
        if line.startswith("| Level |"):
            in_table = True
            continue
        if line.startswith("| --- |"):
            continue
        if not in_table or not line.startswith("|"):
            continue

        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < 4:
            continue

        level = cols[0].strip()
        if level not in ("L1", "L2", "L3"):
            continue

        item = EvidenceChainItem(
            level=level,
            field=cols[1].strip(),
            difficulty_logic=cols[2].strip(),
            evidence_path=cols[3].strip(),
        )

        # Extract operands from evidence path
        item.operands = _extract_operands(item.evidence_path)
        item.equation = _extract_equation(item.evidence_path)

        items.append(item)

    return items


def _extract_operands(evidence: str) -> Dict[str, int]:
    """Extract named operands and their values from evidence path text."""
    operands = {}

    # Pattern: "batting runs 123" or "byes 2" or "extras 21"
    # Also: "25+28+18+43+25 = 139"
    name_val_patterns = [
        (r'(?:batting\s*runs?|bat_runs)\s*(\d+)', 'batting_runs'),
        (r'(?:total\s*extras|extras)\s*(\d+)', 'total_extras'),
        (r'\bbyes\s*(\d+)', 'byes'),
        (r'\bleg[\s-]*byes\s*(\d+)', 'leg_byes'),
        (r'\bno[\s-]*balls?\s*(\d+)', 'no_balls'),
        (r'\bwides\s*(\d+)', 'wides'),
        (r'(?:total|innings\s*total)[\s:]*(\d+)', 'total_runs'),
        (r'(?:margin|by)\s*(\d+)\s*(?:runs?|wickets?)', 'margin'),
        (r'non[\s-]*bowler\s*(?:extras|runs?)\s*(\d+)', 'non_bowler_extras'),
        (r'(?:charged\s*with|conceded)\s*(\d+)', 'bowling_runs_charged'),
    ]

    for pattern, name in name_val_patterns:
        matches = re.findall(pattern, evidence, re.IGNORECASE)
        for m in matches:
            operands[name] = int(m)

    # Extract numeric values from equations like "123 + 21 = 144"
    eq_match = re.search(r'(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)', evidence)
    if eq_match:
        operands.setdefault('batting_runs', int(eq_match.group(1)))
        operands.setdefault('total_extras', int(eq_match.group(2)))
        operands.setdefault('total_runs', int(eq_match.group(3)))

    # Extract bowling sum: "25+28+18+43+25 = 139"
    sum_match = re.search(r'(\d+(?:\+\d+)+)\s*=\s*(\d+)', evidence)
    if sum_match:
        parts = [int(x) for x in sum_match.group(1).split('+')]
        operands['bowling_sum'] = sum(parts)
        operands['bowling_sum_target'] = int(sum_match.group(2))

    # Extract subtraction: "144 - byes 2 - leg byes 3 = 139"
    sub_match = re.search(r'(\d+)\s*-\s*(?:byes?\s*(\d+))?\s*-?\s*(?:leg\s*byes?\s*(\d+))?\s*=\s*(\d+)', evidence, re.IGNORECASE)
    if sub_match:
        operands.setdefault('total_runs', int(sub_match.group(1)))
        if sub_match.group(2): operands.setdefault('byes', int(sub_match.group(2)))
        if sub_match.group(3): operands.setdefault('leg_byes', int(sub_match.group(3)))
        operands.setdefault('bowling_runs_charged', int(sub_match.group(4)))

    # Extract player scores: "Ethan Drake 49", "Nolan Hart 66 not out"
    player_matches = re.findall(r'([A-Z][a-z]+ [A-Z][a-z]+)\s+(\d+)', evidence)
    for name, score in player_matches:
        if name not in ('Field Target',):
            operands[f'player_{name}'] = int(score)

    return operands


def _extract_equation(evidence: str) -> str:
    """Extract arithmetic equation from evidence path."""
    patterns = [
        r'(\d+\s*[\+\-]\s*\d+\s*=\s*\d+)',
        r'(\d+(?:\s*\+\s*\d+)+)\s*=\s*\d+',
    ]
    for p in patterns:
        m = re.search(p, evidence)
        if m:
            return m.group(0)
    return ""


def get_l2_operands(items: List[EvidenceChainItem]) -> Dict[str, List[int]]:
    """Collect all unique numeric values required by L2 items."""
    all_values = {}
    for item in items:
        if item.level == "L2":
            for name, val in item.operands.items():
                if name not in all_values:
                    all_values[name] = []
                all_values[name].append(val)
    return all_values


def get_l1_fields(items: List[EvidenceChainItem]) -> List[Dict]:
    """Extract L1 fields that should appear in commentary."""
    l1 = []
    for item in items:
        if item.level == "L1":
            l1.append({
                "field": item.field,
                "evidence": item.evidence_path,
                "difficulty": item.difficulty_logic,
            })
    return l1
