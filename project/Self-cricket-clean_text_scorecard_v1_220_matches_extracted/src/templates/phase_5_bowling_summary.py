"""Phase 5: Bowling Summary + Extras Accounting (CRITICAL for evidence closure)."""
PHASE_5_TEMPLATES = {
    "bowling_summary": [
        "{bowling_team}'s bowling was led by {best_bowler} with {best_figures}, supported by {support_bowler} who kept the pressure on through the middle overs.",
    ],
    "bowler_spell": [
        "{bowler} finished with {figures}, a spell that combined {quality1} with {quality2} and repeatedly broke partnerships just as they threatened to form.",
        "{bowler}'s {figures} were decisive. He {action_description}, and the innings never recovered from his interventions.",
    ],
    "extras_accounting": [
        "The innings carried {total_extras} extras — {byes} byes, {leg_byes} leg-byes, {no_balls} no-balls and {wides} wides. The byes and leg-byes, {non_bowler_extras} runs in all, are not charged to any bowler, so {bowling_team}'s attack was collectively charged with {bowling_runs_charged} of the {total_runs}.",
        "A breakdown of the extras tells part of the story: {total_extras} sundries in all, with {wides} wides the main offender. Add {no_balls} no-balls, {byes} byes and {leg_byes} leg-byes. Taking away the {non_bowler_extras} runs that did not count against any bowler, {bowling_team}'s bowlers were responsible for {bowling_runs_charged} of the innings total.",
        "The extras column read {total_extras}, including {wides} wides and {no_balls} no-balls that were charged directly to the bowlers, plus {byes} byes and {leg_byes} leg-byes — {non_bowler_extras} runs that bypassed the attack's account. The bowlers were therefore accountable for {bowling_runs_charged} of {batting_team}'s {total_runs}.",
    ],
    "batting_contribution": [
        "From the bat, {batting_team} contributed {batting_runs} runs. The remaining {total_extras} came from extras, meaning the innings leaned more heavily on free runs than {batting_team} would have wanted.",
    ],
}
