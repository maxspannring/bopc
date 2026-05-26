# Run summary — Sections 2.3 and 2.4

## SSH preflight
- Time: 2026-04-27 17:24:58 CEST
- Outcome: ok (login host `hydra-head`)

## Sweep A (Section 2.3 — influence of patch size)
- Job ID: 5118342
- Submitted: 2026-04-27 17:27:16; finished: 2026-04-27 17:30:17; elapsed: 00:03:01
- SLURM state: COMPLETED (ExitCode 0:0)
- Output CSV: `results_patch.csv` (1 header + 21 data rows)
- Runtime stats (s): min 0.4084, mean 8.4322, max 51.1392
  - patch=1 dominates (~50 s/run, 3 reps); all other patches ≤ 4 s.

## Sweep B (Section 2.4 — best patch size)
- Job ID: 5118343
- Submitted: 2026-04-27 17:27:16; finished: 2026-04-27 17:28:46; elapsed: 00:01:30
- SLURM state: COMPLETED (ExitCode 0:0)
- Output CSV: `results_optimal.csv` (1 header + 123 data rows)
- Runtime stats (s): min 0.5351, mean 0.5695, max 0.6175
- Best mean runtime: patch=27 at 0.5376 s. Minimum is shallow (all 41 patches lie within 0.535–0.618 s).

## Files created or modified locally
- `analyze_patch.py` (new)
- `results_patch.csv` (downloaded from hydra)
- `results_optimal.csv` (downloaded from hydra)
- `bench_patch.out`, `bench_optimal.out` (downloaded from hydra)
- `template/sbatch/bench_patch.job` (new)
- `template/sbatch/bench_optimal.job` (new)
- `template/report_assets/pgfdata/patch_influence.dat` (new)
- `template/report_assets/pgfdata/patch_optimal.dat` (new)
- `template/report_assets/table_patch_influence.tex` (new)
- `template/report_assets/table_patch_optimal.tex` (new)
- `template/report_assets/plot_patch_influence.tex` (new)
- `template/report_assets/plot_patch_optimal.tex` (new)
- `template/report_assets/report_section.tex` (appended two new subsections)
- `template/bopc_report.pdf` (rebuilt)
- LaTeX aux files in `template/` (rebuilt as a side effect)

## Files created on hydra
- `~/bench_patch.job`
- `~/bench_optimal.job`
- `~/results_patch_5118342.csv`
- `~/results_optimal_5118343.csv`
- `~/bench_patch_5118342.out`
- `~/bench_optimal_5118343.out`

## LaTeX compile
- Result: success (latexmk; forced rebuild with `-g` to pick up the appended subsections)
- Pages: 11
- Warnings worth noting:
  - `LaTeX Warning: Float too large for page by 12.18387pt on input line 51.` — refers to a Section 2.2 figure region, pre-existing, not introduced here.
  - `pdfTeX warning (ext4): destination with the same identifier (name{table.1}) ...` and similar for `table.2`, `figure.1` … through `table.6`/`figure.6`. These start at table.1, so they pre-date the 2.3/2.4 additions (likely from `\listoftables` / `\listoffigures` interaction with hyperref). Per task instructions, `bopc_report.tex` was not modified.

## Anomalies
- Initial `ssh hydra "sbatch ..."` failed with `bash: sbatch: command not found`; resubmitted via `bash -lc` to pick up the login-shell PATH (`/usr/local/slurm-22.05.11/bin/sbatch`). Otherwise routine.
- `latexmk` first reported "Nothing to do" because its dependency tracking did not detect the `report_section.tex` mtime change in time; a forced rebuild (`-g`) produced the up-to-date 11-page PDF.
- The 41-row `table_patch_optimal.tex` originally used `[htb]` placement and LaTeX deferred the float to the end-of-document area (page 10), away from Section 2.4. Switched its placement specifier to `[H]` (the `float` package is already loaded) so the table renders inline with Section 2.4. After the fix, Table 4 sits on page 8 directly preceding Figure 8 on page 9. `analyze_patch.py` was also updated to emit `[H]` for the optimal table on future re-runs.

## How to verify quickly
```bash
head -5 results_patch.csv
head -5 results_optimal.csv
wc -l results_patch.csv results_optimal.csv         # expect 22 and 124
pdftotext template/bopc_report.pdf - | grep -E "patch_influence|patch_optimal|Influence of patch size|Finding the best patch size"
```
