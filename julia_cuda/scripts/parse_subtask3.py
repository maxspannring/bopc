#!/usr/bin/env python3
"""Parse subtask3 timing CSVs into one tidy table and print BEST_BLOCK.

Input:  results/subtask3/task3_<BX>_<BY>.csv
Output: results/subtask3/subtask3.csv
"""
from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "results" / "subtask3"
OUT = SRC_DIR / "subtask3.csv"

rows = []
for f in sorted(SRC_DIR.glob("task3_*.csv")):
    m = re.match(r"task3_(\d+)_(\d+)\.csv", f.name)
    if not m:
        continue
    bx, by = int(m.group(1)), int(m.group(2))
    with f.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            rep = int(parts[0])
            time_us = int(parts[6])
            rows.append({"block_x": bx, "block_y": by, "rep": rep, "time_us": time_us})

with OUT.open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["block_x", "block_y", "rep", "time_us"])
    w.writeheader()
    w.writerows(rows)

print(f"wrote {OUT} ({len(rows)} rows)\n")

# Compute avg over reps 1-4 (exclude rep 0 = init-dominated)
from collections import defaultdict
steady = defaultdict(list)
for r in rows:
    if r["rep"] > 0:
        steady[(r["block_x"], r["block_y"])].append(r["time_us"])

print(f"{'block':>12}  {'avg_us (reps 1-4)':>20}  {'avg_s':>10}")
print("-" * 48)
best_block = None
best_avg = float("inf")
for (bx, by), times in sorted(steady.items()):
    avg = sum(times) / len(times)
    print(f"  ({bx:4},{by:4})  {avg:>20.0f}  {avg/1e6:>10.3f}")
    if avg < best_avg:
        best_avg = avg
        best_block = (bx, by)

print()
print(f"BEST_BLOCK = {best_block[0]} {best_block[1]}  (avg steady-state {best_avg/1e6:.3f} s)")
