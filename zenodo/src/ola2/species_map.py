"""Species map views for Ola2 attempts (post-run)."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _load_attempts(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _is_finite(val: Any) -> bool:
    try:
        return math.isfinite(float(val))
    except Exception:
        return False


def _rationalize_ratio(ratio: float, max_den: int, epsilon_rel: float) -> Tuple[Optional[str], float]:
    if not _is_finite(ratio) or ratio == 0:
        return None, float("inf")
    frac = Fraction(ratio).limit_denominator(max_den)
    approx = frac.numerator / frac.denominator
    residual_rel = abs(ratio - approx) / abs(ratio)
    if residual_rel <= epsilon_rel:
        return f"{frac.numerator}/{frac.denominator}", residual_rel
    return None, residual_rel


def _prime_factors(n: int) -> List[int]:
    out: List[int] = []
    n = abs(int(n))
    if n <= 1:
        return out
    d = 2
    while d * d <= n:
        while n % d == 0:
            out.append(d)
            n //= d
        d += 1
    if n > 1:
        out.append(n)
    return out


def _lock_signature(
    node_omega_mean: List[float],
    edges: List[List[int]],
    max_den: int,
    epsilon_rel: float,
) -> Tuple[List[Dict[str, Any]], str]:
    entries: List[Dict[str, Any]] = []
    for e in edges:
        if len(e) < 2:
            continue
        i, j = int(e[0]), int(e[1])
        if i < 0 or j < 0 or i >= len(node_omega_mean) or j >= len(node_omega_mean):
            continue
        denom = node_omega_mean[j]
        ratio = node_omega_mean[i] / denom if denom != 0 else float("inf")
        ratio_pq, residual_rel = _rationalize_ratio(ratio, max_den, epsilon_rel)
        p_factors: List[int] = []
        q_factors: List[int] = []
        if ratio_pq:
            p_str, q_str = ratio_pq.split("/")
            p_factors = _prime_factors(int(p_str))
            q_factors = _prime_factors(int(q_str))
        entries.append(
            {
                "edge": [i, j],
                "ratio_raw": ratio,
                "ratio_pq": ratio_pq,
                "residual_rel": residual_rel,
                "p_factors": p_factors,
                "q_factors": q_factors,
            }
        )
    entries_sorted = sorted(entries, key=lambda x: (min(x["edge"]), max(x["edge"])))
    sig_payload = json.dumps(
        [{"edge": e["edge"], "ratio_pq": e["ratio_pq"], "residual_rel": e["residual_rel"]} for e in entries_sorted],
        sort_keys=True,
    )
    ls_hash = hashlib.sha256(sig_payload.encode("utf-8")).hexdigest()
    return entries_sorted, ls_hash


def _write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ola2 Species Map (post-run views)")
    parser.add_argument("--attempts", required=True, help="attempts.jsonl path")
    parser.add_argument("--output-dir", required=True, help="output directory for views")
    parser.add_argument("--max-den", type=int, default=31)
    parser.add_argument("--epsilon-rel", type=float, default=1e-3)
    args = parser.parse_args()

    attempts_path = Path(args.attempts)
    output_dir = Path(args.output_dir)
    views_dir = output_dir / "views"
    species_catalog_path = output_dir / "species_catalog.jsonl"
    species_map_path = views_dir / "species_map.jsonl"
    viable_path = views_dir / "viable.jsonl"
    nonviable_path = views_dir / "nonviable.jsonl"

    species_stats: Dict[str, Dict[str, Any]] = {}
    best_attempt_by_species: Dict[str, Dict[str, Any]] = {}
    viable_rows: List[Dict[str, Any]] = []
    nonviable_rows: List[Dict[str, Any]] = []

    for attempt in _load_attempts(attempts_path):
        tags = attempt.get("tags") or {}
        if tags.get("viable"):
            viable_rows.append(attempt)
        else:
            nonviable_rows.append(attempt)

        structure = attempt.get("structure") or {}
        species_id = structure.get("structure_id")
        if not species_id:
            continue
        metrics = attempt.get("metrics") or {}
        stats = species_stats.get(
            species_id,
            {
                "species_id": species_id,
                "structure_id": species_id,
                "template_name": structure.get("template_name"),
                "assignment": structure.get("assignment", {}).get("block_keys"),
                "edge_weights": structure.get("edge_weight_pattern"),
                "n_trials": 0,
                "n_viable": 0,
                "best_metrics": None,
            },
        )
        stats["n_trials"] += 1
        if tags.get("viable"):
            stats["n_viable"] += 1
        if stats["best_metrics"] is None or (metrics.get("R_mean_lastW") or 0) > (stats["best_metrics"].get("R_mean_lastW") or 0):
            stats["best_metrics"] = metrics
        species_stats[species_id] = stats

        r_mean = metrics.get("R_mean_lastW")
        best = best_attempt_by_species.get(species_id)
        if best is None or (r_mean or 0) > (best.get("metrics", {}).get("R_mean_lastW") or 0):
            best_attempt_by_species[species_id] = attempt

    species_catalog = []
    for sid, stats in species_stats.items():
        trials = stats.get("n_trials", 0)
        n_viable = stats.get("n_viable", 0)
        seed_stability = n_viable / max(trials, 1)
        stats["seed_stability"] = seed_stability
        species_catalog.append(stats)
    species_catalog.sort(key=lambda r: (r.get("seed_stability", 0.0), r.get("n_viable", 0)), reverse=True)

    species_map_rows: List[Dict[str, Any]] = []
    for sid, attempt in best_attempt_by_species.items():
        metrics = attempt.get("metrics") or {}
        node_omega_mean = metrics.get("node_omega_mean_lastW")
        if not isinstance(node_omega_mean, list) or not node_omega_mean:
            continue
        structure = attempt.get("structure") or {}
        edges = structure.get("edges") or []
        entries, ls_hash = _lock_signature(node_omega_mean, edges, args.max_den, args.epsilon_rel)
        species_map_rows.append(
            {
                "species_id": sid,
                "attempt_id": attempt.get("attempt_id"),
                "lock_signature": entries,
                "LS_hash": ls_hash,
                "max_den": args.max_den,
                "epsilon_rel": args.epsilon_rel,
            }
        )

    _write_jsonl(species_catalog_path, species_catalog)
    _write_jsonl(species_map_path, species_map_rows)
    _write_jsonl(viable_path, viable_rows)
    _write_jsonl(nonviable_path, nonviable_rows)


if __name__ == "__main__":
    main()
