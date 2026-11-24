"""Phase 2: First Innings - Early Overs."""
PHASE_2_TEMPLATES = {
    "innings_start": [
        "{opener1} and {opener2} began for {batting_team}, the early overs carrying {tone_description}.",
    ],
    "opener_batting": [
        "{batter} gave the innings its early shape, striking {runs} from {balls} deliveries with {fours} fours.",
        "{batter} was aggressive early, {runs} from {balls} balls forcing {bowling_team} onto the back foot.",
        "{batter} played the anchor role early, taking {balls} balls over his {runs} and giving {batting_team} a foothold.",
    ],
    "wicket_fall": [
        "{bowler} struck early, removing {batter} for {runs} as {batting_team} slipped to {fow_score}.",
        "The breakthrough came when {bowler} had {batter} {dismissal} for {runs}, {batting_team} now {fow_score}.",
        "{batter} fell to {bowler} for {runs}, and at {fow_score} the innings had lost its early cover.",
    ],
    "collapse_continue": [
        "That opened the door. {batter} followed for {runs}, {batting_team} slumping to {fow_score}.",
        "One wicket became two when {batter} departed for {runs}. At {fow_score}, {batting_team} were in trouble.",
    ],
    "partnership_build": [
        "{batter1} and {batter2} then built a stand of {partnership_runs}, the first real resistance {bowling_team} had faced.",
    ],
}
