#!/usr/bin/env python3
"""Generate paper-ready metrics tables and plots for one or more olas."""

from __future__ import annotations

import argparse
import csv
import json
import math
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


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


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


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _aggregate_rates_by_node_count(
    rollups_by_template: List[Dict[str, Any]],
    taxonomy_by_template: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    buckets: Dict[int, Dict[str, Any]] = {}
    for row in rollups_by_template:
        n = _to_int(row.get("N"))
        if n is None:
            continue
        bucket = buckets.setdefault(
            n,
            {
                "attempts_total": 0,
                "candidates_total": 0,
                "sweep_passed_total": 0,
                "promoted_total": 0,
                "promoted_base_total": 0,
            },
        )
        bucket["attempts_total"] += int(_to_int(row.get("attempts_total")) or 0)
        bucket["candidates_total"] += int(_to_int(row.get("candidates_total")) or 0)
        bucket["sweep_passed_total"] += int(_to_int(row.get("sweep_passed_total")) or 0)
    if taxonomy_by_template:
        for row in taxonomy_by_template:
            n = _to_int(row.get("N"))
            if n is None:
                continue
            bucket = buckets.setdefault(
                n,
                {
                    "attempts_total": 0,
                    "candidates_total": 0,
                    "sweep_passed_total": 0,
                    "promoted_total": 0,
                    "promoted_base_total": 0,
                },
            )
            bucket["promoted_total"] += int(_to_int(row.get("promoted_total")) or 0)
            bucket["promoted_base_total"] += int(_to_int(row.get("total")) or 0)
    result = []
    for n, bucket in sorted(buckets.items()):
        attempts = bucket["attempts_total"]
        candidates = bucket["candidates_total"]
        sweep_passed = bucket["sweep_passed_total"]
        promoted_total = bucket["promoted_total"]
        promoted_base = bucket["promoted_base_total"]
        candidate_rate = (candidates / attempts) if attempts else None
        sweep_pass_rate = (sweep_passed / candidates) if candidates else None
        promoted_rate = (promoted_total / promoted_base) if promoted_base else None
        result.append(
            {
                "node_count": n,
                "attempts_total": attempts,
                "candidates_total": candidates,
                "sweep_passed_total": sweep_passed,
                "candidate_rate": candidate_rate,
                "sweep_pass_rate": sweep_pass_rate,
                "promoted_rate": promoted_rate,
                "candidate_rate_ci": _wilson_ci(candidates, attempts) if attempts else None,
                "sweep_pass_rate_ci": _wilson_ci(sweep_passed, candidates) if candidates else None,
                "promoted_rate_ci": _wilson_ci(promoted_total, promoted_base) if promoted_base else None,
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
    candidate = [row["candidate_rate"] for row in rows]
    sweep_pass = [row["sweep_pass_rate"] for row in rows]
    promo = [row["promoted_rate"] for row in rows]
    cand_err = [
        (
            row["candidate_rate_ci"][0] - row["candidate_rate_ci"][1],
            row["candidate_rate_ci"][2] - row["candidate_rate_ci"][0],
        )
        if row.get("candidate_rate_ci")
        else (0.0, 0.0)
        for row in rows
    ]
    sweep_err = [
        (
            row["sweep_pass_rate_ci"][0] - row["sweep_pass_rate_ci"][1],
            row["sweep_pass_rate_ci"][2] - row["sweep_pass_rate_ci"][0],
        )
        if row.get("sweep_pass_rate_ci")
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
    plt.figure(figsize=(6.5, 4))
    plt.errorbar(
        xs,
        candidate,
        yerr=list(zip(*cand_err)),
        marker="o",
        linestyle="-",
        label="candidate_rate",
    )
    plt.errorbar(
        xs,
        sweep_pass,
        yerr=list(zip(*sweep_err)),
        marker="o",
        linestyle="-",
        label="sweep_pass_rate",
    )
    plt.errorbar(
        xs,
        promo,
        yerr=list(zip(*promo_err)),
        marker="o",
        linestyle="-",
        label="promoted_rate",
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


def _template_family(name: str) -> str:
    lowered = name.lower()
    if lowered.startswith("ring"):
        return "ring"
    if lowered.startswith("ladder"):
        return "ladder"
    if lowered.startswith("bipartite"):
        return "bipartite"
    if lowered.startswith("complete"):
        return "complete"
    return "other"


def _template_sort_key(name: str) -> tuple[int, str]:
    order = {"ring": 0, "ladder": 1, "bipartite": 2, "complete": 3, "other": 4}
    family = _template_family(name)
    return (order.get(family, 4), name)


def _plot_heatmap(rows: List[Dict[str, Any]], output_path: Path) -> None:
    plt = _ensure_matplotlib()
    if not rows:
        return
    templates = sorted(
        {str(row.get("template_name") or "unknown") for row in rows},
        key=_template_sort_key,
    )
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
    plt.colorbar(label="sweep_pass_rate (conditional on candidate)")
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
    plt.title("Template vs N (sweep pass rate, conditional on candidate)")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_candidate_rate_heatmap(
    rollups_by_template: List[Dict[str, Any]], output_path: Path
) -> None:
    plt = _ensure_matplotlib()
    if not rollups_by_template:
        return
    templates = sorted(
        {str(row.get("template_name") or "unknown") for row in rollups_by_template},
        key=_template_sort_key,
    )
    node_counts = sorted(
        {int(row["N"]) for row in rollups_by_template if _to_int(row.get("N")) is not None}
    )
    if not templates or not node_counts:
        return
    index = {tpl: i for i, tpl in enumerate(templates)}
    col_index = {n: i for i, n in enumerate(node_counts)}
    attempts = [[0 for _ in node_counts] for _ in templates]
    candidates = [[0 for _ in node_counts] for _ in templates]
    for row in rollups_by_template:
        tpl = str(row.get("template_name") or "unknown")
        n = _to_int(row.get("N"))
        if n is None:
            continue
        i = index[tpl]
        j = col_index[n]
        attempts[i][j] += int(_to_int(row.get("attempts_total")) or 0)
        candidates[i][j] += int(_to_int(row.get("candidates_total")) or 0)
    rates = [
        [
            (candidates[i][j] / attempts[i][j]) if attempts[i][j] else 0.0
            for j in range(len(node_counts))
        ]
        for i in range(len(templates))
    ]
    plt.figure(figsize=(7.5, 0.4 * len(templates) + 2))
    cmap = plt.get_cmap("viridis")
    norm = plt.matplotlib.colors.Normalize(vmin=0.0, vmax=1.0)
    plt.imshow(rates, aspect="auto", cmap=cmap, norm=norm)
    plt.colorbar(label="candidate_rate")
    plt.yticks(range(len(templates)), templates)
    plt.xticks(range(len(node_counts)), [str(n) for n in node_counts])
    for i in range(len(templates)):
        for j in range(len(node_counts)):
            n_attempts = attempts[i][j]
            if n_attempts:
                rate = rates[i][j]
                r, g, b, _ = cmap(norm(rate))
                luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
                text_color = "black" if luminance > 0.6 else "white"
                label = f"{rate:.2f}\\n(n={n_attempts})"
                plt.text(j, i, label, ha="center", va="center", color=text_color, fontsize=7)
    plt.xlabel("N (node_count)")
    plt.title("Template vs N (candidate_rate)")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_explorer_fail_boxplots(attempts_rows: List[Dict[str, Any]], output_path: Path) -> bool:
    plt = _ensure_matplotlib()
    metrics = [
        ("R_mean_lastW", "R_mean_lastW"),
        ("phase_var_lastW", "phase_var_lastW"),
        ("QualityLock", "QualityLock"),
        ("entropy_quality", "entropy_quality"),
    ]
    cand_vals: Dict[str, List[float]] = {name: [] for name, _ in metrics}
    non_vals: Dict[str, List[float]] = {name: [] for name, _ in metrics}
    for row in attempts_rows:
        is_candidate = _to_bool(row.get("is_candidate"))
        metrics_raw = row.get("metrics_raw") or {}
        for name, key in metrics:
            val = _to_float(metrics_raw.get(key))
            if val is None:
                continue
            if is_candidate:
                cand_vals[name].append(val)
            else:
                non_vals[name].append(val)
    if not any(non_vals[name] for name, _ in metrics):
        return False
    fig, axes = plt.subplots(2, 2, figsize=(8, 6))
    for ax, (name, _key) in zip(axes.flatten(), metrics):
        data = [non_vals[name], cand_vals[name]]
        ax.boxplot(data, tick_labels=["non-candidate", "candidate"], showfliers=False)
        ax.set_title(name)
    fig.suptitle("Explorer metrics by is_candidate")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
    return True


def _resolve_particle_library(base_dir: Path) -> Optional[Path]:
    candidates = [
        Path("data/processed/ola1/simple_blocks.json"),
        Path("data/processed/ola1/simple_blocks_canonical.json"),
    ]
    for path in candidates:
        if path.exists():
            return path
    alt = base_dir / "simple_blocks.json"
    return alt if alt.exists() else None


def _normalize_id(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, bool):
        return str(int(value))
    if isinstance(value, int):
        return str(value)
    try:
        fval = float(value)
        if math.isfinite(fval) and fval.is_integer():
            return str(int(fval))
    except Exception:
        pass
    return str(value)


def _particle_name_map(blocks_path: Path) -> Dict[str, str]:
    raw = json.loads(blocks_path.read_text())
    blocks = raw if isinstance(raw, list) else raw.get("blocks", [])
    mapping: Dict[str, str] = {}
    for block in blocks:
        if not isinstance(block, dict):
            continue
        name = block.get("particle_name")
        if not name:
            continue
        block_id = _normalize_id(block.get("block_id"))
        origin_run_id = _normalize_id(block.get("origin_run_id"))
        if block_id is not None:
            mapping[block_id] = str(name)
        if origin_run_id is not None:
            mapping[origin_run_id] = str(name)
    return mapping


def _origin_run_id_map(blocks_path: Path) -> Dict[str, str]:
    raw = json.loads(blocks_path.read_text())
    blocks = raw if isinstance(raw, list) else raw.get("blocks", [])
    mapping: Dict[str, str] = {}
    for block in blocks:
        if not isinstance(block, dict):
            continue
        block_id = _normalize_id(block.get("block_id"))
        origin_run_id = _normalize_id(block.get("origin_run_id"))
        if block_id is None or origin_run_id is None:
            continue
        mapping[block_id] = origin_run_id
    return mapping


def _candidate_block_ids(row: Dict[str, Any]) -> List[str]:
    assignment = row.get("assignment") or {}
    block_ids = assignment.get("block_ids") if isinstance(assignment, dict) else None
    if not block_ids:
        build_plan = row.get("build_plan") or {}
        assignment = build_plan.get("assignment") if isinstance(build_plan, dict) else None
        if isinstance(assignment, dict):
            block_ids = assignment.get("block_ids")
    if not block_ids:
        return []
    return [str(bid) for bid in block_ids]


def _build_particle_enrichment(
    attempts_rows: List[Dict[str, Any]],
    blocks_path: Path,
    pseudocount: float = 0.5,
) -> Optional[List[Dict[str, Any]]]:
    mapping = _particle_name_map(blocks_path)
    origin_map = _origin_run_id_map(Path("data/processed/ola1/simple_blocks_canonical.json"))
    if not mapping or not origin_map:
        return None
    baseline_counts: Dict[str, int] = {}
    for name in mapping.values():
        baseline_counts[name] = baseline_counts.get(name, 0) + 1
    baseline_total = sum(baseline_counts.values())
    if baseline_total == 0:
        return None
    templates = {}
    for row in attempts_rows:
        if not _to_bool(row.get("is_candidate")):
            continue
        template_name = str(row.get("template_name") or "unknown")
        block_ids = _candidate_block_ids(row)
        if not block_ids:
            continue
        t_bucket = templates.setdefault(template_name, {})
        for bid in block_ids:
            particle = mapping.get(bid)
            if not particle:
                origin_run_id = origin_map.get(bid)
                if origin_run_id:
                    particle = mapping.get(origin_run_id)
            if not particle:
                continue
            t_bucket[particle] = t_bucket.get(particle, 0) + 1
    particle_names = sorted(baseline_counts.keys())
    rows: List[Dict[str, Any]] = []
    for template_name, observed_counts in templates.items():
        observed_total = sum(observed_counts.values())
        denom_base = baseline_total + pseudocount * len(particle_names)
        denom_obs = observed_total + pseudocount * len(particle_names)
        for particle in particle_names:
            base_count = baseline_counts.get(particle, 0)
            obs_count = observed_counts.get(particle, 0)
            base_rate = (base_count + pseudocount) / denom_base
            obs_rate = (obs_count + pseudocount) / denom_obs
            log_odds = math.log(obs_rate / base_rate)
            rows.append(
                {
                    "template_name": template_name,
                    "particle_name": particle,
                    "baseline_count": base_count,
                    "baseline_rate": base_rate,
                    "observed_count": obs_count,
                    "observed_rate": obs_rate,
                    "log_odds": log_odds,
                }
            )
    return rows


def _plot_particle_enrichment_heatmap(
    rows: List[Dict[str, Any]], output_path: Path, max_particles: int = 12
) -> None:
    plt = _ensure_matplotlib()
    if not rows:
        return
    particle_totals: Dict[str, int] = {}
    for row in rows:
        particle = str(row.get("particle_name") or "unknown")
        particle_totals[particle] = particle_totals.get(particle, 0) + int(row.get("baseline_count") or 0)
    particles = sorted(particle_totals.keys(), key=lambda p: particle_totals[p], reverse=True)[:max_particles]
    templates = sorted({str(row.get("template_name") or "unknown") for row in rows}, key=_template_sort_key)
    if not particles or not templates:
        return
    index = {tpl: i for i, tpl in enumerate(templates)}
    col_index = {p: i for i, p in enumerate(particles)}
    values = [[0.0 for _ in particles] for _ in templates]
    for row in rows:
        particle = str(row.get("particle_name") or "unknown")
        if particle not in col_index:
            continue
        template = str(row.get("template_name") or "unknown")
        if template not in index:
            continue
        values[index[template]][col_index[particle]] = float(row.get("log_odds") or 0.0)
    plt.figure(figsize=(8, 0.45 * len(templates) + 2))
    cmap = plt.get_cmap("coolwarm")
    plt.imshow(values, aspect="auto", cmap=cmap)
    plt.colorbar(label="log-odds enrichment")
    plt.yticks(range(len(templates)), templates)
    plt.xticks(range(len(particles)), particles, rotation=45, ha="right")
    plt.xlabel("particle_name (top baseline)")
    plt.title("Particle enrichment by template (log-odds)")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _taxonomy_lookup(catalog_dir: Path) -> Dict[str, Dict[str, Any]]:
    taxonomy_csv = catalog_dir / f"genome_layers_{catalog_dir.parent.name}_taxonomy.csv"
    if not taxonomy_csv.exists():
        return {}
    rows = _load_csv(taxonomy_csv)
    lookup: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        entity_id = row.get("entity_id")
        if entity_id:
            lookup[str(entity_id)] = row
    return lookup


def _sweep_status(row: Optional[Dict[str, Any]]) -> Optional[bool]:
    if not row:
        return None
    val = _to_bool(row.get("sweep_passed"))
    if val is not None:
        return val
    evals = _to_int(row.get("sweep_evals_total"))
    if evals and evals > 0:
        return True
    return False


def _promoted_status(row: Optional[Dict[str, Any]]) -> Optional[bool]:
    if not row:
        return None
    val = _to_bool(row.get("promoted"))
    if val is not None:
        return val
    return None


def _build_lineage_links(
    attempts_rows: List[Dict[str, Any]],
    blocks_path: Path,
    taxonomy_lookup: Dict[str, Dict[str, Any]],
    max_particles: int = 12,
) -> Optional[Tuple[List[List[str]], Dict[Tuple[int, str, str], int]]]:
    mapping = _particle_name_map(blocks_path)
    origin_map = _origin_run_id_map(Path("data/processed/ola1/simple_blocks_canonical.json"))
    if not mapping or not origin_map:
        return None
    particle_counts: Dict[str, int] = {}
    template_counts: Dict[str, int] = {}
    link_counts: Dict[Tuple[int, str, str], int] = {}
    for row in attempts_rows:
        template_name = str(row.get("template_name") or "unknown")
        candidate = _to_bool(row.get("is_candidate"))
        entity_id = str(row.get("entity_id") or "")
        block_ids = _candidate_block_ids(row)
        if not block_ids:
            continue
        tax_row = taxonomy_lookup.get(entity_id)
        sweep_passed = _sweep_status(tax_row)
        promoted = _promoted_status(tax_row)
        if not candidate:
            sweep_label = "not_candidate"
            promote_label = "not_candidate"
        else:
            sweep_label = "sweep_pass" if sweep_passed else "sweep_fail" if sweep_passed is False else "no_eval"
            promote_label = (
                "promoted"
                if promoted
                else "not_promoted"
                if promoted is False
                else "no_eval"
            )
        for bid in block_ids:
            particle = mapping.get(bid)
            if not particle:
                origin_run_id = origin_map.get(bid)
                if origin_run_id:
                    particle = mapping.get(origin_run_id)
            if not particle:
                continue
            particle_counts[particle] = particle_counts.get(particle, 0) + 1
            template_counts[template_name] = template_counts.get(template_name, 0) + 1
            for idx, (src, dst) in enumerate(
                [
                    (particle, template_name),
                    (template_name, "candidate" if candidate else "non_candidate"),
                    ("candidate" if candidate else "non_candidate", sweep_label),
                    (sweep_label, promote_label),
                ]
            ):
                key = (idx, str(src), str(dst))
                link_counts[key] = link_counts.get(key, 0) + 1
    if not link_counts:
        return None
    top_particles = {
        name for name, _count in sorted(particle_counts.items(), key=lambda kv: kv[1], reverse=True)[:max_particles]
    }
    if len(particle_counts) > len(top_particles):
        adjusted: Dict[Tuple[int, str, str], int] = {}
        for (idx, src, dst), count in link_counts.items():
            if idx == 0:
                src = src if src in top_particles else "other"
            adjusted[(idx, src, dst)] = adjusted.get((idx, src, dst), 0) + count
        link_counts = adjusted
        particle_counts = {k: v for k, v in particle_counts.items() if k in top_particles}
        particle_counts["other"] = sum(
            count for name, count in particle_counts.items() if name not in top_particles
        )
    stages = [
        sorted(
            {src for (idx, src, _dst) in link_counts if idx == 0},
            key=lambda p: particle_counts.get(p, 0),
            reverse=True,
        ),
        sorted(template_counts.keys(), key=lambda t: template_counts.get(t, 0), reverse=True),
        ["candidate", "non_candidate"],
        ["sweep_pass", "sweep_fail", "no_eval", "not_candidate"],
        ["promoted", "not_promoted", "no_eval", "not_candidate"],
    ]
    return stages, link_counts


def _plot_lineage_sankey(
    stages: List[List[str]],
    link_counts: Dict[Tuple[int, str, str], int],
    output_path: Path,
) -> None:
    plt = _ensure_matplotlib()
    stage_totals: List[Dict[str, int]] = [dict() for _ in stages]
    for (idx, src, dst), count in link_counts.items():
        stage_totals[idx][src] = stage_totals[idx].get(src, 0) + count
        stage_totals[idx + 1][dst] = stage_totals[idx + 1].get(dst, 0) + count
    max_total = max((sum(stage.values()) for stage in stage_totals if stage), default=0)
    if max_total == 0:
        return
    pad = max_total * 0.02
    node_pos: List[Dict[str, Tuple[float, float]]] = []
    for stage_idx, nodes in enumerate(stages):
        pos: Dict[str, Tuple[float, float]] = {}
        cursor = 0.0
        for node in nodes:
            height = float(stage_totals[stage_idx].get(node, 0))
            pos[node] = (cursor, cursor + height)
            cursor += height + pad
        node_pos.append(pos)
    fig_height = max(4.0, 0.12 * sum(len(stage) for stage in stages))
    plt.figure(figsize=(10, fig_height))
    ax = plt.gca()
    ax.set_axis_off()
    stage_offsets: List[Dict[str, float]] = [
        {node: 0.0 for node in stage} for stage in stages
    ]
    colors = plt.get_cmap("tab20").colors
    color_map = {node: colors[i % len(colors)] for i, node in enumerate(stages[0])}
    for (idx, src, dst), count in sorted(link_counts.items(), key=lambda kv: kv[0][0]):
        src_y0, src_y1 = node_pos[idx][src]
        dst_y0, dst_y1 = node_pos[idx + 1][dst]
        src_off = stage_offsets[idx][src]
        dst_off = stage_offsets[idx + 1][dst]
        src_span = (src_y0 + src_off, src_y0 + src_off + count)
        dst_span = (dst_y0 + dst_off, dst_y0 + dst_off + count)
        stage_offsets[idx][src] += count
        stage_offsets[idx + 1][dst] += count
        x0 = idx
        x1 = idx + 1
        polygon = plt.Polygon(
            [
                (x0, src_span[0]),
                (x0, src_span[1]),
                (x1, dst_span[1]),
                (x1, dst_span[0]),
            ],
            closed=True,
            facecolor=color_map.get(src, (0.6, 0.6, 0.6)),
            alpha=0.4,
            edgecolor="none",
        )
        ax.add_patch(polygon)
    for stage_idx, nodes in enumerate(stages):
        for node in nodes:
            y0, y1 = node_pos[stage_idx][node]
            if y1 <= y0:
                continue
            ax.text(
                stage_idx - 0.05,
                (y0 + y1) / 2,
                f"{node} ({int(stage_totals[stage_idx].get(node, 0))})",
                ha="right",
                va="center",
                fontsize=8,
            )
    ax.set_xlim(-0.5, len(stages) - 0.5)
    ax.set_ylim(0, max_total + pad * max(len(stage) for stage in stages))
    ax.set_title("Lineage flow (particle → template → explorer → sweep → promotion)")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_candidate_rate_vs_density(
    rollups_by_template: List[Dict[str, Any]],
    density_by_template: Dict[str, float],
    output_path: Path,
) -> None:
    plt = _ensure_matplotlib()
    xs = []
    ys = []
    cs = []
    for row in rollups_by_template:
        attempts = _to_int(row.get("attempts_total"))
        candidates = _to_int(row.get("candidates_total"))
        n_nodes = _to_int(row.get("N"))
        template_name = str(row.get("template_name") or "unknown")
        density = density_by_template.get(template_name)
        if attempts is None or candidates is None or n_nodes is None or density is None:
            continue
        if attempts <= 0:
            continue
        xs.append(density)
        ys.append(candidates / attempts)
        cs.append(n_nodes)
    if not xs:
        return
    plt.figure(figsize=(6.5, 4.5))
    sc = plt.scatter(xs, ys, c=cs, cmap="viridis", alpha=0.7)
    plt.colorbar(sc, label="N (node_count)")
    plt.xlabel("edge_density")
    plt.ylabel("candidate_rate")
    plt.title("Candidate rate vs edge density")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_robustness_vs_density(
    rows: List[Dict[str, Any]], output_path: Path
) -> None:
    plt = _ensure_matplotlib()
    xs = []
    ys = []
    cs = []
    for row in rows:
        density = _to_float(row.get("density"))
        robust = _to_float(row.get("robust_score_v1"))
        n_nodes = _to_int(row.get("node_count"))
        if density is None or robust is None or n_nodes is None:
            continue
        xs.append(density)
        ys.append(robust)
        cs.append(n_nodes)
    if not xs:
        return
    plt.figure(figsize=(6.5, 4.5))
    sc = plt.scatter(xs, ys, c=cs, cmap="viridis", alpha=0.7)
    plt.colorbar(sc, label="N (node_count)")
    plt.xlabel("edge_density")
    plt.ylabel("robust_score_v1")
    plt.title("Robustness vs edge density")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _linear_fit(xs: List[float], ys: List[float]) -> tuple[float, float, float, float, float]:
    n = len(xs)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    sxx = sum((x - x_mean) ** 2 for x in xs)
    if sxx == 0:
        return 0.0, y_mean, 0.0, 0.0, 0.0
    sxy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = y_mean - slope * x_mean
    residuals = [y - (slope * x + intercept) for x, y in zip(xs, ys)]
    sse = sum(r ** 2 for r in residuals)
    sst = sum((y - y_mean) ** 2 for y in ys)
    r2 = 1.0 - (sse / sst) if sst else 0.0
    if n < 3:
        return slope, intercept, r2, 0.0, 0.0
    mse = sse / (n - 2)
    slope_se = (mse / sxx) ** 0.5
    slope_ci = 1.96 * slope_se
    return slope, intercept, r2, slope_se, slope_ci


def _pearson_r(xs: List[float], ys: List[float]) -> Optional[float]:
    n = len(xs)
    if n < 2:
        return None
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    sxx = sum((x - x_mean) ** 2 for x in xs)
    syy = sum((y - y_mean) ** 2 for y in ys)
    sxy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    if sxx == 0 or syy == 0:
        return None
    return sxy / (sxx * syy) ** 0.5


def _approx_p_value_from_r(r: float, n: int) -> Optional[float]:
    if n < 3:
        return None
    denom = max(1e-9, 1.0 - r * r)
    t_val = abs(r) * ((n - 2) / denom) ** 0.5
    # Normal approximation for two-sided p-value.
    return math.erfc(t_val / (2 ** 0.5))


def _plot_scatter(rows: List[Dict[str, Any]], output_path: Path) -> None:
    plt = _ensure_matplotlib()
    xs = []
    ys = []
    cs = []
    for row in rows:
        evals_total = _to_int(row.get("sweep_evals_total"))
        if evals_total is not None and evals_total <= 0:
            continue
        if evals_total is None and not _to_bool(row.get("sweep_passed")):
            continue
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
    slope, intercept, r2, _slope_se, _slope_ci = _linear_fit(xs, ys)
    x_min = min(xs)
    x_max = max(xs)
    plt.plot([x_min, x_max], [slope * x_min + intercept, slope * x_max + intercept], color="black", lw=1.5)
    r_val = _pearson_r(xs, ys)
    p_val = _approx_p_value_from_r(r_val, len(xs)) if r_val is not None else None
    stat_line = f"slope={slope:.3f}  R2={r2:.3f}"
    if r_val is not None and p_val is not None:
        stat_line += f"  r={r_val:.3f}  p≈{p_val:.3g}"
    plt.text(0.02, 0.98, stat_line, transform=plt.gca().transAxes, va="top")
    plt.colorbar(sc, label="N (node_count)")
    plt.xlabel("R_network_S1_mean")
    plt.ylabel("PE_lockS1_norm_mean")
    plt.title("Coherence vs Complexity")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_candidate_rate_regression(
    rollups_by_template: List[Dict[str, Any]], output_path: Path
) -> None:
    plt = _ensure_matplotlib()
    xs = []
    ys = []
    labels = []
    for row in rollups_by_template:
        attempts = _to_int(row.get("attempts_total"))
        candidates = _to_int(row.get("candidates_total"))
        n_nodes = _to_int(row.get("N"))
        template_name = str(row.get("template_name") or "unknown")
        if attempts is None or candidates is None or n_nodes is None:
            continue
        p_hat = (candidates + 0.5) / (attempts + 1.0)
        xs.append(float(n_nodes))
        ys.append(math.log(p_hat))
        labels.append(template_name)
    if not xs:
        return
    slope, intercept, r2, _slope_se, slope_ci = _linear_fit(xs, ys)
    plt.figure(figsize=(6.5, 4.5))
    plt.scatter(xs, ys, alpha=0.8)
    x_min = min(xs)
    x_max = max(xs)
    plt.plot([x_min, x_max], [slope * x_min + intercept, slope * x_max + intercept], color="black", lw=1.5)
    plt.xlabel("N (node_count)")
    plt.ylabel("log(candidate_rate)")
    plt.title("log(candidate_rate) vs N (Jeffreys smoothing)")
    plt.text(0.02, 0.98, f"slope={slope:.3f} ± {slope_ci:.3f}  R2={r2:.3f}",
             transform=plt.gca().transAxes, va="top")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _fit_candidate_rate_model(
    rollups_by_template: List[Dict[str, Any]],
    density_by_template: Dict[str, float],
) -> Optional[Dict[str, Any]]:
    xs: List[List[float]] = []
    ys: List[float] = []
    for row in rollups_by_template:
        attempts = _to_int(row.get("attempts_total"))
        candidates = _to_int(row.get("candidates_total"))
        n_nodes = _to_int(row.get("N"))
        template_name = str(row.get("template_name") or "unknown")
        density = density_by_template.get(template_name)
        if attempts is None or candidates is None or n_nodes is None or density is None:
            continue
        p_hat = (candidates + 0.5) / (attempts + 1.0)
        family = _template_family(template_name)
        xs.append(
            [
                1.0,
                float(n_nodes),
                float(density),
                1.0 if family == "ring" else 0.0,
                1.0 if family == "ladder" else 0.0,
                1.0 if family == "bipartite" else 0.0,
                1.0 if family == "complete" else 0.0,
            ]
        )
        ys.append(math.log(p_hat))
    if len(xs) < 3:
        return None
    xtx = [[0.0 for _ in range(len(xs[0]))] for _ in range(len(xs[0]))]
    xty = [0.0 for _ in range(len(xs[0]))]
    for row, y in zip(xs, ys):
        for i in range(len(row)):
            xty[i] += row[i] * y
            for j in range(len(row)):
                xtx[i][j] += row[i] * row[j]
    # Solve xtx * beta = xty (basic Gauss-Jordan).
    n = len(xty)
    aug = [xtx[i] + [xty[i]] for i in range(n)]
    for i in range(n):
        pivot = aug[i][i]
        if abs(pivot) < 1e-12:
            return None
        for j in range(i, n + 1):
            aug[i][j] /= pivot
        for k in range(n):
            if k == i:
                continue
            factor = aug[k][i]
            for j in range(i, n + 1):
                aug[k][j] -= factor * aug[i][j]
    beta = [aug[i][n] for i in range(n)]
    preds = [sum(b * x for b, x in zip(beta, row)) for row in xs]
    y_mean = sum(ys) / len(ys)
    sse = sum((y - yhat) ** 2 for y, yhat in zip(ys, preds))
    sst = sum((y - y_mean) ** 2 for y in ys)
    r2 = 1.0 - sse / sst if sst else 0.0
    return {
        "coefficients": {
            "intercept": beta[0],
            "N": beta[1],
            "density": beta[2],
            "family_ring": beta[3],
            "family_ladder": beta[4],
            "family_bipartite": beta[5],
            "family_complete": beta[6],
        },
        "r2": r2,
        "n_templates": len(xs),
    }


def _plot_candidate_rate_residuals(
    rollups_by_template: List[Dict[str, Any]],
    density_by_template: Dict[str, float],
    model: Dict[str, Any],
    output_path: Path,
) -> None:
    plt = _ensure_matplotlib()
    coeff = model["coefficients"]
    families = ["ring", "ladder", "bipartite", "complete", "other"]
    points: Dict[str, List[float]] = {fam: [] for fam in families}
    for row in rollups_by_template:
        attempts = _to_int(row.get("attempts_total"))
        candidates = _to_int(row.get("candidates_total"))
        n_nodes = _to_int(row.get("N"))
        template_name = str(row.get("template_name") or "unknown")
        density = density_by_template.get(template_name)
        if attempts is None or candidates is None or n_nodes is None or density is None:
            continue
        p_hat = (candidates + 0.5) / (attempts + 1.0)
        y = math.log(p_hat)
        family = _template_family(template_name)
        pred = (
            coeff["intercept"]
            + coeff["N"] * n_nodes
            + coeff["density"] * density
            + coeff["family_ring"] * (1.0 if family == "ring" else 0.0)
            + coeff["family_ladder"] * (1.0 if family == "ladder" else 0.0)
            + coeff["family_bipartite"] * (1.0 if family == "bipartite" else 0.0)
            + coeff["family_complete"] * (1.0 if family == "complete" else 0.0)
        )
        points[family].append(y - pred)
    if not any(points.values()):
        return
    plt.figure(figsize=(7, 4))
    data = [points[fam] for fam in families]
    plt.boxplot(data, labels=families, showfliers=False)
    plt.axhline(0.0, color="black", linewidth=1.0)
    plt.ylabel("Residual (log candidate_rate)")
    plt.title("Residuals by template family (N + density controlled)")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_r_threshold(
    rows: List[Dict[str, Any]], output_path: Path, threshold: float
) -> None:
    plt = _ensure_matplotlib()
    xs = []
    ys = []
    for row in rows:
        n = _to_int(row.get("node_count"))
        r = _to_float(row.get("R_mean_lastW_mean"))
        if n is None or r is None:
            continue
        xs.append(n)
        ys.append(r)
    if not xs:
        return
    plt.figure(figsize=(6.5, 4.2))
    plt.scatter(xs, ys, alpha=0.7)
    plt.axhline(threshold, color="red", linestyle="--", linewidth=1.2)
    plt.xlabel("N (node_count)")
    plt.ylabel("R_mean_lastW_mean")
    plt.title("R_mean_lastW_mean vs N (Explorer threshold)")
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


def _fit_power_law(xs: List[float], ys: List[float]) -> Optional[Tuple[float, float, float]]:
    if not xs or not ys or len(xs) != len(ys):
        return None
    log_xs = []
    log_ys = []
    for x, y in zip(xs, ys):
        if x <= 0 or y <= 0:
            continue
        log_xs.append(math.log(x))
        log_ys.append(math.log(y))
    if len(log_xs) < 2:
        return None
    slope, intercept, r2, _slope_se, _slope_ci = _linear_fit(log_xs, log_ys)
    a = math.exp(intercept)
    b = slope
    return a, b, r2


def _plot_coherence_decay(rows: List[Dict[str, Any]], output_path: Path) -> None:
    plt = _ensure_matplotlib()
    groups = {
        "Wave 2 (Simple)": {"xs": [], "ys": [], "color": "tab:blue"},
        "Wave 3 (Complex)": {"xs": [], "ys": [], "color": "tab:orange"},
        "Other": {"xs": [], "ys": [], "color": "tab:gray"},
    }
    means_by_n: Dict[int, List[float]] = {}
    for row in rows:
        n = _to_int(row.get("node_count"))
        r = _to_float(row.get("R_network_S1_mean"))
        if n is None or r is None:
            continue
        ola = str(row.get("ola") or "")
        if "ola2" in ola:
            group_key = "Wave 2 (Simple)"
        elif "ola3" in ola:
            group_key = "Wave 3 (Complex)"
        else:
            group_key = "Other"
        groups[group_key]["xs"].append(n)
        groups[group_key]["ys"].append(r)
        means_by_n.setdefault(n, []).append(r)
    if not any(group["xs"] for group in groups.values()):
        return
    plt.figure(figsize=(7.5, 4.6))
    for label, group in groups.items():
        if not group["xs"]:
            continue
        plt.scatter(group["xs"], group["ys"], alpha=0.6, label=label, color=group["color"])
    mean_xs = sorted(means_by_n.keys())
    mean_ys = [sum(vals) / len(vals) for n in mean_xs for vals in [means_by_n[n]]]
    plt.scatter(mean_xs, mean_ys, color="black", marker="X", s=70, label="Mean per N")
    fit = _fit_power_law(mean_xs, mean_ys)
    if fit:
        a, b, _r2 = fit
        x_min = min(mean_xs)
        x_max = max(mean_xs)
        x_line = [x_min, x_max]
        y_line = [a * (x_min ** b), a * (x_max ** b)]
        plt.plot(x_line, y_line, color="red", linestyle="--", linewidth=1.5,
                 label=f"Power-law fit: R ≈ {a:.2f} · N^{b:.2f}")
    plt.xlabel("Number of Nodes (N)")
    plt.ylabel("Global Coherence (R)")
    plt.title("Coherence Decay (Lock Strength) vs Size (N)")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="upper right")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _plot_memory_s2(rows: List[Dict[str, Any]], output_path: Path) -> None:
    plt = _ensure_matplotlib()
    xs = []
    ys = []
    for row in rows:
        n = _to_int(row.get("node_count"))
        s2 = _to_float(row.get("H_part_norm_mean"))
        if n is None or s2 is None:
            continue
        xs.append(n)
        ys.append(s2)
    if not xs:
        return
    means_by_n: Dict[int, List[float]] = {}
    for n, s2 in zip(xs, ys):
        means_by_n.setdefault(n, []).append(s2)
    mean_xs = sorted(means_by_n.keys())
    mean_ys = [sum(vals) / len(vals) for n in mean_xs for vals in [means_by_n[n]]]
    plt.figure(figsize=(7.5, 4.6))
    sc = plt.scatter(xs, ys, c=ys, cmap="viridis", alpha=0.7)
    plt.plot(mean_xs, mean_ys, color="black", marker="o", linewidth=1.5, label="Mean S2 share")
    plt.colorbar(sc, label="S2 intensity")
    plt.xlabel("Number of Nodes (N)")
    plt.ylabel("S2 Participation (0.0–1.0)")
    plt.title("Memory (S2 layer) vs Complexity")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="lower left")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def _paper_rows(rows: List[Dict[str, Any]], ola_label: Optional[str] = None) -> List[Dict[str, Any]]:
    out = []
    for row in rows:
        ola_val = row.get("ola") or ola_label
        r_mean = _to_float(row.get("R_network_S1_mean"))
        h_part = _to_float(row.get("H_part_norm_mean"))
        e_disorder = None
        s_topo = None
        if r_mean is not None and h_part is not None:
            e_disorder = (1.0 - r_mean) * h_part
            if e_disorder > 0:
                s_topo = 1.0 / e_disorder
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
                "E_disorder": e_disorder,
                "S_topo": s_topo,
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


def _paper_summary_from_paper_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
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
    parser.add_argument("--out-root", default="paper/data")
    parser.add_argument("--skip-plots", action="store_true", help="Skip plot generation (data-only).")
    parser.add_argument("--all", action="store_true", help="Generate consolidated output in /all.")
    parser.add_argument(
        "--all-only",
        action="store_true",
        help="Generate only consolidated output in /all (skip per-ola outputs).",
    )
    args = parser.parse_args()

    all_rows: List[Dict[str, Any]] = []
    all_paper_rows: List[Dict[str, Any]] = []
    all_rollups_by_template: List[Dict[str, Any]] = []
    all_taxonomy_by_template: List[Dict[str, Any]] = []
    for ola_dir in _resolve_ola_dirs(args):
        ola_name = ola_dir.name
        catalog_dir = ola_dir / "catalog"
        taxonomy_csv = catalog_dir / f"genome_layers_{ola_name}_taxonomy.csv"
        if not taxonomy_csv.exists():
            print(f"[paper_pack] WARNING - STOPPED: missing {taxonomy_csv}")
            continue
        rollups_path = catalog_dir / "rollups.json"
        rollups: Dict[str, Any] = {}
        if rollups_path.exists():
            rollups = _load_json(rollups_path)
        rollups_by_template = rollups.get("by_template", []) if isinstance(rollups, dict) else []
        taxonomy_rollups_path = catalog_dir / "taxonomy_rollups.json"
        taxonomy_rollups: Dict[str, Any] = {}
        if taxonomy_rollups_path.exists():
            taxonomy_rollups = _load_json(taxonomy_rollups_path)
        taxonomy_by_template = (
            taxonomy_rollups.get("by_template", []) if isinstance(taxonomy_rollups, dict) else []
        )
        rows = _prepare_rows(_load_csv(taxonomy_csv))
        density_by_template: Dict[str, float] = {}
        density_counts: Dict[str, int] = {}
        for row in rows:
            template_name = str(row.get("template_name") or "unknown")
            density = _to_float(row.get("density"))
            if density is None:
                continue
            density_by_template[template_name] = density_by_template.get(template_name, 0.0) + density
            density_counts[template_name] = density_counts.get(template_name, 0) + 1
        for key, total in list(density_by_template.items()):
            count = density_counts.get(key, 0)
            density_by_template[key] = total / count if count else total
        paper_rows = _paper_rows(rows, ola_label=ola_name)
        fieldnames = list(paper_rows[0].keys()) if paper_rows else []
        if not args.all_only:
            out_dir = Path(args.out_root) / ola_name
            out_dir.mkdir(parents=True, exist_ok=True)
            _write_csv(out_dir / f"paper_metrics_{ola_name}.csv", fieldnames, paper_rows)

        plots: List[str] = []
        if not args.skip_plots and not args.all_only:
            agg_rows = _aggregate_rates_by_node_count(rollups_by_template, taxonomy_by_template)
            _plot_rates_vs_n(agg_rows, out_dir / "rates_vs_n.png")
            _plot_candidate_rate_regression(rollups_by_template, out_dir / "candidate_rate_regression.png")
            _plot_candidate_rate_heatmap(rollups_by_template, out_dir / "candidate_rate_heatmap.png")
            _plot_heatmap(rows, out_dir / "heatmap_template_vs_n.png")
            _plot_scatter(rows, out_dir / "scatter_R_vs_PE.png")
            _plot_robustness(rows, out_dir / "robustness_vs_n.png")
            _plot_h_part(rows, out_dir / "h_part_vs_n.png")
            _plot_coherence_decay(rows, out_dir / "coherence_decay_vs_n.png")
            _plot_memory_s2(rows, out_dir / "memory_s2_vs_n.png")
            _plot_r_threshold(rows, out_dir / "r_mean_lastw_vs_n.png", 0.75)
            model = _fit_candidate_rate_model(rollups_by_template, density_by_template)
            if model:
                (out_dir / "candidate_rate_model.json").write_text(json.dumps(model, indent=2))
                _plot_candidate_rate_residuals(
                    rollups_by_template,
                    density_by_template,
                    model,
                    out_dir / "candidate_rate_residuals.png",
                )
            attempts_path = ola_dir / "raw" / "attempts.jsonl"
            if attempts_path.exists():
                attempts_rows = _load_jsonl(attempts_path)
                _plot_explorer_fail_boxplots(attempts_rows, out_dir / "explorer_fail_boxplots.png")
                particle_lib = _resolve_particle_library(Path("."))
                if particle_lib is not None:
                    enrichment_rows = _build_particle_enrichment(attempts_rows, particle_lib)
                    if enrichment_rows:
                        _write_csv(out_dir / "particle_enrichment_by_template.csv", list(enrichment_rows[0].keys()), enrichment_rows)
                        _plot_particle_enrichment_heatmap(
                            enrichment_rows, out_dir / "particle_enrichment_heatmap.png"
                        )
                    lineage_data = _build_lineage_links(
                        attempts_rows, particle_lib, _taxonomy_lookup(catalog_dir)
                    )
                    if lineage_data:
                        stages, link_counts = lineage_data
                        edges = [
                            {"stage_index": idx, "source": src, "target": dst, "count": count}
                            for (idx, src, dst), count in link_counts.items()
                        ]
                        _write_csv(
                            out_dir / "lineage_sankey_edges.csv",
                            ["stage_index", "source", "target", "count"],
                            edges,
                        )
                        _plot_lineage_sankey(
                            stages, link_counts, out_dir / "lineage_sankey.png"
                        )
            _plot_candidate_rate_vs_density(
                rollups_by_template, density_by_template, out_dir / "candidate_rate_vs_density.png"
            )
            _plot_robustness_vs_density(rows, out_dir / "robustness_vs_density.png")

            plots = [
                "rates_vs_n.png",
                "candidate_rate_regression.png",
                "candidate_rate_heatmap.png",
                "heatmap_template_vs_n.png",
                "scatter_R_vs_PE.png",
                "robustness_vs_n.png",
                "h_part_vs_n.png",
                "coherence_decay_vs_n.png",
                "memory_s2_vs_n.png",
                "r_mean_lastw_vs_n.png",
            ]
            if (out_dir / "candidate_rate_residuals.png").exists():
                plots.append("candidate_rate_residuals.png")
            if (out_dir / "explorer_fail_boxplots.png").exists():
                plots.append("explorer_fail_boxplots.png")
            if (out_dir / "particle_enrichment_heatmap.png").exists():
                plots.append("particle_enrichment_heatmap.png")
            if (out_dir / "particle_enrichment_by_template.csv").exists():
                plots.append("particle_enrichment_by_template.csv")
            if (out_dir / "lineage_sankey.png").exists():
                plots.append("lineage_sankey.png")
            if (out_dir / "lineage_sankey_edges.csv").exists():
                plots.append("lineage_sankey_edges.csv")
            if (out_dir / "candidate_rate_vs_density.png").exists():
                plots.append("candidate_rate_vs_density.png")
            if (out_dir / "robustness_vs_density.png").exists():
                plots.append("robustness_vs_density.png")
        if not args.all_only:
            summary = {
                "ola_dir": str(ola_dir),
                "taxonomy_csv": str(taxonomy_csv),
                "paper_csv": str(out_dir / f"paper_metrics_{ola_name}.csv"),
                "plots": plots,
                "rows": len(rows),
            }
            (out_dir / "paper_metrics_manifest.json").write_text(json.dumps(summary, indent=2))
            summary_from_rows = _paper_summary(rows)
            summary_from_paper = _paper_summary_from_paper_rows(paper_rows)
            if summary_from_rows != summary_from_paper:
                raise RuntimeError(
                    "paper_metrics_summary mismatch: summary derived from taxonomy rows does not match paper CSV rows"
                )
            (out_dir / "paper_metrics_summary.json").write_text(json.dumps(summary_from_paper, indent=2))
            print(f"[paper_pack] wrote {out_dir}")

        all_rows.extend(rows)
        all_paper_rows.extend(paper_rows)
        if isinstance(rollups_by_template, list):
            all_rollups_by_template.extend(rollups_by_template)
        if isinstance(taxonomy_by_template, list):
            all_taxonomy_by_template.extend(taxonomy_by_template)

    if args.all and all_rows:
        out_dir = Path(args.out_root)
        out_dir.mkdir(parents=True, exist_ok=True)
        fieldnames = list(all_paper_rows[0].keys()) if all_paper_rows else []
        _write_csv(out_dir / "paper_metrics_all.csv", fieldnames, all_paper_rows)
        density_by_template: Dict[str, float] = {}
        density_counts: Dict[str, int] = {}
        for row in all_rows:
            template_name = str(row.get("template_name") or "unknown")
            density = _to_float(row.get("density"))
            if density is None:
                continue
            density_by_template[template_name] = density_by_template.get(template_name, 0.0) + density
            density_counts[template_name] = density_counts.get(template_name, 0) + 1
        for key, total in list(density_by_template.items()):
            count = density_counts.get(key, 0)
            density_by_template[key] = total / count if count else total
        plots = []
        if not args.skip_plots:
            agg_rows = _aggregate_rates_by_node_count(all_rollups_by_template, all_taxonomy_by_template)
            _plot_rates_vs_n(agg_rows, out_dir / "rates_vs_n.png")
            _plot_candidate_rate_regression(all_rollups_by_template, out_dir / "candidate_rate_regression.png")
            _plot_candidate_rate_heatmap(all_rollups_by_template, out_dir / "candidate_rate_heatmap.png")
            _plot_heatmap(all_rows, out_dir / "heatmap_template_vs_n.png")
            _plot_scatter(all_rows, out_dir / "scatter_R_vs_PE.png")
            _plot_robustness(all_rows, out_dir / "robustness_vs_n.png")
            _plot_h_part(all_rows, out_dir / "h_part_vs_n.png")
            _plot_coherence_decay(all_rows, out_dir / "coherence_decay_vs_n.png")
            _plot_memory_s2(all_rows, out_dir / "memory_s2_vs_n.png")
            _plot_r_threshold(all_rows, out_dir / "r_mean_lastw_vs_n.png", 0.75)
            model = _fit_candidate_rate_model(all_rollups_by_template, density_by_template)
            if model:
                (out_dir / "candidate_rate_model.json").write_text(json.dumps(model, indent=2))
                _plot_candidate_rate_residuals(
                    all_rollups_by_template,
                    density_by_template,
                    model,
                    out_dir / "candidate_rate_residuals.png",
                )
            _plot_candidate_rate_vs_density(
                all_rollups_by_template, density_by_template, out_dir / "candidate_rate_vs_density.png"
            )
            _plot_robustness_vs_density(all_rows, out_dir / "robustness_vs_density.png")
            plots = [
                "rates_vs_n.png",
                "heatmap_template_vs_n.png",
                "scatter_R_vs_PE.png",
                "robustness_vs_n.png",
                "h_part_vs_n.png",
                "coherence_decay_vs_n.png",
                "memory_s2_vs_n.png",
            ]
            if (out_dir / "candidate_rate_residuals.png").exists():
                plots.append("candidate_rate_residuals.png")
            if (out_dir / "candidate_rate_vs_density.png").exists():
                plots.append("candidate_rate_vs_density.png")
            if (out_dir / "robustness_vs_density.png").exists():
                plots.append("robustness_vs_density.png")
        summary = {
            "olas": sorted({row.get("ola") for row in all_paper_rows}),
            "paper_csv": str(out_dir / "paper_metrics_all.csv"),
            "plots": plots,
            "rows": len(all_rows),
        }
        (out_dir / "paper_metrics_manifest.json").write_text(json.dumps(summary, indent=2))
        summary_from_rows = _paper_summary(all_rows)
        summary_from_paper = _paper_summary_from_paper_rows(all_paper_rows)
        if summary_from_rows != summary_from_paper:
            raise RuntimeError(
                "paper_metrics_summary mismatch (all): summary derived from taxonomy rows does not match paper CSV rows"
            )
        (out_dir / "paper_metrics_summary.json").write_text(json.dumps(summary_from_paper, indent=2))
        print(f"[paper_pack] wrote {out_dir}")


if __name__ == "__main__":
    main()
