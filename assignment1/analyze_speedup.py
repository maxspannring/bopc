"""
analyze_speedup.py

Reads results_speedup.csv, computes mean runtime / relative speed-up /
parallel efficiency for each (c_label, size, nprocs), and produces:

    overview_plots.png            -- matplotlib overview (sanity check)
    derived_metrics.csv           -- raw computed numbers

    report_assets/
        table_cb.tex              -- LaTeX table for c_b
        table_cs.tex              -- LaTeX table for c_s
        plot_cb_mean_runtime.tex  -- pgfplots snippet
        plot_cb_speedup.tex
        plot_cb_efficiency.tex
        plot_cs_mean_runtime.tex
        plot_cs_speedup.tex
        plot_cs_efficiency.tex
        report_section.tex        -- wrapper section pulling everything in
        pgfdata/
            cb_120.dat            -- data for pgfplots (one file per c+size)
            cb_1030.dat
            cs_120.dat
            cs_1030.dat
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
CSV_PATH = "results_speedup_5118230.csv"      # <-- change to your real CSV path
OUT_DIR  = Path("report_assets")
DAT_DIR  = OUT_DIR / "pgfdata"
OUT_DIR.mkdir(exist_ok=True)
DAT_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------------------------
# 1. Load + compute
# ----------------------------------------------------------------------
df = pd.read_csv(
    CSV_PATH,
    header=0,
    names=["c_label", "size", "patch", "nprocs", "runtime", "rep"],
)

mean_df = (
    df.groupby(["c_label", "size", "nprocs"], as_index=False)["runtime"]
      .mean()
      .rename(columns={"runtime": "mean_runtime"})
      .sort_values(["c_label", "size", "nprocs"])
      .reset_index(drop=True)
)
mean_df["T1"] = (
    mean_df.groupby(["c_label", "size"])["mean_runtime"].transform("first")
)
mean_df["speedup"]    = mean_df["T1"] / mean_df["mean_runtime"]
mean_df["efficiency"] = mean_df["speedup"] / mean_df["nprocs"]
mean_df.to_csv("derived_metrics.csv", index=False)

# ----------------------------------------------------------------------
# 2. Matplotlib overview plot (3x2 grid)
# ----------------------------------------------------------------------
fig, axes = plt.subplots(3, 2, figsize=(12, 11), sharex=True)
columns = [("student",   0, "$c_s$ (student)"),
           ("benchmark", 1, "$c_b$ (benchmark)")]
metrics_mpl = [("mean_runtime", "Mean runtime (s)"),
               ("speedup",      "Relative speed-up"),
               ("efficiency",   "Parallel efficiency")]
color_map = {120: "blue", 1030: "red"}

for c_label, col, col_title in columns:
    for row, (metric, ylabel) in enumerate(metrics_mpl):
        ax = axes[row, col]
        for size in [120, 1030]:
            sub = mean_df[(mean_df["c_label"] == c_label) &
                          (mean_df["size"]   == size)]
            ax.plot(sub["nprocs"], sub[metric],
                    color=color_map[size], linestyle=":",
                    marker="*", markersize=12,
                    label=f"size = {size}")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        ax.legend()
        if row == 0:
            ax.set_title(col_title)
        if row == 2:
            ax.set_xlabel("Number of workers $p$")
fig.suptitle("Julia set parallel benchmark - overview", fontsize=14)
fig.tight_layout()
fig.savefig("overview_plots.png", dpi=120, bbox_inches="tight")
plt.close(fig)

# ----------------------------------------------------------------------
# 3. PGFPlots data files (one per c_label x size)
# ----------------------------------------------------------------------
SHORT = {"benchmark": "cb", "student": "cs"}
MATH  = {"benchmark": "c_b", "student": "c_s"}

for (c_label, size), sub in mean_df.groupby(["c_label", "size"]):
    short = SHORT[c_label]
    path  = DAT_DIR / f"{short}_{size}.dat"
    with open(path, "w") as f:
        f.write("nprocs mean_runtime speedup efficiency\n")
        for _, r in sub.iterrows():
            f.write(f"{int(r['nprocs'])} "
                    f"{r['mean_runtime']:.6f} "
                    f"{r['speedup']:.6f} "
                    f"{r['efficiency']:.6f}\n")

# ----------------------------------------------------------------------
# 4. LaTeX tables (booktabs)
# ----------------------------------------------------------------------
def make_table(c_label):
    """Match the format already in the user's bopc_report.tex template:
       - [htb] placement
       - caption with label embedded
       - rrrrr columns, booktabs rules
       - \\sizes / \\sizel macros for the size column
       - label tab:runtime_cs / tab:runtime_cb
    """
    sub = mean_df[mean_df["c_label"] == c_label]
    short = SHORT[c_label]   # "cb" or "cs"
    cmath = MATH[c_label]    # "c_b" or "c_s"

    sizes_in_data = sorted(sub["size"].unique())
    # smaller size -> \sizes, larger size -> \sizel
    size_macro = {sizes_in_data[0]: r"\sizes",
                  sizes_in_data[1]: r"\sizel"}

    out = []
    out.append(r"\begin{table}[htb]")
    out.append(r" \centering")
    out.append(r"\caption{\label{tab:runtime_" + short + r"}"
               r"Runtime and speed-up of parallel Julia set generator "
               r"for $" + cmath + r"$ case.}")
    out.append(r"\begin{tabular}{rrrrr}")
    out.append(r"  \toprule")
    out.append(r"  size & p & mean runtime (s) & speed-up & par. eff.\\")
    out.append(r"  \midrule")
    for _, r in sub.iterrows():
        macro = size_macro[int(r["size"])]
        p     = int(r["nprocs"])
        out.append(f"  {macro} & {p} & {r['mean_runtime']:.4f} & "
                   f"{r['speedup']:.3f} & {r['efficiency']:.3f} \\\\")
    out.append(r"  \bottomrule")
    out.append(r"\end{tabular}")
    out.append(r"\end{table}")
    return "\n".join(out) + "\n"

for c in ["benchmark", "student"]:
    (OUT_DIR / f"table_{SHORT[c]}.tex").write_text(make_table(c))

# ----------------------------------------------------------------------
# 5. PGFPlots snippets
# ----------------------------------------------------------------------
def make_plot(c_label, metric, ylabel):
    short = SHORT[c_label]
    cmath = MATH[c_label]
    f120  = f"report_assets/pgfdata/{short}_120.dat"
    f1030 = f"report_assets/pgfdata/{short}_1030.dat"
    return rf"""\begin{{tikzpicture}}
\begin{{axis}}[
    xlabel={{Number of workers $p$}},
    ylabel={{{ylabel}}},
    title={{${cmath}$}},
    legend pos=north east,
    grid=major,
    width=0.85\linewidth,
    height=6cm,
    xtick={{1,2,4,8,16,24,32}},
]
\addplot[blue, dotted, thick, mark=star, mark size=3pt]
    table[x=nprocs, y={metric}] {{{f120}}};
\addlegendentry{{size = 120}}
\addplot[red, dotted, thick, mark=star, mark size=3pt]
    table[x=nprocs, y={metric}] {{{f1030}}};
\addlegendentry{{size = 1030}}
\end{{axis}}
\end{{tikzpicture}}
"""

plot_specs = [
    ("mean_runtime", "Mean runtime (s)"),
    ("speedup",      "Relative speed-up"),
    ("efficiency",   "Parallel efficiency"),
]
for c_label in ["benchmark", "student"]:
    for metric, ylabel in plot_specs:
        path = OUT_DIR / f"plot_{SHORT[c_label]}_{metric}.tex"
        path.write_text(make_plot(c_label, metric, ylabel))

# ----------------------------------------------------------------------
# 6. Wrapper section with discussion placeholders
# ----------------------------------------------------------------------
section = r"""% Auto-generated section for Assignment 2.2.
% Required packages in the main document:
%     \usepackage{booktabs}
%     \usepackage{float}        % for [H] placement on figures
%     \usepackage{pgfplots}
%     \pgfplotsset{compat=1.18}
%
% Required \def lines in the main document (update to match the data!):
%     \def\sizes{120}
%     \def\sizel{1030}

\input{report_assets/table_cs.tex}

\input{report_assets/table_cb.tex}

Tables~\ref{tab:runtime_cs} and~\ref{tab:runtime_cb} present the parallel
runtime measurements and the respective speed-up and efficiency values
for the cases $c_s$ and $c_b$.

\subsubsection*{Plots for $c = c_b$ (benchmark)}

\begin{figure}[H]
\centering
\input{report_assets/plot_cb_mean_runtime.tex}
\caption{Mean runtime versus number of workers for $c = c_b$.}
\label{fig:cb-runtime}
\end{figure}

\noindent\textit{[Placeholder discussion of Figure~\ref{fig:cb-runtime}:
2--3 sentences describing how runtime decreases with $p$ for both problem
sizes and where diminishing returns set in.]}

\begin{figure}[H]
\centering
\input{report_assets/plot_cb_speedup.tex}
\caption{Relative speed-up versus number of workers for $c = c_b$.}
\label{fig:cb-speedup}
\end{figure}

\noindent\textit{[Placeholder discussion of Figure~\ref{fig:cb-speedup}:
2--3 sentences on how close speed-up is to the ideal $S(p)=p$ line and
how the two sizes compare.]}

\begin{figure}[H]
\centering
\input{report_assets/plot_cb_efficiency.tex}
\caption{Parallel efficiency versus number of workers for $c = c_b$.}
\label{fig:cb-efficiency}
\end{figure}

\noindent\textit{[Placeholder discussion of Figure~\ref{fig:cb-efficiency}:
2--3 sentences on how efficiency drops with $p$ and which size tolerates
parallelism better.]}

\subsubsection*{Plots for $c = c_s$ (student)}

\begin{figure}[H]
\centering
\input{report_assets/plot_cs_mean_runtime.tex}
\caption{Mean runtime versus number of workers for $c = c_s$.}
\label{fig:cs-runtime}
\end{figure}

\noindent\textit{[Placeholder discussion of Figure~\ref{fig:cs-runtime}.]}

\begin{figure}[H]
\centering
\input{report_assets/plot_cs_speedup.tex}
\caption{Relative speed-up versus number of workers for $c = c_s$.}
\label{fig:cs-speedup}
\end{figure}

\noindent\textit{[Placeholder discussion of Figure~\ref{fig:cs-speedup}.]}

\begin{figure}[H]
\centering
\input{report_assets/plot_cs_efficiency.tex}
\caption{Parallel efficiency versus number of workers for $c = c_s$.}
\label{fig:cs-efficiency}
\end{figure}

\noindent\textit{[Placeholder discussion of Figure~\ref{fig:cs-efficiency}.]}

\subsubsection*{Comparison of $c_b$ and $c_s$}

\noindent\textit{[Placeholder: a few sentences contrasting the two
workloads and explaining how the different per-pixel iteration counts
of $c_b$ and $c_s$ influence absolute runtime, scalability, and
efficiency.]}
"""

(OUT_DIR / "report_section.tex").write_text(section)

print("Done.")
print("  matplotlib overview : overview_plots.png")
print("  derived numbers     : derived_metrics.csv")
print("  LaTeX assets        :", OUT_DIR.resolve())
