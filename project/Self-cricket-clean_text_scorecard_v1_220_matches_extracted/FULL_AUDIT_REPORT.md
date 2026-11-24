# Cricket Text-to-Table Dataset: Complete Reversibility Audit

## Executive Summary

**Audit Date:** 2026-05-10  
**Dataset:** 220 matches (96 ODI, 94 T20, 30 Other)  
**Deep Audit Sample:** 30 randomly selected matches, 1,916 individual field checks  
**Overall Verdict:** Dataset has strong internal consistency but **only ~45% of scorecard fields are recoverable from commentary alone**. The dataset as-is is a **B-grade benchmark**, not yet an A-grade strict text-to-table reasoning test.

---

## 1. Key Findings

### 1.1 Overall Recoverability

| Classification | Count | % | Meaning |
|---|---|---|---|
| **L1 (Direct)** | 355 | 18.5% | Value explicitly stated in commentary |
| **L2 (Inferred)** | 502 | 26.2% | Can be computed from commentary numbers |
| **L4-C (Not Recoverable)** | 1,007 | 52.6% | Cannot be reconstructed from commentary alone |
| **Invalid** | 52 | 2.7% | Scorecard internal inconsistency |

**Total recoverable (L1+L2): 44.7%**

### 1.2 Internal Arithmetic (Excellent)

The scorecards are mathematically sound:

| Check | Pass Rate | Notes |
|---|---|---|
| Batting Runs + Extras = Total | 429/437 (98.2%) | 8 innings have minor mismatch |
| Extras Breakdown (B+LB+NB+W) | 437/437 (100%) | Perfect |
| Bowling Runs Reconciliation | 418/437 (95.7%) | Minor mismatches in edge cases |
| Bowling Wicket Sum | 261/437 (59.7%) | Run-outs included; not an error |

### 1.3 Per-Match Quality Distribution

| Rating | Count (of 30) | Definition |
|---|---|---|
| **A** (≥75% recoverable, ≤1 invalid) | 0 | Core benchmark ready |
| **B** (≥60% recoverable, ≤2 invalid) | 4 | Usable, some gaps |
| **C** (≥40% recoverable) | 18 | Partial value |
| **D** (<40% recoverable) | 8 | Needs repair |

**No match qualifies as A-grade.** The best matches (B-grade) score ~67-75% recoverability.

---

## 2. Field-Level Gap Analysis

### 2.1 What Works Well (70%+ recoverable)

- **Match winner / result / toss:** Nearly always directly stated or trivially inferable
- **Player of the Match:** Stated explicitly in commentary in ~90% of cases
- **Innings totals:** Usually stated ("all out for 144", "reached 145 for 5")
- **Top scorer runs:** Major scorers (>30) are typically mentioned with their score
- **Result margin:** Wicket/runs margin inferable from innings totals
- **Partnership consistency:** Internal partnership sum math is always correct

### 2.2 What Partially Works (30-60% recoverable)

- **Mid-range batting scores (10-30 runs):** Player is mentioned by name, but score is usually NOT stated. The reader knows they "contributed" but not the exact runs.
- **Key bowler wickets:** Wicket counts for best bowlers (3+ wickets) are often mentioned. Economy rates and runs conceded almost never.
- **Fall of wickets:** Major FOW scores sometimes mentioned. The full chain is mathematically consistent but not independently verifiable from commentary.

### 2.3 What Does NOT Work (<10% recoverable) — CRITICAL GAPS

| Field | Direct in Commentary | Gap Description |
|---|---|---|
| **Total Extras** | 3% | "Extras helped" but number almost never given |
| **Byes** | 2% | Never stated numerically |
| **Leg Byes** | 7% | Rarely stated |
| **No Balls** | 5% | Rarely stated |
| **Wides** | 7% | "Wides" mentioned qualitatively in 57% of cases, but the exact count almost never |
| **Bowler Overs** | <2% | "Bowled 7 overs" style statements essentially absent |
| **Bowler Economy** | <2% | Never stated |
| **Bowler Maidens** | <2% | "Maiden over" sometimes mentioned, but count never |
| **Run Rate** | <5% | Rarely stated numerically |

### 2.4 The Fundamental Problem

The commentary is **natural cricket prose** — it tells the story of the match beautifully, with tension, narrative arc, and qualitative analysis. But it omits the accounting details that a scorecard records:

> Commentary: "Nolan Hart owned the center with five wickets for 12 in a spell that combined patience, control, and perfectly timed dismissals."

This gives us: bowler=Nolan Hart, wickets=5, runs=12. ✓ Excellent.

> Commentary: "Connor Vale gave the innings its first hard shape, a little untidy in the margins with a couple of extras scattered through his early work."

This gives us: bowler=Connor Vale bowled well, some extras happened. ✗ We cannot extract: his exact figures (3/17), the extras breakdown (4w, 2nb), or the overs (7).

**The commentary is a match report, not a scorecard reconstruction tool.**

---

## 3. Visualizations

Three visualization files are saved at:
- `audit_visualization.png` — 6-panel overview (classification pie, format distribution, match ratings, area recoverability, arithmetic consistency, extras gap)
- `audit_match_quality.png` — Per-match recoverability score bar chart
- `audit_recoverability_radar.png` — Field-level recoverability radar chart

---

## 4. Why This Dataset Is Still Valuable

Despite the gaps, this dataset is NOT broken. It has unique strengths:

1. **Natural language quality:** The commentary reads like real cricket journalism, not a template
2. **Multi-hop reasoning:** Many inferable fields require 2-3 steps of cricket logic (e.g., chase margin = target - current score, with wicket context)
3. **No table leakage:** The commentary does NOT contain mini-tables or structured data — a model must truly read
4. **Clean structure:** 4-file format per match is consistent and machine-parseable
5. **220 matches:** Large enough for statistical significance

The issue is that the commentary was **designed as narrative**, and the scorecard was **designed as the ground truth**, but the two were not systematically aligned for every numeric field.

---

## 5. Actionable Improvement Plan

### 5.1 Tiered Strategy

I recommend a **three-tier approach** rather than trying to make every field recoverable:

```
TIER 1: Core Benchmark Fields (target: 80%+ L1+L2)
├── Match winner, result, toss, POM
├── Innings totals + overs
├── Top 3 batter scores per innings
├── Best bowling figures (top 2 bowlers per innings)
├── Result margin + chase logic
└── Max partnership

TIER 2: Advanced Reasoning Fields (target: 60%+ L1+L2)
├── Batting runs + extras = total (arithmetic validation)
├── Wicket sum (bowler wickets + runouts = all out)
├── FOW chain (partnership accumulation)
├── Player partnership contribution (major players)
└── Extras total (not breakdown)

TIER 3: Diagnostic-Only Fields (no target; report separately)
├── Full extras breakdown (byes, leg-byes, no-balls, wides)
├── Complete bowling allocation (overs per bowler)
├── Individual economy rates
├── Minor batter scores (under 10 runs)
└── Ball-count consistency
```

### 5.2 Minimal Commentary Patching Guide

For each match, add **at most 3-4 sentences** of natural cricket prose to close the Tier 1 and Tier 2 gaps. Never add tables, lists, or accounting-style sentences.

**Example — Before (current commentary end of innings):**
> ...and Redmoor were all out for 42 in 24.2 overs.

**Example — After (with minimal natural patch):**
> ...and Redmoor were all out for 42 in 24.2 overs. The innings carried ten extras, seven of them wides with two no-balls and a single leg-bye, which meant the bowlers were only responsible for 32 of the 42.

This ONE sentence now makes recoverable:
- Total extras (10) ✓
- Wides (7) ✓
- No-balls (2) ✓
- Leg-byes (1) ✓
- Bowling runs = 42-0-1 = 41 (byes=0 implied) ✓

**Patch placement rules:**
- Extras evidence: right after innings total summary
- Bowling runs evidence: after bowling paragraph
- FOW evidence: after major partnership description
- Never append all patches to end
- Never break narrative flow

### 5.3 Estimated Work

| Task | Matches to Touch | Effort per Match | Total |
|---|---|---|---|
| Tier 1 gaps (major scores, bowling figures) | ~100 matches | 2 sentences | 2-3 hours |
| Tier 2 gaps (extras total, FOW) | ~200 matches | 2-3 sentences | 5-7 hours |
| Tier 3 (optional, expert-only) | ~50 matches | 4-5 sentences | 2-3 hours |

**Total: ~10-15 hours of manual patching for a near-perfect dataset.**

### 5.4 What NOT to Patch

Do not try to make these fields recoverable — they would require artificial-sounding sentences:
- Complete extras breakdown for every innings
- Economy rates for every bowler
- Overs per bowler
- Exact ball counts
- Minor batter (sub-5 run) scores

These should remain **diagnostic fields** — reported separately as indicators of model capability on hard inference, not mixed into the main benchmark score.

---

## 6. Validation Protocol

After patching, validate with:

1. **Re-run this audit** on patched matches — target 70%+ overall L1+L2 (up from 45%)
2. **Spot-check 20 random matches** manually — verify patches feel natural
3. **Multi-model verification** — run Qwen + GPT-4 + Claude on same matches, check agreement
4. **Reviewer consistency check** — have a second human verify L4-A vs L4-B classifications

---

## 7. Final Assessment

| Dimension | Current | After Tier 1+2 Patching |
|---|---|---|
| Overall recoverability | 45% | 70-75% |
| A-grade matches | 0/30 | 15-20/30 |
| B-grade matches | 4/30 | 8-12/30 |
| Extras coverage | 5% | 80% (total only; breakdown remains diagnostic) |
| Batting score coverage (major) | 70% | 90% |
| Bowling figure coverage | 10% | 60% (key bowlers) |

The dataset is **already valuable as-is** for core reasoning evaluation. With targeted patching, it can become a **gold-standard cricket text-to-table reasoning benchmark**. The key insight is: keep Tier 3 fields as diagnostic, focus patching on Tier 1 and Tier 2, and preserve the natural narrative quality that makes this dataset unique.
