"""Dynamic sweep scheduler (central assignment)."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from olar import sweep as sweep_module


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _resolve_path(path_str: str, base_dir: Path) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return base_dir / path


def _write_claim(claim_path: Path, payload: Dict[str, Any]) -> None:
    claim_path.parent.mkdir(parents=True, exist_ok=True)
    with claim_path.open("a") as f:
        f.write(json.dumps(payload) + "\n")


def _build_worker_config(base_cfg: Dict[str, Any]) -> Dict[str, Any]:
    cfg = json.loads(json.dumps(base_cfg))
    cfg["candidate_shard"] = {"enabled": False}
    outputs = cfg.get("outputs", {})
    outputs["evaluations_jsonl"] = "raw/evaluations.jsonl"
    outputs["raw_dir"] = "raw"
    outputs["report_md"] = "sweep_report.md"
    cfg["outputs"] = outputs
    return cfg


def main() -> None:
    parser = argparse.ArgumentParser(description="Dynamic sweep scheduler (central assignment).")
    parser.add_argument("--config", required=True, help="Path to sweep_dynamic config JSON.")
    args = parser.parse_args()

    config_path = Path(args.config)
    cfg = _load_json(config_path)
    base_dir = config_path.parent
    sweep_cfg_path = _resolve_path(str(cfg.get("sweep_config", "")), base_dir)
    if not sweep_cfg_path.exists():
        raise RuntimeError(f"sweep_config not found: {sweep_cfg_path}")

    max_parallel = int(cfg.get("max_parallel", 0) or 0)
    if max_parallel <= 0:
        raise RuntimeError("max_parallel must be > 0")

    worker_root = _resolve_path(str(cfg.get("worker_output_root", "")), base_dir)
    if not worker_root:
        raise RuntimeError("worker_output_root required")
    worker_root.mkdir(parents=True, exist_ok=True)

    claim_log = cfg.get("claim_log") or str(worker_root / "claims.jsonl")
    claim_path = _resolve_path(str(claim_log), base_dir)

    base_cfg = _load_json(sweep_cfg_path)
    base_cfg["candidate_shard"] = {"enabled": False}
    inputs = base_cfg.get("inputs", {})
    entities_path = Path(inputs.get("entities_candidates_jsonl", "data/processed/ola2/raw/entities_candidates.jsonl"))
    if not entities_path.exists():
        raise RuntimeError(f"No entities found in {entities_path}")

    entities, skipped_filter, skipped_shard = sweep_module._select_candidates(base_cfg, entities_path)
    if not entities:
        raise RuntimeError("No candidates found for sweep.")

    entity_ids = [str(row.get("entity_id")) for row in entities if row.get("entity_id")]
    print(
        "[olar_sweep_dynamic] candidates="
        f"{len(entity_ids)} skipped_filter={skipped_filter} skipped_shard={skipped_shard}",
        flush=True,
    )

    worker_cfg_template = _build_worker_config(base_cfg)
    worker_cfg_paths: Dict[int, Path] = {}
    for worker_id in range(max_parallel):
        worker_dir = worker_root / f"worker_{worker_id:02d}"
        worker_dir.mkdir(parents=True, exist_ok=True)
        cfg_path = worker_dir / "sweep_config.json"
        cfg_path.write_text(json.dumps(worker_cfg_template, indent=2))
        worker_cfg_paths[worker_id] = cfg_path

    queue = list(entity_ids)
    available = list(range(max_parallel))
    running: List[Dict[str, Any]] = []
    failures: List[Dict[str, Any]] = []

    while queue or running:
        while queue and available:
            worker_id = available.pop(0)
            entity_id = queue.pop(0)
            worker_dir = worker_root / f"worker_{worker_id:02d}"
            cmd = [
                sys.executable,
                "-m",
                "olar.sweep",
                "--config",
                str(worker_cfg_paths[worker_id]),
                "--output-dir",
                str(worker_dir),
                "--entity-id",
                entity_id,
            ]
            _write_claim(
                claim_path,
                {
                    "timestamp_utc": _utc_now(),
                    "status": "claimed",
                    "entity_id": entity_id,
                    "worker_id": worker_id,
                    "cmd": cmd,
                },
            )
            proc = subprocess.Popen(cmd)
            running.append(
                {
                    "proc": proc,
                    "entity_id": entity_id,
                    "worker_id": worker_id,
                    "started": time.time(),
                }
            )

        completed_any = False
        for item in list(running):
            ret = item["proc"].poll()
            if ret is None:
                continue
            completed_any = True
            running.remove(item)
            available.append(item["worker_id"])
            status = "done" if ret == 0 else "failed"
            _write_claim(
                claim_path,
                {
                    "timestamp_utc": _utc_now(),
                    "status": status,
                    "entity_id": item["entity_id"],
                    "worker_id": item["worker_id"],
                    "exit_code": ret,
                    "duration_s": round(time.time() - item["started"], 3),
                },
            )
            if ret != 0:
                failures.append(
                    {
                        "entity_id": item["entity_id"],
                        "worker_id": item["worker_id"],
                        "exit_code": ret,
                    }
                )
        if not completed_any:
            time.sleep(0.2)

    if failures:
        sample = ", ".join(
            [f\"{f['entity_id']}@{f['worker_id']} (code={f['exit_code']})\" for f in failures[:5]]
        )
        raise RuntimeError(f"olar_sweep_dynamic failures: {sample}")


if __name__ == "__main__":
    main()
