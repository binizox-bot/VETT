"""Classify match narrative type from scorecard structure for phase emphasis selection."""
from src.parser import MatchData


def classify_story(md: MatchData) -> dict:
    """Return story type + phase emphasis weights."""
    inns = md.innings
    if len(inns) < 2:
        return {"type": "abandoned", "emphasis": [0.8, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.5]}

    inn1, inn2 = inns[0], inns[1]
    result_type = md.result_type
    total1, total2 = inn1.total_runs, inn2.total_runs

    # Base emphasis (all phases get at least 0.5)
    emphasis = [0.8, 1.0, 1.0, 1.0, 0.8, 1.0, 1.0, 1.0]

    # Compute features
    margin_runs = abs(total1 - total2)
    margin_wickets = 10 - inn2.total_wickets if result_type == "wickets" else 0
    is_blowout = (result_type == "runs" and margin_runs >= 100) or \
                 (result_type == "wickets" and margin_wickets >= 8)
    is_close = (result_type == "runs" and margin_runs <= 20) or \
               (result_type == "wickets" and margin_wickets <= 3)

    # Early collapse?
    early_collapse_inn1 = len(inn1.fow) >= 3 and inn1.fow[2].score < 50
    early_collapse_inn2 = len(inn2.fow) >= 3 and inn2.fow[2].score < 50

    # Big partnership?
    has_big = any(p.runs >= 80 for inn in inns for p in inn.partnerships)

    # Chase wobble?
    chase_wobble = inn2.total_wickets >= 6

    # All-round POM?
    pom_clean = md.player_of_match
    for suffix in [" (c)", " (wk)"]:
        pom_clean = pom_clean.replace(suffix, "")
    batters_all = [(b.name.replace("(c)", "").replace("(wk)", "").strip(), b.runs)
                   for inn in inns for b in inn.batters if b.runs > 0]
    bowlers_all = [(b.name, b.wickets) for inn in inns for b in inn.bowlers if b.wickets >= 1]
    pom_bat = any(pom_clean in name and runs >= 20 for name, runs in batters_all)
    pom_bowl = any(pom_clean in name and wkts >= 1 for name, wkts in bowlers_all)
    is_all_round = pom_bat and pom_bowl

    # Story type determination
    if is_blowout:
        if inn2.total_runs < 100:
            story = "bowling_rout"
            emphasis = [0.8, 0.8, 0.8, 0.8, 1.5, 0.5, 0.3, 1.0]
        else:
            story = "dominant_bat"
            emphasis = [0.8, 1.2, 1.2, 1.2, 1.0, 0.5, 0.5, 1.0]

    elif is_close:
        story = "nail_biter"
        emphasis = [0.8, 1.0, 1.0, 1.2, 0.8, 1.0, 1.5, 1.5]

    elif early_collapse_inn1 and has_big:
        story = "rescue_innings"
        emphasis = [0.8, 1.0, 1.5, 1.2, 1.0, 1.0, 1.0, 1.0]

    elif early_collapse_inn1:
        story = "collapse_defense"
        emphasis = [0.8, 0.8, 1.0, 0.8, 1.2, 1.0, 1.0, 1.0]

    elif has_big:
        story = "partnership_match"
        emphasis = [0.8, 1.0, 1.3, 1.0, 1.0, 1.0, 1.0, 1.0]

    elif is_all_round:
        story = "all_round_showcase"
        emphasis = [0.8, 0.8, 1.0, 1.0, 1.2, 1.0, 1.0, 1.2]

    elif chase_wobble:
        story = "chase_wobble"
        emphasis = [0.8, 1.0, 1.0, 0.8, 1.0, 1.0, 1.3, 1.2]

    else:
        story = "balanced"
        emphasis = [0.8, 1.0, 1.0, 1.0, 0.8, 1.0, 1.0, 1.0]

    return {"type": story, "emphasis": emphasis}


# Story-type-specific narrative descriptors
STORY_DESCRIPTORS = {
    "bowling_rout": {
        "tone": "decisive, clinical",
        "first_innings_arc": "one team dominated with ball, the other never built a response",
        "chase_arc": "minimal threat, quick finish",
    },
    "dominant_bat": {
        "tone": "commanding, inevitable",
        "first_innings_arc": "batting side built in waves, posting a mountain",
        "chase_arc": "target too large, chase never launched",
    },
    "nail_biter": {
        "tone": "tense, fluctuating",
        "first_innings_arc": "competitive total, neither side felt secure",
        "chase_arc": "pressure swung repeatedly, decided late",
    },
    "rescue_innings": {
        "tone": "dramatic, redemptive",
        "first_innings_arc": "early collapse, middle-order rescue, late lift",
        "chase_arc": "platform built then tested",
    },
    "collapse_defense": {
        "tone": "unforgiving, grinding",
        "first_innings_arc": "batters struggled throughout, extras propped up total",
        "chase_arc": "small target made to feel larger by tight bowling",
    },
    "partnership_match": {
        "tone": "constructive, building",
        "first_innings_arc": "defined by one or two major stands",
        "chase_arc": "steady accumulation with key partnership",
    },
    "all_round_showcase": {
        "tone": "individual brilliance",
        "first_innings_arc": "one player dominated with bat and ball",
        "chase_arc": "POM contribution in both disciplines",
    },
    "chase_wobble": {
        "tone": "uncertain, tense finish",
        "first_innings_arc": "strong total posted",
        "chase_arc": "comfortable start, middle wobble, calm finish",
    },
    "balanced": {
        "tone": "even, competitive",
        "first_innings_arc": "competitive total built through contributions",
        "chase_arc": "controlled chase with minor interruptions",
    },
}
