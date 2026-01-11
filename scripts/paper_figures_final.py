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
from scipy.stats import spearmanr, ttest_ind, pearsonr
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.patches import Rectangle


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


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40, 40)))


def _fit_logistic_regression(
    X: np.ndarray,
    y: np.ndarray,
    l2: float = 1e-4,
    max_iter: int = 60,
    tol: float = 1e-6,
) -> np.ndarray:
    n_features = X.shape[1]
    beta = np.zeros(n_features, dtype=float)
    for _ in range(max_iter):
        p = _sigmoid(X @ beta)
        w = p * (1.0 - p)
        w = np.clip(w, 1e-6, None)
        z = X @ beta + (y - p) / w
        XTW = X.T * w
        XTWX = XTW @ X
        XTWX += np.eye(n_features) * l2
        XTWz = XTW @ z
        try:
            beta_new = np.linalg.solve(XTWX, XTWz)
        except np.linalg.LinAlgError:
            beta_new = np.linalg.lstsq(XTWX, XTWz, rcond=None)[0]
        if np.linalg.norm(beta_new - beta) < tol:
            beta = beta_new
            break
        beta = beta_new
    return beta


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
    mask = (x_mean > 0) & (y_mean > 0)
    x_fit = x_mean[mask]
    y_fit = y_mean[mask]
    log_x = np.log(x_fit)
    log_y = np.log(y_fit)
    b_fit, a_log = np.polyfit(log_x, log_y, 1)
    a_fit = np.exp(a_log)

    rng = np.random.default_rng(42)
    b_samples = []
    if len(x_fit) >= 2:
        for _ in range(2000):
            idx = rng.integers(0, len(x_fit), size=len(x_fit))
            xs = x_fit[idx]
            ys = y_fit[idx]
            if np.any(xs <= 0) or np.any(ys <= 0):
                continue
            try:
                b_s, a_log_s = np.polyfit(np.log(xs), np.log(ys), 1)
            except np.linalg.LinAlgError:
                continue
            if np.isfinite(b_s):
                b_samples.append(b_s)
    if b_samples:
        b_mean = float(np.mean(b_samples))
        b_ci_low, b_ci_high = np.quantile(b_samples, [0.025, 0.975])
    else:
        b_mean = float(b_fit)
        b_ci_low = float("nan")
        b_ci_high = float("nan")

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
    if np.isfinite(b_ci_low) and np.isfinite(b_ci_high):
        label_fit = f"Fit: b={b_mean:.2f} [CI {b_ci_low:.2f}, {b_ci_high:.2f}]"
    else:
        label_fit = f"Fit: b={b_mean:.2f}"
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
    plt.legend(loc="lower left")

    if len(x_fit) >= 2 and len(y_fit) >= 2:
        ax_main = plt.gca()
        ax_in = ax_main.inset_axes([0.57, 0.57, 0.4, 0.4])
        ax_in.plot(x_fit, y_fit, "o", color="#444444", markersize=4)
        x_line_in = np.linspace(x_fit.min(), x_fit.max(), 100)
        y_line_in = _power_law(x_line_in, a_fit, b_fit)
        ax_in.plot(x_line_in, y_line_in, color="red", linewidth=1.5)
        ax_in.set_xscale("log")
        ax_in.set_yscale("log")
        ax_in.set_xlabel("N", fontsize=8)
        ax_in.set_ylabel("R", fontsize=8)
        if np.isfinite(b_ci_low) and np.isfinite(b_ci_high):
            label_ci = f"b={b_mean:.2f} [{b_ci_low:.2f}, {b_ci_high:.2f}]"
        else:
            label_ci = f"b={b_mean:.2f}"
        ax_in.text(0.05, 0.95, label_ci, transform=ax_in.transAxes, va="top", fontsize=8)

    plt.gcf().subplots_adjust(left=0.09, right=0.98, bottom=0.1, top=0.92)
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
    df["S2_Share"] = _coerce_numeric(df["S2_Share"])
    df = df[df["S2_Share"].notna()].copy()

    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")

    stats = df.groupby(["node_count", promoted_col])["S2_Share"].agg(mean="mean", count="count").reset_index()
    rng = np.random.default_rng(42)
    ci_rows = []
    for (n_val, is_promoted), group in df.groupby(["node_count", promoted_col]):
        vals = group["S2_Share"].dropna().to_numpy()
        if vals.size == 0:
            ci_rows.append(
                {"node_count": n_val, promoted_col: is_promoted, "ci_low": np.nan, "ci_high": np.nan}
            )
            continue
        means = []
        for _ in range(1000):
            sample = rng.choice(vals, size=len(vals), replace=True)
            means.append(float(np.mean(sample)))
        ci_low, ci_high = np.quantile(means, [0.025, 0.975])
        ci_rows.append(
            {"node_count": n_val, promoted_col: is_promoted, "ci_low": ci_low, "ci_high": ci_high}
        )
    stats = stats.merge(pd.DataFrame(ci_rows), on=["node_count", promoted_col], how="left")

    order = sorted(df["node_count"].unique())
    min_n_line = 10
    colors = {True: "#2ca02c", False: "#7f7f7f"}
    labels = {True: "Promoted (Survivor)", False: "Failed (non-survivor)"}

    for is_promoted in [True, False]:
        subset = stats[stats[promoted_col] == is_promoted].sort_values("node_count")
        if subset.empty:
            continue
        x_vals = subset["node_count"].to_numpy()
        y_vals = subset["mean"].to_numpy()
        y_err = np.vstack(
            [
                y_vals - subset["ci_low"].to_numpy(),
                subset["ci_high"].to_numpy() - y_vals,
            ]
        )
        counts = subset["count"].to_numpy()
        mask_line = counts >= min_n_line
        # draw line segments only where we have enough data
        if mask_line.any():
            idxs = np.where(mask_line)[0]
            seg_start = idxs[0]
            for i in range(1, len(idxs) + 1):
                if i == len(idxs) or (x_vals[idxs[i]] - x_vals[idxs[i - 1]] > 1):
                    seg = idxs[seg_start : i]
                    plt.plot(
                        x_vals[seg],
                        y_vals[seg],
                        color=colors[is_promoted],
                        linewidth=2.5,
                        marker="o",
                        markersize=8,
                        label=labels[is_promoted] if seg_start == idxs[0] else None,
                    )
                    if i < len(idxs):
                        seg_start = idxs[i]
        low_mask = ~mask_line
        if low_mask.any():
            # dashed connectors for any segment that includes low-n points
            for i in range(len(x_vals) - 1):
                if not (mask_line[i] and mask_line[i + 1]):
                    if is_promoted and x_vals[i + 1] >= 7:
                        continue
                    plt.plot(
                        [x_vals[i], x_vals[i + 1]],
                        [y_vals[i], y_vals[i + 1]],
                        color=colors[is_promoted],
                        linewidth=1.8,
                        linestyle="--",
                        alpha=0.6,
                    )
            for x, y, n in zip(x_vals[low_mask], y_vals[low_mask], counts[low_mask]):
                plt.scatter(
                    x,
                    y,
                    color=colors[is_promoted],
                    s=60,
                    edgecolor="white",
                    linewidth=0.5,
                    alpha=0.7,
                )
                if is_promoted:
                    plt.annotate(
                        f"n={int(n)}",
                        (x, y),
                        textcoords="offset points",
                        xytext=(0, 8),
                        ha="center",
                        fontsize=8,
                        color=colors[is_promoted],
                    )

    plt.title("Figure 2: Memory Overhead (S2) - Promoted vs Non-promoted", fontsize=14)
    plt.ylabel("S2 Participation (Memory Cost)", fontsize=12)
    plt.xlabel("Network Complexity (N)", fontsize=12)
    plt.legend(title="Outcome", loc="upper right")
    plt.text(
        0.02,
        0.04,
        "No failures observed for N≤5",
        transform=plt.gca().transAxes,
        fontsize=9,
        color="#444444",
    )
    plt.tight_layout()
    plt.savefig(out_dir / "Figure_2_Memory_Overhead.png", dpi=300)
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


def _parse_int(text: str) -> int:
    try:
        return int(text)
    except Exception:
        return 9999


def _template_sort_key(name: str) -> Tuple[int, int, str]:
    family_order = {"ring": 0, "ladder": 1, "bipartite": 2, "complete": 3, "other": 4}
    if not isinstance(name, str):
        return (family_order["other"], 9999, str(name))
    lower = name.lower()
    if lower.startswith("ring_"):
        size = _parse_int(lower.replace("ring_", ""))
        return (family_order["ring"], size, name)
    if lower.startswith("ladder_"):
        size = _parse_int(lower.replace("ladder_", ""))
        return (family_order["ladder"], size, name)
    if lower.startswith("complete_"):
        size = _parse_int(lower.replace("complete_", ""))
        return (family_order["complete"], size, name)
    if lower.startswith("bipartite_"):
        parts = lower.replace("bipartite_", "").split("_")
        if len(parts) >= 2:
            a = _parse_int(parts[0])
            b = _parse_int(parts[1])
            return (family_order["bipartite"], a + b, name)
        return (family_order["bipartite"], 9999, name)
    return (family_order["other"], 9999, name)


def _wilson_interval(k: np.ndarray, n: np.ndarray, z: float = 1.96) -> Tuple[np.ndarray, np.ndarray]:
    k = k.astype(float)
    n = n.astype(float)
    p = np.divide(k, n, out=np.zeros_like(k), where=n > 0)
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
    ci_low = np.where(n > 0, center - half, np.nan)
    ci_high = np.where(n > 0, center + half, np.nan)
    return ci_low, ci_high


def _add_wave_bands(ax: plt.Axes, columns: Iterable) -> None:
    try:
        cols = [int(c) for c in columns]
    except Exception:
        return
    ranges = [
        (2, 5, "#377eb8"),
        (6, 8, "#ff7f00"),
        (9, 12, "#4daf4a"),
    ]
    for n_min, n_max, color in ranges:
        idx = [i for i, n in enumerate(cols) if n_min <= n <= n_max]
        if not idx:
            continue
        left = min(idx)
        right = max(idx) + 1
        ax.axvspan(left, right, color=color, alpha=0.12, linewidth=0)


def figure_3_selection_funnel(
    df2: pd.DataFrame, df3: pd.DataFrame, out_dir: Path, df4: Optional[pd.DataFrame] = None
) -> None:
    _style()
    frames = [df2, df3]
    if df4 is not None:
        frames.append(df4)
    df = pd.concat(frames, ignore_index=True)
    cand_col = _select_candidate_column(df)
    if cand_col is None:
        print("[paper_figures] skip Figure_3_selection_funnel (missing candidate flag).")
        return
    promoted_col = _select_promoted_column(df)
    df[cand_col] = df[cand_col].fillna(False)
    df[promoted_col] = df[promoted_col].fillna(False)

    stats = df.groupby("node_count").agg(
        evaluated_count=("entity_id", "count"),
        candidate_count=(cand_col, "sum"),
        promoted_count=(promoted_col, "sum"),
    ).reset_index().sort_values("node_count")

    stats["candidate_rate"] = stats["candidate_count"] / stats["evaluated_count"].replace(0, np.nan)
    stats["promoted_rate"] = stats["promoted_count"] / stats["evaluated_count"].replace(0, np.nan)
    stats["promoted_given_candidate"] = stats["promoted_count"] / stats["candidate_count"].replace(0, np.nan)

    ci_cand = _wilson_interval(stats["candidate_count"].to_numpy(), stats["evaluated_count"].to_numpy())
    ci_prom = _wilson_interval(stats["promoted_count"].to_numpy(), stats["evaluated_count"].to_numpy())
    ci_prom_given = _wilson_interval(stats["promoted_count"].to_numpy(), stats["candidate_count"].to_numpy())

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True, gridspec_kw={"height_ratios": [2.2, 1]})
    ax_rates, ax_counts = axes

    ax_rates.errorbar(
        stats["node_count"],
        stats["candidate_rate"],
        yerr=[
            stats["candidate_rate"] - ci_cand[0],
            ci_cand[1] - stats["candidate_rate"],
        ],
        fmt="o-",
        color="#1f77b4",
        capsize=3,
        label="Candidate rate",
    )
    ax_rates.errorbar(
        stats["node_count"],
        stats["promoted_rate"],
        yerr=[
            stats["promoted_rate"] - ci_prom[0],
            ci_prom[1] - stats["promoted_rate"],
        ],
        fmt="o-",
        color="#d62728",
        capsize=3,
        label="Promoted rate",
    )
    ax_rates.errorbar(
        stats["node_count"],
        stats["promoted_given_candidate"],
        yerr=[
            stats["promoted_given_candidate"] - ci_prom_given[0],
            ci_prom_given[1] - stats["promoted_given_candidate"],
        ],
        fmt="o-",
        color="#2ca02c",
        capsize=3,
        label="Promoted | Candidate",
    )
    ax_rates.axvspan(7.5, 9.5, color="#999999", alpha=0.12)
    ax_rates.set_ylim(0, 1.0)
    ax_rates.set_ylabel("Rate")
    ax_rates.set_title("Selection funnel rates vs N (N≈8–9 highlighted)")
    ax_rates.legend(loc="upper right")
    ax_rates.text(
        0.02,
        0.02,
        "Candidate threshold: R ≥ 0.85 (see Appendix E: Common-threshold sensitivity)",
        transform=ax_rates.transAxes,
        fontsize=9,
        color="#444444",
        va="bottom",
    )

    ax_counts.plot(stats["node_count"], stats["evaluated_count"], "o-", label="Evaluated", color="#444444")
    ax_counts.plot(stats["node_count"], stats["candidate_count"], "o-", label="Candidate", color="#1f77b4")
    ax_counts.plot(stats["node_count"], stats["promoted_count"], "o-", label="Promoted", color="#d62728")
    ax_counts.axvspan(7.5, 9.5, color="#999999", alpha=0.12)
    ax_counts.set_ylabel("Count")
    ax_counts.set_xlabel("Network complexity (N)")
    ax_counts.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(out_dir / "Figure_3_Selection_Funnel.png")
    plt.close()


def figure_3_phase_boundary_spearman(
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
    r_col = "R_network_S1_mean"
    df[r_col] = _coerce_numeric(df[r_col])
    df["S2_Share"] = _coerce_numeric(df["S2_Share"])
    df = df[df[r_col].notna() & df["S2_Share"].notna()].copy()

    rows = []
    rng = np.random.default_rng(42)
    for n_val, group in df.groupby("node_count"):
        if group["S2_Share"].nunique() < 2 or group[r_col].nunique() < 2:
            continue
        rho, _pval = spearmanr(group["S2_Share"], group[r_col])
        boot = []
        vals = group[["S2_Share", r_col]].to_numpy()
        if len(vals) >= 2:
            for _ in range(200):
                idx = rng.integers(0, len(vals), size=len(vals))
                s2 = vals[idx, 0]
                r = vals[idx, 1]
                if np.unique(s2).size < 2 or np.unique(r).size < 2:
                    continue
                b_rho, _ = spearmanr(s2, r)
                if np.isfinite(b_rho):
                    boot.append(b_rho)
        if boot:
            ci_low, ci_high = np.quantile(boot, [0.025, 0.975])
        else:
            ci_low = np.nan
            ci_high = np.nan
        rows.append(
            {
                "node_count": n_val,
                "rho": rho,
                "ci_low": ci_low,
                "ci_high": ci_high,
                "n": len(group),
            }
        )
    if not rows:
        print("[paper_figures] skip Figure_3_phase_boundary_spearman (insufficient data).")
        return
    stats = pd.DataFrame(rows).sort_values("node_count")

    plt.figure(figsize=(10, 6))
    yerr = np.vstack(
        [
            stats["rho"] - stats["ci_low"],
            stats["ci_high"] - stats["rho"],
        ]
    )
    plt.errorbar(
        stats["node_count"],
        stats["rho"],
        yerr=yerr,
        fmt="o-",
        color="#1f77b4",
        capsize=3,
        linewidth=1.8,
    )
    for _, row in stats.iterrows():
        plt.annotate(
            f"n={int(row['n'])}",
            (row["node_count"], row["rho"]),
            textcoords="offset points",
            xytext=(0, 8 if row["rho"] >= 0 else -10),
            ha="center",
            fontsize=9,
        )
    plt.axhline(0, color="#999999", linewidth=1)
    plt.title("Phase boundary signature: Spearman(S2, R) within N")
    plt.xlabel("Network complexity (N)")
    plt.ylabel("Spearman rho")
    plt.tight_layout()
    plt.savefig(out_dir / "Figure_3_Phase_Boundary_Spearman.png")
    plt.close()


def figure_3_topology_heatmap(
    df2: pd.DataFrame,
    df3: pd.DataFrame,
    out_dir: Path,
    df4: Optional[pd.DataFrame] = None,
    template_classes: Optional[Dict[str, str]] = None,
) -> None:
    _style()
    frames = []
    df2 = df2.copy()
    df2["wave_label"] = "W2"
    frames.append(df2)
    df3 = df3.copy()
    df3["wave_label"] = "W3"
    frames.append(df3)
    if df4 is not None:
        df4 = df4.copy()
        df4["wave_label"] = "W4"
        frames.append(df4)
    df = pd.concat(frames, ignore_index=True)
    if template_classes:
        df["template_class"] = df["template_name"].map(template_classes).fillna("other")
    else:
        df["template_class"] = "other"

    r_col = _select_r_column(df)
    df[r_col] = _coerce_numeric(df[r_col])
    coherence_threshold = 0.85
    stats = df.groupby(["template_name", "node_count", "wave_label"]).agg(
        coherence_rate=(r_col, lambda s: (s >= coherence_threshold).mean()),
        n=("entity_id", "count"),
    ).reset_index()

    wave_priority = {"W4": 3, "W3": 2, "W2": 1}
    stats["wave_rank"] = stats["wave_label"].map(wave_priority).fillna(0)
    stats = stats.sort_values(["template_name", "node_count", "wave_rank"], ascending=[True, True, False])
    stats = stats.drop_duplicates(subset=["template_name", "node_count"], keep="first")

    pivot_rate = stats.pivot(index="template_name", columns="node_count", values="coherence_rate")
    pivot_count = stats.pivot(index="template_name", columns="node_count", values="n")
    pivot_wave = stats.pivot(index="template_name", columns="node_count", values="wave_label")
    pivot_rate = pivot_rate.sort_index(axis=1).sort_index(axis=0)
    pivot_count = pivot_count.reindex(index=pivot_rate.index, columns=pivot_rate.columns)
    pivot_wave = pivot_wave.reindex(index=pivot_rate.index, columns=pivot_rate.columns)

    annot = _build_heatmap_annotations(pivot_rate, pivot_count)
    # keep only rate and (n=...) in annotations (no wave labels to reduce clutter)

    plt.figure(figsize=(15, 10.5))
    ax = sns.heatmap(
        pivot_rate,
        annot=annot,
        fmt="",
        cmap="RdYlBu",
        linewidths=0.5,
        cbar_kws={"label": f"Coherence rate (R ≥ {coherence_threshold:.2f})"},
        vmin=0,
        vmax=1,
        annot_kws={"fontsize": 8},
    )
    ax.set_title("Topological ceiling by coherence threshold (N≈8–9)")
    ax.set_xlabel("Network size (N)")
    ax.set_ylabel("Topology (template)")
    n_min = 30
    for i, row_name in enumerate(pivot_rate.index):
        for j, col_name in enumerate(pivot_rate.columns):
            n_val = pivot_count.loc[row_name, col_name]
            if pd.notna(n_val) and n_val < n_min:
                ax.add_patch(
                    Rectangle(
                        (j, i),
                        1,
                        1,
                        fill=True,
                        facecolor="white",
                        alpha=0.35,
                        linewidth=1.0,
                        edgecolor="#444444",
                        linestyle=":",
                    )
                )
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
            cbar_kws={"label": f"Coherence rate (R ≥ {coherence_threshold:.2f})"},
            vmin=0,
            vmax=1,
            annot_kws={"fontsize": 8},
        )
        ax.set_title("Topological ceiling by coherence threshold (N≈8–9)")
        ax.set_xlabel("Network size (N)")
        ax.set_ylabel("Topology (template)")
        for i, row_name in enumerate(pivot_rate.index):
            for j, col_name in enumerate(pivot_rate.columns):
                n_val = pivot_count.loc[row_name, col_name]
                if pd.notna(n_val) and n_val < n_min:
                    ax.add_patch(
                        Rectangle(
                            (j, i),
                            1,
                            1,
                            fill=True,
                            facecolor="white",
                            alpha=0.35,
                            linewidth=1.0,
                            edgecolor="#444444",
                            linestyle=":",
                        )
                    )
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
    promoted_col = _select_promoted_column(df)
    df[promoted_col] = df[promoted_col].fillna(False)
    df_prom = df[df[promoted_col] == True]
    df_non = df[df[promoted_col] == False]
    plt.scatter(
        df_non["S2_Share"],
        df_non["R_resid"],
        marker="x",
        color="#6e6e6e",
        alpha=0.45,
        s=35,
        label="False",
        zorder=1,
    )
    plt.scatter(
        df_prom["S2_Share"],
        df_prom["R_resid"],
        marker="o",
        facecolor="#1b7f5a",
        edgecolor="white",
        linewidth=0.6,
        alpha=0.85,
        s=70,
        label="True",
        zorder=2,
    )

    if len(df) >= 2 and df["S2_Share"].nunique() >= 2:
        coeff = None
        try:
            coeff = np.polyfit(df["S2_Share"], df["R_resid"], deg=1)
        except np.linalg.LinAlgError:
            coeff = None
        if coeff is not None and np.isfinite(coeff).all():
            x_line = np.linspace(df["S2_Share"].min(), df["S2_Share"].max(), 200)
            y_line = coeff[0] * x_line + coeff[1]
            plt.plot(x_line, y_line, "k--", linewidth=2, label=f"Trend: slope={coeff[0]:.3f}")

            rng = np.random.default_rng(42)
            slopes = []
            x_vals = df["S2_Share"].to_numpy()
            y_vals = df["R_resid"].to_numpy()
            for _ in range(1000):
                idx = rng.integers(0, len(x_vals), size=len(x_vals))
                try:
                    b_s, _a_s = np.polyfit(x_vals[idx], y_vals[idx], deg=1)
                except np.linalg.LinAlgError:
                    continue
                if np.isfinite(b_s):
                    slopes.append(b_s)
            if slopes:
                slope_ci = np.quantile(slopes, [0.025, 0.975])
                plt.plot(
                    x_line,
                    (np.mean(slopes) * x_line + coeff[1]),
                    color="black",
                    linestyle="--",
                    linewidth=2,
                    label=f"Slope CI [{slope_ci[0]:.3f}, {slope_ci[1]:.3f}]",
                )
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
    n_min = 30
    stats.loc[stats["n"] < n_min, "candidate_rate"] = np.nan
    pivot_rate = stats.pivot(index="template_name", columns="node_count", values="candidate_rate")
    pivot_count = stats.pivot(index="template_name", columns="node_count", values="n")
    pivot_rate = pivot_rate.sort_index(axis=1).sort_index(axis=0)
    pivot_count = pivot_count.reindex(index=pivot_rate.index, columns=pivot_rate.columns)
    ordered_templates = sorted(pivot_rate.index, key=_template_sort_key)
    pivot_rate = pivot_rate.reindex(index=ordered_templates)
    pivot_count = pivot_count.reindex(index=ordered_templates)
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


def appendix_c_topology_triptych(
    df2: pd.DataFrame, df3: pd.DataFrame, out_dir: Path, df4: Optional[pd.DataFrame] = None
) -> None:
    _style()
    frames = [df2, df3]
    if df4 is not None:
        frames.append(df4)
    df = pd.concat(frames, ignore_index=True)
    cand_col = _select_candidate_column(df)
    if cand_col is None:
        print("[paper_figures] skip Appendix_C_topology_triptych (missing candidate flag).")
        return
    promoted_col = _select_promoted_column(df)
    df[cand_col] = df[cand_col].fillna(False)
    df[promoted_col] = df[promoted_col].fillna(False)

    stats = df.groupby(["template_name", "node_count"]).agg(
        n=("entity_id", "count"),
        candidate_count=(cand_col, "sum"),
        promoted_count=(promoted_col, "sum"),
    ).reset_index()
    stats["candidate_rate"] = stats["candidate_count"] / stats["n"].replace(0, np.nan)
    stats["promoted_rate"] = stats["promoted_count"] / stats["n"].replace(0, np.nan)
    stats["promoted_given_candidate"] = stats["promoted_count"] / stats["candidate_count"].replace(0, np.nan)

    n_min = 30
    stats.loc[stats["n"] < n_min, ["candidate_rate", "promoted_rate", "promoted_given_candidate"]] = np.nan

    def _pivot(metric: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        pivot_rate = stats.pivot(index="template_name", columns="node_count", values=metric)
        pivot_count = stats.pivot(index="template_name", columns="node_count", values="n")
        pivot_rate = pivot_rate.sort_index(axis=1).sort_index(axis=0)
        pivot_count = pivot_count.reindex(index=pivot_rate.index, columns=pivot_rate.columns)
        ordered_templates = sorted(pivot_rate.index, key=_template_sort_key)
        pivot_rate = pivot_rate.reindex(index=ordered_templates)
        pivot_count = pivot_count.reindex(index=ordered_templates)
        return pivot_rate, pivot_count

    metrics = [
        ("candidate_rate", "Candidate rate"),
        ("promoted_rate", "Promoted rate"),
        ("promoted_given_candidate", "Promoted | Candidate"),
    ]

    fig, axes = plt.subplots(3, 1, figsize=(12, 14), sharex=True)
    for ax, (metric, label) in zip(axes, metrics):
        pivot_rate, pivot_count = _pivot(metric)
        annot = _build_heatmap_annotations(pivot_rate, pivot_count)
        sns.heatmap(
            pivot_rate,
            annot=annot,
            fmt="",
            cmap="RdYlBu",
            linewidths=0.5,
            cbar_kws={"label": label},
            vmin=0,
            vmax=1,
            ax=ax,
        )
        ax.set_xlabel("Network size (N)")
        ax.set_ylabel("Topology (template)")
        ax.set_title(label)
    plt.tight_layout()
    plt.savefig(out_dir / "Appendix_C_topology_triptych.png")
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


def appendix_d_promprob_vs_s2(
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
    df["S2_Share"] = _coerce_numeric(df["S2_Share"])
    df = df[df["S2_Share"].between(0, 1)]
    df = df[df["node_count"].notna() & df["template_name"].notna()].copy()
    df = df[df[promoted_col].notna()].copy()

    if df.empty:
        print("[paper_figures] skip Appendix_D_promprob_vs_s2 (empty data).")
        return

    df["node_count"] = df["node_count"].astype(int)
    df["template_name"] = df["template_name"].astype(str)
    y = df[promoted_col].astype(int).to_numpy()
    s2 = df["S2_Share"].to_numpy()

    node_dummies = pd.get_dummies(df["node_count"].astype(str), prefix="N", drop_first=True)
    template_dummies = pd.get_dummies(df["template_name"], prefix="T", drop_first=True)
    X = np.column_stack(
        [
            np.ones(len(df)),
            s2,
            node_dummies.to_numpy(),
            template_dummies.to_numpy(),
        ]
    )

    beta = _fit_logistic_regression(X, y)

    nodes_sorted = sorted(df["node_count"].unique().tolist())
    preferred = [2, 4, 6, 9, 12]
    prom_counts = df.groupby("node_count")[promoted_col].sum().to_dict()
    total_counts = df.groupby("node_count")[promoted_col].size().to_dict()
    nonprom_counts = {n: total_counts.get(n, 0) - prom_counts.get(n, 0) for n in nodes_sorted}
    min_prom = 5
    min_non = 5
    n_values = [
        n
        for n in preferred
        if n in nodes_sorted and prom_counts.get(n, 0) >= min_prom and nonprom_counts.get(n, 0) >= min_non
    ]

    s2_grid = np.linspace(df["S2_Share"].min(), df["S2_Share"].max(), 120)

    node_cols = list(node_dummies.columns)
    template_cols = list(template_dummies.columns)

    def build_row(val_s2: float, n_val: int, tmpl: str) -> np.ndarray:
        vec = np.zeros(X.shape[1], dtype=float)
        vec[0] = 1.0
        vec[1] = val_s2
        n_key = f"N_{n_val}"
        if n_key in node_cols:
            vec[2 + node_cols.index(n_key)] = 1.0
        t_key = f"T_{tmpl}"
        if t_key in template_cols:
            vec[2 + len(node_cols) + template_cols.index(t_key)] = 1.0
        return vec

    tmpl_counts_by_n = df.groupby(["node_count", "template_name"]).size().reset_index(name="count")
    combo_counts = df.groupby(["node_count", "template_name"]).size().reset_index(name="count")
    combo_weights = combo_counts["count"].to_numpy().astype(float)
    combo_weights /= combo_weights.sum()
    combo_nodes = combo_counts["node_count"].to_list()
    combo_templates = combo_counts["template_name"].to_list()

    def predicted_curve(beta_vec: np.ndarray, n_val: int) -> np.ndarray:
        tmpl_counts = tmpl_counts_by_n[tmpl_counts_by_n["node_count"] == n_val]
        if tmpl_counts.empty:
            tmpl_counts = tmpl_counts_by_n.groupby("template_name")["count"].sum().reset_index()
        weights = tmpl_counts["count"].to_numpy().astype(float)
        weights /= weights.sum()
        templates = tmpl_counts["template_name"].to_list()
        preds = []
        for s2_val in s2_grid:
            lin = 0.0
            for w, tmpl in zip(weights, templates):
                x_row = build_row(s2_val, n_val, tmpl)
                lin += w * (x_row @ beta_vec)
            preds.append(_sigmoid(np.array([lin]))[0])
        return np.array(preds)

    def predicted_curve_overall(beta_vec: np.ndarray) -> np.ndarray:
        preds = []
        for s2_val in s2_grid:
            lin = 0.0
            for w, n_val, tmpl in zip(combo_weights, combo_nodes, combo_templates):
                x_row = build_row(s2_val, int(n_val), tmpl)
                lin += w * (x_row @ beta_vec)
            preds.append(_sigmoid(np.array([lin]))[0])
        return np.array(preds)

    n_boot = 300
    boot_curves = {n_val: [] for n_val in n_values}
    boot_overall = []
    rng = np.random.default_rng(42)
    for _ in range(n_boot):
        idx = rng.integers(0, len(df), size=len(df))
        beta_b = _fit_logistic_regression(X[idx], y[idx])
        for n_val in n_values:
            boot_curves[n_val].append(predicted_curve(beta_b, n_val))
        if not n_values:
            boot_overall.append(predicted_curve_overall(beta_b))

    plt.figure(figsize=(10, 6))
    colors = ["#1b9e77", "#d95f02", "#7570b3", "#8c564b", "#9467bd"]
    if n_values:
        for n_val, color in zip(n_values, colors):
            curve = predicted_curve(beta, n_val)
            n_prom = int(prom_counts.get(n_val, 0))
            n_non = int(nonprom_counts.get(n_val, 0))
            if boot_curves[n_val]:
                boot_arr = np.vstack(boot_curves[n_val])
                ci_low, ci_high = np.quantile(boot_arr, [0.025, 0.975], axis=0)
                plt.fill_between(s2_grid, ci_low, ci_high, color=color, alpha=0.15)
            plt.plot(
                s2_grid,
                curve,
                color=color,
                linewidth=2.2,
                label=f"N={n_val} (prom={n_prom}, non={n_non})",
                zorder=5,
            )
    else:
        curve = predicted_curve_overall(beta)
        if boot_overall:
            boot_arr = np.vstack(boot_overall)
            ci_low, ci_high = np.quantile(boot_arr, [0.025, 0.975], axis=0)
            plt.fill_between(s2_grid, ci_low, ci_high, color="#1b9e77", alpha=0.15)
        plt.plot(s2_grid, curve, color="#1b9e77", linewidth=2.2, label="Overall (avg N, template)")

    plt.title("Promotion probability vs S2 (controlling for N, template)")
    plt.xlabel("S2 participation")
    plt.ylabel("P(promoted)")
    plt.ylim(0, 1)
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(out_dir / "Appendix_D_PromProb_vs_S2.png")
    plt.close()


def appendix_f_fluctuation_peak(
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
    df = df[df[r_col].notna() & df["S2_Share"].notna()].copy()

    def iqr(series: pd.Series) -> float:
        q1, q3 = np.quantile(series, [0.25, 0.75])
        return float(q3 - q1)

    stats = df.groupby("node_count").agg(
        R_iqr=(r_col, iqr),
        S2_iqr=("S2_Share", iqr),
    ).reset_index().sort_values("node_count")

    fig, axes = plt.subplots(2, 1, figsize=(9.5, 7.5), sharex=True)
    ax_r, ax_s2 = axes
    ax_r.plot(stats["node_count"], stats["R_iqr"], "o-", color="#1f77b4", linewidth=2)
    ax_r.axvspan(6, 8, color="#999999", alpha=0.12)
    ax_r.set_ylabel("IQR(R | N)")
    ax_r.set_title("Fluctuation peak: dispersion vs N")
    ax_s2.plot(stats["node_count"], stats["S2_iqr"], "o-", color="#d95f02", linewidth=2)
    ax_s2.axvspan(6, 8, color="#999999", alpha=0.12)
    ax_s2.set_ylabel("IQR(S2 | N)")
    ax_s2.set_xlabel("Network complexity (N)")
    plt.tight_layout()
    plt.savefig(out_dir / "Appendix_F_Fluctuation_Peak.png")
    plt.close()


def appendix_g_critical_dynamics_variance(
    df2: pd.DataFrame, df3: pd.DataFrame, out_dir: Path, df4: Optional[pd.DataFrame] = None
) -> None:
    _style()
    frames = [df2, df3]
    if df4 is not None:
        frames.append(df4)
    df = pd.concat(frames, ignore_index=True)
    if "phase_var_lastW_mean" not in df.columns:
        print("[paper_figures] skip Appendix_G_critical_dynamics (missing phase_var_lastW_mean).")
        return
    r_col = _select_r_column(df)
    df[r_col] = _coerce_numeric(df[r_col])
    df["phase_var_lastW_mean"] = _coerce_numeric(df["phase_var_lastW_mean"])
    df = df[df[r_col].notna() & df["phase_var_lastW_mean"].notna()].copy()

    def iqr(series: pd.Series) -> float:
        q1, q3 = np.quantile(series, [0.25, 0.75])
        return float(q3 - q1)

    stats = df.groupby("node_count").agg(
        R_iqr=(r_col, iqr),
        phase_iqr=("phase_var_lastW_mean", iqr),
        n=("entity_id", "count"),
    ).reset_index().sort_values("node_count")

    fig, axes = plt.subplots(2, 1, figsize=(9.5, 7.5), sharex=True)
    ax_r, ax_phase = axes
    ax_r.plot(stats["node_count"], stats["R_iqr"], "o-", color="#1f77b4", linewidth=2)
    ax_r.axvspan(6, 8, color="#999999", alpha=0.12)
    ax_r.set_ylabel("IQR(R | N)")
    ax_r.set_title("Critical dynamics: dispersion vs N")

    ax_phase.plot(stats["node_count"], stats["phase_iqr"], "o-", color="#d95f02", linewidth=2)
    ax_phase.axvspan(6, 8, color="#999999", alpha=0.12)
    for _, row in stats.iterrows():
        ax_phase.annotate(
            f"n={int(row['n'])}",
            (row["node_count"], row["phase_iqr"]),
            textcoords="offset points",
            xytext=(0, 6),
            ha="center",
            fontsize=8,
            color="#444444",
        )
    ax_phase.set_ylabel("IQR(phase variance | N)")
    ax_phase.set_xlabel("Network complexity (N)")
    plt.tight_layout()
    plt.savefig(out_dir / "Appendix_G_Critical_Dynamics.png")
    plt.close()


def figure_5_critical_heterogeneity_onset(
    df2: pd.DataFrame, df3: pd.DataFrame, out_dir: Path, df4: Optional[pd.DataFrame] = None
) -> None:
    _style()
    frames = [df2, df3]
    if df4 is not None:
        frames.append(df4)
    df = pd.concat(frames, ignore_index=True)
    if "phase_var_lastW_mean" not in df.columns:
        print("[paper_figures] skip Figure5_Critical_Heterogeneity_Onset (missing phase_var_lastW_mean).")
        return
    if "sweep_passed" in df.columns:
        df = df[df["sweep_passed"] == True].copy()
    else:
        df = df[df[r_col].notna()].copy()
    df["phase_var_lastW_mean"] = _coerce_numeric(df["phase_var_lastW_mean"])
    df = df[df["phase_var_lastW_mean"].notna()].copy()

    stats = df.groupby("node_count").agg(
        q1=("phase_var_lastW_mean", lambda s: float(np.quantile(s, 0.25))),
        q3=("phase_var_lastW_mean", lambda s: float(np.quantile(s, 0.75))),
        n=("entity_id", "count"),
    ).reset_index().sort_values("node_count")
    stats["iqr"] = stats["q3"] - stats["q1"]

    plt.figure(figsize=(10, 6))
    plt.plot(stats["node_count"], stats["iqr"], "o-", color="#7b1fa2", linewidth=2.4)
    plt.fill_between(
        stats["node_count"],
        stats["q1"],
        stats["q3"],
        color="#ce93d8",
        alpha=0.2,
    )
    for _, row in stats.iterrows():
        plt.annotate(
            f"n={int(row['n'])}",
            (row["node_count"], row["iqr"]),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=8,
            color="#4a148c",
        )
    plt.yscale("log")
    plt.title("Critical heterogeneity onset")
    plt.xlabel("Network size (N)")
    plt.ylabel("IQR of phase variance (log scale)")
    plt.tight_layout()
    plt.savefig(out_dir / "Figure5_Critical_Heterogeneity_Onset.png")
    plt.close()


def appendix_b_sensitivity_scaling(
    df2: pd.DataFrame, df3: pd.DataFrame, out_dir: Path, df4: Optional[pd.DataFrame] = None
) -> None:
    _style()
    all_path = Path("paper/data/paper_metrics_all.csv")
    legacy_all = Path("data/processed/paper/data/all/paper_metrics_all.csv")
    if all_path.exists():
        df = pd.read_csv(all_path)
    elif legacy_all.exists():
        df = pd.read_csv(legacy_all)
    else:
        frames = [df2, df3]
        if df4 is not None:
            frames.append(df4)
        df = pd.concat(frames, ignore_index=True)
    r_col = "R_network_S1_mean" if "R_network_S1_mean" in df.columns else _select_r_column(df)
    df[r_col] = _coerce_numeric(df[r_col])
    if "was_swept" in df.columns:
        df = df[df["was_swept"] == True]
    df = df[df[r_col].notna()].copy()

    def _power_law_neg(x: np.ndarray, a: float, b: float) -> np.ndarray:
        return a * np.power(x, -b)

    thresholds = np.linspace(0.0, 0.55, 15)
    rows = []
    for thr in thresholds:
        sub = df[df[r_col] >= thr]
        if sub.empty:
            continue
        stats = sub.groupby("node_count")[r_col].agg(["mean", "count"])
        unique_ns = len(stats.index)
        if unique_ns < 4:
            continue
        x = stats.index.to_numpy(dtype=float)
        y = stats["mean"].to_numpy(dtype=float)
        try:
            popt, pcov = curve_fit(_power_law_neg, x, y, p0=[1.0, 0.33], maxfev=2000)
        except Exception:
            continue
        _a_fit, b_fit = popt
        if pcov is None:
            continue
        b_err = float(np.sqrt(np.diag(pcov))[1])
        if not np.isfinite(b_err):
            continue
        b_mean = float(b_fit)
        rows.append(
            {
                "thr": thr,
                "b_mean": b_mean,
                "b_err": b_err,
                "n_nodes": unique_ns,
            }
        )

    if not rows:
        print("[paper_figures] skip Appendix_B_Sensitivity_of_Scaling (no valid fits).")
        return
    stats = pd.DataFrame(rows)

    plt.figure(figsize=(9, 6))
    plt.fill_between(
        stats["thr"],
        stats["b_mean"] - stats["b_err"],
        stats["b_mean"] + stats["b_err"],
        color="#1f77b4",
        alpha=0.2,
        label="95% Conf. Interval",
    )
    plt.plot(stats["thr"], stats["b_mean"], "-", color="#1f77b4", linewidth=2)
    low_n_mask = stats["n_nodes"] < 5
    plt.scatter(
        stats.loc[~low_n_mask, "thr"],
        stats.loc[~low_n_mask, "b_mean"],
        color="#1f77b4",
        s=35,
        label="Measured Exponent b̂",
    )
    plt.scatter(
        stats.loc[low_n_mask, "thr"],
        stats.loc[low_n_mask, "b_mean"],
        color="#1f77b4",
        s=35,
        alpha=0.4,
    )
    for _thr, _b, _n in stats.loc[low_n_mask, ["thr", "b_mean", "n_nodes"]].itertuples(index=False):
        plt.text(_thr, _b + 0.008, f"n={int(_n)}", fontsize=8, ha="center")
    plt.axhline(1.0 / 3.0, color="red", linestyle="--", linewidth=2, label="Reference 1/3")
    plt.title("Sensitivity of scaling exponent b")
    plt.xlabel("Minimum coherence threshold (R_surv)")
    plt.ylabel("Scaling exponent (b̂)")
    plt.ylim(0.18, 0.35)
    plt.xlim(-0.03, 0.53)
    plt.legend(loc="lower left")
    plt.grid(True, which="major", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(out_dir / "Appendix_B_Sensitivity_of_Scaling.png")
    plt.close()


def draft_cod1_fig2_clean(df: pd.DataFrame, out_dir: Path) -> None:
    _style()
    promoted_col = _select_promoted_column(df)
    df[promoted_col] = df[promoted_col].fillna(False)
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    sns.lineplot(
        data=df,
        x="node_count",
        y="S2_Share",
        hue=promoted_col,
        style=promoted_col,
        markers=True,
        dashes=False,
        palette={True: "#2ca02c", False: "#7f7f7f"},
        linewidth=2.5,
        markersize=8,
    )
    plt.title("Memory Overhead (S2) - Promoted vs Non-promoted", fontsize=14)
    plt.ylabel("S2 Participation (Memory Cost)", fontsize=12)
    plt.xlabel("Network Complexity (N)", fontsize=12)
    plt.legend(title="Outcome", labels=["Failed/Candidate", "Promoted (Survivor)"])
    plt.tight_layout()
    plt.savefig(out_dir / "Draft_Fig2_Clean_Trajectories_cod1.png", dpi=300)
    plt.close()


def draft_cod1_fig4_binned(df: pd.DataFrame, out_dir: Path) -> None:
    _style()
    plt.figure(figsize=(10, 6))
    df = df.copy()
    df["S2_Bin"] = pd.cut(df["S2_Share"], bins=15)
    stats = df.groupby("S2_Bin", observed=True).agg(
        R_Res_Mean=("R_Residual", "mean"),
        R_Res_Err=("R_Residual", "sem"),
        S2_Center=("S2_Share", "mean"),
    ).reset_index()
    plt.scatter(df["S2_Share"], df["R_Residual"], color="gray", alpha=0.05, s=10, label="Raw Data")
    plt.errorbar(
        x=stats["S2_Center"],
        y=stats["R_Res_Mean"],
        yerr=stats["R_Res_Err"],
        fmt="-o",
        color="darkblue",
        ecolor="red",
        capsize=5,
        linewidth=2,
        markersize=8,
        label="Binned Trend (Mean ± SEM)",
    )
    plt.axhline(0, color="black", linestyle="--", linewidth=1)
    plt.title("Mechanism Check (Binned Residuals)", fontsize=14)
    plt.xlabel("Memory Participation (S2)", fontsize=12)
    plt.ylabel("Coherence Residual (R - Mean[R|N])", fontsize=12)
    plt.text(
        0.1,
        0.1,
        "Residual > 0 = higher than expected",
        color="darkblue",
        transform=plt.gca().transAxes,
        fontsize=9,
    )
    # Optional global slope with bootstrap CI
    x_vals = df["S2_Share"].to_numpy()
    y_vals = df["R_Residual"].to_numpy()
    if len(x_vals) >= 2 and np.unique(x_vals).size >= 2:
        try:
            slope, intercept = np.polyfit(x_vals, y_vals, 1)
        except np.linalg.LinAlgError:
            slope = None
        if slope is not None:
            rng = np.random.default_rng(42)
            slopes = []
            for _ in range(300):
                idx = rng.integers(0, len(x_vals), size=len(x_vals))
                try:
                    b_s, _a_s = np.polyfit(x_vals[idx], y_vals[idx], 1)
                except np.linalg.LinAlgError:
                    continue
                if np.isfinite(b_s):
                    slopes.append(b_s)
            if slopes:
                ci_low, ci_high = np.quantile(slopes, [0.025, 0.975])
                plt.text(
                    0.62,
                    0.9,
                    f"slope ≈ {np.mean(slopes):.3f} [{ci_low:.3f}, {ci_high:.3f}]",
                    transform=plt.gca().transAxes,
                    fontsize=9,
                    color="#444444",
                )
    plt.legend()
    plt.text(
        0.02,
        0.02,
        "Binned mean ± SEM; raw points in gray; residual computed within-N",
        transform=plt.gca().transAxes,
        fontsize=9,
        color="#444444",
        va="bottom",
    )
    plt.tight_layout()
    plt.savefig(out_dir / "Figure_4_Mechanism_Binned.png", dpi=300)
    plt.close()


def appendix_a_pipeline_handshake(
    df2: pd.DataFrame, df3: pd.DataFrame, out_dir: Path, df4: Optional[pd.DataFrame] = None
) -> None:
    _style()
    all_path = Path("paper/data/paper_metrics_all.csv")
    legacy_all = Path("data/processed/paper/data/all/paper_metrics_all.csv")
    if all_path.exists():
        df = pd.read_csv(all_path)
    elif legacy_all.exists():
        df = pd.read_csv(legacy_all)
    else:
        frames = [df2, df3]
        if df4 is not None:
            frames.append(df4)
        df = pd.concat(frames, ignore_index=True)
    r_col = "R_network_S1_mean" if "R_network_S1_mean" in df.columns else _select_r_column(df)
    n_col = "node_count" if "node_count" in df.columns else "N"
    wave_col = "ola" if "ola" in df.columns else ("wave" if "wave" in df.columns else None)
    if wave_col is None:
        print("[paper_figures] skip Appendix_A_Pipeline_Handshake (no wave/ola column).")
        return
    df[r_col] = _coerce_numeric(df[r_col])
    df[n_col] = _coerce_numeric(df[n_col])
    df[wave_col] = _coerce_numeric(df[wave_col])
    if "was_swept" in df.columns:
        df = df[df["was_swept"] == True]
    df = df[df[r_col].notna() & df[n_col].notna() & df[wave_col].notna()].copy()
    df = df[df[n_col] == 9]
    df = df[df[wave_col].isin([3, 4])]
    if df.empty or df[wave_col].nunique() < 2:
        print("[paper_figures] skip Appendix_A_Pipeline_Handshake (insufficient N=9 overlap).")
        return

    r3 = df[df[wave_col] == 3][r_col].to_numpy()
    r4 = df[df[wave_col] == 4][r_col].to_numpy()
    delta = float(np.mean(r4) - np.mean(r3))
    tstat, pval = ttest_ind(r3, r4, equal_var=False, nan_policy="omit")

    plt.figure(figsize=(6, 5))
    sns.boxplot(
        data=df,
        x=wave_col,
        y=r_col,
        hue=wave_col,
        order=[3, 4],
        hue_order=[3, 4],
        palette={3: "#66c2a5", 4: "#fc8d62"},
        dodge=False,
        width=0.8,
        legend=False,
    )
    sns.stripplot(
        data=df,
        x=wave_col,
        y=r_col,
        order=[3, 4],
        color="#444444",
        size=3,
        alpha=0.6,
        jitter=0.22,
    )
    plt.xlabel("Pipeline stage (Ola)")
    plt.ylabel("Global coherence (R)")
    plt.title(f"Pipeline Handshake (N=9)\nΔR = {delta:.4f}, p-value = {pval:.3f}")
    plt.tight_layout()
    plt.savefig(out_dir / "Appendix_A_Pipeline_Handshake.png", dpi=300)
    plt.close()


def appendix_d_raw_scatter(
    df2: pd.DataFrame, df3: pd.DataFrame, out_dir: Path, df4: Optional[pd.DataFrame] = None
) -> None:
    _style()
    all_path = Path("paper/data/paper_metrics_all.csv")
    legacy_all = Path("data/processed/paper/data/all/paper_metrics_all.csv")
    if all_path.exists():
        df = pd.read_csv(all_path)
    elif legacy_all.exists():
        df = pd.read_csv(legacy_all)
    else:
        frames = [df2, df3]
        if df4 is not None:
            frames.append(df4)
        df = pd.concat(frames, ignore_index=True)
    r_col = "R_network_S1_mean" if "R_network_S1_mean" in df.columns else _select_r_column(df)
    n_col = "node_count" if "node_count" in df.columns else "N"
    s2_col = "H_part_norm_mean" if "H_part_norm_mean" in df.columns else "S2_Share"
    if s2_col not in df.columns:
        print("[paper_figures] skip Appendix_D_Raw_Scatter (no S2 column).")
        return
    df[r_col] = _coerce_numeric(df[r_col])
    df[n_col] = _coerce_numeric(df[n_col])
    df[s2_col] = _coerce_numeric(df[s2_col])
    if "was_swept" in df.columns:
        df = df[df["was_swept"] == True]
    df = df[df[r_col].notna() & df[n_col].notna() & df[s2_col].notna()].copy()
    target_n = None
    for candidate_n in (9, 8):
        if (df[n_col] == candidate_n).any():
            target_n = candidate_n
            break
    if target_n is None:
        print("[paper_figures] skip Appendix_D_Raw_Scatter (no N=9/8 data).")
        return
    df = df[df[n_col] == target_n]
    if df.empty:
        print("[paper_figures] skip Appendix_D_Raw_Scatter (empty selection).")
        return

    plt.figure(figsize=(7, 5))
    sns.regplot(
        data=df,
        x=s2_col,
        y=r_col,
        scatter_kws={"s": 28, "alpha": 0.6, "color": "#4c78a8"},
        line_kws={"color": "#e45756", "linewidth": 2},
        ci=95,
        truncate=False,
    )
    r_val, p_val = pearsonr(df[s2_col], df[r_col])
    plt.xlabel("Memory participation (S2 proxy)")
    plt.ylabel("Global coherence (R)")
    plt.title(
        f"Cost of Survival (N={int(target_n)})\nPearson r = {r_val:.3f} (p={p_val:.3f})"
    )
    plt.tight_layout()
    plt.savefig(out_dir / "Appendix_D_Raw_Scatter.png", dpi=300)
    plt.close()


def memory_weighted_proxy_comparation(
    df2: pd.DataFrame, df3: pd.DataFrame, out_dir: Path, df4: Optional[pd.DataFrame] = None
) -> None:
    _style()
    frames = [df2, df3]
    if df4 is not None:
        frames.append(df4)
    df = pd.concat(frames, ignore_index=True)
    if "phase_var_lastW_mean" not in df.columns:
        print("[paper_figures] skip memory_weighted_proxy_comparation (missing phase_var_lastW_mean).")
        return
    r_col = "R_network_S1_mean"
    df[r_col] = _coerce_numeric(df[r_col])
    df["H_part_norm_mean"] = _coerce_numeric(df["H_part_norm_mean"])
    df["phase_var_lastW_mean"] = _coerce_numeric(df["phase_var_lastW_mean"])
    if "sweep_passed" in df.columns:
        df = df[df["sweep_passed"] == True].copy()
    else:
        df = df[df[r_col].notna()].copy()
    df = df[df["H_part_norm_mean"].notna() & df["phase_var_lastW_mean"].notna()].copy()
    df["E_disorder"] = (1.0 - df[r_col]) * df["H_part_norm_mean"]
    df = df[df["E_disorder"].notna()].copy()
    if df.empty:
        print("[paper_figures] skip memory_weighted_proxy_comparation (empty data).")
        return

    def _panel_stats(df_in: pd.DataFrame, y_col: str) -> pd.DataFrame:
        stats = df_in.groupby("node_count").agg(
            mean=(y_col, "mean"),
            std=(y_col, "std"),
            n=(y_col, "count"),
        ).reset_index().sort_values("node_count")
        stats["se"] = stats["std"] / np.sqrt(stats["n"].clip(lower=1))
        stats["lnN"] = np.log(stats["node_count"].astype(float))
        return stats

    def _fit_line(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
        if x.size < 2:
            return np.array([]), float("nan")
        coeffs = np.polyfit(x, y, 1)
        y_hat = coeffs[0] * x + coeffs[1]
        ss_res = float(np.sum((y - y_hat) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        return y_hat, r2

    stats_phase = _panel_stats(df, "phase_var_lastW_mean")
    stats_disorder = _panel_stats(df, "E_disorder")
    if stats_phase.empty or stats_disorder.empty:
        print("[paper_figures] skip memory_weighted_proxy_comparation (insufficient stats).")
        return

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), sharex=False)
    panel_cfgs = [
        {
            "ax": axes[0],
            "stats": stats_phase,
            "title": "(a) Phase variance proxy",
            "y_label": "phase_var_lastW",
            "marker": "o",
            "color": "#d62728",
        },
        {
            "ax": axes[1],
            "stats": stats_disorder,
            "title": "(b) Memory-weighted proxy",
            "y_label": r"$E_{disorder} = (1 - R) \times H_{part}$",
            "marker": "s",
            "color": "#2ca02c",
        },
    ]

    for cfg in panel_cfgs:
        ax = cfg["ax"]
        stats = cfg["stats"]
        x = stats["lnN"].to_numpy()
        y = stats["mean"].to_numpy()
        y_hat, r2 = _fit_line(x, y)
        ax.errorbar(
            x,
            y,
            yerr=stats["se"].to_numpy(),
            fmt=cfg["marker"],
            color=cfg["color"],
            ecolor=cfg["color"],
            capsize=4,
            markersize=7,
            linestyle="none",
            label="Data",
        )
        if y_hat.size:
            ax.plot(x, y_hat, "--", color="#666666", linewidth=2, label=f"Fit: $R^2$ = {r2:.2f}")
        ax.set_title(cfg["title"])
        ax.set_xlabel("ln N")
        ax.set_ylabel(cfg["y_label"])
        ax.legend(loc="upper left")

        top_ax = ax.secondary_xaxis("top")
        tick_ns = [2, 3, 5, 7, 10, 12]
        tick_ns = [n for n in tick_ns if n in stats["node_count"].tolist()]
        if tick_ns:
            top_ax.set_xticks(np.log(tick_ns))
            top_ax.set_xticklabels([str(n) for n in tick_ns])
        top_ax.set_xlabel("N")

    plt.tight_layout()
    plt.savefig(out_dir / "memory_weighted_proxy_comparation.png", dpi=300)
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
    parser.add_argument("--out-dir", default="paper/figures", help="Output directory.")
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
    # appendix_c_topology_triptych(df2, df3, out_dir, df4=df4)
    # appendix_e_grade_compare(df2, df3, out_dir, df4=df4)
    appendix_c_spearman_by_n(
        Path(args.metrics_ola3),
        Path(args.genome_ola3),
        out_dir,
        metrics_ola2=Path(args.metrics_ola2) if args.metrics_ola2 else None,
        genome_ola2=Path(args.genome_ola2) if args.genome_ola2 else None,
        metrics_ola4=Path(args.metrics_ola4) if args.metrics_ola4 else None,
        genome_ola4=Path(args.genome_ola4) if args.genome_ola4 else None,
    )
    appendix_f_fluctuation_peak(
        Path(args.metrics_ola3),
        Path(args.genome_ola3),
        out_dir,
        metrics_ola2=Path(args.metrics_ola2) if args.metrics_ola2 else None,
        genome_ola2=Path(args.genome_ola2) if args.genome_ola2 else None,
        metrics_ola4=Path(args.metrics_ola4) if args.metrics_ola4 else None,
        genome_ola4=Path(args.genome_ola4) if args.genome_ola4 else None,
    )
    appendix_g_critical_dynamics_variance(df2, df3, out_dir, df4=df4)
    figure_5_critical_heterogeneity_onset(df2, df3, out_dir, df4=df4)
    appendix_b_sensitivity_scaling(df2, df3, out_dir, df4=df4)
    appendix_a_pipeline_handshake(df2, df3, out_dir, df4=df4)
    appendix_d_raw_scatter(df2, df3, out_dir, df4=df4)
    memory_weighted_proxy_comparation(df2, df3, out_dir, df4=df4)

    df2_s2 = _load_s2_dataset(Path(args.metrics_ola2), Path(args.genome_ola2), "Wave 2") if args.genome_ola2 else None
    df3_s2 = _load_s2_dataset(Path(args.metrics_ola3), Path(args.genome_ola3), "Wave 3")
    df4_s2 = _load_s2_dataset(Path(args.metrics_ola4), Path(args.genome_ola4), "Wave 4") if args.genome_ola4 else None
    frames = [df3_s2]
    if df2_s2 is not None:
        frames.insert(0, df2_s2)
    if df4_s2 is not None:
        frames.append(df4_s2)
    df_cod1 = pd.concat(frames, ignore_index=True)
    r_col = _select_r_column(df_cod1)
    df_cod1[r_col] = _coerce_numeric(df_cod1[r_col])
    df_cod1["S2_Share"] = _coerce_numeric(df_cod1["S2_Share"])
    df_cod1 = df_cod1[df_cod1[r_col].notna() & df_cod1["S2_Share"].notna()].copy()
    df_cod1["R"] = df_cod1[r_col]
    df_cod1["N"] = df_cod1["node_count"]
    df_cod1["R_Mean_by_N"] = df_cod1.groupby("N")["R"].transform("mean")
    df_cod1["R_Residual"] = df_cod1["R"] - df_cod1["R_Mean_by_N"]
    draft_cod1_fig4_binned(df_cod1, out_dir)

    print(f"[paper_figures] wrote {out_dir}")


if __name__ == "__main__":
    main()
