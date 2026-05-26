#!/usr/bin/env python3
"""Parse subtask4 raw CSVs into tidy CSV and summary CSV."""
from pathlib import Path
from collections import defaultdict
import csv, re

ROOT    = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "results" / "subtask4"
OUT     = SRC_DIR / "subtask4.csv"
SUMMARY = SRC_DIR / "subtask4_summary.csv"

def load_files(pattern):
    by_res = defaultdict(list)  # {res: [(rep, time_us)]}
    for f in sorted(SRC_DIR.glob(pattern)):
        m = re.search(r"_(\d+)\.csv$", f.name)
        if not m: continue
        res = int(m.group(1))
        with f.open() as fh:
            for line in fh:
                parts = line.strip().split(";")
                if len(parts) < 7: continue
                by_res[res].append((int(parts[0]), int(parts[6])))
    return by_res

gpu = load_files("task4_gpu_*.csv")
cpu = load_files("task4_cpu_*.csv")

# write flat tidy CSV
rows = []
for res in sorted(gpu):
    for rep, t in gpu[res]:
        rows.append({"device": "GPU", "resolution": res, "rep": rep, "time_us": t})
for res in sorted(cpu):
    for rep, t in cpu[res]:
        rows.append({"device": "CPU", "resolution": res, "rep": rep, "time_us": t})
rows.sort(key=lambda r: (r["device"], r["resolution"], r["rep"]))
with OUT.open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["device","resolution","rep","time_us"])
    w.writeheader(); w.writerows(rows)
print(f"wrote {OUT} ({len(rows)} rows)")

# write summary (avg steady = reps 1-4)
resolutions = sorted(set(gpu) | set(cpu))
print(f"\n{'res':>8}  {'GPU avg s':>12}  {'CPU avg s':>12}  {'speedup':>8}")
print("-" * 46)
summary = []
for res in resolutions:
    g = [t for rep, t in gpu[res] if rep > 0]
    c = [t for rep, t in cpu[res] if rep > 0]
    g_avg = sum(g)/len(g)/1e6
    c_avg = sum(c)/len(c)/1e6
    sp = c_avg / g_avg
    summary.append({"resolution": res,
                     "gpuavgs": f"{g_avg:.4f}",
                     "cpuavgs": f"{c_avg:.4f}",
                     "speedup": f"{sp:.2f}"})
    print(f"{res:>8}  {g_avg:>12.4f}  {c_avg:>12.4f}  {sp:>8.2f}")

with SUMMARY.open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["resolution","gpuavgs","cpuavgs","speedup"])
    w.writeheader(); w.writerows(summary)
print(f"\nwrote {SUMMARY}")
