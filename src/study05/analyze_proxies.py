"""Offline analysis of proxies and family distances for Study05."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List

import numpy as np

from study05.families import FamilySpec, build_fingerprint, compute_family_distance, load_family_spec


def _resolve_output_dir(output: Path, case: str) -> Path:
    """Place outputs under data/processed/<case>/combined by default."""
    if output == Path("reports"):
        return Path("data/processed") / case / "combined"
    if output == Path("data/processed"):
        return output / case / "combined"
    return output


def load_runs(case: str, results_path: Path | None = None) -> List[Dict]:
    candidates = []
    if results_path:
        candidates.append(Path(results_path))
    candidates.append(Path("data/processed") / case / "global" / "study05_sweep_results.json")
    candidates.append(Path("data/ola1/processed") / case / "global" / "study05_sweep_results.json")
    candidates.append(Path("data/processed/ola1") / case / "global" / "study05_sweep_results.json")
    candidates.append(Path("data/processed/ola1/processed") / case / "global" / "study05_sweep_results.json")
    for path in candidates:
        if path.exists():
            data = json.loads(path.read_text())
            return data.get("runs", [])
    raise FileNotFoundError(f"No sweep results found. Checked: {', '.join(str(c) for c in candidates)}")


def compute_basic_proxies(run: Dict) -> Dict:
    spacings = np.array(run.get("band_spacing_gev", []))
    energies = run.get("band_energies_gev", [])
    proxies = {
        "run_id": run.get("run_id"),
        "band_count": run.get("band_count", 0),
        "spacing_mean": float(np.mean(spacings)) if spacings.size else float("nan"),
        "spacing_std": float(np.std(spacings)) if spacings.size else float("nan"),
        "first_energy": energies[0] if len(energies) > 0 else float("nan"),
        "second_energy": energies[1] if len(energies) > 1 else float("nan"),
        "third_energy": energies[2] if len(energies) > 2 else float("nan"),
        "band_energies_gev": json.dumps(energies),
        "has_s2_dominant": 1 if run.get("has_s2_dominant") else 0,
        "has_s3_dominant": 1 if run.get("has_s3_dominant") else 0,
        "s2_band_fraction": run.get("s2_band_fraction", 0.0),
        "s3_band_fraction": run.get("s3_band_fraction", 0.0),
        "s2_total_fraction": run.get("s2_total_fraction", 0.0),
        "s3_total_fraction": run.get("s3_total_fraction", 0.0),
        "s2_state": run.get("s2_state"),
        "s3_state": run.get("s3_state"),
        "lock_quality_Q": run.get("lock_quality_Q"),
        "lock_quality_S1": run.get("lock_quality_S1"),
        "lock_quality_S2": run.get("lock_quality_S2"),
        "structure_tier": run.get("structure_tier"),
        "R_S1_Q": run.get("R_S1_Q"),
        "R_S2_S1": run.get("R_S2_S1"),
        "R_S3_S2": run.get("R_S3_S2"),
    }
    return proxies


def load_family_specs(paths: List[Path]) -> Dict[str, FamilySpec]:
    specs = {}
    for p in paths:
        if not p.exists():
            # try lowercase filename
            alt = p.with_name(p.name.lower())
            if alt.exists():
                p = alt
        if p.exists():
            spec = load_family_spec(p)
            specs[spec.name] = spec
    return specs


def analyze(case: str, families: List[str], output: Path, results_path: Path | None = None):
    runs = load_runs(case, results_path)
    if not runs:
        print("No runs found.")
        return
    output_dir = _resolve_output_dir(output, case)

    family_paths = []
    for f in families:
        path = Path(f)
        if not path.suffix:
            path = Path(f"data/raw/config/{f}.json")
        family_paths.append(path)
    specs = load_family_specs(family_paths)
    fps = {name: build_fingerprint(spec) for name, spec in specs.items()}

    rows: List[Dict] = []
    for run in runs:
        base = compute_basic_proxies(run)
        band_energies = run.get("band_energies_gev", [])
        for name, spec in specs.items():
            fp = fps[name]
            levels = [e for e in band_energies if spec.energy_window[0] <= e <= spec.energy_window[1]]
            dist = compute_family_distance(levels, None, fp, use_widths=False) if len(levels) >= fp.n_levels_target else None
            base[f"{name}_has_enough_levels"] = len(levels) >= fp.n_levels_target
            if dist:
                base[f"{name}_d_total"] = dist.d_total
                base[f"{name}_d_spacing"] = dist.d_spacing
                base[f"{name}_is_match"] = dist.is_match
                base[f"{name}_n_levels_sim"] = dist.n_levels_sim
            else:
                base[f"{name}_d_total"] = float("nan")
                base[f"{name}_d_spacing"] = float("nan")
                base[f"{name}_is_match"] = False
                base[f"{name}_n_levels_sim"] = len(levels)
        rows.append(base)

    output_dir.mkdir(parents=True, exist_ok=True)
    # Save CSV using proper quoting to avoid column shifts
    keys = sorted({k for row in rows for k in row.keys()})
    csv_path = output_dir / f"{case}_all_runs_proxies.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in keys})

    # Correlation with S2 dominance (Pearson)
    s2 = np.array([r.get("has_s2_dominant", 0) for r in rows], dtype=float)
    corr_rows = []
    for key in keys:
        if key == "has_s2_dominant":
            continue
        vals_raw = [r.get(key, np.nan) for r in rows]
        # skip non-numeric columns (e.g., JSON strings)
        try:
            vals = np.array(vals_raw, dtype=float)
        except Exception:
            continue
        mask = np.isfinite(vals)
        if mask.sum() < 3:
            continue
        v = vals[mask]
        s = s2[mask]
        denom = np.std(v) * np.std(s)
        corr = float(np.corrcoef(v, s)[0, 1]) if denom > 0 else float("nan")
        corr_rows.append({"proxy": key, "corr_with_s2": corr})
    corr_lines = ["proxy,corr_with_s2"]
    corr_lines += [f"{r['proxy']},{r['corr_with_s2']}" for r in corr_rows]
    (output_dir / f"{case}_s2_correlations.csv").write_text("\n".join(corr_lines))


def main():
    parser = argparse.ArgumentParser(description="Analyze proxies and family distances.")
    parser.add_argument("--case", required=True, help="Case name (e.g., CaseB_debug).")
    parser.add_argument("--families", nargs="+", default=[], help="Family names or paths to JSON configs.")
    parser.add_argument("--output", type=Path, default=Path("data/processed"), help="Output directory root.")
    parser.add_argument("--results-json", type=Path, default=None, help="Optional explicit path to sweep results JSON.")
    args = parser.parse_args()
    analyze(args.case, args.families, args.output, results_path=args.results_json)


if __name__ == "__main__":
    main()
