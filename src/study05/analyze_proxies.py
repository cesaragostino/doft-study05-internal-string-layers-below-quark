"""Offline analysis of proxies and family distances for Study05."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List

import numpy as np

from study05.families import FamilySpec, build_fingerprint, compute_family_distance


def _resolve_output_dir(output: Path, case: str) -> Path:
    """Place outputs under data/processed/<case>/combined by default."""
    if output in (Path("reports"), Path("data/processed")):
        return Path("data/processed") / case / "combined"
    if str(output).endswith("/ola1"):
        return output
    return output


def _load_runs_from_path(path: Path) -> List[Dict]:
    """Load runs from a JSON or JSONL file."""
    if not path.exists():
        return []
    try:
        # Try JSON first
        data = json.loads(path.read_text())
        if isinstance(data, dict) and "runs" in data:
            return data.get("runs", [])
        if isinstance(data, list):
            return data
    except Exception:
        pass
    # Fallback to JSONL (one run per line)
    runs: List[Dict] = []
    try:
        with path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    runs.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []
    return runs


def load_runs(case: str, results_path: Path | None = None) -> List[Dict]:
    candidates = []
    if results_path:
        candidates.append(Path(results_path))
    candidates.append(Path("data/processed") / case / "global" / "study05_sweep_results.json")
    candidates.append(Path("data/processed/ola1") / f"{case}_study05_sweep_results.json")
    candidates.append(Path("data/processed/ola1") / case / "global" / "study05_sweep_results.json")
    candidates.append(Path("data/processed/ola1") / "raw" / f"{case}_study05_sweep_params.json")
    candidates.append(Path("data/raw") / "study05_sweep_results.json")
    for path in candidates:
        if path.exists():
            runs = _load_runs_from_path(path)
            if runs:
                return runs
    raise FileNotFoundError(f"No sweep results found. Checked: {', '.join(str(c) for c in candidates)}")


def compute_basic_proxies(run: Dict) -> Dict:
    spacings = np.array(run.get("band_spacing_gev", []))
    energies = run.get("band_energies_gev", [])
    proxies = {
        "run_id": run.get("run_id"),
        "run_session_id": run.get("run_session_id"),
        "session_tag": run.get("session_tag"),
        "engine_config_path": run.get("engine_config_path"),
        "engine_config_hash": run.get("engine_config_hash"),
        "band_count": run.get("band_count", 0),
        "band_count_structural": run.get("band_count_structural"),
        "band_structural_cap_hit": run.get("band_structural_cap_hit"),
        "peak_cap": run.get("peak_cap"),
        "peak_cap_hit": run.get("peak_cap_hit"),
        "peaks_raw_count": run.get("peaks_raw_count"),
        "peaks_kept_count": run.get("peaks_kept_count"),
        "band_dom_counts_total": json.dumps(run.get("band_dom_counts_total", {})),
        "band_dom_counts_structural": json.dumps(run.get("band_dom_counts_structural", {})),
        "spacing_mean": float(np.mean(spacings)) if spacings.size else float("nan"),
        "spacing_std": float(np.std(spacings)) if spacings.size else float("nan"),
        "first_energy": energies[0] if len(energies) > 0 else float("nan"),
        "second_energy": energies[1] if len(energies) > 1 else float("nan"),
        "third_energy": energies[2] if len(energies) > 2 else float("nan"),
        "band_energies_gev": json.dumps(energies),
        "has_s2_dominant": 1 if run.get("has_s2_dominant") else 0,
        "has_s3_dominant": 1 if run.get("has_s3_dominant") else 0,
        "s2_band_fraction": run.get("s2_band_fraction", 0.0),
        "s2_band_fraction_total": run.get("s2_band_fraction_total", 0.0),
        "s2_state_lock": run.get("s2_state_lock"),
        "s2_state_bands": run.get("s2_state_bands"),
        "s3_band_fraction": run.get("s3_band_fraction", 0.0),
        "s2_total_fraction": run.get("s2_total_fraction", 0.0),
        "s3_total_fraction": run.get("s3_total_fraction", 0.0),
        "s2_state": run.get("s2_state"),
        "s3_state": run.get("s3_state"),
        "lock_quality_Q": run.get("lock_quality_Q"),
        "lock_quality_S1": run.get("lock_quality_S1"),
        "lock_quality_S2": run.get("lock_quality_S2"),
        "participation_entropy": run.get("participation_entropy"),
        "min_layer_fraction": run.get("min_layer_fraction"),
        "layer_energy_fraction": json.dumps(run.get("layer_energy_fraction", {})),
        "structure_tier": run.get("structure_tier"),
        "R_S1_Q": run.get("R_S1_Q"),
        "R_S2_S1": run.get("R_S2_S1"),
        "R_S3_S2": run.get("R_S3_S2"),
        "band_structural_energies_gev": json.dumps(run.get("band_structural_energies_gev", [])),
        "band_count_structural": run.get("band_count_structural"),
        "bands_all_json": run.get("bands_all_json"),
        "bands_structural_json": run.get("bands_structural_json"),
        "band_power_capture": run.get("band_power_capture"),
        "band_flags": ";".join(run.get("band_flags", [])) if run.get("band_flags") else "",
    }
    adapt = run.get("adaptive_lock") or {}
    for pair in adapt.get("pairs", []):
        name = pair.get("name", "pair")
        prefix = f"lock_{name}"
        proxies[f"{prefix}_L"] = pair.get("L_mean")
        proxies[f"{prefix}_ratio"] = pair.get("ratio_eff")
        proxies[f"{prefix}_locked"] = int(pair.get("locked", False))
    return proxies


def load_families_from_universe(path: Path) -> Dict[str, FamilySpec]:
    uni = json.loads(path.read_text())
    fams: Dict[str, FamilySpec] = {}
    for f in uni.get("families", []):
        proto = f.get("prototype", {})
        masses = proto.get("masses_gev", [])
        widths = proto.get("widths_gev")
        energy_window = f.get("energy_window", [0.1, 3.0])
        fams[f["name"]] = FamilySpec(
            name=f["name"],
            hadron_type=f.get("type", "meson"),
            masses_gev=masses,
            widths_gev=widths,
            jpc=None,
            energy_window=tuple(energy_window),
        )
    return fams


def analyze(case: str, sm_universe: Path, output: Path, results_path: Path | None = None):
    runs = load_runs(case, results_path)
    if not runs:
        print("No runs found.")
        return
    output_dir = _resolve_output_dir(output, case)

    specs = load_families_from_universe(sm_universe)
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
    parser.add_argument("--case", required=True, help="Case name (e.g., Core3L_Hadron).")
    parser.add_argument("--sm-universe", type=Path, default=Path("data/raw/sm_universe.json"), help="SM universe JSON.")
    parser.add_argument("--output", type=Path, default=Path("data/processed"), help="Output directory root.")
    parser.add_argument("--results-json", type=Path, default=None, help="Optional explicit path to sweep results JSON.")
    args = parser.parse_args()
    analyze(args.case, args.sm_universe, args.output, results_path=args.results_json)


if __name__ == "__main__":
    main()
