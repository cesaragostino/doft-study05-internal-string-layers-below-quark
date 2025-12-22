"""Lightweight runner to execute a sequence of CLI modules described in JSON."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List


def _build_cmd(step: Dict[str, Any]) -> List[str]:
    module = step.get("module")
    args = step.get("args", {})
    cmd = ["python3", "-m", module]
    for k, v in args.items():
        flag = f"--{k.replace('_', '-')}"
        if isinstance(v, bool):
            if v:
                cmd.append(flag)
            continue
        if isinstance(v, list):
            cmd.append(flag)
            cmd.extend([str(x) for x in v])
        else:
            cmd.extend([flag, str(v)])
    return cmd


def run_sequence(seq_path: Path):
    steps = json.loads(seq_path.read_text())
    for step in steps:
        name = step.get("step", step.get("module"))
        cmd = _build_cmd(step)
        print(f"[pipeline] {name}: {' '.join(cmd)}", flush=True)
        subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Run pipeline steps from JSON sequence.")
    parser.add_argument("--sequence", type=Path, required=True, help="Path to sequence.json")
    args = parser.parse_args()
    run_sequence(args.sequence)


if __name__ == "__main__":
    main()
