import json
import secrets
from pathlib import Path


rng = secrets.SystemRandom()

root = Path(__file__).resolve().parent

aaron_early = rng.choice([1, 2, 3])
corrected_extra = rng.choice([2, 4])
corrected_extra_kind = rng.choice(["byes", "leg_byes"])
connor_score = rng.choice([2, 3])
dylan_boundary = rng.choice([4, 6])
ethan_final = rng.choice([3, 4])

events = [
    {"id": "e01", "bowler": "Frost", "batter": "Aaron", "legal": 1, "bat": 0},
    {"id": "e02", "bowler": "Frost", "batter": "Aaron", "legal": 1, "bat": aaron_early},
    {
        "id": "e03",
        "bowler": "Frost",
        "batter": "Aaron",
        "legal": 1,
        "bat": 0,
        corrected_extra_kind: corrected_extra,
    },
    {"id": "e04", "bowler": "Frost", "batter": "Aaron", "legal": 1, "bat": 1},
    {"id": "e05", "bowler": "Frost", "batter": "Connor", "legal": 0, "wide": 1},
    {"id": "e06", "bowler": "Frost", "batter": "Connor", "legal": 0, "no_ball": 1, "bat": 0},
    {"id": "e07", "bowler": "Frost", "batter": "Connor", "legal": 1, "bat": connor_score},
    {"id": "e08", "bowler": "Frost", "batter": "Aaron", "legal": 1, "bat": 0, "wicket": 1},
    {"id": "e09", "bowler": "Pike", "batter": "Dylan", "legal": 1, "bat": dylan_boundary},
    {"id": "e10", "bowler": "Pike", "batter": "Dylan", "legal": 1, "bat": 1},
    {"id": "e11", "bowler": "Pike", "batter": "Connor", "legal": 1, "bat": 2},
    {"id": "e12", "bowler": "Pike", "batter": "Connor", "legal": 1, "bat": 0, "wicket": 1},
    {"id": "e13", "bowler": "Pike", "batter": "Ethan", "legal": 1, "bat": 0, "byes": 1},
    {"id": "e14", "bowler": "Pike", "batter": "Ethan", "legal": 1, "bat": ethan_final},
]

batters = ["Aaron", "Connor", "Dylan", "Ethan"]
bowlers = ["Frost", "Pike"]

gold = {
    "summary": {
        "runs": 0,
        "wickets": 0,
        "legal_balls": 0,
        "wides": 0,
        "no_balls": 0,
        "byes": 0,
        "leg_byes": 0,
    },
    "batting": {
        name: {"runs": 0, "balls": 0, "out": False}
        for name in batters
    },
    "bowling": {
        name: {"legal_balls": 0, "runs_conceded": 0, "wickets": 0}
        for name in bowlers
    },
    "fall_of_wickets": [],
}

for event in events:
    bat = event.get("bat", 0)
    wd = event.get("wide", 0)
    nb = event.get("no_ball", 0)
    byes = event.get("byes", 0)
    leg_byes = event.get("leg_byes", 0)
    event_total = bat + wd + nb + byes + leg_byes

    gold["summary"]["runs"] += event_total
    gold["summary"]["legal_balls"] += event["legal"]
    gold["summary"]["wides"] += wd
    gold["summary"]["no_balls"] += nb
    gold["summary"]["byes"] += byes
    gold["summary"]["leg_byes"] += leg_byes

    gold["batting"][event["batter"]]["runs"] += bat
    if event["legal"] or nb:
        gold["batting"][event["batter"]]["balls"] += 1

    gold["bowling"][event["bowler"]]["legal_balls"] += event["legal"]
    gold["bowling"][event["bowler"]]["runs_conceded"] += bat + wd + nb

    if event.get("wicket", 0):
        gold["summary"]["wickets"] += 1
        gold["batting"][event["batter"]]["out"] = True
        gold["bowling"][event["bowler"]]["wickets"] += 1
        gold["fall_of_wickets"].append(
            {
                "batter": event["batter"],
                "team_runs": gold["summary"]["runs"],
                "wicket_number": gold["summary"]["wickets"],
            }
        )

number_word = {1: "one", 2: "a pair", 3: "three", 4: "four", 6: "six"}
extra_phrase = (
    "off the pads with no bat involved"
    if corrected_extra_kind == "leg_byes"
    else "past everyone without touching bat or body"
)
ethan_initial = 6 if ethan_final in (3, 4) else ethan_final

commentary = f"""
SCORING CONVENTIONS FOR THIS CASE
- A wide is neither a legal ball nor a ball faced.
- A no-ball is not legal, but it counts as a ball faced here.
- Byes and leg-byes count as legal balls and balls faced, but are not charged to the bowler.
- A later OFFICIAL SCORER correction replaces the earlier description of the same delivery.
- Replay and recap descriptions do not create new deliveries.

TARGET SCHEMA
Return innings summary; batting runs/balls/out for Aaron, Connor, Dylan and Ethan;
bowling legal-balls/runs-conceded/wickets for Frost and Pike; and the fall of wickets.

COMMENTARY
Frost begins with Aaron pinned down: no run.
Next one is worked away and they come back for {number_word[aaron_early]}.
The following delivery is celebrated as four to Aaron, at least on the first call.
Aaron then turns Frost into the leg side for a single.
Frost loses his line to Connor; the umpire stretches both arms.
Huge appeal next ball and Connor is caught behind. The fielding side is already celebrating.
Hold on—the front-foot replay has arrived. It is a no-ball, so the catch is cancelled. Connor added nothing with the bat.
Connor responds by running {number_word[connor_score]} from the next legitimate delivery.
Frost comes back to Aaron and knocks the stumps over. This dismissal stands.

Pike takes over. Dylan launches his first ball for {number_word[dylan_boundary]}.
The next is pushed for one.
Connor collects a pair from Pike before edging the following legal ball to the keeper. That wicket stands.
Ethan lets one go through; they scamper a bye.
He then appears to clear the rope for six.

Broadcast recap: Aaron had a boundary during Frost's spell, Connor was caught twice, and Ethan finished the passage with a six.
Career-note graphic: Frost took four wickets in his previous match; Connor's season tally before today was 218.

OFFICIAL SCORER CORRECTION 1:
The earlier apparent boundary to Aaron from Frost is reclassified as {corrected_extra} {extra_phrase}.
Remove those runs from Aaron; the team total from that delivery is unchanged.

OFFICIAL SCORER CORRECTION 2:
Ethan's last hit landed inside the rope. Replace the original six with {ethan_final} runs to Ethan.

Final radio summary: two wickets are down. The caught-behind off the no-ball remains void.
""".strip()

(root / "blind_case.txt").write_text(commentary, encoding="utf-8")
(root / "blind_gold.json").write_text(json.dumps(gold, indent=2), encoding="utf-8")

print(commentary)
