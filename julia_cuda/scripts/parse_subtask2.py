#!/usr/bin/env python3
"""Parse subtask2 raw CSVs into one tidy table.

Input:  results/subtask2/task2_<RES>.csv (semicolon-separated, no header)
        columns: rep;res_x;res_y;scale;block_x;block_y;time_us
Output: results/subtask2/subtask2.csv (comma-separated, with header)
"""
from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "results" / "subtask2"
OUT = SRC_DIR / "subtask2.csv"

rows = []
for f in sorted(SRC_DIR.glob("task2_*.csv")):
    m = re.match(r"task2_(\d+)\.csv", f.name)
    if not m:
        continue
    res = int(m.group(1))
    with f.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            rep = int(parts[0])
            time_us = int(parts[6])
            rows.append({"resolution": res, "rep": rep, "time_us": time_us})

rows.sort(key=lambda r: (r["resolution"], r["rep"]))

with OUT.open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["resolution", "rep", "time_us"])
    w.writeheader()
    w.writerows(rows)

print(f"wrote {OUT} ({len(rows)} rows)")
