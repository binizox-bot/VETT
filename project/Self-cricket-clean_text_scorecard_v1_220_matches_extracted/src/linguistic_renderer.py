"""Linguistic Renderer v3: tier-specific templates for multi-level difficulty."""
import random
import re
from typing import List, Dict, Any, Optional
from src.narrative_planner import NarrativePlan, CompositeSlot
from src.number_formatter import spell_number


# ═══════════════════════════════════════════════════════════════════
# TIER-SPECIFIC TEMPLATES
#
# D1 (Easy):    Explicit statement, number adjacent to name
# D2 (Medium):  Arithmetic context, operands in same sentence
# D3 (Hard):    Cricket rule implied, operands distributed
# D4 (Expert):  Qualitative hints, deep inference required
# ═══════════════════════════════════════════════════════════════════

TEMPLATES = {
    # ── Phase 1: Setting (D2 only) ──
    "setting_opening": {
        "D2": [
            "At {venue}, {toss_team} chose to {toss_decision} after winning the toss, reading {toss_reason}. {team1} would bat first with {team2} to chase.",
            "{venue} provided the stage. {toss_team} won the toss and elected to {toss_decision}, a decision shaped by {toss_reason}.",
        ],
        "D3": [
            "{toss_team} sent {team1} in at {venue}, the toss going the way of the side that preferred to {toss_decision} on a surface offering {toss_reason}.",
        ],
    },

    # ── Phase 2: Innings Start (D2 only) ──
    "innings_start": {
        "D2": [
            "{batting_team} began through {opener1} and {opener2}. The early exchanges set a tone of {tone}.",
            "{opener1} and {opener2} took guard for {batting_team}, the new ball asking questions that would define the early shape of the innings.",
        ],
        "D3": [
            "The innings opened with {opener1} facing the first delivery from {bowler1}, {opener2} watching from the non-striker's end as {batting_team} began their work.",
        ],
    },

    # ── Wicket Fall (D1/D2/D3) ──
    "wicket_fall": {
        "D1": [
            "{bowler} struck, removing {batter} for {runs} from {balls} balls. {batting_team} were {fow_score}.",
            "{batter} threatened briefly with {runs} before {bowler} found the edge. {batting_team} slipped to {fow_score}.",
        ],
        "D2": [
            "{bowler} broke through — {batter} gone for {runs}. {batting_team} were {fow_score}.",
            "When {batter} fell to {bowler} for {runs}, the scoreboard read {fow_score}.",
            "{bowler} found the breakthrough, {batter} departing for {runs} to leave {batting_team} at {fow_score}.",
        ],
        "D3": [
            "Then {bowler} struck again. {batter} made only {runs}, and {batting_team} were now {fow_score}.",
            "The innings lurched. {batter} gone for {runs} to {bowler}, the board showing {fow_score}.",
            "{bowler} returned to take {batter} for {runs}. {batting_team} now {fow_score}, the collapse deepening.",
            "Another one. {batter} could only manage {runs} before {bowler} sent him back. {fow_score}.",
            "And that is the problem with losing wickets in clusters — {batter} went for {runs} to {bowler}, and suddenly it is {fow_score} and the innings has a very different complexion.",
        ],
        "D4": [
            "The slide continued. {bowler} again, {batter} this time for {runs}. {fow_score} reads the board now, and you would not want to be the next man in.",
        ],
    },

    # ── Partnership Build ──
    "partnership_build": {
        "D1": [
            "{batter1} and {batter2} then added {partnership_runs} together. {batter1} made {runs1}, {batter2} scored {runs2}, and the stand took {batting_team} from {fow_before} to {fow_after}.",
        ],
        "D2": [
            "A stand of {partnership_runs} between {batter1} and {batter2} rebuilt the innings. The arithmetic was straightforward — {runs1} from {batter1}, {runs2} from {batter2} — and the scoreboard shifted from {fow_before} to {fow_after}.",
            "{batter1} and {batter2} constructed a repair worth {partnership_runs}. With {batter1} scoring {runs1} and {batter2} contributing {runs2}, {batting_team} moved from {fow_before} to {fow_after}.",
        ],
        "D3": [
            "{batter1} found an ally in {batter2}. By the time their stand ended, {batting_team} had reached {fow_after}, the partnership having carried them from {fow_before}. {batter1} had contributed {runs1} and {batter2} added {runs2}.",
            "Together {batter1} and {batter2} lifted the innings. {runs1} from the former, {runs2} from the latter, and the scoreboard shifted from {fow_before} to {fow_after}.",
        ],
        "D4": [
            "{batter1} and {batter2} then found each other. {runs1} and {runs2} — those were the individual contributions within a stand that moved the score from {fow_before} through to {fow_after}.",
        ],
    },

    # ── Anchor Batter ──
    "anchor_batter": {
        "D1": [
            "{batter} became the innings' anchor. His {runs} from {balls} deliveries, with {fours} fours and {sixes} sixes, gave {batting_team}'s total its spine.",
        ],
        "D2": [
            "Through the middle phase, {batter} held firm, compiling {runs} from {balls} balls. The {fours} boundaries and {sixes} sixes told only part of the story — the real value was the time he bought for {batting_team}.",
        ],
    },

    # ── Tail Wicket (D1/D2/D3) ──
    "tail_wicket": {
        "D1": [
            "{batter} added a late {runs} before the tail was cleaned up, {batting_team} slipping to {fow_score}.",
        ],
        "D2": [
            "The lower order flickered briefly — {batter} made {runs} — but {batting_team} were {fow_score} and the innings was nearly done.",
        ],
        "D3": [
            "The innings wound down. {batter} managed {runs}, the score moving to {fow_score}, and the end was near.",
        ],
    },

    # ── Innings Close (D1/D2 — D2 removes batting/extras breakdown for single-source difficulty) ──
    "innings_close": {
        "D1": [
            "{batting_team} were all out for {total_runs} in {overs} overs. Of those, {batting_runs} came from the bat and {extras_total} from sundries.",
        ],
        "D2": [
            "The innings closed at {total_runs} from {overs} overs.",
            "{batting_team} finished on {total_runs} in {overs} overs.",
        ],
    },

    # ── Bowling Summary (D1/D2/D3) ──
    "bowling_summary": {
        "D1": [
            "With the ball, {bowler1} led the attack, taking {bowler1_wkts} for {bowler1_runs}. {bowler2} supported with {bowler2_wkts} for {bowler2_runs}.",
        ],
        "D2": [
            "{bowling_team}'s bowling effort was led by {bowler1}, whose {bowler1_wkts} for {bowler1_runs} made the deepest incisions. {bowler2} kept the pressure on with {bowler2_wkts} for {bowler2_runs}, and together they ensured no partnership could breathe.",
        ],
        "D3": [
            "{bowler1} claimed {bowler1_wkts} of the wickets, {bowler2} the other {bowler2_wkts} among the attack. Between them they leaked {bowler1_runs} and {bowler2_runs} runs respectively, the bulk of the damage done by the two spearheads.",
        ],
        "D4": [
            "The wickets fell to {bowler1} ({bowler1_wkts}) and {bowler2} ({bowler2_wkts}), the runs conceded reading {bowler1_runs} and {bowler2_runs}. The rest of the attack filled the gaps.",
        ],
    },

    # ── ★ EXTRAS ACCOUNTING (the most critical tiered template) ★ ──
    "extras_accounting": {
        "D1": [
            # D1: Everything explicitly stated, rule explained
            "The extras column requires a closer look. {total_extras} sundries broke down into {byes} byes, {leg_byes} leg-byes, {no_balls} no-balls and {wides} wides. Byes and leg-byes — {non_bowler_extras} runs in all — do not count against any bowler under cricket's scoring laws, so the attack was collectively charged with {bowling_runs_charged} of the {total_runs} conceded. With {batting_runs} from the bat, the full accounting is {batting_runs} plus {total_extras} equals {total_runs}.",
        ],
        "D2": [
            # D2: Operands present, arithmetic required, rule hinted
            "A breakdown of the extras is revealing. {total_extras} sundries comprised {wides} wides, {no_balls} no-balls, {byes} byes and {leg_byes} leg-byes. The batting contribution stood at {batting_runs}, which together with the {total_extras} extras made {total_runs}.",
        ],
        "D3": [
            # D3: Cricket rule NOT explained — model must know it
            "The total included {total_extras} extras, with {wides} wides and {no_balls} no-balls coming directly from the bowlers' accounts. Another {byes} byes and {leg_byes} leg-byes also found their way into the score. The batters themselves accounted for {batting_runs}. All told, the innings reached {total_runs}.",
            "The sundries column read {total_extras}: {wides} wides, {no_balls} no-balls, plus {byes} byes and {leg_byes} leg-byes. The batters produced {batting_runs} between them. The bowling side's ledger showed {bowling_runs_charged} charged to the attack, the remainder of the {total_runs} having arrived through routes that bypass the bowler's figures.",
        ],
        "D4": [
            # D4: Qualitative, deeply embedded — model must infer structure
            "The innings total of {total_runs} included {total_extras} in sundries — wides ({wides}), no-balls ({no_balls}), byes ({byes}) and leg-byes ({leg_byes}) — alongside {batting_runs} from the bat. The bowlers' collective charge came to {bowling_runs_charged}, the remainder of the total having arrived through means that sit outside a bowler's individual analysis.",
        ],
    },

    # ── Chase Start (D1/D2) ──
    "chase_start": {
        "D1": [
            "Chasing {target}, {opener1} and {opener2} began {team2}'s reply.",
            "A target of {target} was the requirement. {opener1} and {opener2} carried the early responsibility for {team2}.",
        ],
        "D2": [
            "Set {target} to win, {team2} sent out {opener1} and {opener2}. The chase would test temperament as much as technique.",
        ],
    },

    # ── Chase Wicket (D1/D2/D3) ──
    "chase_wicket": {
        "D1": [
            "{bowler} struck early in the chase, removing {batter} for {runs}. At {fow_score} chasing {target}, {team2} had lost early momentum.",
        ],
        "D2": [
            "The chase took a hit when {batter} fell to {bowler} for {runs}. At {fow_score}, with {target} still needed, the pressure that had been theoretical was now real.",
            "{bowler} broke through — {batter} gone for {runs}. {team2} were {fow_score} chasing {target}, and the innings needed a partnership.",
        ],
        "D3": [
            "{batter} could not extend the chase — {bowler} found the way through for {runs}. {team2} now {fow_score}, the required runs still {target}.",
            "{bowler} broke the chase open, {batter} departing for {runs}. {team2} at {fow_score}, still {target} away.",
            "The pursuit lost {batter} to {bowler} for {runs}. {fow_score} the score, {target} the target.",
        ],
    },

    # ── Chase Partnership (D1/D2/D3) ──
    "chase_partnership": {
        "D1": [
            "{batter1} and {batter2} then added {partnership_runs} together, {batter1} scoring {runs1} and {batter2} making {runs2}, taking {team2} from {fow_before} to {fow_after}.",
        ],
        "D2": [
            "The stand that changed the chase came from {batter1} and {batter2}. Their {partnership_runs} — {runs1} from {batter1}, {runs2} from {batter2} — carried {team2} from {fow_before} to {fow_after}, transforming the equation.",
            "{batter1} and {batter2} constructed {partnership_runs} together. With {batter1} contributing {runs1} and {batter2} adding {runs2}, {team2} moved from {fow_before} to {fow_after}. The target of {target} had come into view.",
        ],
        "D3": [
            "{batter1} and {batter2} rebuilt the pursuit. {runs1} and {runs2} were their respective shares of a stand that lifted {team2} to {fow_after}, the earlier {fow_before} now a fading memory with {target} the objective.",
            "{batter1} ({runs1}) and {batter2} ({runs2}) combined to move {team2} from {fow_before} to {fow_after}, the {target}-run target now measurably closer.",
        ],
        "D4": [
            "{batter1} contributed {runs1}, {batter2} the other {runs2}, as the pursuit advanced from {fow_before} to {fow_after} with {target} still the destination.",
        ],
    },

    # ── Chase Anchor ──
    "chase_anchor": {
        "D1": [
            "{batter} anchored the pursuit. His {runs} from {balls} balls, with {fours} fours and {sixes} sixes, was the innings around which {team2}'s chase of {target} organised itself.",
        ],
        "D2": [
            "The chase found its centre in {batter}, whose {runs} from {balls} deliveries carried {team2} from uncertainty toward their target of {target}. The {fours} fours and {sixes} sixes were the visible markers of an innings built in stages.",
        ],
    },

    # ── Chase Close (D1/D2) ──
    "chase_close": {
        "D1": [
            "{team2} reached {total_runs} for {total_wickets} in {overs} overs, winning by {margin}.",
            "The winning runs arrived with {margin} to spare, {team2} finishing on {total_runs} for {total_wickets} from {overs} overs.",
        ],
        "D2": [
            "{team2} closed on {total_runs} for {total_wickets} from {overs} overs, the {margin} margin reflecting a chase that had been tested but never broken.",
        ],
    },

    # ── Match Result (D1/D2) ──
    "match_result": {
        "D1": [
            "{result}. {pom} was named Player of the Match.",
            "The match ended: {result}. {pom} took the Player-of-the-Match honours for a performance that shaped the contest from its earliest exchanges.",
        ],
        "D2": [
            "{result}, with {pom} recognised as Player of the Match after a performance that influenced both halves of the contest.",
        ],
    },

}


def _get_tiered_template(category: str, tier: str, idx: int) -> Optional[str]:
    """Get a template for a specific category and tier, falling back to lower tiers."""
    cat_templates = TEMPLATES.get(category, {})
    if not cat_templates:
        return None

    # Try requested tier first
    if tier in cat_templates:
        templates = cat_templates[tier]
        return templates[idx % len(templates)]

    # Fall back: try lower tiers in order D3→D2→D1
    for fallback in ["D3", "D2", "D1"]:
        if fallback in cat_templates:
            templates = cat_templates[fallback]
            return templates[idx % len(templates)]

    # Last resort: first available tier
    first_tier = list(cat_templates.keys())[0]
    templates = cat_templates[first_tier]
    return templates[idx % len(templates)]


# ── Color commentary: oral-style observations injected between evidence ──
COLOR_PHRASES = {
    "innings_pressure": [
        "The scoreboard was beginning to tell an uncomfortable story now.",
        "You could feel the innings tilting. This was not a surface where you could afford to lose wickets in clusters.",
        "Fair to say the dressing room would have been getting restless at this point.",
        "The thing about collapses is they rarely announce themselves — they just arrive, and suddenly the batting side is in a different game entirely.",
        "That period of play was exactly what the fielding side had been working toward all morning.",
    ],
    "partnership_relief": [
        "At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.",
        "You could sense the mood shifting. This was proper Test-match accumulation now, or as close as the format allows.",
        "There is something reassuring about a partnership that builds rather than explodes — it suggests the batters have read the situation.",
    ],
    "bowling_credit": [
        "Credit to the bowler here. He had been asking these questions all spell and finally got the answer he deserved.",
        "Sometimes the wicket comes from sustained pressure rather than one magic ball. This was one of those times.",
    ],
    "chase_commentary": [
        "Chases like this have a rhythm. You lose an early wicket, you absorb the pressure, you find one partnership — and suddenly the target looks different.",
        "The asking rate was not the issue. The wickets were. Lose another one here and the conversation changes completely.",
        "There is a fine line between a controlled chase and a wobble. The next twenty minutes would tell us which side of it this innings would land on.",
    ],
    "match_context": [
        "In the broader shape of this contest, that passage mattered more than the raw numbers would suggest.",
        "It is easy to look at the scorecard afterward and miss these turning points. But this was where the match tilted.",
    ],
    "extras_observation": [
        "Extras can feel like small change in the moment — a wide here, a leg-bye there — but they add up. They always add up.",
        "The extras column is one of those things coaches circle after the game. It tells you who kept their discipline and who did not.",
    ],
}

class LinguisticRenderer:
    """Renders CompositeSlots into natural flowing cricket prose with tier-specific difficulty."""

    def __init__(self, rng: random.Random):
        self.rng = rng
        self._used = {}
        self._color_used = {}

    def render(self, plan: NarrativePlan) -> str:
        sentences = []
        last_phase = 0
        for phase in range(1, 9):
            phase_slots = [s for s in plan.slots if s.phase == phase]
            if not phase_slots:
                continue

            # Inject color commentary between phases (25% chance, not before phase 1)
            if last_phase >= 2 and self.rng.random() < 0.25:
                color = self._pick_color(phase)
                if color:
                    sentences.append(color)

            for i, slot in enumerate(phase_slots):
                sent = self._render_slot(slot)
                if sent:
                    sentences.append(sent)
                    # Inject color within phase after key moments (15% chance)
                    if slot.category in ("wicket_fall", "partnership_build", "extras_accounting"):
                        if self.rng.random() < 0.15:
                            color = self._pick_color(phase)
                            if color:
                                sentences.append(color)

            last_phase = phase

        return self._weave(sentences)

    def _pick_color(self, phase: int) -> Optional[str]:
        if phase == 2:
            pools = ["bowling_credit"]
        elif phase == 3:
            pools = ["innings_pressure", "partnership_relief", "bowling_credit", "match_context"]
        elif phase == 4:
            pools = ["innings_pressure", "extras_observation", "match_context"]
        elif phase == 5:
            pools = ["extras_observation", "match_context"]
        elif phase == 6:
            pools = ["chase_commentary", "match_context"]
        elif phase == 7:
            pools = ["chase_commentary", "partnership_relief", "match_context"]
        elif phase == 8:
            pools = ["match_context"]
        else:
            return None

        pool_name = self.rng.choice(pools)
        phrases = COLOR_PHRASES.get(pool_name, [])
        if not phrases:
            return None

        idx = self._color_used.get(pool_name, 0) % len(phrases)
        self._color_used[pool_name] = idx + 1
        return phrases[idx]

    def _render_slot(self, slot: CompositeSlot) -> Optional[str]:
        idx = self._used.get(slot.category, 0)
        self._used[slot.category] = idx + 1

        template = _get_tiered_template(slot.category, slot.tier, idx)
        if not template:
            return None

        result = self._fill(template, slot.values)
        if "{" in result:
            return None
        return result

    def _fill(self, template: str, vals: Dict[str, Any]) -> str:
        def replacer(m):
            key = m.group(1)
            val = vals.get(key)
            if val is None or val == "":
                return m.group(0)
            if isinstance(val, float) and val == int(val):
                val = int(val)
            return str(val)
        return re.sub(r'\{([a-z_0-9]+)\}', replacer, template)

    def _weave(self, sentences: List[str]) -> str:
        clean = [s for s in sentences if "{" not in s and "}" not in s]
        if not clean:
            return ""

        seen = set()
        unique = []
        for s in clean:
            key = s[:40]
            if key not in seen:
                seen.add(key)
                unique.append(s)

        # Simple connectors — oral feel comes from color commentary, not connectors
        result = unique[0]
        for s in unique[1:]:
            result += ". " + s

        result = result.replace("The The ", "The ")
        result = re.sub(r'\b1 (\w+?)es\b', r'1 \1', result)
        result = re.sub(r'\b1 (\w+?)s\b', r'1 \1', result)
        result = re.sub(r'\b1 (\w+-\w+?)s\b', r'1 \1', result)
        result = re.sub(r'\b1 (\w+?)es\b', r'1 \1', result)
        result = re.sub(r'\b1 (\w+?)s\b', r'1 \1', result)
        result = re.sub(r'\b1 (\w+-\w+?)s\b', r'1 \1', result)

        return result


def render_commentary(plan: NarrativePlan, rng: random.Random) -> str:
    return LinguisticRenderer(rng).render(plan)
