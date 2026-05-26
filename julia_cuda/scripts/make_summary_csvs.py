#!/usr/bin/env python3
"""Generate aggregated summary CSVs for LaTeX csvsimple tables."""
from pathlib import Path
from collections import defaultdict
import csv

ROOT = Path(__file__).resolve().parent.parent

# ── Subtask 2 summary ──────────────────────────────────────────────────────────
rows2 = list(csv.DictReader((ROOT / "results/subtask2/subtask2.csv").open()))
by_res = defaultdict(list)
by_res_all = defaultdict(list)
for r in rows2:
    res, rep, t = int(r["resolution"]), int(r["rep"]), int(r["time_us"])
    by_res_all[res].append(t)
    if rep > 0:
        by_res[res].append(t)

out2 = ROOT / "results/subtask2/subtask2_summary.csv"
with out2.open("w", newline="") as fh:
    w = csv.writer(fh)
    # column names must be valid LaTeX identifiers (no underscores, no digits)
    # csvsimple maps these directly to \macroname
    w.writerow(["resolution", "avgsteadys", "maxs", "speedupvsk"])
    base = sum(by_res[1000]) / len(by_res[1000])
    for res in sorted(by_res):
        avg = sum(by_res[res]) / len(by_res[res])
        mx  = max(by_res_all[res])
        w.writerow([res, f"{avg/1e6:.4f}", f"{mx/1e6:.4f}", f"{avg/base:.2f}"])
print(f"wrote {out2}")

# ── Subtask 3 summary ──────────────────────────────────────────────────────────
rows3     = list(csv.DictReader((ROOT / "results/subtask3/subtask3.csv").open()))
rows3_p   = list(csv.DictReader((ROOT / "results/subtask3/subtask3_profile.csv").open()))
prof = {(int(r["block_x"]), int(r["block_y"])): r for r in rows3_p}

steady3 = defaultdict(list)
for r in rows3:
    if int(r["rep"]) > 0:
        steady3[(int(r["block_x"]), int(r["block_y"]))].append(int(r["time_us"]))

order = [(1, 1), (32, 1), (1, 32), (128, 1), (1024, 1)]
out3 = ROOT / "results/subtask3/subtask3_summary.csv"
with out3.open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["block", "threads", "avgsteadys", "occupancypct",
                "gstGBs", "warpeff"])
    for bx, by in order:
        times = steady3[(bx, by)]
        avg   = sum(times) / len(times) / 1e6
        p     = prof.get((bx, by), {})
        w.writerow([
            f"{bx}x{by}",   # no commas — avoids splitting in csvsimple
            bx * by,
            f"{avg:.3f}",
            p.get("occupancy_pct", ""),
            p.get("gst_throughput_GBs", ""),
            p.get("warp_thread_eff", ""),
        ])
print(f"wrote {out3}")

# ── Subtask 4 summary (placeholder — fill after job runs) ─────────────────────
out4 = ROOT / "results/subtask4/subtask4_summary.csv"
if not out4.exists():
    with out4.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["resolution", "gpuavgs", "cpuavgs", "speedup"])
        for res in [1000, 2000, 4000, 8000, 16000]:
            w.writerow([res, "TODO", "TODO", "TODO"])
    print(f"wrote {out4} (placeholder)")
else:
    print(f"skipped {out4} (already exists)")
