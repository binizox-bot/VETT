#!/usr/bin/env python3
"""
Generate visualizations for the cricket text-to-table dataset audit.
"""
import json, os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

BASE = Path(r"E:\New_Framework\data\Self-cricket-clean_text_scorecard_v1")

# Load audit data
with open(BASE / "audit_report.json", "r", encoding="utf-8") as f:
    report = json.load(f)

# Set up style
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'figure.dpi': 150,
})

# ── Figure 1: Classification Pie Chart ──
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle("Cricket Text-to-Table Dataset: Complete Reversibility Audit", fontsize=16, fontweight='bold', y=0.98)

# 1a. Overall classification
ax = axes[0, 0]
cls = report["classification_distribution"]
labels = ["L1 (Direct)", "L2 (Inferred)", "L4-C (Not Recoverable)", "Invalid"]
sizes = [cls.get("L1", 0), cls.get("L2", 0), cls.get("L4_c", 0), cls.get("Invalid", 0)]
colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12']
explode = (0.02, 0.02, 0.08, 0.02)
wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                    autopct='%1.1f%%', startangle=140)
for at in autotexts:
    at.set_fontsize(10)
ax.set_title("Overall Field Classification\n(30-match sample)")

# 1b. Format distribution
ax = axes[0, 1]
fmt = report["format_distribution"]
fmt_labels = list(fmt.keys())
fmt_sizes = list(fmt.values())
fmt_colors = ['#9b59b6', '#e67e22', '#1abc9c']
ax.pie(fmt_sizes, labels=fmt_labels, colors=fmt_colors, autopct='%1.1f%%', startangle=90)
ax.set_title("Match Format Distribution\n(all 220 matches)")

# 1c. Per-match rating distribution
ax = axes[0, 2]
ratings = [r["rating"] for r in report["per_match_ratings"]]
r_counts = {r: ratings.count(r) for r in ["A", "B", "C", "D"]}
r_colors = {'A': '#2ecc71', 'B': '#3498db', 'C': '#f39c12', 'D': '#e74c3c'}
bars = ax.bar(list(r_counts.keys()), list(r_counts.values()),
              color=[r_colors[r] for r in r_counts])
for bar, val in zip(bars, r_counts.values()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, str(val),
            ha='center', fontweight='bold', fontsize=12)
ax.set_title("Per-Match Quality Rating\n(30-match sample)")
ax.set_ylabel("Number of Matches")
ax.set_ylim(0, max(r_counts.values()) + 3)

# ── Figure 1d: Area-level recoverability ──
ax = axes[1, 0]
area_data = report["area_breakdown"]
areas_short = [k.replace("inn1_", "Inn1-").replace("inn2_", "Inn2-").replace("_", "\n") for k in area_data.keys()]
l1_vals = [area_data[a].get("L1", 0) for a in area_data]
l2_vals = [area_data[a].get("L2", 0) for a in area_data]
l4c_vals = [area_data[a].get("L4_c", 0) for a in area_data]
inv_vals = [area_data[a].get("Invalid", 0) for a in area_data]

x = np.arange(len(areas_short))
width = 0.6
totals = [l1_vals[i] + l2_vals[i] + l4c_vals[i] + inv_vals[i] for i in range(len(x))]
l1_pct = [100*l1/t if t else 0 for l1, t in zip(l1_vals, totals)]
l2_pct = [100*l2/t if t else 0 for l2, t in zip(l2_vals, totals)]

ax.barh(x, l1_pct, height=width, color='#2ecc71', label='L1 (Direct)')
ax.barh(x, l2_pct, height=width, left=l1_pct, color='#3498db', label='L2 (Inferred)')
ax.set_yticks(x)
ax.set_yticklabels(areas_short, fontsize=8)
ax.set_xlabel("% Recoverable from Commentary")
ax.set_title("Field Area Recoverability")
ax.legend(loc='lower right', fontsize=8)
ax.set_xlim(0, 110)

# 1e. Arithmetic consistency
ax = axes[1, 1]
arith = report["arithmetic_consistency"]
checks = ["Batting+Extras\n=Total", "Extras\nBreakdown", "Bowling Runs\nReconciliation", "Bowling\nWicket Sum*"]
check_ok = [arith["bat_plus_extras_ok"], arith["extras_breakdown_ok"],
            arith["bowl_r_ok"], arith["bowl_w_ok"]]
check_total = arith["total"]
check_pct = [100 * ok / check_total for ok in check_ok]
bar_colors = ['#2ecc71' if p >= 95 else '#f39c12' if p >= 70 else '#e74c3c' for p in check_pct]
bars = ax.bar(checks, check_pct, color=bar_colors, edgecolor='white', linewidth=1.5)
for bar, pct, ok in zip(bars, check_pct, check_ok):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
            f"{ok}/{check_total}\n({pct:.1f}%)", ha='center', fontweight='bold', fontsize=10, color='white')
ax.set_title("Internal Scorecard Arithmetic\nConsistency (n=437 innings)")
ax.set_ylabel("% Consistent")
ax.set_ylim(0, 105)
ax.axhline(y=95, color='green', linestyle='--', alpha=0.3, label='95% target')
ax.text(3.5, 96, '*Bowling wicket sum excludes run-outs &\nnon-bowler dismissals', fontsize=7, ha='right')

# 1f. Extras gap - detailed
ax = axes[1, 2]
extras_fields = ["total_extras", "byes", "leg_byes", "no_balls", "wides"]
extras_data = {
    "Direct Number": [2, 1, 4, 3, 4],
    "Type Mentioned\n(qualitative)": [0, 6, 2, 8, 34],
    "Not in Commentary": [58, 53, 54, 49, 22]
}

y_pos = np.arange(len(extras_fields))
left = np.zeros(len(extras_fields))
extras_colors = ['#2ecc71', '#f39c12', '#e74c3c']

for i, (label, values) in enumerate(extras_data.items()):
    bars = ax.barh(y_pos, values, left=left, color=extras_colors[i], label=label, height=0.6)
    left += values

ax.set_yticks(y_pos)
ax.set_yticklabels(extras_fields)
ax.set_xlabel("Number of Occurrences (60 samples)")
ax.set_title("Extras Fields: Commentary Coverage Gap")
ax.legend(loc='lower right', fontsize=7)

plt.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(BASE / "audit_visualization.png", dpi=150, bbox_inches='tight')
print(f"Saved: {BASE / 'audit_visualization.png'}")

# ── Figure 2: Heatmap of match quality ──
fig2, ax2 = plt.subplots(figsize=(14, 5))

match_ratings = report["per_match_ratings"]
match_names = [r["match"] for r in match_ratings]
match_scores = [r["score"] for r in match_ratings]
match_invalid = [r["invalid"] for r in match_ratings]
match_ratings_letter = [r["rating"] for r in match_ratings]

# Color mapping
rating_color_map = {'A': '#2ecc71', 'B': '#3498db', 'C': '#f39c12', 'D': '#e74c3c'}
bar_colors = [rating_color_map[r] for r in match_ratings_letter]

bars = ax2.bar(range(len(match_names)), match_scores, color=bar_colors, edgecolor='white', linewidth=0.5)
ax2.set_xticks(range(len(match_names)))
ax2.set_xticklabels([n.replace("match_", "") for n in match_names], rotation=45, ha='right', fontsize=8)
ax2.set_ylabel("Recoverability Score (L1+L2)/Total")
ax2.set_title("Per-Match Text-to-Table Recoverability Score (30 random samples)")
ax2.set_ylim(0, 1.05)
ax2.axhline(y=0.75, color='#2ecc71', linestyle='--', alpha=0.5, label='A-grade (0.75)')
ax2.axhline(y=0.60, color='#3498db', linestyle='--', alpha=0.5, label='B-grade (0.60)')
ax2.axhline(y=0.40, color='#f39c12', linestyle='--', alpha=0.5, label='C-grade (0.40)')

# Add invalid count as text
for i, (score, inv, rating) in enumerate(zip(match_scores, match_invalid, match_ratings_letter)):
    color = 'white' if score < 0.5 else 'black'
    ax2.text(i, score/2, f"{rating}\n{inv}inv", ha='center', fontsize=7, fontweight='bold', color=color)

ax2.legend(loc='upper right', fontsize=8)
plt.tight_layout()
fig2.savefig(BASE / "audit_match_quality.png", dpi=150, bbox_inches='tight')
print(f"Saved: {BASE / 'audit_match_quality.png'}")

# ── Figure 3: What's missing - summary radar ──
fig3, ax3 = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))

categories = ['Match\nWinner', 'Result\nMargin', 'Toss\nDecision', 'Player of\nMatch',
              'Innings\nTotal', 'Top\nScorer', 'Best\nBowler',
              'Extras\nTotal', 'Extras\nBreakdown', 'Partnership\nRuns',
              'FOW\nChain', 'Bowler\nOvers']
# Direct recoverability rate per category (approximate from our data)
direct_rates = [95, 85, 90, 90, 75, 70, 60, 3, 5, 50, 15, 2]
inferred_rates = [5, 15, 10, 10, 20, 25, 30, 35, 15, 44, 42, 3]
not_recoverable = [100-d-i for d, i in zip(direct_rates, inferred_rates)]

N = len(categories)
angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
angles += angles[:1]

direct_rates_p = direct_rates + direct_rates[:1]
inferred_rates_p = inferred_rates + inferred_rates[:1]
not_recoverable_p = not_recoverable + not_recoverable[:1]

ax3.fill(angles, direct_rates_p, alpha=0.4, color='#2ecc71', label='Direct (L1)')
ax3.fill(angles, [d+i for d,i in zip(direct_rates_p, inferred_rates_p)], alpha=0.3, color='#3498db', label='+Inferred (L1+L2)')
ax3.set_xticks(angles[:-1])
ax3.set_xticklabels(categories, fontsize=9)
ax3.set_ylim(0, 100)
ax3.set_yticks([25, 50, 75, 100])
ax3.set_yticklabels(['25%', '50%', '75%', '100%'], fontsize=8)
ax3.set_title("Field-Level Recoverability Radar (estimated from 30-match audit)", pad=25)
ax3.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))

plt.tight_layout()
fig3.savefig(BASE / "audit_recoverability_radar.png", dpi=150, bbox_inches='tight')
print(f"Saved: {BASE / 'audit_recoverability_radar.png'}")
