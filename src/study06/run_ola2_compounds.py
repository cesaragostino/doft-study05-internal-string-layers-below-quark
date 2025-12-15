"""Wave 2 (Ola2) runner using the reloaded phase/memory model.

This replaces the old physical DOFT integration. It stitches Ola1 blocks into
templates, rehydrates them as oscillators (mass/frequency from Ola1 bands),
runs the light Ola2 engine (scripts/ola2_reloaded_sim.py) and writes a CSV
with the Ola2 metrics.

Spec reference: docs/STUDY05_ola2_reloaded_global_memory.md
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import math
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence

import numpy as np

# Import simulator from scripts/ (repo root)
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

try:
    from scripts.ola2_reloaded_sim import simulate_ola2  # type: ignore
except Exception as exc:  # pragma: no cover - defensive load
    raise ImportError("No se pudo importar scripts.ola2_reloaded_sim") from exc


def _load_json(path: Path):
    return json.loads(path.read_text())


def _load_blocks(path: Path) -> List[Dict[str, Any]]:
    return json.loads(path.read_text()) if path.exists() else []


def _parse_band_energies(raw: Any) -> List[float]:
    if raw is None or (isinstance(raw, float) and math.isnan(raw)):
        return []
    if isinstance(raw, (list, tuple)):
        return [float(x) for x in raw if _is_finite(x)]
    if isinstance(raw, str):
        try:
            val = json.loads(raw)
        except Exception:
            try:
                val = ast.literal_eval(raw)
            except Exception:
                return []
        return _parse_band_energies(val)
    return []


def _load_proxies(proxies_csv: Path) -> Dict[int, Dict[str, Any]]:
    """Map run_id -> proxy info (band_energies_gev, lock_quality, etc.)."""
    if not proxies_csv.exists():
        return {}
    out: Dict[int, Dict[str, Any]] = {}
    with proxies_csv.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rid = int(float(row.get("run_id", "nan")))
            except Exception:
                continue
            bands = _parse_band_energies(row.get("band_energies_gev"))
            out[rid] = {"band_energies_gev": bands}
    return out


def _is_finite(x: Any) -> bool:
    try:
        v = float(x)
    except Exception:
        return False
    return math.isfinite(v)


def _lock_entropy(lock_q: Dict[str, Any]) -> float:
    q = max(float(lock_q.get("Q", 0.0)), 0.0)
    s1 = max(float(lock_q.get("S1", 0.0)), 0.0)
    s2 = max(float(lock_q.get("S2", 0.0)), 0.0)
    s = q + s1 + s2
    if s <= 1e-12:
        return math.log(3) / math.log(3)
    p = [q / s, s1 / s, s2 / s]
    return float(-sum(pi * math.log(pi + 1e-12) for pi in p) / math.log(3))


def _sample_blocks(pool: List[Dict[str, Any]], families: Sequence[str], k: int, rng: random.Random) -> List[Dict[str, Any]]:
    fam_lower = {f.lower() for f in families} if families else set()
    if "match_any" in fam_lower:
        filtered = list(pool)
    else:
        filtered = [b for b in pool if (not fam_lower or str(b.get("family", "")).lower() in fam_lower)]
    if len(filtered) < k:
        return []
    weights = []
    for b in filtered:
        d = b.get("match_score", {}).get("d_total")
        try:
            d = float(d)
        except Exception:
            d = math.inf
        w = 1.0 / (1.0 + d) if math.isfinite(d) else 0.1
        weights.append(max(w, 1e-3))
    return rng.choices(filtered, weights=weights, k=k)


def _resolve_blocks_path(cfg_path: Path) -> Path:
    if cfg_path.exists():
        return cfg_path
    fallback = Path("data/processed/ola1-chaos/simple_blocks.json")
    return fallback if fallback.exists() else cfg_path


def _resolve_proxies_path(cfg: Dict[str, Any], override: Path | None) -> Path | None:
    if override:
        return override
    if "ola1_proxies_csv" in cfg:
        return Path(cfg["ola1_proxies_csv"])
    guess = Path("data/processed/ola1-chaos/Ola1_3-2-5_all_runs_proxies.csv")
    return guess if guess.exists() else None


def run_from_rules(
    rules_path: Path,
    blocks_override: Path | None = None,
    proxies_override: Path | None = None,
    output_root: Path | None = None,
    seed: int | None = None,
    runs_override: int | None = None,
    log_every: int = 0,
):
    rng = random.Random(seed)
    rules = _load_json(rules_path)
    blocks_path = _resolve_blocks_path(Path(blocks_override or rules.get("blocks_input", "data/processed/ola1-chaos/simple_blocks.json")))
    blocks = _load_blocks(blocks_path)
    if not blocks:
        print(json.dumps({"status": "skip", "reason": "no_blocks", "blocks_input": str(blocks_path)}))
        return

    proxies_path = _resolve_proxies_path(rules, proxies_override)
    proxies_map = _load_proxies(proxies_path) if proxies_path else {}

    templates_path = Path(rules.get("templates_json", "data/raw/compound_templates.json"))
    templates = {t["name"]: t for t in _load_json(templates_path)}
    for t in rules.get("templates_definitions", []):
        name = t.get("name")
        if name:
            templates[name] = t

    engine_cfg = rules.get("engine", {})
    dt = float(engine_cfg.get("dt", 1.0))
    T_ticks = int(engine_cfg.get("T_ticks", 120))
    sigma0 = float(engine_cfg.get("sigma0", 0.30))
    sigma_tc = float(engine_cfg.get("sigma_tc", 60.0))
    sigma_theta_init = float(engine_cfg.get("sigma_theta_init", 0.5))
    K_local = float(engine_cfg.get("K_local", 0.15))
    kappa_global = float(engine_cfg.get("kappa_global", 0.25))
    tau_field = float(engine_cfg.get("tau_field", 20.0))
    window_W = int(engine_cfg.get("window_W", 20))
    gamma = float(engine_cfg.get("gamma", 0.007))
    gamma_max = float(engine_cfg.get("gamma_max", 0.02))
    mass_min = float(engine_cfg.get("mass_min", 0.01))

    out_base = Path(output_root or rules.get("output_root", "data/processed/ola2"))
    out_base.mkdir(parents=True, exist_ok=True)

    targets_cfg = rules.get("targets", [])
    print(f"[ola2] targets a procesar: {len(targets_cfg)}")

    for tgt_cfg in targets_cfg:
        target_name = tgt_cfg.get("name") or tgt_cfg.get("particle_name") or "unknown"
        families = [f.lower() for f in tgt_cfg.get("allowed_block_families", [])]
        template_names = tgt_cfg.get("templates", [])
        runs_per_target = int(runs_override or tgt_cfg.get("runs_per_target", rules.get("runs_per_target", 100)))
        out_csv = out_base / f"ola2_{target_name}.csv"
        rows: List[Dict[str, Any]] = []

        for run_idx in range(runs_per_target):
            if log_every and (run_idx % log_every == 0):
                print(f"[ola2] {target_name}: run {run_idx+1}/{runs_per_target}")
            tmpl_name = rng.choice(template_names) if template_names else None
            tmpl = templates.get(tmpl_name) if tmpl_name else None
            if tmpl is None:
                rows.append({"run_id": run_idx, "status": "skip", "reason": "no_template"})
                continue
            nodes = int(tmpl.get("nodes", 0))
            picked = _sample_blocks(blocks, families, nodes, rng)
            if len(picked) != nodes:
                rows.append(
                    {
                        "run_id": run_idx,
                        "status": "skip",
                        "reason": "not_enough_blocks",
                        "template_name": tmpl_name,
                        "nodes_required": nodes,
                        "picked": len(picked),
                    }
                )
                continue

            fms: List[float] = []
            masses: List[float] = []
            omegas: List[float] = []
            lockq: List[Dict[str, float]] = []
            fm_missing = False
            for b in picked:
                rid = b.get("origin_run_id") or b.get("source_run")
                try:
                    rid_int = int(float(rid))
                except Exception:
                    rid_int = None
                bands = proxies_map.get(rid_int, {}).get("band_energies_gev", []) if rid_int is not None else []
                mass_field = b.get("mass")
                fm_candidate = b.get("F_m") or b.get("f_m")
                fm = None
                if bands:
                    fm = min(bands)
                elif fm_candidate is not None:
                    fm = fm_candidate
                elif mass_field is not None:
                    fm = mass_field
                else:
                    fm_missing = True
                    fm = 1.0
                fms.append(float(fm))
                mass_val = mass_field if mass_field is not None else fm
                masses.append(float(mass_val))
                omegas.append(float(fm))  # omega = F_m
                lq = b.get("lock_quality")
                if not lq and b.get("quality") is not None:
                    try:
                        qv = float(b.get("quality"))
                        lq = {"Q": qv, "S1": 0.0, "S2": 0.0}
                    except Exception:
                        lq = {}
                lockq.append(lq or {})

            sim_res = simulate_ola2(
                masses=np.array(masses, dtype=float),
                omegas=np.array(omegas, dtype=float),
                theta0=None,
                template=tmpl,
                lock_quality=lockq,
                dt=dt,
                T_ticks=T_ticks,
                sigma0=sigma0,
                sigma_tc=sigma_tc,
                sigma_theta_init=sigma_theta_init,
                K_local=K_local,
                kappa_global=kappa_global,
                tau_field=tau_field,
                window_W=window_W,
                gamma=gamma,
                gamma_max=gamma_max,
                mass_min=mass_min,
            )

            metrics = sim_res.get("metrics", {})
            mass_block = sim_res.get("mass", {})
            result_block = sim_res.get("result", {})
            topo_block = sim_res.get("topology", {})

            row = {
                "run_id": run_idx,
                "target": target_name,
                "template_name": tmpl_name,
                "status": "ok" if result_block.get("success") else "fail",
                "reason": result_block.get("reason"),
                "success": bool(result_block.get("success")),
                "R_final": metrics.get("R_final"),
                "R_mean_lastW": metrics.get("R_mean_lastW"),
                "phase_var_lastW": metrics.get("phase_var_lastW"),
                "PE_tick_norm": metrics.get("PE_tick_norm"),
                "memory_score_k10": metrics.get("memory_score_k10"),
                "QualityLock": metrics.get("QualityLock"),
                "entropy_quality": metrics.get("entropy_quality"),
                "sumM": mass_block.get("sumM"),
                "E_bind_mass": mass_block.get("E_bind_mass"),
                "mass_defect": mass_block.get("mass_defect"),
                "M_final": mass_block.get("M_final"),
                "nodes": topo_block.get("nodes"),
                "edges_count": topo_block.get("edges_count"),
                "degree_raw": topo_block.get("degree_raw"),
                "degree_normalized": topo_block.get("degree_normalized"),
                "effective_degree": topo_block.get("effective_degree"),
                "block_ids": json.dumps([b.get("block_id") for b in picked]),
                "block_particles": json.dumps([b.get("particle_name") or b.get("name") for b in picked]),
                "block_families": json.dumps([b.get("family") for b in picked]),
                "F_m_list": json.dumps(fms),
                "mass_list": json.dumps(masses),
                "fm_missing": fm_missing,
                "origin_run_ids": json.dumps([b.get("origin_run_id") or b.get("source_run") for b in picked]),
                "H_block_mean": float(np.mean([_lock_entropy(q) for q in lockq])) if lockq else None,
            }
            rows.append(row)

        if rows:
            fieldnames = sorted({k for r in rows for k in r.keys()})
            out_csv.parent.mkdir(parents=True, exist_ok=True)
            with out_csv.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print(f"[ola2] escrito {out_csv} ({len(rows)} rows)")


def main():
    parser = argparse.ArgumentParser(description="Run Ola2 reloaded (phase/memory) on simple blocks + templates.")
    parser.add_argument("--wave2-config", type=Path, default=Path("data/raw/wave2_compounds.json"), help="Archivo de reglas/targets.")
    parser.add_argument("--blocks-json", type=Path, default=None, help="Override de blocks Ola1 (simple_blocks.json).")
    parser.add_argument("--proxies-csv", type=Path, default=None, help="CSV con proxies Ola1 (band_energies_gev por run_id).")
    parser.add_argument("--output-root", type=Path, default=None, help="Carpeta base de salida.")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--runs-per-target", type=int, default=None, help="Override global de runs por target.")
    parser.add_argument("--log-every", type=int, default=0, help="Loguea progreso cada N runs (0 desactiva).")
    args = parser.parse_args()

    run_from_rules(
        args.wave2_config,
        blocks_override=args.blocks_json,
        proxies_override=args.proxies_csv,
        output_root=args.output_root,
        seed=args.seed,
        runs_override=args.runs_per_target,
        log_every=args.log_every,
    )


if __name__ == "__main__":
    main()
