"""Phase 4: First Innings - Late Overs + Close."""
PHASE_4_TEMPLATES = {
    "late_acceleration": [
        "{batter} gave the innings a late push, striking {runs} from {balls} balls to drag {batting_team} toward a more competitive total.",
    ],
    "tail_wicket": [
        "The tail offered brief resistance. {batter} made {runs} before {dismissal_detail2}, pushing {batting_team} past {total_runs}.",
    ],
    "late_wicket": [
        "{batter} fell for {runs}, {dismissal_detail}, as {batting_team} continued to lose wickets at the wrong moments.",
    ],
    "innings_close": [
        "{batting_team} were all out for {total_runs} in {overs} overs, a total that felt {total_assessment}.",
        "The innings closed at {total_runs} for {total_wickets} from {overs} overs, built in fragments rather than one complete structure.",
        "{batting_team} reached {total_runs} all out in {overs} overs. The score was {total_assessment}, and the chase would test whether that was hope or reality.",
    ],
    "extras_at_close": [
        "The extras column had reached {total_extras} by the close, {wides} of them wides, a sign of the bowling indiscipline that padded the total.",
    ],
}
