"""
analyze_speedup.py

Reads the benchmark CSV produced by bench_speedup.job, computes mean runtime
per configuration, then derives relative speedup and parallel efficiency.
Finally produces a 3x2 grid of overview plots:

                c_s (student)        c_b (benchmark)
    row 0:      runtime              runtime
    row 1:      speedup              speedup
    row 2:      efficiency           efficiency

Two lines per subplot: blue stars = size 120, red stars = size 1030,
connected by dotted lines.
"""

import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# 1. Load
# ----------------------------------------------------------------------
CSV_PATH = "results_speedup_5118230.csv"   # <-- change to your real CSV path
df = pd.read_csv(
    CSV_PATH,
    skiprows=1,                    # skip the wrong header
    names=["c_label", "size", "patch", "nprocs", "runtime", "rep"],
)
# ----------------------------------------------------------------------
# 2. Mean runtime per (c_label, size, nprocs)
# ----------------------------------------------------------------------
mean_df = (
    df.groupby(["c_label", "size", "nprocs"], as_index=False)["runtime"]
      .mean()
      .rename(columns={"runtime": "mean_runtime"})
      .sort_values(["c_label", "size", "nprocs"])
      .reset_index(drop=True)
)

# ----------------------------------------------------------------------
# 3. Speedup and efficiency
#    S(p) = T(1) / T(p)
#    E(p) = S(p) / p
# ----------------------------------------------------------------------
# Pull T(1) for each (c_label, size) group and broadcast it to all rows
# in that group via groupby.transform.
mean_df["T1"] = (
    mean_df.groupby(["c_label", "size"])["mean_runtime"]
           .transform("first")           # works because we sorted by nprocs
)
mean_df["speedup"]    = mean_df["T1"] / mean_df["mean_runtime"]
mean_df["efficiency"] = mean_df["speedup"] / mean_df["nprocs"]

print(mean_df.to_string(index=False))
mean_df.to_csv("derived_metrics.csv", index=False)

# ----------------------------------------------------------------------
# 4. Plot 3x2 grid
# ----------------------------------------------------------------------
fig, axes = plt.subplots(3, 2, figsize=(12, 11), sharex=True)

# Column order: c_s on the left, c_b on the right
columns = [("student",   0, "$c_s$ (student)"),
           ("benchmark", 1, "$c_b$ (benchmark)")]

# Row order: runtime, speedup, efficiency
metrics = [("mean_runtime", "Mean runtime (s)"),
           ("speedup",      "Relative speedup"),
           ("efficiency",   "Parallel efficiency")]

color_map = {120: "blue", 1030: "red"}

for c_label, col, col_title in columns:
    for row, (metric, ylabel) in enumerate(metrics):
        ax = axes[row, col]
        for size in [120, 1030]:
            sub = mean_df[(mean_df["c_label"] == c_label) &
                          (mean_df["size"]   == size)]
            ax.plot(sub["nprocs"], sub[metric],
                    color=color_map[size],
                    linestyle=":",
                    marker="*",
                    markersize=12,
                    label=f"size = {size}")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        ax.legend()
        if row == 0:
            ax.set_title(col_title)
        if row == 2:
            ax.set_xlabel("Number of workers $p$")

fig.suptitle("Julia set parallel benchmark — overview", fontsize=14)
fig.tight_layout()
fig.savefig("overview_plots.png", dpi=120, bbox_inches="tight")
plt.show()
