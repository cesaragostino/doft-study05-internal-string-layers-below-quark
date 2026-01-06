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
from scipy.stats import spearmanr


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


def _coerce_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _select_r_column(df: pd.DataFrame) -> str:
    candidates = ["R_mean_lastW_mean", "R_network_S1_mean", "R_mean_lastW"]
    for col in candidates:
        if col in df.columns and _coerce_numeric(df[col]).notna().any():
            return col
    raise RuntimeError("No usable R column found in metrics CSV.")


def _select_coherence_column_for_scaling(df: pd.DataFrame) -> str:
    candidates = ["R_network_S1_mean", "R_mean_lastW_mean", "R_mean_lastW"]
    for col in candidates:
        if col in df.columns and _coerce_numeric(df[col]).notna().any():
            return col
    raise RuntimeError("No usable coherence column found in metrics CSV.")


def _load_template_classes(path: Optional[Path]) -> Dict[str, str]:
    if path is None:
        return {}
    if not path.exists():
        raise FileNotFoundError(f"Missing template classes file: {path}")
    if path.suffix.lower() == ".json":
        data = pd.read_json(path)
    else:
        data = pd.read_csv(path)
    if "template_name" not in data.columns or "template_class" not in data.columns:
        raise RuntimeError("Template class file must include template_name and template_class columns.")
    return dict(zip(data["template_name"].astype(str), data["template_class"].astype(str)))


def _select_promoted_column(df: pd.DataFrame) -> str:
    for col in ["promoted", "is_promoted"]:
        if col in df.columns:
            return col
    raise RuntimeError("No promoted flag found in metrics CSV.")


def _select_candidate_column(df: pd.DataFrame) -> Optional[str]:
    for col in ["is_candidate", "candidate"]:
        if col in df.columns:
            return col
    return None


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

    r_col = _select_coherence_column_for_scaling(df)
    df[r_col] = _coerce_numeric(df[r_col])
    df = df[df[r_col].notna()].copy()
    stats = df.groupby("node_count")[r_col].mean().reset_index()
    x_mean = stats["node_count"].values
    y_mean = stats[r_col].values

    popt, _pcov = curve_fit(_power_law, x_mean, y_mean, p0=[0.8, -0.33], maxfev=10000)
    a_fit, b_fit = popt

    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df,
        x="node_count",
        y=r_col,
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
    vals = df[r_col].dropna().to_numpy()
    if vals.size:
        q_lo = np.quantile(vals, 0.01)
        q_hi = np.quantile(vals, 0.99)
        y_min = max(0.15, q_lo - 0.03)
        y_max = min(1.0, q_hi + 0.03)
        if y_max - y_min < 0.2:
            y_min = max(0.15, vals.min() - 0.03)
            y_max = min(1.0, vals.max() + 0.03)
        plt.ylim(y_min, y_max)
    else:
        plt.ylim(0, 1.0)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(out_dir / "Figure_1_Coherence_Scaling.png")
    plt.close()


def _load_s2_dataset(metrics_csv: Path, genome_csv: Optional[Path], wave_label: str) -> pd.DataFrame:
    df_met = _load_csv(metrics_csv)
    if "S2_share" in df_met.columns:
        df = df_met.copy()
        df["S2_Share"] = _coerce_numeric(df["S2_share"])
    else:
        if genome_csv is None:
            raise RuntimeError("Missing genome CSV for S2_share derivation.")
        df_gen = _load_csv(genome_csv)
        cols_gen = ["entity_id", "pS1_mean", "pS2_mean"]
        for col in cols_gen:
            if col not in df_gen.columns:
                raise RuntimeError(f"Missing column in genome CSV: {col}")
        df = pd.merge(df_met, df_gen[cols_gen], on="entity_id", how="inner")
        df["S2_Share"] = df["pS2_mean"] / (df["pS1_mean"] + df["pS2_mean"] + 1e-9)
    df["Wave"] = wave_label
    return df


def figure_2_memory_overhead(
    metrics_ola3: Path,
    genome_ola3: Path,
    out_dir: Path,
    metrics_ola2: Optional[Path] = None,
    genome_ola2: Optional[Path] = None,
    metrics_ola4: Optional[Path] = None,
    genome_ola4: Optional[Path] = None,
) -> None:
    _style()
    frames = []
    if metrics_ola2 and genome_ola2:
        frames.append(_load_s2_dataset(metrics_ola2, genome_ola2, "Wave 2"))
    frames.append(_load_s2_dataset(metrics_ola3, genome_ola3, "Wave 3"))
    if metrics_ola4 and genome_ola4:
        frames.append(_load_s2_dataset(metrics_ola4, genome_ola4, "Wave 4"))
    df = pd.concat(frames, ignore_index=True)
    promoted_col = _select_promoted_column(df)
    df[promoted_col] = df[promoted_col].fillna(False)

    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df,
        x="node_count",
        y="S2_Share",
        hue=promoted_col,
        style=promoted_col,
        palette={True: "#2ca02c", False: "#7f7f7f"},
        markers={True: "o", False: "X"},
        alpha=0.6,
        s=70,
    )

    stats = df.groupby(["node_count", promoted_col])["S2_Share"].agg(
        mean="mean",
        median="median",
        count="count",
    ).reset_index()
    for is_promoted, color, label_prefix in [(True, "#1b9e77", "Promoted"), (False, "#666666", "Non-promoted")]:
        subset = stats[stats[promoted_col] == is_promoted].sort_values("node_count")
        label = f"{label_prefix} mean"
        plt.plot(subset["node_count"], subset["mean"], "o-", color=color, linewidth=2, label=label)
        for _, row in subset.iterrows():
            plt.annotate(
                f"n={int(row['count'])}",
                (row["node_count"], row["mean"]),
                textcoords="offset points",
                xytext=(0, 8 if is_promoted else -10),
                ha="center",
                fontsize=9,
                color=color,
            )

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
    df2: pd.DataFrame,
    df3: pd.DataFrame,
    out_dir: Path,
    df4: Optional[pd.DataFrame] = None,
    template_classes: Optional[Dict[str, str]] = None,
) -> None:
    _style()
    frames = [df2, df3]
    if df4 is not None:
        frames.append(df4)
    df = pd.concat(frames, ignore_index=True)
    if template_classes:
        df["template_class"] = df["template_name"].map(template_classes).fillna("other")
    else:
        df["template_class"] = "other"

    stats = df.groupby(["template_name", "node_count"]).agg(
        promoted_rate=("promoted", "mean"),
        n=("entity_id", "count"),
    ).reset_index()

    pivot_rate = stats.pivot(index="template_name", columns="node_count", values="promoted_rate")
    pivot_count = stats.pivot(index="template_name", columns="node_count", values="n")
    pivot_rate = pivot_rate.sort_index(axis=1).sort_index(axis=0)
    pivot_count = pivot_count.reindex(index=pivot_rate.index, columns=pivot_rate.columns)

    annot = _build_heatmap_annotations(pivot_rate, pivot_count)

    plt.figure(figsize=(13, 9))
    ax = sns.heatmap(
        pivot_rate,
        annot=annot,
        fmt="",
        cmap="RdYlBu",
        linewidths=0.5,
        cbar_kws={"label": "Promoted rate"},
        vmin=0,
        vmax=1,
        annot_kws={"fontsize": 9},
    )
    ax.set_title("Topological selectivity and monolithic ceiling (N≈8–9)")
    ax.set_xlabel("Network size (N)")
    ax.set_ylabel("Topology (template)")
    if template_classes:
        class_order = ["monolithic", "modular", "other"]
        template_to_class = df[["template_name", "template_class"]].drop_duplicates().set_index("template_name")[
            "template_class"
        ]
        ordered_templates = sorted(
            pivot_rate.index,
            key=lambda name: (class_order.index(template_to_class.get(name, "other")), name),
        )
        pivot_rate = pivot_rate.reindex(index=ordered_templates)
        pivot_count = pivot_count.reindex(index=ordered_templates)
        annot = _build_heatmap_annotations(pivot_rate, pivot_count)
        ax.clear()
        ax = sns.heatmap(
            pivot_rate,
            annot=annot,
            fmt="",
            cmap="RdYlBu",
            linewidths=0.5,
            cbar_kws={"label": "Promoted rate"},
            vmin=0,
            vmax=1,
            annot_kws={"fontsize": 9},
        )
        ax.set_title("Topological selectivity and monolithic ceiling (N≈8–9)")
        ax.set_xlabel("Network size (N)")
        ax.set_ylabel("Topology (template)")
        class_counts = (
            pd.Series(ordered_templates)
            .map(lambda name: template_to_class.get(name, "other"))
            .value_counts()
        )
        offset = 0
        for cls in class_order:
            count = class_counts.get(cls, 0)
            if count:
                ax.hlines(offset + count, *ax.get_xlim(), colors="black", linewidth=1)
                ax.text(
                    ax.get_xlim()[1] + 0.1,
                    offset + count / 2,
                    cls,
                    va="center",
                    fontsize=10,
                )
                offset += count
    plt.tight_layout()
    plt.savefig(out_dir / "Figure_3_Topology_Ceiling.png")
    plt.close()


def figure_4_mechanism_s2_r_residual(
    metrics_ola3: Path,
    genome_ola3: Path,
    out_dir: Path,
    metrics_ola2: Optional[Path] = None,
    genome_ola2: Optional[Path] = None,
    metrics_ola4: Optional[Path] = None,
    genome_ola4: Optional[Path] = None,
) -> None:
    _style()
    frames = []
    if metrics_ola2 and genome_ola2:
        frames.append(_load_s2_dataset(metrics_ola2, genome_ola2, "Wave 2"))
    frames.append(_load_s2_dataset(metrics_ola3, genome_ola3, "Wave 3"))
    if metrics_ola4 and genome_ola4:
        frames.append(_load_s2_dataset(metrics_ola4, genome_ola4, "Wave 4"))
    df = pd.concat(frames, ignore_index=True)
    r_col = _select_r_column(df)
    df[r_col] = _coerce_numeric(df[r_col])
    df["S2_Share"] = _coerce_numeric(df["S2_Share"])
    df = df[df[r_col] > 0.0]

    base = df.groupby("node_count")[r_col].mean().rename("R_hat").reset_index()
    df = df.merge(base, on="node_count", how="left")
    df["R_resid"] = df[r_col] - df["R_hat"]
    df = df[np.isfinite(df["S2_Share"]) & np.isfinite(df["R_resid"])].copy()

    plt.figure(figsize=(10, 6))
    size_vals = df.get("robust_score_v2")
    sizes = None
    if size_vals is not None:
        size_vals = _coerce_numeric(size_vals)
        if np.isfinite(size_vals).any():
            sizes = 20 + 80 * (size_vals.fillna(0).clip(0, 1))

    sc = plt.scatter(
        df["S2_Share"],
        df["R_resid"],
        c=df["node_count"],
        cmap="viridis",
        s=sizes if sizes is not None else 50,
        alpha=0.7,
        edgecolor="none",
    )
    plt.colorbar(sc, label="N (nodes)")
    if len(df) >= 2 and df["S2_Share"].nunique() >= 2:
        try:
            coeff = np.polyfit(df["S2_Share"], df["R_resid"], deg=1)
        except np.linalg.LinAlgError:
            coeff = None
        if coeff is not None and np.isfinite(coeff).all():
            x_line = np.linspace(df["S2_Share"].min(), df["S2_Share"].max(), 100)
            y_line = coeff[0] * x_line + coeff[1]
            plt.plot(x_line, y_line, "k--", linewidth=2, label=f"Trend: slope={coeff[0]:.3f}")
            plt.legend(loc="upper left")
    plt.title("Mechanism check: S2 vs coherence residual (within-N)")
    plt.xlabel("S2 participation")
    plt.ylabel("Coherence residual (R - mean_R(N))")
    plt.tight_layout()
    plt.savefig(out_dir / "Figure_4_Mechanism_S2_R_residual.png")
    plt.close()


def appendix_b_candidate_heatmap(
    df2: pd.DataFrame, df3: pd.DataFrame, out_dir: Path, df4: Optional[pd.DataFrame] = None
) -> None:
    _style()
    frames = [df2, df3]
    if df4 is not None:
        frames.append(df4)
    df = pd.concat(frames, ignore_index=True)
    cand_col = _select_candidate_column(df)
    if cand_col is None:
        print("[paper_figures] skip Appendix_B_candidate_heatmap (missing candidate flag).")
        return
    df[cand_col] = df[cand_col].fillna(False)

    stats = df.groupby(["template_name", "node_count"]).agg(
        candidate_rate=(cand_col, "mean"),
        n=("entity_id", "count"),
    ).reset_index()
    pivot_rate = stats.pivot(index="template_name", columns="node_count", values="candidate_rate")
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
        cbar_kws={"label": "Candidate rate"},
        vmin=0,
        vmax=1,
    )
    ax.set_title("Candidate-rate by topology and N")
    ax.set_xlabel("Network size (N)")
    ax.set_ylabel("Topology (template)")
    plt.tight_layout()
    plt.savefig(out_dir / "Appendix_B_candidate_heatmap.png")
    plt.close()


def appendix_e_funnel(df2: pd.DataFrame, df3: pd.DataFrame, out_dir: Path, df4: Optional[pd.DataFrame] = None) -> None:
    _style()
    frames = [df2, df3]
    if df4 is not None:
        frames.append(df4)
    df = pd.concat(frames, ignore_index=True)
    cand_col = _select_candidate_column(df)
    if cand_col is None:
        print("[paper_figures] skip Appendix_E funnel (missing candidate flag).")
        return
    promoted_col = _select_promoted_column(df)
    df[cand_col] = df[cand_col].fillna(False)
    df[promoted_col] = df[promoted_col].fillna(False)

    stats = df.groupby("node_count").agg(
        evaluated_count=("entity_id", "count"),
        candidate_count=(cand_col, "sum"),
        promoted_count=(promoted_col, "sum"),
    ).reset_index()
    stats["candidate_rate"] = stats["candidate_count"] / stats["evaluated_count"].replace(0, np.nan)
    stats["promoted_rate"] = stats["promoted_count"] / stats["evaluated_count"].replace(0, np.nan)
    stats["promoted_given_candidate"] = stats["promoted_count"] / stats["candidate_count"].replace(0, np.nan)

    plt.figure(figsize=(10, 6))
    plt.plot(stats["node_count"], stats["evaluated_count"], "o-", label="Evaluated")
    plt.plot(stats["node_count"], stats["candidate_count"], "o-", label="Candidate")
    plt.plot(stats["node_count"], stats["promoted_count"], "o-", label="Promoted")
    plt.title("Selection funnel counts vs N")
    plt.xlabel("Network size (N)")
    plt.ylabel("Count")
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(out_dir / "Appendix_E_funnel_counts.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(stats["node_count"], stats["candidate_rate"], "o-", label="Candidate rate")
    plt.plot(stats["node_count"], stats["promoted_rate"], "o-", label="Promoted rate")
    plt.plot(stats["node_count"], stats["promoted_given_candidate"], "o-", label="Promoted | Candidate")
    plt.title("Selection funnel rates vs N")
    plt.xlabel("Network size (N)")
    plt.ylabel("Rate")
    plt.ylim(0, 1.0)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(out_dir / "Appendix_E_funnel_rates.png")
    plt.close()


def appendix_e_sensitivity_common_threshold(
    df2: pd.DataFrame, df3: pd.DataFrame, out_dir: Path, df4: Optional[pd.DataFrame] = None, r_common: float = 0.85
) -> None:
    _style()
    frames = [df2, df3]
    if df4 is not None:
        frames.append(df4)
    df = pd.concat(frames, ignore_index=True)
    r_col = _select_r_column(df)
    df[r_col] = _coerce_numeric(df[r_col])
    df = df[df[r_col].notna()]
    df["candidate_common"] = df[r_col] >= r_common

    stats = df.groupby("node_count").agg(
        candidate_common_rate=("candidate_common", "mean"),
        n=("entity_id", "count"),
    ).reset_index()

    plt.figure(figsize=(10, 6))
    plt.plot(stats["node_count"], stats["candidate_common_rate"], "o-", label=f"R >= {r_common}")
    plt.title("Common-threshold sensitivity (candidate rate)")
    plt.xlabel("Network size (N)")
    plt.ylabel("Candidate rate (common threshold)")
    plt.ylim(0, 1.0)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(out_dir / "Appendix_E_sensitivity_common_threshold.png")
    plt.close()


def appendix_e_grade_compare(
    df2: pd.DataFrame, df3: pd.DataFrame, out_dir: Path, df4: Optional[pd.DataFrame] = None
) -> None:
    _style()
    frames = [df2, df3]
    if df4 is not None:
        frames.append(df4)
    df = pd.concat(frames, ignore_index=True)
    if "dof_grade" not in df.columns:
        print("[paper_figures] skip Appendix_E_grade_compare (missing dof_grade).")
        return
    r_col = _select_r_column(df)
    df[r_col] = _coerce_numeric(df[r_col])

    df_a = df[df["dof_grade"] == "A"]
    df_ab = df[df["dof_grade"].isin(["A", "B"])]
    stats_a = df_a.groupby("node_count")[r_col].mean().reset_index()
    stats_ab = df_ab.groupby("node_count")[r_col].mean().reset_index()

    plt.figure(figsize=(10, 6))
    plt.plot(stats_a["node_count"], stats_a[r_col], "o-", label="Grade A")
    plt.plot(stats_ab["node_count"], stats_ab[r_col], "o-", label="Grade A/B")
    plt.title("Grade sensitivity (mean coherence vs N)")
    plt.xlabel("Network size (N)")
    plt.ylabel("Mean coherence (R)")
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(out_dir / "Appendix_E_grade_compare.png")
    plt.close()


def appendix_c_spearman_by_n(
    metrics_ola3: Path,
    genome_ola3: Path,
    out_dir: Path,
    metrics_ola2: Optional[Path] = None,
    genome_ola2: Optional[Path] = None,
    metrics_ola4: Optional[Path] = None,
    genome_ola4: Optional[Path] = None,
) -> None:
    _style()
    frames = []
    if metrics_ola2 and genome_ola2:
        frames.append(_load_s2_dataset(metrics_ola2, genome_ola2, "Wave 2"))
    frames.append(_load_s2_dataset(metrics_ola3, genome_ola3, "Wave 3"))
    if metrics_ola4 and genome_ola4:
        frames.append(_load_s2_dataset(metrics_ola4, genome_ola4, "Wave 4"))
    df = pd.concat(frames, ignore_index=True)
    r_col = _select_coherence_column_for_scaling(df)
    df[r_col] = _coerce_numeric(df[r_col])
    df["S2_Share"] = _coerce_numeric(df["S2_Share"])
    df = df[df[r_col].notna() & df["S2_Share"].notna()].copy()

    rows = []
    for n_val, group in df.groupby("node_count"):
        if group["S2_Share"].nunique() < 2 or group[r_col].nunique() < 2:
            continue
        rho, pval = spearmanr(group["S2_Share"], group[r_col])
        rows.append({"node_count": n_val, "rho": rho, "pval": pval, "n": len(group)})
    if not rows:
        print("[paper_figures] skip Appendix_C_spearman_by_n (insufficient data).")
        return
    stats = pd.DataFrame(rows).sort_values("node_count")

    plt.figure(figsize=(10, 6))
    plt.bar(stats["node_count"], stats["rho"], color="#4c72b0", alpha=0.8)
    for _, row in stats.iterrows():
        plt.annotate(
            f"n={int(row['n'])}",
            (row["node_count"], row["rho"]),
            textcoords="offset points",
            xytext=(0, 6 if row["rho"] >= 0 else -10),
            ha="center",
            fontsize=9,
        )
    plt.axhline(0, color="black", linewidth=1)
    plt.title("Within-N Spearman correlation: S2 vs coherence")
    plt.xlabel("Network size (N)")
    plt.ylabel("Spearman rho")
    plt.tight_layout()
    plt.savefig(out_dir / "Appendix_C_spearman_rho_by_n.png")
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate final paper figures and appendix plots.")
    parser.add_argument("--metrics-ola2", required=True, help="CSV for ola2 paper metrics.")
    parser.add_argument("--metrics-ola3", required=True, help="CSV for ola3 paper metrics.")
    parser.add_argument("--genome-ola2", help="Genome layers CSV for ola2.")
    parser.add_argument("--genome-ola3", required=True, help="Genome layers CSV for ola3.")
    parser.add_argument("--genome-ola4", help="Genome layers CSV for ola4.")
    parser.add_argument("--metrics-ola4", help="CSV for ola4 paper metrics.")
    parser.add_argument(
        "--template-classes",
        help="Optional CSV/JSON with template_name, template_class (monolithic/modular/other).",
    )
    parser.add_argument("--out-dir", default="data/processed/paper/final", help="Output directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    _ensure_dir(out_dir)

    df2 = _load_csv(Path(args.metrics_ola2))
    df3 = _load_csv(Path(args.metrics_ola3))
    df4 = _load_csv(Path(args.metrics_ola4)) if args.metrics_ola4 else None
    template_classes = _load_template_classes(Path(args.template_classes)) if args.template_classes else {}

    figure_1_coherence_scaling(df2, df3, out_dir, df4=df4)
    figure_2_memory_overhead(
        Path(args.metrics_ola3),
        Path(args.genome_ola3),
        out_dir,
        metrics_ola2=Path(args.metrics_ola2) if args.metrics_ola2 else None,
        genome_ola2=Path(args.genome_ola2) if args.genome_ola2 else None,
        metrics_ola4=Path(args.metrics_ola4) if args.metrics_ola4 else None,
        genome_ola4=Path(args.genome_ola4) if args.genome_ola4 else None,
    )
    figure_3_topology_heatmap(df2, df3, out_dir, df4=df4, template_classes=template_classes)
    figure_4_mechanism_s2_r_residual(
        Path(args.metrics_ola3),
        Path(args.genome_ola3),
        out_dir,
        metrics_ola2=Path(args.metrics_ola2) if args.metrics_ola2 else None,
        genome_ola2=Path(args.genome_ola2) if args.genome_ola2 else None,
        metrics_ola4=Path(args.metrics_ola4) if args.metrics_ola4 else None,
        genome_ola4=Path(args.genome_ola4) if args.genome_ola4 else None,
    )
    appendix_b_candidate_heatmap(df2, df3, out_dir, df4=df4)
    appendix_e_funnel(df2, df3, out_dir, df4=df4)
    appendix_e_sensitivity_common_threshold(df2, df3, out_dir, df4=df4)
    appendix_e_grade_compare(df2, df3, out_dir, df4=df4)
    appendix_c_spearman_by_n(
        Path(args.metrics_ola3),
        Path(args.genome_ola3),
        out_dir,
        metrics_ola2=Path(args.metrics_ola2) if args.metrics_ola2 else None,
        genome_ola2=Path(args.genome_ola2) if args.genome_ola2 else None,
        metrics_ola4=Path(args.metrics_ola4) if args.metrics_ola4 else None,
        genome_ola4=Path(args.genome_ola4) if args.genome_ola4 else None,
    )

    print(f"[paper_figures] wrote {out_dir}")


if __name__ == "__main__":
    main()
