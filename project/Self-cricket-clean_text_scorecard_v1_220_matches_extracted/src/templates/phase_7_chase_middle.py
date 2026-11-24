"""Phase 7: Second Innings - Middle Pressure/Wobble."""
PHASE_7_TEMPLATES = {
    "chase_pressure": [
        "The chase tightened. At {fow_score}, the target of {target} was still within reach but the pressure was accumulating.",
        "At {fow_score}, the asking rate was manageable but {bowling_team} had the field up and the noise was back in the game.",
    ],
    "chase_wobble": [
        "The chase wobbled. {batter} fell to {bowler} for {runs}, and at {fow_score} chasing {target}, {batting_team} had moved from control into uncertainty.",
        "Two quick wickets shifted the match. {batter1} went for {runs1}, {batter2} followed for {runs2}, and at {fow_score} {batting_team} were suddenly exposed.",
    ],
    "chase_partnership": [
        "{batter1} and {batter2} then gave the chase its decisive shape. Their stand of {partnership_runs} dragged {batting_team} from {fow_before} to {fow_score}, changing the equation from danger back into calculation.",
        "The partnership that defined the chase came from {batter1} and {batter2}. {batter1} made {runs1}, {batter2} contributed {runs2}, and their stand of {partnership_runs} was the passage where {batting_team} took control.",
        "{batter1} and {batter2} added {partnership_runs} together, {batter1} scoring {runs1} and {batter2} making {runs2}. By the time the stand ended, the target was within reach.",
    ],
    "chase_anchor": [
        "{batter} stayed through the pressure. His {runs} not out was built in stages — early restraint, middle-overs management, and the calm to see the chase through.",
        "The innings belonged to {batter}. {runs} from {balls} deliveries, compiled with the patience of someone who knew the chase did not need heroics. It needed one batter to stay until the job was done.",
    ],
    "extras_in_chase": [
        "Extras in the chase added {total_extras}, with {wides} wides the main donation from a {bowling_team} attack feeling the pressure of a chase slipping away.",
    ],
}
