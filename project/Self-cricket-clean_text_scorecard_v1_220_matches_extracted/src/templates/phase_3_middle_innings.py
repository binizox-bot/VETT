"""Phase 3: First Innings - Middle Rebuild/Collapse."""
PHASE_3_TEMPLATES = {
    "partnership_build": [
        "{batter1} and {batter2} then gave {batting_team} their most substantial recovery, a stand of {partnership_runs} that carried the innings from {fow_before} to {fow_score}.",
        "The rescue came through {batter1} and {batter2}, who added {partnership_runs} and forced {bowling_team} to work through overs rather than simply collect wickets.",
        "A partnership of {partnership_runs} between {batter1} and {batter2} changed the innings' direction. {batter1} made {runs1}, {batter2} added {runs2}, and the scoreboard began to look healthier.",
    ],
    "anchor_batter": [
        "{batter} anchored the innings with {runs} from {balls} deliveries, the one batter who refused to let {bowling_team} take complete control.",
        "Through the middle phase, {batter} held firm. His {runs} was not explosive but it was precisely the occupation {batting_team} needed.",
    ],
    "wicket_interruption": [
        "Just as the recovery was taking shape, {bowler} removed {batter} for {runs}. The stand had been worth {partnership_runs}, but at {fow_score} the innings was back in the balance.",
        "{bowler} broke the stand, {batter} falling for {runs} after a partnership of {partnership_runs}. {batting_team} were {fow_score} and the repair was incomplete.",
    ],
    "middle_phase": [
        "The middle overs became a grinding passage, {batting_team} adding runs in ones and twos while {bowling_team} kept the pressure tight.",
    ],
}
