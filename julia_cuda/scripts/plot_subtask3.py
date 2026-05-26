#!/usr/bin/env python3
"""Plot subtask 3: block-size sweep — avg steady-state time."""
import csv
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "results" / "subtask3" / "subtask3.csv"
OUT  = ROOT / "plots" / "subtask3.png"

rows = list(csv.DictReader(DATA.open()))
steady = defaultdict(list)
for r in rows:
    if int(r["rep"]) > 0:
        steady[(int(r["block_x"]), int(r["block_y"]))].append(int(r["time_us"]))

# Display order matches assignment spec
order = [(1, 1), (32, 1), (1, 32), (128, 1), (1024, 1)]
labels = ["(1,1)", "(32,1)", "(1,32)", "(128,1)", "(1024,1)"]
avgs   = [sum(steady[b]) / len(steady[b]) / 1e6 for b in order]
colors = ["#e74c3c" if b == (1, 1) else
          "#2ecc71" if b == (1, 32) else
          "#3498db" for b in order]

fig, ax = plt.subplots(figsize=(7, 4.5))
bars = ax.bar(labels, avgs, color=colors, edgecolor="white", width=0.6)
ax.bar_label(bars, fmt="%.3f s", padding=3, fontsize=9)

ax.set_xlabel("Block size (block_x, block_y)")
ax.set_ylabel("Avg time (s)  [reps 1–4]")
ax.set_title("Subtask 3 — Julia set GPU timing vs. block size\n(r = 20 000×20 000, nrep=5)")
ax.set_ylim(0, max(avgs) * 1.2)
ax.grid(True, axis="y", alpha=0.3)

# annotate best
best_idx = avgs.index(min(avgs))
ax.get_children()[best_idx].set_edgecolor("#27ae60")
ax.get_children()[best_idx].set_linewidth(2.5)
ax.annotate("BEST", xy=(best_idx, avgs[best_idx]),
            xytext=(best_idx, avgs[best_idx] + max(avgs) * 0.08),
            ha="center", color="#27ae60", fontweight="bold", fontsize=10)

fig.tight_layout()
fig.savefig(OUT, dpi=150)
print(f"saved {OUT}")
