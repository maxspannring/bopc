#!/usr/bin/env python3
"""Plot subtask 2: resolution sweep — avg and max time across 5 reps."""
import csv
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "results" / "subtask2" / "subtask2.csv"
OUT  = ROOT / "plots" / "subtask2.png"

rows = list(csv.DictReader(DATA.open()))
by_res = defaultdict(list)
for r in rows:
    by_res[int(r["resolution"])].append(int(r["time_us"]))

resolutions = sorted(by_res)
avg_s = [sum(by_res[r]) / len(by_res[r]) / 1e6 for r in resolutions]
max_s = [max(by_res[r]) / 1e6 for r in resolutions]
# steady-state avg (exclude rep 0 = CUDA init) — need per-rep data
with DATA.open() as fh:
    rows2 = list(csv.DictReader(fh))
by_res_steady = defaultdict(list)
for r in rows2:
    if int(r["rep"]) > 0:
        by_res_steady[int(r["resolution"])].append(int(r["time_us"]))
avg_steady_s = [sum(by_res_steady[r]) / len(by_res_steady[r]) / 1e6 for r in resolutions]

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(resolutions, max_s,         "o-", label="max (rep 0, incl. CUDA init)", color="#e74c3c")
ax.plot(resolutions, avg_steady_s,  "s-", label="avg steady-state (reps 1–4)",  color="#2980b9")

ax.set_xlabel("Resolution (N×N pixels)")
ax.set_ylabel("Time (s)")
ax.set_title("Subtask 2 — Julia set GPU timing vs. resolution\n(default 16×16 block, nrep=5)")
ax.legend()
ax.set_xticks(resolutions)
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"{y:.3f}"))
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(OUT, dpi=150)
print(f"saved {OUT}")
