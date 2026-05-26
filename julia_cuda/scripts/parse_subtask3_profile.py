#!/usr/bin/env python3
"""Parse ncu profile txt files into a tidy CSV.

Output: results/subtask3/subtask3_profile.csv
"""
from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "results" / "subtask3"
OUT = SRC_DIR / "subtask3_profile.csv"

# Metric labels we want from the ncu output
METRICS = {
    "sm__warps_active.avg.pct_of_peak_sustained_active": "occupancy_pct",
    "l1tex__t_bytes_pipe_lsu_mem_global_op_ld.sum.per_second": "gld_throughput",
    "l1tex__t_bytes_pipe_lsu_mem_global_op_st.sum.per_second": "gst_throughput_GBs",
    "smsp__thread_inst_executed_per_inst_executed.ratio": "warp_thread_eff",
}

def parse_value(val_str):
    # e.g. "48,97" (German locale commas) or "0" or "41,82"
    return float(val_str.replace(",", "."))

rows = []
for f in sorted(SRC_DIR.glob("ncu_*.txt")):
    m = re.match(r"ncu_(\d+)_(\d+)\.txt", f.name)
    if not m:
        continue
    bx, by = int(m.group(1)), int(m.group(2))
    row = {"block_x": bx, "block_y": by}
    text = f.read_text()
    for metric_key, col_name in METRICS.items():
        # Each data line: "    <metric_name>  <unit>  <value>"
        # Grab the last whitespace-delimited token on the line containing the metric key
        pat = re.compile(rf"^\s*{re.escape(metric_key)}\s+.*\s+(\S+)\s*$", re.MULTILINE)
        match = pat.search(text)
        row[col_name] = parse_value(match.group(1)) if match else None
    rows.append(row)

fields = ["block_x", "block_y"] + list(METRICS.values())
with OUT.open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

print(f"wrote {OUT}\n")
print(f"{'block':>12}  {'occupancy%':>12}  {'gst GB/s':>10}  {'warp_eff/32':>12}")
print("-" * 52)
for r in sorted(rows, key=lambda x: (x["block_x"], x["block_y"])):
    bstr = f"({r['block_x']},{r['block_y']})"
    print(f"  {bstr:>10}  {r['occupancy_pct']:>12.2f}  {r['gst_throughput_GBs']:>10.2f}  "
          f"{r['warp_thread_eff']:>12.2f}")
