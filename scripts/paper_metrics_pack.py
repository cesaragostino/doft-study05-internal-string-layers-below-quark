#!/usr/bin/env python3
"""Generate paper-ready metrics tables and plots for one or more olas."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _to_float(val: Any) -> Optional[float]:
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str) and val.strip():
        try:
            return float(val)
        except ValueError:
            return None
    return None


def _to_int(val: Any) -> Optional[int]:
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val)
    if isinstance(val, str) and val.strip():
        try:
            return int(float(val))
        except ValueError:
            return None
    return None


def _to_bool(val: Any) -> Optional[bool]:
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        lowered = val.strip().lower()
        if lowered in ("true", "1", "yes"):
            return True
        if lowered in ("false", "0", "no"):
            return False
    return None


def _load_csv(path: Path) -> List[Dict[str, Any]]:
    with path.open() as f:
        reader = csv.DictReader(f)
        return list(reader)


def _ensure_matplotlib() -> Any:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except Exception as exc:  # pragma: no cover - runtime import
        raise RuntimeError("matplotlib required for plotting") from exc
    return plt


def _group_by(items: Iterable[Dict[str, Any]], key: str) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for row in items:
        val = row.get(key)
        grouped.setdefault(str(val), []).append(row)
    return grouped


def _aggregate_by_node_count(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    buckets: Dict[int, Dict[str, Any]] = {}
    for row in rows:
        n = _to_int(row.get("node_count"))
        if n is None:
            continue
        bucket = buckets.setdefault(n, {"total": 0, "passed": 0, "promoted": 0, "viable_tax": 0})
        bucket["total"] += 1
        if _to_bool(row.get("sweep_passed")):
            bucket["passed"] += 1
        if _to_bool(row.get("promoted")):
            bucket["promoted"] += 1
        attractor = str(row.get("attractor_class") or "")
        if attractor in ("FUNCTIONAL_LOCK", "HYPER_SYNC"):
            bucket["viable_tax"] += 1
    result = []
    for n, bucket in sorted(buckets.items()):
        total = bucket["total"]
        passed_rate = (bucket["passed"] / total) if total else None
        promoted_rate = (bucket["promoted"] / total) if total else None
        viable_rate = (bucket["viable_tax"] / total) if total else None
        passed_ci = _wilson_ci(bucket["passed"], total)
        promoted_ci = _wilson_ci(bucket["promoted"], total)
        viable_ci = _wilson_ci(bucket["viable_tax"], total)
        result.append(
            {
                "node_count": n,
                "total": total,
                "technical_viable_rate": passed_rate,
                "promoted_rate": promoted_rate,
                "viable_rate_taxonomic": viable_rate,
                "technical_viable_ci": passed_ci,
                "promoted_rate_ci": promoted_ci,
                "viable_rate_taxonomic_ci": viable_ci,
            }
        )
    return result


def _wilson_ci(successes: int, total: int, z: float = 1.96) -> Optional[Tuple[float, float, float]]:
    if total <= 0:
        return None
    p = successes / total
    denom = 1.0 + (z**2) / total
    center = (p + (z**2) / (2 * total)) / denom
    margin = z * ((p * (1 - p) / total + (z**2) / (4 * total * total)) ** 0.5) / denom
    lo = max(0.0, center - margin)
    hi = min(1.0, center + margin)
    return center, lo, hi


def _write_csv(path: Path, fieldnames: List[str], rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _plot_rates_vs_n(rows: List[Dict[str, Any]], output_path: Path) -> None:
    plt = _ensure_matplotlib()
    if not rows:
        return
    xs = [row["node_count"] for row in rows]
    tech = [row["technical_viable_rate"] for row in rows]
    promo = [row["promoted_rate"] for row in rows]
    tax = [row["viable_rate_taxonomic"] for row in rows]
    tech_err = [
        (
            row["technical_viable_ci"][0] - row["technical_viable_ci"][1],
            row["technical_viable_ci"][2] - row["technical_viable_ci"][0],
        )
        if row.get("technical_viable_ci")
        else (0.0, 0.0)
        for row in rows
    ]
    promo_err = [
        (
            row["promoted_rate_ci"][0] - row["promoted_rate_ci"][1],
            row["promoted_rate_ci"][2] - row["promoted_rate_ci"][0],
        )
        if row.get("promoted_rate_ci")
        else (0.0, 0.0)
        for row in rows
    ]
    tax_err = [
        (
            row["viable_rate_taxonomic_ci"][0] - row["viable_rate_taxonomic_ci"][1],
            row["viable_rate_taxonomic_ci"][2] - row["viable_rate_taxonomic_ci"][0],
        )
        if row.get("viable_rate_taxonomic_ci")
        else (0.0, 0.0)
        for row in rows
    ]
    plt.figure(figsize=(6.5, 4))
    plt.errorbar(
        xs,
        tech,
        yerr=list(zip(*tech_err)),
        marker="o",
        linestyle="-",
        label="technical_viable_rate",
    )
    plt.errorbar(
        xs,
        promo,
        yerr=list(zip(*promo_err)),
        marker="o",
        linestyle="-",
        label="promoted_rate",
    )
    plt.errorbar(
        xs,
        tax,
        yerr=list(zip(*tax_err)),
        marker="o",
        linestyle="-",
        label="viable_rate_taxonomic",
    )
    plt.xlabel("N (node_count)")
    plt.ylabel("Rate")
    plt.title("Rates vs N")
    plt.legend()
    plt.grid(True, alpha=0.3)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_heatmap(rows: List[Dict[str, Any]], output_path: Path) -> None:
    plt = _ensure_matplotlib()
    if not rows:
        return
    templates = sorted({str(row.get("template_name") or "unknown") for row in rows})
    node_counts = sorted({int(row["node_count"]) for row in rows if _to_int(row.get("node_count")) is not None})
    if not templates or not node_counts:
        return
    index = {tpl: i for i, tpl in enumerate(templates)}
    col_index = {n: i for i, n in enumerate(node_counts)}
    total = [[0 for _ in node_counts] for _ in templates]
    passed = [[0 for _ in node_counts] for _ in templates]
    for row in rows:
        tpl = str(row.get("template_name") or "unknown")
        n = _to_int(row.get("node_count"))
        if n is None:
            continue
        i = index[tpl]
        j = col_index[n]
        total[i][j] += 1
        if _to_bool(row.get("sweep_passed")):
            passed[i][j] += 1
    rates = [
        [passed[i][j] / total[i][j] if total[i][j] else 0.0 for j in range(len(node_counts))]
        for i in range(len(templates))
    ]
    plt.figure(figsize=(7.5, 0.4 * len(templates) + 2))
    cmap = plt.get_cmap("viridis")
    norm = plt.matplotlib.colors.Normalize(vmin=0.0, vmax=1.0)
    plt.imshow(rates, aspect="auto", cmap=cmap, norm=norm)
    plt.colorbar(label="technical_viable_rate")
    plt.yticks(range(len(templates)), templates)
    plt.xticks(range(len(node_counts)), [str(n) for n in node_counts])
    for i in range(len(templates)):
        for j in range(len(node_counts)):
            count = total[i][j]
            if count:
                r, g, b, _ = cmap(norm(rates[i][j]))
                luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
                text_color = "black" if luminance > 0.6 else "white"
                plt.text(j, i, str(count), ha="center", va="center", color=text_color, fontsize=8)
    plt.xlabel("N (node_count)")
    plt.title("Template vs N (technical viable rate)")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_scatter(rows: List[Dict[str, Any]], output_path: Path) -> None:
    plt = _ensure_matplotlib()
    xs = []
    ys = []
    cs = []
    for row in rows:
        r = _to_float(row.get("R_network_S1_mean"))
        pe = _to_float(row.get("PE_lockS1_norm_mean"))
        n = _to_int(row.get("node_count"))
        if r is None or pe is None or n is None:
            continue
        xs.append(r)
        ys.append(pe)
        cs.append(n)
    if not xs:
        return
    plt.figure(figsize=(6.5, 4.5))
    sc = plt.scatter(xs, ys, c=cs, cmap="viridis", alpha=0.7)
    plt.colorbar(sc, label="N (node_count)")
    plt.xlabel("R_network_S1_mean")
    plt.ylabel("PE_lockS1_norm_mean")
    plt.title("Coherence vs Complexity")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_robustness(rows: List[Dict[str, Any]], output_path: Path) -> None:
    plt = _ensure_matplotlib()
    xs = []
    ys = []
    for row in rows:
        n = _to_int(row.get("node_count"))
        robust = _to_float(row.get("robust_score_v1"))
        if n is None or robust is None:
            continue
        xs.append(n)
        ys.append(robust)
    if not xs:
        return
    plt.figure(figsize=(6.5, 4))
    plt.scatter(xs, ys, alpha=0.7)
    plt.xlabel("N (node_count)")
    plt.ylabel("robust_score_v1")
    plt.title("Robustness vs N")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_h_part(rows: List[Dict[str, Any]], output_path: Path) -> None:
    plt = _ensure_matplotlib()
    xs = []
    ys = []
    colors = []
    class_map = {
        "FUNCTIONAL_LOCK": "tab:blue",
        "HYPER_SYNC": "tab:orange",
        "INCOHERENT": "tab:red",
        "UNMEASURED": "tab:gray",
    }
    for row in rows:
        n = _to_int(row.get("node_count"))
        h = _to_float(row.get("H_part_norm_mean"))
        if n is None or h is None:
            continue
        attractor = str(row.get("attractor_class") or "UNMEASURED")
        xs.append(n)
        ys.append(h)
        colors.append(class_map.get(attractor, "tab:gray"))
    if not xs:
        return
    plt.figure(figsize=(6.5, 4))
    plt.scatter(xs, ys, alpha=0.7, c=colors)
    plt.xlabel("N (node_count)")
    plt.ylabel("H_part_norm_mean")
    plt.title("Participation Entropy vs N (by attractor_class)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _paper_rows(rows: List[Dict[str, Any]], ola_label: Optional[str] = None) -> List[Dict[str, Any]]:
    out = []
    for row in rows:
        ola_val = row.get("ola") or ola_label
        out.append(
            {
                "entity_id": row.get("entity_id"),
                "ola": ola_val,
                "template_name": row.get("template_name"),
                "node_count": row.get("node_count"),
                "edge_count": row.get("edge_count"),
                "density": row.get("density"),
                "degree_mean": row.get("degree_mean"),
                "degree_std": row.get("degree_std"),
                "sweep_evals_planned": row.get("sweep_evals_planned"),
                "sweep_evals_total": row.get("sweep_evals_total"),
                "seed_evals_total": row.get("seed_evals_total"),
                "seed_success_count": row.get("seed_success_count"),
                "sweep_passed_total": row.get("sweep_passed_total"),
                "sweep_passed": row.get("sweep_passed"),
                "is_candidate": row.get("is_candidate"),
                "was_swept": row.get("was_swept"),
                "bins_used_count": row.get("bins_used_count"),
                "taxonomy_kingdom": row.get("taxonomy_kingdom"),
                "viable_state": row.get("viable_state"),
                "viability_state": row.get("viability_state"),
                "locked": row.get("locked"),
                "attractor_class": row.get("attractor_class"),
                "dof_grade": row.get("dof_grade"),
                "promoted": row.get("promoted"),
                "R_network_S1_mean": row.get("R_network_S1_mean"),
                "PE_lockS1_norm_mean": row.get("PE_lockS1_norm_mean"),
                "H_part_norm_mean": row.get("H_part_norm_mean"),
                "R_mean_lastW_mean": row.get("R_mean_lastW_mean"),
                "phase_var_lastW_mean": row.get("phase_var_lastW_mean"),
                "QualityLock_mean": row.get("QualityLock_mean"),
                "seed_success_rate": row.get("seed_success_rate"),
                "robust_score_v1": row.get("robust_score_v1"),
                "robust_score_v2": row.get("robust_score_v2"),
                "runtime_sec_mean": row.get("runtime_sec_mean"),
                "nan_primary_rate": row.get("nan_primary_rate"),
                "confirmed_family_id": row.get("confirmed_family_id"),
            }
        )
    return out


def _prepare_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for row in rows:
        row["node_count"] = _to_int(row.get("node_count"))
        row["edge_count"] = _to_int(row.get("edge_count"))
        row["density"] = _to_float(row.get("density"))
        row["degree_mean"] = _to_float(row.get("degree_mean"))
        row["degree_std"] = _to_float(row.get("degree_std"))
        row["sweep_passed"] = _to_bool(row.get("sweep_passed"))
        row["promoted"] = _to_bool(row.get("promoted"))
        row["locked"] = _to_bool(row.get("locked"))
        row["is_candidate"] = _to_bool(row.get("is_candidate"))
        row["was_swept"] = _to_bool(row.get("was_swept"))
        row["sweep_evals_total"] = _to_int(row.get("sweep_evals_total"))
    return rows


def _paper_summary(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(rows)
    evaluated = sum(1 for row in rows if _to_int(row.get("sweep_evals_total")) or 0)
    passed = sum(1 for row in rows if _to_bool(row.get("sweep_passed")))
    promoted = sum(1 for row in rows if _to_bool(row.get("promoted")))
    return {
        "candidates_total": total,
        "evaluated_total": evaluated,
        "sweep_passed_total": passed,
        "technical_viable_rate": (passed / total) if total else None,
        "promoted_total": promoted,
        "promoted_rate": (promoted / total) if total else None,
    }


def _resolve_ola_dirs(args: argparse.Namespace) -> List[Path]:
    if args.ola_dir:
        return [Path(val) for val in args.ola_dir]
    if not args.olas:
        raise SystemExit("Provide --olas or --ola-dir.")
    root = Path(args.processed_root)
    olas = [part.strip() for part in args.olas.split(",") if part.strip()]
    return [root / f"ola{val}" for val in olas]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate paper metrics + plots per ola.")
    parser.add_argument("--olas", help="Comma-separated ola numbers (e.g. 2,3,4).")
    parser.add_argument("--processed-root", default="data/processed")
    parser.add_argument("--ola-dir", action="append", help="Explicit ola directory (repeatable).")
    parser.add_argument("--out-root", default="data/processed/paper")
    parser.add_argument("--all", action="store_true", help="Generate consolidated output in /all.")
    args = parser.parse_args()

    all_rows: List[Dict[str, Any]] = []
    all_paper_rows: List[Dict[str, Any]] = []
    for ola_dir in _resolve_ola_dirs(args):
        ola_name = ola_dir.name
        catalog_dir = ola_dir / "catalog"
        taxonomy_csv = catalog_dir / f"genome_layers_{ola_name}_taxonomy.csv"
        if not taxonomy_csv.exists():
            print(f"[paper_pack] WARNING - STOPPED: missing {taxonomy_csv}")
            continue
        rows = _prepare_rows(_load_csv(taxonomy_csv))
        out_dir = Path(args.out_root) / ola_name
        out_dir.mkdir(parents=True, exist_ok=True)

        paper_rows = _paper_rows(rows, ola_label=ola_name)
        fieldnames = list(paper_rows[0].keys()) if paper_rows else []
        _write_csv(out_dir / f"paper_metrics_{ola_name}.csv", fieldnames, paper_rows)

        agg_rows = _aggregate_by_node_count(rows)
        _plot_rates_vs_n(agg_rows, out_dir / "rates_vs_n.png")
        _plot_heatmap(rows, out_dir / "heatmap_template_vs_n.png")
        _plot_scatter(rows, out_dir / "scatter_R_vs_PE.png")
        _plot_robustness(rows, out_dir / "robustness_vs_n.png")
        _plot_h_part(rows, out_dir / "h_part_vs_n.png")

        summary = {
            "ola_dir": str(ola_dir),
            "taxonomy_csv": str(taxonomy_csv),
            "paper_csv": str(out_dir / f"paper_metrics_{ola_name}.csv"),
            "plots": [
                "rates_vs_n.png",
                "heatmap_template_vs_n.png",
                "scatter_R_vs_PE.png",
                "robustness_vs_n.png",
                "h_part_vs_n.png",
            ],
            "rows": len(rows),
        }
        (out_dir / "paper_metrics_manifest.json").write_text(json.dumps(summary, indent=2))
        (out_dir / "paper_metrics_summary.json").write_text(json.dumps(_paper_summary(rows), indent=2))
        print(f"[paper_pack] wrote {out_dir}")

        all_rows.extend(rows)
        all_paper_rows.extend(paper_rows)

    if args.all and all_rows:
        out_dir = Path(args.out_root) / "all"
        out_dir.mkdir(parents=True, exist_ok=True)
        fieldnames = list(all_paper_rows[0].keys()) if all_paper_rows else []
        _write_csv(out_dir / "paper_metrics_all.csv", fieldnames, all_paper_rows)
        agg_rows = _aggregate_by_node_count(all_rows)
        _plot_rates_vs_n(agg_rows, out_dir / "rates_vs_n.png")
        _plot_heatmap(all_rows, out_dir / "heatmap_template_vs_n.png")
        _plot_scatter(all_rows, out_dir / "scatter_R_vs_PE.png")
        _plot_robustness(all_rows, out_dir / "robustness_vs_n.png")
        _plot_h_part(all_rows, out_dir / "h_part_vs_n.png")
        summary = {
            "olas": sorted({row.get("ola") for row in all_paper_rows}),
            "paper_csv": str(out_dir / "paper_metrics_all.csv"),
            "plots": [
                "rates_vs_n.png",
                "heatmap_template_vs_n.png",
                "scatter_R_vs_PE.png",
                "robustness_vs_n.png",
                "h_part_vs_n.png",
            ],
            "rows": len(all_rows),
        }
        (out_dir / "paper_metrics_manifest.json").write_text(json.dumps(summary, indent=2))
        (out_dir / "paper_metrics_summary.json").write_text(json.dumps(_paper_summary(all_rows), indent=2))
        print(f"[paper_pack] wrote {out_dir}")


if __name__ == "__main__":
    main()
