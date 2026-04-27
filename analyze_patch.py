#!/usr/bin/env python3
"""Generate report assets for Sections 2.3 and 2.4 from sweep CSVs."""

import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "template" / "report_assets"
PGFDATA = ASSETS / "pgfdata"


def load(csv_path):
    """Return (size, nprocs, [(patch, [runtimes])]) sorted by patch."""
    by_patch = defaultdict(list)
    sizes, nprocs = set(), set()
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            sizes.add(int(row["size"]))
            nprocs.add(int(row["nprocs"]))
            by_patch[int(row["patch"])].append(float(row["runtime"]))
    assert len(sizes) == 1 and len(nprocs) == 1
    rows = sorted((p, rts) for p, rts in by_patch.items())
    return sizes.pop(), nprocs.pop(), rows


def write_dat(path, rows):
    with open(path, "w") as f:
        f.write("patch mean_runtime\n")
        for patch, rts in rows:
            f.write(f"{patch} {sum(rts) / len(rts):.6f}\n")


def write_table(path, size, nprocs, rows, caption, label, placement="htb"):
    with open(path, "w") as f:
        f.write(f"\\begin{{table}}[{placement}]\n")
        f.write(" \\centering\n")
        f.write(f"\\caption{{\\label{{{label}}}{caption}}}\n")
        f.write("\\begin{tabular}{rrrr}\n")
        f.write("  \\toprule\n")
        f.write("  size & p & patch & mean runtime (s)\\\\\n")
        f.write("  \\midrule\n")
        for patch, rts in rows:
            mean = sum(rts) / len(rts)
            f.write(f"  {size} & {nprocs} & {patch} & {mean:.4f} \\\\\n")
        f.write("  \\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")


def write_plot_log(path, dat_rel, title, xticks):
    ticks = ",".join(str(t) for t in xticks)
    with open(path, "w") as f:
        f.write(
            "\\begin{tikzpicture}\n"
            "\\begin{axis}[\n"
            "    xlabel={Patch size},\n"
            "    ylabel={Mean runtime (s)},\n"
            f"    title={{{title}}},\n"
            "    xmode=log,\n"
            "    log basis x=10,\n"
            f"    xtick={{{ticks}}},\n"
            "    xticklabels={" + ",".join(str(t) for t in xticks) + "},\n"
            "    log ticks with fixed point,\n"
            "    grid=major,\n"
            "    width=0.85\\linewidth,\n"
            "    height=6cm,\n"
            "]\n"
            "\\addplot[black, dotted, thick, mark=star, mark size=3pt]\n"
            f"    table[x=patch, y=mean_runtime] {{{dat_rel}}};\n"
            "\\end{axis}\n"
            "\\end{tikzpicture}\n"
        )


def write_plot_linear(path, dat_rel, title, xtick_step, xmin, xmax):
    with open(path, "w") as f:
        f.write(
            "\\begin{tikzpicture}\n"
            "\\begin{axis}[\n"
            "    xlabel={Patch size},\n"
            "    ylabel={Mean runtime (s)},\n"
            f"    title={{{title}}},\n"
            f"    xmin={xmin}, xmax={xmax},\n"
            f"    xtick distance={xtick_step},\n"
            "    minor x tick num=4,\n"
            "    grid=major,\n"
            "    width=0.85\\linewidth,\n"
            "    height=6cm,\n"
            "]\n"
            "\\addplot[black, dotted, thick, mark=star, mark size=3pt]\n"
            f"    table[x=patch, y=mean_runtime] {{{dat_rel}}};\n"
            "\\end{axis}\n"
            "\\end{tikzpicture}\n"
        )


def main():
    PGFDATA.mkdir(parents=True, exist_ok=True)

    # Section 2.3
    size_a, nproc_a, rows_a = load(ROOT / "results_patch.csv")
    write_dat(PGFDATA / "patch_influence.dat", rows_a)
    write_table(
        ASSETS / "table_patch_influence.tex",
        size_a, nproc_a, rows_a,
        caption=(
            "Mean runtime as a function of patch size, with $size = 880$ and "
            "$p = 32$, three repetitions per configuration."
        ),
        label="tab:patch_influence",
    )
    write_plot_log(
        ASSETS / "plot_patch_influence.tex",
        "report_assets/pgfdata/patch_influence.dat",
        title="$c_s$, size = 880, $p = 32$",
        xticks=[1, 5, 10, 20, 55, 150, 400],
    )

    # Section 2.4
    size_b, nproc_b, rows_b = load(ROOT / "results_optimal.csv")
    write_dat(PGFDATA / "patch_optimal.dat", rows_b)
    write_table(
        ASSETS / "table_patch_optimal.tex",
        size_b, nproc_b, rows_b,
        caption=(
            "Mean runtime as a function of patch size, with $size = 900$ and "
            "$p = 20$, three repetitions per configuration."
        ),
        label="tab:patch_optimal",
        placement="H",
    )
    write_plot_linear(
        ASSETS / "plot_patch_optimal.tex",
        "report_assets/pgfdata/patch_optimal.dat",
        title="$c_s$, size = 900, $p = 20$",
        xtick_step=5,
        xmin=20,
        xmax=60,
    )

    # Append the new subsections to report_section.tex
    section_path = ASSETS / "report_section.tex"
    existing = section_path.read_text()
    appendix = r"""

\subsection{Influence of patch size (Section 2.3)}

\input{report_assets/table_patch_influence.tex}

\begin{figure}[H]
\centering
\input{report_assets/plot_patch_influence.tex}
\caption{Mean runtime versus patch size for $c = c_s$, $size = 880$, $p = 32$.}
\label{fig:patch-influence}
\end{figure}

\noindent\textit{[Placeholder discussion of Figure~\ref{fig:patch-influence}:
2--3 sentences. Mention the trade-off between very small patches (high task
dispatch / serialization overhead in \texttt{multiprocessing.Pool}) and very
large patches (load imbalance, since some workers finish early).]}

\subsection{Finding the best patch size (Section 2.4)}

\input{report_assets/table_patch_optimal.tex}

\begin{figure}[H]
\centering
\input{report_assets/plot_patch_optimal.tex}
\caption{Mean runtime versus patch size for $c = c_s$, $size = 900$, $p = 20$,
fine sweep over $\text{patch} \in [20, 60]$.}
\label{fig:patch-optimal}
\end{figure}

\noindent\textit{[Placeholder discussion of Figure~\ref{fig:patch-optimal}:
2--3 sentences. Identify the patch size at which the minimum runtime occurs,
note how shallow or sharp the minimum is, and comment on whether 3 repetitions
is enough to clearly resolve the optimum given measurement noise.]}
"""
    if "tab:patch_influence" not in existing:
        section_path.write_text(existing + appendix)
        print("Appended subsections to report_section.tex")
    else:
        print("report_section.tex already contains 2.3/2.4 subsections; not re-appending")

    # Quick stdout summary
    print(f"\n[2.3] size={size_a} p={nproc_a} {len(rows_a)} patches")
    for p, rts in rows_a:
        print(f"  patch={p:>4d}  mean={sum(rts)/len(rts):8.4f}s  (n={len(rts)})")
    print(f"\n[2.4] size={size_b} p={nproc_b} {len(rows_b)} patches")
    best = min(rows_b, key=lambda pr: sum(pr[1]) / len(pr[1]))
    bp, brts = best
    print(f"  best patch = {bp}  mean={sum(brts)/len(brts):.4f}s")


if __name__ == "__main__":
    main()
