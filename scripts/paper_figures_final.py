#!/usr/bin/env python3
"""Generate final paper figures (1-4) with consistent styling."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit


def _load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing CSV: {path}")
    return pd.read_csv(path)


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _power_law(x: np.ndarray, a: float, b: float) -> np.ndarray:
    return a * np.power(x, b)


def _style() -> None:
    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 300,
            "font.family": "DejaVu Sans",
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "legend.fontsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )


def figure_1_coherence_scaling(
    df2: pd.DataFrame, df3: pd.DataFrame, out_dir: Path, df4: Optional[pd.DataFrame] = None
) -> None:
    _style()
    df2 = df2.copy()
    df3 = df3.copy()
    df2["Wave"] = "Wave 2 (Simple)"
    df3["Wave"] = "Wave 3 (Complex)"
    frames = [df2, df3]
    palette = ["#377eb8", "#ff7f00"]
    if df4 is not None:
        df4 = df4.copy()
        df4["Wave"] = "Wave 4 (Large)"
        frames.append(df4)
        palette.append("#4daf4a")
    df = pd.concat(frames, ignore_index=True)

    stats = df.groupby("node_count")["R_network_S1_mean"].mean().reset_index()
    x_mean = stats["node_count"].values
    y_mean = stats["R_network_S1_mean"].values

    popt, _pcov = curve_fit(_power_law, x_mean, y_mean, p0=[0.8, -0.33], maxfev=10000)
    a_fit, b_fit = popt

    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df,
        x="node_count",
        y="R_network_S1_mean",
        hue="Wave",
        alpha=0.35,
        palette=palette,
        edgecolor="none",
    )

    x_line = np.linspace(df["node_count"].min(), df["node_count"].max(), 200)
    y_line = _power_law(x_line, a_fit, b_fit)
    label_fit = f"Fit: R ~ N^{b_fit:.2f} (ref ~ -0.33)"
    plt.plot(x_line, y_line, "r--", linewidth=2.2, label=label_fit)

    plt.plot(x_mean, y_mean, "kX", markersize=8, label="Mean per N")
    plt.title("Geometric decay of coherence (R) vs complexity (N)")
    plt.xlabel("Number of nodes (N)")
    plt.ylabel("Global coherence (R)")
    plt.ylim(0, 1.0)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(out_dir / "Figure_1_Coherence_Scaling.png")
    plt.close()


def figure_2_memory_overhead(
    metrics_csv: Path, genome_csv: Path, out_dir: Path
) -> None:
    _style()
    df_met = _load_csv(metrics_csv)
    df_gen = _load_csv(genome_csv)

    cols_gen = ["entity_id", "pS1_mean", "pS2_mean"]
    for col in cols_gen:
        if col not in df_gen.columns:
            raise RuntimeError(f"Missing column in genome CSV: {col}")

    df = pd.merge(df_met, df_gen[cols_gen], on="entity_id", how="inner")
    df["S2_Share"] = df["pS2_mean"] / (df["pS1_mean"] + df["pS2_mean"] + 1e-9)

    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df,
        x="node_count",
        y="S2_Share",
        hue="promoted",
        style="promoted",
        palette={True: "#2ca02c", False: "#7f7f7f"},
        markers={True: "o", False: "X"},
        alpha=0.6,
        s=70,
    )

    means = df.groupby("node_count")["S2_Share"].mean().reset_index()
    plt.plot(means["node_count"], means["S2_Share"], "k--", linewidth=2, label="Mean trend")

    plt.title("Memory overhead: S2 participation vs N")
    plt.xlabel("Network complexity (N)")
    plt.ylabel("S2 participation (0.0–1.0)")
    plt.legend(title="Promoted", loc="upper left")
    plt.tight_layout()
    plt.savefig(out_dir / "Figure_2_Memory_Overhead.png")
    plt.close()


def _build_heatmap_annotations(pivot_rate: pd.DataFrame, counts: pd.DataFrame) -> pd.DataFrame:
    ann = pivot_rate.copy().astype(object)
    for row_name in ann.index:
        for col_name in ann.columns:
            rate = pivot_rate.loc[row_name, col_name]
            n_val = counts.loc[row_name, col_name] if row_name in counts.index else np.nan
            if pd.isna(rate) or pd.isna(n_val):
                ann.loc[row_name, col_name] = ""
            else:
                ann.loc[row_name, col_name] = f"{rate:.2f}\n(n={int(n_val)})"
    return ann


def figure_3_topology_heatmap(
    df2: pd.DataFrame, df3: pd.DataFrame, out_dir: Path, df4: Optional[pd.DataFrame] = None
) -> None:
    _style()
    frames = [df2, df3]
    if df4 is not None:
        frames.append(df4)
    df = pd.concat(frames, ignore_index=True)

    stats = df.groupby(["template_name", "node_count"]).agg(
        promoted_rate=("promoted", "mean"),
        n=("entity_id", "count"),
    ).reset_index()

    pivot_rate = stats.pivot(index="template_name", columns="node_count", values="promoted_rate")
    pivot_count = stats.pivot(index="template_name", columns="node_count", values="n")
    pivot_rate = pivot_rate.sort_index(axis=1).sort_index(axis=0)
    pivot_count = pivot_count.reindex(index=pivot_rate.index, columns=pivot_rate.columns)

    annot = _build_heatmap_annotations(pivot_rate, pivot_count)

    plt.figure(figsize=(12, 8))
    ax = sns.heatmap(
        pivot_rate,
        annot=annot,
        fmt="",
        cmap="RdYlBu",
        linewidths=0.5,
        cbar_kws={"label": "Promoted rate"},
        vmin=0,
        vmax=1,
    )
    ax.set_title("Topological selectivity and monolithic ceiling (N≈8–9)")
    ax.set_xlabel("Network size (N)")
    ax.set_ylabel("Topology (template)")
    plt.tight_layout()
    plt.savefig(out_dir / "Figure_3_Topology_Ceiling.png")
    plt.close()


def figure_4_mechanism_s2_r(
    metrics_csv: Path, genome_csv: Path, out_dir: Path
) -> None:
    _style()
    df_met = _load_csv(metrics_csv)
    df_gen = _load_csv(genome_csv)
    cols_gen = ["entity_id", "pS1_mean", "pS2_mean"]
    for col in cols_gen:
        if col not in df_gen.columns:
            raise RuntimeError(f"Missing column in genome CSV: {col}")
    df = pd.merge(df_met, df_gen[cols_gen], on="entity_id", how="inner")
    df["S2_Share"] = df["pS2_mean"] / (df["pS1_mean"] + df["pS2_mean"] + 1e-9)
    df = df[df["R_network_S1_mean"] > 0.2]

    plt.figure(figsize=(10, 6))
    size_vals = df.get("robust_score_v2")
    sizes = None
    if size_vals is not None and np.isfinite(size_vals).any():
        sizes = 20 + 80 * (size_vals.fillna(0).clip(0, 1))

    sc = plt.scatter(
        df["S2_Share"],
        df["R_network_S1_mean"],
        c=df["node_count"],
        cmap="viridis",
        s=sizes if sizes is not None else 50,
        alpha=0.7,
        edgecolor="none",
    )
    plt.colorbar(sc, label="N (nodes)")
    plt.title("Mechanism check: coherence vs S2 memory")
    plt.xlabel("S2 participation")
    plt.ylabel("Global coherence (R)")
    plt.tight_layout()
    plt.savefig(out_dir / "Figure_4_Mechanism_S2_R.png")
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate final paper figures (1-4).")
    parser.add_argument("--metrics-ola2", required=True, help="CSV for ola2 paper metrics.")
    parser.add_argument("--metrics-ola3", required=True, help="CSV for ola3 paper metrics.")
    parser.add_argument("--genome-ola3", required=True, help="Genome layers CSV for ola3.")
    parser.add_argument("--metrics-ola4", help="CSV for ola4 paper metrics.")
    parser.add_argument("--out-dir", default="data/processed/paper/final", help="Output directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    _ensure_dir(out_dir)

    df2 = _load_csv(Path(args.metrics_ola2))
    df3 = _load_csv(Path(args.metrics_ola3))
    df4 = _load_csv(Path(args.metrics_ola4)) if args.metrics_ola4 else None

    figure_1_coherence_scaling(df2, df3, out_dir, df4=df4)
    figure_2_memory_overhead(Path(args.metrics_ola3), Path(args.genome_ola3), out_dir)
    figure_3_topology_heatmap(df2, df3, out_dir, df4=df4)
    figure_4_mechanism_s2_r(Path(args.metrics_ola3), Path(args.genome_ola3), out_dir)

    print(f"[paper_figures] wrote {out_dir}")


if __name__ == "__main__":
    main()
