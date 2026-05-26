#!/usr/bin/env python3
"""Plot subtask 4: CPU vs GPU time sweep.

Run this after results/subtask4/ is populated.
"""
import csv
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import sys

ROOT = Path(__file__).resolve().parent.parent
GPU_DIR = ROOT / "results" / "subtask4"
OUT     = ROOT / "plots" / "subtask4.png"

def load_avg_steady(glob_pattern, directory):
    """Return {resolution: avg_steady_us} for files matching glob."""
    by_res = defaultdict(list)
    for f in sorted(directory.glob(glob_pattern)):
        with f.open() as fh:
            for line in fh:
                parts = line.strip().split(";")
                if len(parts) < 7:
                    continue
                rep = int(parts[0])
                res = int(parts[1])
                t   = int(parts[6])
                if rep > 0:
                    by_res[res].append(t)
    return {r: sum(v)/len(v)/1e6 for r, v in by_res.items()}

gpu_data = load_avg_steady("task4_gpu_*.csv", GPU_DIR)
cpu_data = load_avg_steady("task4_cpu_*.csv", GPU_DIR)

if not gpu_data or not cpu_data:
    print("ERROR: no data found in results/subtask4/ — run the subtask4 job first.")
    sys.exit(1)

resolutions = sorted(set(gpu_data) | set(cpu_data))
gpu_times = [gpu_data.get(r) for r in resolutions]
cpu_times = [cpu_data.get(r) for r in resolutions]

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.loglog(resolutions, gpu_times, "o-", label="GPU (block 1×32)", color="#2980b9")
ax.loglog(resolutions, cpu_times, "s-", label="CPU (OMP)",        color="#e67e22")

# highlight crossover if any
crossover = None
for i in range(len(resolutions) - 1):
    if gpu_times[i] is None or cpu_times[i] is None:
        continue
    if (gpu_times[i] > cpu_times[i]) != (gpu_times[i+1] > cpu_times[i+1]):
        crossover = resolutions[i]
        ax.axvline(crossover, linestyle="--", color="grey", alpha=0.6, label=f"crossover ~{crossover:,}")
        break

ax.set_xlabel("Resolution (N×N pixels)")
ax.set_ylabel("Avg time (s)  [reps 1–4, log scale]")
ax.set_title("Subtask 4 — CPU vs GPU Julia set timing\n(nrep=5, GPU block 1×32)")
ax.legend()
ax.set_xticks(resolutions)
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"{y:.3f}"))
ax.grid(True, which="both", alpha=0.3)
fig.tight_layout()
fig.savefig(OUT, dpi=150)
print(f"saved {OUT}")
if crossover:
    print(f"crossover at ~r={crossover:,}")
else:
    print("no crossover detected in measured range")
