"""Ola-recursive pipeline runner (V1)."""

from __future__ import annotations

import argparse
import glob
import json
import subprocess
import sys
from pathlib import Path
import shutil
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _resolve_path(path_str: str, output_root: Optional[Path]) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    if output_root is not None:
        return output_root / path
    return path


def _resolve_path_with_base(path_str: str, output_root: Optional[Path], base_dir: Path) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    if path_str.startswith("."):
        return base_dir / path
    if path_str.startswith(("data/", "src/", "docs/", "scripts/")):
        return path
    if output_root is not None:
        return output_root / path
    candidate = base_dir / path
    if candidate.exists():
        return candidate
    return path


def _candidate_paths(path_str: str, output_root: Optional[Path], base_dir: Path) -> List[Path]:
    path = Path(path_str)
    if path.is_absolute():
        return [path]
    candidates: List[Path] = []
    if path_str.startswith("."):
        candidates.append(base_dir / path)
    if path_str.startswith(("data/", "src/", "docs/", "scripts/")):
        candidates.append(path)
    if output_root is not None:
        candidates.append(output_root / path)
    candidates.append(base_dir / path)
    candidates.append(path)
    seen = set()
    unique: List[Path] = []
    for cand in candidates:
        key = str(cand)
        if key in seen:
            continue
        seen.add(key)
        unique.append(cand)
    return unique


def _run_step(step_id: str, cmd: List[str]) -> None:
    print(f"[olar_pipeline] step={step_id} status=running", flush=True)
    print(f"[olar_pipeline] step={step_id} cmd={' '.join(cmd)}", flush=True)
    subprocess.run(cmd, check=True)
    print(f"[olar_pipeline] step={step_id} status=done", flush=True)


def _count_jsonl_rows(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    with path.open() as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def _build_ola1_export_cmd(config_path: Path) -> List[str]:
    cfg = _load_json(config_path)
    proxies_csv = cfg.get("proxies_csv")
    output_csv = cfg.get("output_csv")
    if not proxies_csv or not output_csv:
        raise RuntimeError("ola1_export_dna config requires proxies_csv and output_csv")
    cmd = [sys.executable, "-m", "ola1.ola1_dof_dna_catalog", "--proxies-csv", str(proxies_csv), "--output", str(output_csv)]
    sm_universe = cfg.get("sm_universe")
    if sm_universe:
        cmd.extend(["--sm-universe", str(sm_universe)])
    hbar_sim = cfg.get("hbar_sim")
    if hbar_sim:
        cmd.extend(["--hbar-sim", str(hbar_sim)])
    if cfg.get("with_sm_trace"):
        cmd.append("--with-sm-trace")
    if cfg.get("update_proxies"):
        cmd.append("--update-proxies")
    if cfg.get("cluster_radii"):
        cmd.append("--cluster-radii")
    return cmd


def _build_core_promotion_cmd(config_path: Path) -> List[str]:
    cfg = _load_json(config_path)
    base_dir = config_path.parent
    ola_from = cfg.get("ola_from")
    ola_to = cfg.get("ola_to")
    if ola_from is None or ola_to is None:
        raise RuntimeError("core_promotion config requires ola_from and ola_to")
    cmd = [
        sys.executable,
        "-m",
        "core.promotion.blocks_from_ola",
        "--ola-from",
        str(int(ola_from)),
        "--ola-to",
        str(int(ola_to)),
    ]
    if cfg.get("entities_jsonl"):
        entities_jsonl = _resolve_path_with_base(str(cfg.get("entities_jsonl")), None, base_dir)
        cmd.extend(["--entities", str(entities_jsonl)])
    if cfg.get("genome_layer_csv"):
        genome_layer_csv = _resolve_path_with_base(str(cfg.get("genome_layer_csv")), None, base_dir)
        cmd.extend(["--genome", str(genome_layer_csv)])
    if cfg.get("blocks_prev_json"):
        blocks_prev_json = _resolve_path_with_base(str(cfg.get("blocks_prev_json")), None, base_dir)
        cmd.extend(["--blocks-prev", str(blocks_prev_json)])
    if cfg.get("blocks_prev_block_id_key"):
        cmd.extend(["--blocks-prev-id-key", str(cfg.get("blocks_prev_block_id_key"))])
    if cfg.get("require_node_theta_internal"):
        cmd.append("--require-node-theta-internal")
    if cfg.get("allowed_grades"):
        cmd.extend(["--allowed-grades", ",".join([str(g) for g in cfg.get("allowed_grades")])])
    if cfg.get("output_blocks_json"):
        output_blocks_json = _resolve_path_with_base(str(cfg.get("output_blocks_json")), None, base_dir)
        cmd.extend(["--output", str(output_blocks_json)])
    if cfg.get("dna_output_csv"):
        dna_output_csv = _resolve_path_with_base(str(cfg.get("dna_output_csv")), None, base_dir)
        cmd.extend(["--dna-output", str(dna_output_csv)])
    return cmd


def _build_ola1_export_block_id_cmd(config_path: Path) -> List[str]:
    cfg = _load_json(config_path)
    blocks_json = cfg.get("blocks_json")
    dna_csv = cfg.get("dna_csv")
    output_csv = cfg.get("output_csv")
    if not blocks_json or not dna_csv or not output_csv:
        raise RuntimeError("ola1_export_dna_block_id config requires blocks_json, dna_csv, output_csv")
    cmd = [
        sys.executable,
        "-m",
        "ola1.legacy.ola1_export_dna_block_id",
        "--blocks-json",
        str(blocks_json),
        "--dna-csv",
        str(dna_csv),
        "--output",
        str(output_csv),
    ]
    if cfg.get("allow_missing_dna"):
        cmd.append("--allow-missing-dna")
    return cmd


def _build_merge_evaluations_cmd(config_path: Path) -> List[str]:
    cfg = _load_json(config_path)
    inputs = cfg.get("inputs")
    output = cfg.get("output")
    stats_output = cfg.get("stats_output")
    sample_size = cfg.get("sample_size")
    if not inputs or not output:
        raise RuntimeError("merge_evaluations config requires inputs and output")
    if isinstance(inputs, str):
        inputs_list = [inputs]
    elif isinstance(inputs, list):
        inputs_list = [str(val) for val in inputs if isinstance(val, str)]
    else:
        inputs_list = []
    if not inputs_list:
        raise RuntimeError("merge_evaluations config requires inputs list")
    cmd = [
        sys.executable,
        "scripts/merge_evaluations.py",
        "--inputs",
        *inputs_list,
        "--output",
        str(output),
    ]
    if stats_output:
        cmd.extend(["--stats-output", str(stats_output)])
    if isinstance(sample_size, int):
        cmd.extend(["--sample-size", str(sample_size)])
    return cmd


def _load_sweep_shards_config(config_path: Path) -> Dict[str, Any]:
    cfg = _load_json(config_path)
    configs = cfg.get("configs")
    if not isinstance(configs, list) or not configs:
        raise RuntimeError("olar_sweep_shards config requires configs list.")
    max_parallel = cfg.get("max_parallel", 0)
    try:
        max_parallel = int(max_parallel)
    except Exception:
        max_parallel = 0
    return {"configs": [str(c) for c in configs], "max_parallel": max_parallel}


def _run_sweep_shards(config_path: Path) -> None:
    cfg = _load_sweep_shards_config(config_path)
    configs = [str(Path(c)) for c in cfg["configs"]]
    max_parallel = int(cfg["max_parallel"] or 0)
    if max_parallel <= 0 or max_parallel > len(configs):
        max_parallel = len(configs)
    procs: List[Tuple[str, subprocess.Popen]] = []
    idx = 0
    failures: List[Tuple[str, int]] = []

    while idx < len(configs) or procs:
        while idx < len(configs) and len(procs) < max_parallel:
            cfg_path = configs[idx]
            cmd = [sys.executable, "-m", "olar.sweep", "--config", cfg_path]
            print(f"[olar_pipeline] step=olar_sweep_shards spawn cmd={' '.join(cmd)}", flush=True)
            procs.append((cfg_path, subprocess.Popen(cmd)))
            idx += 1
        cfg_path, proc = procs.pop(0)
        ret = proc.wait()
        if ret != 0:
            failures.append((cfg_path, ret))

    if failures:
        sample = ", ".join([f"{p} (code={c})" for p, c in failures[:5]])
        raise RuntimeError(f"olar_sweep_shards failures: {sample}")


def _iter_cfg_paths(cfg: Dict[str, Any], keys: Iterable[str]) -> Iterable[str]:
    for key in keys:
        val = cfg.get(key)
        if isinstance(val, str) and val:
            yield val


def _collect_step_inputs(step_type: str, cfg: Dict[str, Any]) -> List[str]:
    if step_type in ("olar_explorer", "olar_sweep", "core_catalog_build", "core_taxonomy"):
        inputs = cfg.get("inputs", {})
        if isinstance(inputs, dict):
            return [str(v) for v in inputs.values() if isinstance(v, str)]
    if step_type == "ola1_export_dna":
        return list(_iter_cfg_paths(cfg, ("proxies_csv", "sm_universe")))
    if step_type == "ola1_export_dna_block_id":
        return list(_iter_cfg_paths(cfg, ("blocks_json", "dna_csv")))
    if step_type == "core_promote_blocks":
        return list(
            _iter_cfg_paths(
                cfg,
                ("entities_jsonl", "genome_layer_csv", "blocks_prev_json"),
            )
        )
    if step_type == "olar_sweep_shards":
        configs = cfg.get("configs", [])
        if isinstance(configs, list):
            return [str(c) for c in configs if isinstance(c, str)]
    if step_type == "olar_sweep_dynamic":
        sweep_cfg = cfg.get("sweep_config")
        return [str(sweep_cfg)] if isinstance(sweep_cfg, str) else []
    if step_type == "merge_evaluations":
        inputs = cfg.get("inputs")
        if isinstance(inputs, str):
            return [inputs]
        if isinstance(inputs, list):
            return [str(v) for v in inputs if isinstance(v, str)]
    return []


def _collect_step_outputs(step_type: str, cfg: Dict[str, Any]) -> List[str]:
    if step_type in ("olar_explorer", "olar_sweep", "core_catalog_build", "core_taxonomy"):
        outputs = cfg.get("outputs", {})
        if isinstance(outputs, dict):
            optional_keys = {str(k) for k in (cfg.get("optional_outputs") or [])}
            return [
                str(v)
                for k, v in outputs.items()
                if isinstance(v, str) and str(k) not in optional_keys
            ]
    if step_type == "ola1_export_dna":
        return list(_iter_cfg_paths(cfg, ("output_csv",)))
    if step_type == "ola1_export_dna_block_id":
        return list(_iter_cfg_paths(cfg, ("output_csv",)))
    if step_type == "core_promote_blocks":
        return list(_iter_cfg_paths(cfg, ("output_blocks_json", "dna_output_csv")))
    if step_type == "olar_sweep_shards":
        return []
    if step_type == "merge_evaluations":
        return list(_iter_cfg_paths(cfg, ("output", "stats_output")))
    if step_type == "olar_sweep_dynamic":
        return list(_iter_cfg_paths(cfg, ("worker_output_root", "claim_log")))
    return []


def _maybe_remove(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def _reset_step_outputs(step_type: str, cfg: Dict[str, Any], output_root: Optional[Path], base_dir: Path) -> None:
    if step_type == "olar_explorer":
        outputs = cfg.get("outputs", {})
        for key in ("attempts_jsonl", "entities_candidates_jsonl", "report_md"):
            val = outputs.get(key)
            if isinstance(val, str) and val:
                path = _resolve_path_with_base(val, output_root, base_dir)
                _maybe_remove(path)
                _maybe_remove(path.with_suffix(path.suffix + ".resume.json"))
        raw_dir = outputs.get("raw_dir")
        if isinstance(raw_dir, str) and raw_dir:
            _maybe_remove(_resolve_path_with_base(raw_dir, output_root, base_dir))
        return
    if step_type == "olar_sweep":
        outputs = cfg.get("outputs", {})
        for key in ("evaluations_jsonl", "report_md"):
            val = outputs.get(key)
            if isinstance(val, str) and val:
                _maybe_remove(_resolve_path_with_base(val, output_root, base_dir))
        raw_dir = outputs.get("raw_dir")
        if isinstance(raw_dir, str) and raw_dir:
            _maybe_remove(_resolve_path_with_base(raw_dir, output_root, base_dir))
        return
    if step_type == "olar_sweep_shards":
        configs = cfg.get("configs", [])
        if isinstance(configs, list):
            for cfg_path in configs:
                if not isinstance(cfg_path, str):
                    continue
                shard_cfg = _load_json(_resolve_path_with_base(cfg_path, output_root, base_dir))
                _reset_step_outputs("olar_sweep", shard_cfg, output_root, base_dir)
        return
    if step_type == "merge_evaluations":
        for key in ("output", "stats_output"):
            val = cfg.get(key)
            if isinstance(val, str) and val:
                _maybe_remove(_resolve_path_with_base(val, output_root, base_dir))
        return
    if step_type == "olar_sweep_dynamic":
        worker_root = cfg.get("worker_output_root")
        claim_log = cfg.get("claim_log")
        if isinstance(worker_root, str) and worker_root:
            _maybe_remove(_resolve_path_with_base(worker_root, output_root, base_dir))
        if isinstance(claim_log, str) and claim_log:
            _maybe_remove(_resolve_path_with_base(claim_log, output_root, base_dir))
        return
    if step_type == "core_catalog_build":
        outputs = cfg.get("outputs", {})
        for key in ("catalog_dir", "entities_jsonl", "genome_layer_csv", "rollups_json", "explorer_report_md", "sweep_report_md"):
            val = outputs.get(key)
            if isinstance(val, str) and val:
                _maybe_remove(_resolve_path_with_base(val, output_root, base_dir))
        return
    if step_type == "core_taxonomy":
        outputs = cfg.get("outputs", {})
        for key in ("genome_layer_out_csv", "taxonomy_rollups_json"):
            val = outputs.get(key)
            if isinstance(val, str) and val:
                _maybe_remove(_resolve_path_with_base(val, output_root, base_dir))
        return
    if step_type == "core_promote_blocks":
        for key in ("output_blocks_json", "dna_output_csv"):
            val = cfg.get(key)
            if isinstance(val, str) and val:
                _maybe_remove(_resolve_path_with_base(val, output_root, base_dir))
        return


def _validate_paths(
    paths: Iterable[str],
    output_root: Optional[Path],
    base_dir: Path,
    label: str,
    step_id: str,
) -> None:
    missing = []
    for path_str in paths:
        if "*" in path_str or "?" in path_str or "[" in path_str:
            resolved = _resolve_path_with_base(path_str, output_root, base_dir)
            matches = glob.glob(str(resolved))
            if not matches:
                missing.append(str(resolved))
            continue
        candidates = _candidate_paths(path_str, output_root, base_dir)
        if not any(cand.exists() for cand in candidates):
            missing.append(str(_resolve_path_with_base(path_str, output_root, base_dir)))
    if missing:
        raise RuntimeError(f"[olar_pipeline] step={step_id} missing {label}: {missing}")


def main() -> None:
    parser = argparse.ArgumentParser(description="olar pipeline (V1).")
    parser.add_argument("--sequence", required=True, help="Path to run_sequence.json.")
    parser.add_argument("--output-root", required=False, help="Override output root.")
    parser.add_argument(
        "--RESET",
        action="store_true",
        dest="reset_outputs",
        help="Remove pipeline outputs before running (uppercase only).",
    )
    args = parser.parse_args()

    sequence_path = Path(args.sequence)
    cfg = _load_json(sequence_path)
    output_root = Path(args.output_root) if args.output_root else None

    steps = cfg.get("steps", [])
    print("[olar_pipeline] step summary:", flush=True)
    for step in steps:
        step_id = step.get("id", "unknown")
        step_type = step.get("type", "unknown")
        enabled = bool(step.get("enabled", True))
        status = "DISABLED" if not enabled else "ENABLED"
        print(f"[olar_pipeline] {step_id} ({step_type}) -> {status}", flush=True)
    if args.reset_outputs:
        for step in steps:
            if not step.get("enabled", True):
                continue
            step_type = step.get("type")
            if step_type not in (
                "olar_explorer",
                "olar_sweep",
                "olar_sweep_shards",
                "olar_sweep_dynamic",
                "merge_evaluations",
                "core_catalog_build",
                "core_taxonomy",
                "core_promote_blocks",
            ):
                continue
            config_path = _resolve_path(step.get("config", ""), output_root)
            if not config_path.exists():
                continue
            step_cfg = _load_json(config_path)
            _reset_step_outputs(step_type, step_cfg, output_root, config_path.parent)
    for step in steps:
        if not step.get("enabled", True):
            continue
        step_id = step.get("id", "unknown")
        step_type = step.get("type")
        config_path = _resolve_path(step.get("config", ""), output_root)
        if not config_path.exists():
            raise RuntimeError(f"Config not found for step {step_id}: {config_path}")

        step_cfg = _load_json(config_path)
        input_paths = _collect_step_inputs(step_type, step_cfg)
        if input_paths:
            _validate_paths(input_paths, output_root, config_path.parent, "inputs", step_id)

        if step_type == "olar_explorer":
            cmd = [sys.executable, "-m", "olar.explorer", "--config", str(config_path)]
        elif step_type == "olar_sweep":
            cmd = [sys.executable, "-m", "olar.sweep", "--config", str(config_path)]
        elif step_type == "core_catalog_build":
            cmd = [sys.executable, "-m", "core.catalog.builder", "--config", str(config_path)]
        elif step_type == "core_taxonomy":
            cmd = [sys.executable, "-m", "core.taxonomy.builder", "--config", str(config_path)]
        elif step_type == "ola1_export_dna":
            cmd = _build_ola1_export_cmd(config_path)
        elif step_type == "ola1_export_dna_block_id":
            cmd = _build_ola1_export_block_id_cmd(config_path)
        elif step_type == "core_promote_blocks":
            cmd = _build_core_promotion_cmd(config_path)
        elif step_type == "olar_sweep_shards":
            _run_sweep_shards(config_path)
            output_paths = _collect_step_outputs(step_type, step_cfg)
            if output_paths:
                _validate_paths(output_paths, output_root, config_path.parent, "outputs", step_id)
            continue
        elif step_type == "olar_sweep_dynamic":
            cmd = [sys.executable, "-m", "olar.sweep_dynamic", "--config", str(config_path)]
        elif step_type == "merge_evaluations":
            cmd = _build_merge_evaluations_cmd(config_path)
        else:
            raise RuntimeError(f"Unknown step type: {step_type}")

        _run_step(step_id, cmd)
        if step_type == "olar_explorer" and step.get("halt_if_no_candidates"):
            outputs = step_cfg.get("outputs", {})
            attempts_path = outputs.get("attempts_jsonl")
            entities_path = outputs.get("entities_candidates_jsonl")
            if isinstance(attempts_path, str) and isinstance(entities_path, str):
                attempts_count = _count_jsonl_rows(_resolve_path_with_base(attempts_path, output_root, config_path.parent))
                entities_count = _count_jsonl_rows(_resolve_path_with_base(entities_path, output_root, config_path.parent))
                if attempts_count == 0 and entities_count == 0:
                    print("[olar_pipeline] no explorer candidates; halting pipeline", flush=True)
                    break
        output_paths = _collect_step_outputs(step_type, step_cfg)
        if output_paths:
            _validate_paths(output_paths, output_root, config_path.parent, "outputs", step_id)


if __name__ == "__main__":
    main()
