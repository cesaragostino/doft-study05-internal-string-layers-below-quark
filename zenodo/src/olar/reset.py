#!/usr/bin/env python3
"""Reset generated outputs for a single ola directory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Iterable, List


def _collect_paths(ola_dir: Path) -> List[Path]:
    return [
        ola_dir / "raw",
        ola_dir / "sweep_shards",
        ola_dir / "sweep_workers",
        ola_dir / "sweep_merged",
        ola_dir / "catalog",
        ola_dir / "promoted",
        ola_dir / "explorer_report.md",
        ola_dir / "sweep_report.md",
        ola_dir / "report.md",
    ]


def _validate_target(ola_dir: Path) -> None:
    if not ola_dir.exists():
        raise SystemExit(f"[olar_reset] ola_dir not found: {ola_dir}")
    if not ola_dir.is_dir():
        raise SystemExit(f"[olar_reset] ola_dir is not a directory: {ola_dir}")
    resolved = ola_dir.resolve()
    if resolved == resolved.root:
        raise SystemExit("[olar_reset] refusing to operate on filesystem root")
    if "processed" not in resolved.parts:
        raise SystemExit(f"[olar_reset] ola_dir must live under data/processed: {resolved}")


def _print_plan(paths: Iterable[Path]) -> None:
    print("[olar_reset] planned deletions:")
    for path in paths:
        if path.exists():
            print(f"- {path}")


def _delete_paths(paths: Iterable[Path]) -> None:
    for path in paths:
        if not path.exists():
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset generated outputs for one ola.")
    parser.add_argument("--ola-dir", required=True, help="Processed ola directory to reset.")
    parser.add_argument(
        "--YES",
        action="store_true",
        help="Required confirmation flag to perform deletion.",
    )
    args = parser.parse_args()

    ola_dir = Path(args.ola_dir)
    _validate_target(ola_dir)
    paths = _collect_paths(ola_dir)
    _print_plan(paths)

    if not args.YES:
        raise SystemExit("[olar_reset] STOPPED: pass --YES to apply deletions.")

    _delete_paths(paths)
    print(f"[olar_reset] completed reset for {ola_dir}")


if __name__ == "__main__":
    main()
