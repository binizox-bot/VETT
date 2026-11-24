"""Phase 6: Second Innings - Early Chase."""
PHASE_6_TEMPLATES = {
    "chase_start": [
        "Chasing {target}, {batting_team} sent out {opener1} and {opener2} needing a start that would make the target feel {target_assessment}.",
        "A target of {target} was {target_assessment} on this surface. {opener1} and {opener2} walked out with the responsibility of setting the chase's tone.",
    ],
    "chase_batter": [
        "{batter} began the chase with intent, striking {runs} from {balls} to make the target feel immediately smaller.",
        "{batter} was watchful early, his {runs} from {balls} balls more about time than tempo.",
    ],
    "early_wicket_chase": [
        "{bowler} struck early in the chase, removing {batter} for {runs}. At {fow_score} chasing {target}, {batting_team} had lost the early momentum.",
        "The chase suffered an early blow when {batter} fell to {bowler} for {runs}. {batting_team} were {fow_score}, and chasing {target}, the pressure was already building.",
    ],
    "chase_platform": [
        "{batter1} and {batter2} put on {partnership_runs} for the opening stand, giving {batting_team} a platform without exposing the middle order too early.",
    ],
}
