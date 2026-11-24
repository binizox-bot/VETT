"""Phase 8: Chase Finish + POM Summary."""
PHASE_8_TEMPLATES = {
    "chase_completed": [
        "{batting_team} reached {total_runs} for {total_wickets} in {overs} overs, winning by {margin}. The chase had been {chase_character}.",
        "The target was overhauled with {margin} to spare, {batting_team} finishing on {total_runs} for {total_wickets} from {overs} overs.",
        "{batting_team} crossed the line at {total_runs} for {total_wickets} in {overs} overs, the margin of {margin} a fair reflection of a chase that {chase_summary}.",
    ],
    "match_close": [
        "The match had been a proper contest, decided by {deciding_factor}, and the scorecard would show a {margin} margin that only hinted at how often the advantage had shifted.",
    ],
    "pom_justification": [
        "{pom} was the correct Player of the Match because {justification}. His contribution crossed both halves of the match in a way no other player could claim.",
        "The Player of the Match award went to {pom}, and it was difficult to argue. {justification}.",
        "{pom} was named Player of the Match. {bat_contribution} with the bat, {bowl_contribution} with the ball — a complete performance that gave his side control of both halves of the contest.",
    ],
    "not_out_finisher": [
        "{batter} stayed there at the end, unbeaten on {runs} from {balls}, the calm presence that saw the chase through its final overs.",
    ],
}
