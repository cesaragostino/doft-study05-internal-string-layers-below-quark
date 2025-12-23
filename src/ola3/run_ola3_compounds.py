"""Ola3 runner using the reloaded phase/memory model.

It stitches Ola3 blocks into templates, rehydrates them as oscillators
(mass/frequency from Ola3/Ola1 bands), runs the light Ola3 engine and
writes a CSV with the metrics.
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
import hashlib

try:
    from ola3.ola3_reloaded_sim import simulate_ola2
except Exception as exc:  # pragma: no cover - defensive load
    raise ImportError("No se pudo importar ola3.ola3_reloaded_sim") from exc


def _load_json(path: Path):
    return json.loads(path.read_text())


def _load_blocks(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    if path.suffix == ".jsonl":
        blocks: List[Dict[str, Any]] = []
        for line in path.read_text().splitlines():
            try:
                blocks.append(json.loads(line))
            except Exception:
                continue
        return blocks
    return json.loads(path.read_text())


def _load_hbar(path: Path | None) -> float | None:
    if not path or not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except Exception:
        return None
    for key in ("hbar_sim", "hbar_sim_live", "hbar"):
        val = data.get(key)
        try:
            if val is not None:
                return float(val)
        except Exception:
            continue
    return None


def _mass_from_block(raw: Dict[str, Any]) -> float | None:
    for key in ("mass_sim_gev", "mass_gev", "mass"):
        try:
            val = raw.get(key)
            if val is not None:
                return float(val)
        except Exception:
            continue
    return None


def _load_simple_blocks(path: Path | None) -> Dict[str, float]:
    if not path or not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {}
    out: Dict[str, float] = {}
    if not isinstance(data, list):
        return out
    for item in data:
        if not isinstance(item, dict):
            continue
        bid = item.get("block_id") or item.get("id")
        if not bid:
            continue
        mass = _mass_from_block(item)
        if mass is None:
            continue
        out[str(bid)] = mass
    return out


def _load_species_blocks(
    species_path: Path,
    hbar_sim: float | None,
    simple_blocks: Dict[str, float],
) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []
    for line in species_path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except Exception:
            continue
        if not isinstance(raw, dict):
            continue
        species_id = raw.get("species_id") or raw.get("id")
        best = raw.get("best_metrics") or {}
        omega_eff = best.get("omega_eff")
        try:
            omega_eff = float(omega_eff) if omega_eff is not None else None
        except Exception:
            omega_eff = None
        mass = (omega_eff * hbar_sim) if (omega_eff is not None and hbar_sim is not None) else None
        assignment = raw.get("assignment") or raw.get("node_assignment") or []
        if not isinstance(assignment, list):
            assignment = []
        sum_masses = sum(simple_blocks.get(str(bid), 0.0) for bid in assignment) if assignment else 0.0
        e_bind_mass = (sum_masses - mass) if (mass is not None and assignment) else None
        qlock = best.get("QualityLock")
        try:
            qlock_val = float(qlock) if qlock is not None else None
        except Exception:
            qlock_val = None
        blocks.append(
            {
                "id": species_id,
                "block_id": species_id,
                "name": species_id,
                "particle_name": raw.get("template_name") or species_id,
                "family": "species",
                "F_m": omega_eff,
                "f_m": omega_eff,
                "omega_eff": omega_eff,
                "mass": mass,
                "mass_units": "GeV",
                "quality": best.get("R_final"),
                "lock_quality": {"Q": qlock_val, "S1": 0.0, "S2": 0.0} if qlock_val is not None else {},
                "composition": assignment,
                "binding_energy": e_bind_mass,
            }
        )
    return blocks


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
    fallback = Path("data/processed/ola3/ola3_blocks.json")
    return fallback if fallback.exists() else cfg_path


def _resolve_proxies_path(cfg: Dict[str, Any], override: Path | None) -> Path | None:
    if override:
        return override
    if "ola1_proxies_csv" in cfg:
        return Path(cfg["ola1_proxies_csv"])
    guess = Path("data/processed/ola1/Ola1_3-2-5_all_runs_proxies.csv")
    return guess if guess.exists() else None


def run_from_rules(
    rules_path: Path,
    blocks_override: Path | None = None,
    proxies_override: Path | None = None,
    output_root: Path | None = None,
    seed: int | None = None,
    runs_override: int | None = None,
    log_every: int = 0,
    harvest_jsonl: Path | None = None,
    harvest_rej_jsonl: Path | None = None,
    species_catalog: Path | None = None,
    simple_blocks_path: Path | None = None,
    hbar_path: Path | None = None,
    memory_var_threshold: float | None = None,
):
    rng = random.Random(seed)
    rules = _load_json(rules_path)
    blocks: List[Dict[str, Any]] = []
    if species_catalog is not None:
        hbar_sim = _load_hbar(hbar_path)
        parent_masses = _load_simple_blocks(simple_blocks_path)
        blocks = _load_species_blocks(species_catalog, hbar_sim, parent_masses)
        blocks_path = species_catalog
    else:
        blocks_path = _resolve_blocks_path(Path(blocks_override or rules.get("blocks_input", "data/processed/ola3/ola3_blocks.json")))
        blocks = _load_blocks(blocks_path)
    if not blocks:
        print(json.dumps({"status": "skip", "reason": "no_blocks", "blocks_input": str(blocks_path)}))
        return

    proxies_path = _resolve_proxies_path(rules, proxies_override)
    proxies_map = _load_proxies(proxies_path) if proxies_path else {}

    templates_path = Path(rules.get("templates_json", "data/raw/wave3_templates.json"))
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
    if memory_var_threshold is None:
        memory_var_threshold = float(engine_cfg.get("memory_var_threshold", 1e-10))
    if memory_var_threshold is None or not math.isfinite(memory_var_threshold):
        memory_var_threshold = 1e-10

    out_base = Path(output_root or rules.get("output_root", "data/processed/ola3"))
    out_base.mkdir(parents=True, exist_ok=True)

    targets_cfg = rules.get("targets", [])
    print(f"[ola3] targets a procesar: {len(targets_cfg)}")
    config_hash = hashlib.sha256(rules_path.read_bytes()).hexdigest()[:16]

    for tgt_cfg in targets_cfg:
        target_name = tgt_cfg.get("name") or tgt_cfg.get("particle_name") or "unknown"
        families = [f.lower() for f in tgt_cfg.get("allowed_block_families", [])]
        allowed_particle_names = {n.lower() for n in tgt_cfg.get("allowed_particle_names", [])} if tgt_cfg.get("allowed_particle_names") else None
        template_names = tgt_cfg.get("templates", [])
        runs_per_target = int(runs_override or tgt_cfg.get("runs_per_target", rules.get("runs_per_target", 100)))
        out_csv = out_base / f"ola3_{target_name}.csv"
        rows: List[Dict[str, Any]] = []

        for run_idx in range(runs_per_target):
            if log_every and (run_idx % log_every == 0):
                print(f"[ola3] {target_name}: run {run_idx+1}/{runs_per_target}")
            tmpl_name = rng.choice(template_names) if template_names else None
            tmpl = templates.get(tmpl_name) if tmpl_name else None
            if tmpl is None:
                rows.append({"run_id": run_idx, "status": "skip", "reason": "no_template"})
                if harvest_rej_jsonl:
                    harvest_rej_jsonl.parent.mkdir(parents=True, exist_ok=True)
                    with harvest_rej_jsonl.open("a") as hf:
                        hf.write(
                            json.dumps(
                                {
                                    "compound_id": None,
                                    "run_id": run_idx,
                "wave": "ola3",
                                    "target_name": target_name,
                                    "particle_name": target_name or "unknown",
                                    "template_name": None,
                                    "seed": seed,
                                    "config_hash": config_hash,
                                    "status": "skip",
                                    "reason": "no_template",
                                }
                            )
                            + "\n"
                        )
                continue
            nodes = int(tmpl.get("nodes", 0))
            picked = _sample_blocks(blocks, families, nodes, rng)
            if allowed_particle_names:
                picked = [b for b in picked if str(b.get("particle_name") or b.get("name", "")).lower() in allowed_particle_names]
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
                if harvest_rej_jsonl:
                    harvest_rej_jsonl.parent.mkdir(parents=True, exist_ok=True)
                    with harvest_rej_jsonl.open("a") as hf:
                        hf.write(
                            json.dumps(
                                {
                                    "compound_id": None,
                                    "run_id": run_idx,
                                    "wave": "ola3",
                                    "target_name": target_name,
                                    "particle_name": target_name or "unknown",
                                    "template_name": tmpl_name,
                                    "seed": seed,
                                    "config_hash": config_hash,
                                    "status": "skip",
                                    "reason": "not_enough_blocks",
                                }
                            )
                            + "\n"
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
                memory_var_threshold=memory_var_threshold,
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
                "binding_energy": mass_block.get("E_bind_mass"),
                "mass_defect": mass_block.get("mass_defect"),
                "binding_energy_pos": mass_block.get("E_bind_mass"),
                "mass_defect_pos": mass_block.get("mass_defect"),
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

            # Harvest jsonl append
            if harvest_jsonl:
                harvest_jsonl.parent.mkdir(parents=True, exist_ok=True)
                compound_id = hashlib.sha256(
                    f"{target_name}|{tmpl_name}|{run_idx}|{seed}|{config_hash}".encode()
                ).hexdigest()
                edges = tmpl.get("edges", [])
                # agregamos k_edge/g_edge por arista como listas; si vacío, valores globales
                k_edge_used = [K_local for _ in edges] if edges else [K_local]
                g_edge_used = [kappa_global for _ in edges] if edges else [kappa_global]
                lockq_mean = {}
                if lockq:
                    lockq_mean = {
                        "Q": float(np.mean([q.get("Q", 0.0) for q in lockq])),
                        "S1": float(np.mean([q.get("S1", 0.0) for q in lockq])),
                        "S2": float(np.mean([q.get("S2", 0.0) for q in lockq])),
                    }
                harvest_entry = {
                    "compound_id": compound_id,
                    "run_id": run_idx,
                    "wave": "ola3",
                    "target_name": target_name,
                    "particle_name": target_name if target_name else "unknown",
                    "template_name": tmpl_name,
                    "seed": seed,
                    "config_hash": config_hash,
                    "parent_ids": [b.get("block_id") or b.get("id") for b in picked],
                    "parent_names": [b.get("particle_name") or b.get("name") for b in picked],
                    "parent_families": [b.get("family") for b in picked],
                    "edges": edges,
                    "k_edge_used": k_edge_used,
                    "g_edge_used": g_edge_used,
                    "coupling_mode": tmpl.get("coupling_mode"),
                    "mass_gev": mass_block.get("M_final"),
                    "binding_energy": mass_block.get("mass_defect"),
                    "binding_energy_pos": mass_block.get("E_bind_mass"),
                    "mass_defect_pos": mass_block.get("mass_defect"),
                    "R_final": metrics.get("R_final"),
                    "Q_lock": metrics.get("QualityLock"),
                    "d_total": row.get("match_d_total"),
                    "lock_quality_Q": lockq_mean.get("Q") if lockq_mean else None,
                    "lock_quality_S1": lockq_mean.get("S1") if lockq_mean else None,
                    "lock_quality_S2": lockq_mean.get("S2") if lockq_mean else None,
                    "structure_tier": row.get("structure_tier_compound", row.get("structure_tier")),
                    "band_count_structural": row.get("band_count_compound", row.get("band_count")),
                    "memory_score_k10": metrics.get("memory_score_k10"),
                    "H_lock": row.get("H_block_mean"),
                    "PE": metrics.get("PE_tick_norm"),
                    "status": row["status"],
                    "reason": row.get("reason"),
                }
                with harvest_jsonl.open("a") as hf:
                    hf.write(json.dumps(harvest_entry) + "\n")

        if rows:
            fieldnames = sorted({k for r in rows for k in r.keys()})
            out_csv.parent.mkdir(parents=True, exist_ok=True)
            with out_csv.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print(f"[ola3] escrito {out_csv} ({len(rows)} rows)")


def main():
    parser = argparse.ArgumentParser(description="Run Ola3 reloaded (phase/memory) on blocks + templates.")
    parser.add_argument("--ola3-config", type=Path, default=Path("data/raw/wave3_compounds.json"), help="Archivo de reglas/targets.")
    parser.add_argument("--blocks-json", type=Path, default=None, help="Override de blocks Ola3 (ola3_blocks.json).")
    parser.add_argument("--species-catalog", type=Path, default=None, help="species_catalog.jsonl (Explorer v3).")
    parser.add_argument("--simple-blocks", type=Path, default=Path("data/processed/ola1/simple_blocks.json"), help="simple_blocks.json para masas padre.")
    parser.add_argument("--hbar-sim", type=Path, default=Path("data/processed/ola1/hbar_sim_calibration.json"), help="hbar_sim_calibration.json de Ola1.")
    parser.add_argument("--proxies-csv", type=Path, default=None, help="CSV con proxies Ola1 (band_energies_gev por run_id).")
    parser.add_argument("--output-root", type=Path, default=None, help="Carpeta base de salida.")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--runs-per-target", type=int, default=None, help="Override global de runs por target.")
    parser.add_argument("--log-every", type=int, default=0, help="Loguea progreso cada N runs (0 desactiva).")
    parser.add_argument("--harvest-jsonl", type=Path, default=None, help="Escribe harvest completo JSONL (append).")
    parser.add_argument("--harvest-rejections-jsonl", type=Path, default=None, help="Opcional: log de rechazos JSONL.")
    parser.add_argument("--memory-var-threshold", type=float, default=None, help="Override de memory_var_threshold.")
    args = parser.parse_args()

    run_from_rules(
        args.ola3_config,
        blocks_override=args.blocks_json,
        proxies_override=args.proxies_csv,
        output_root=args.output_root,
        seed=args.seed,
        runs_override=args.runs_per_target,
        log_every=args.log_every,
        harvest_jsonl=args.harvest_jsonl,
        harvest_rej_jsonl=args.harvest_rejections_jsonl,
        species_catalog=args.species_catalog,
        simple_blocks_path=args.simple_blocks,
        hbar_path=args.hbar_sim,
        memory_var_threshold=args.memory_var_threshold,
    )


if __name__ == "__main__":
    main()
