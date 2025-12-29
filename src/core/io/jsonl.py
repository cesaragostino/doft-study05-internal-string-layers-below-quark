"""Append-only JSONL utilities (V1)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Set, Tuple


def append_jsonl(
    path: Path,
    rows: Iterable[Dict[str, Any]],
    validate: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> int:
    """Append rows to JSONL file and return count written (fail fast on validation)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("a") as f:
        for row in rows:
            if validate is not None:
                validate(row)
            f.write(json.dumps(row) + "\n")
            count += 1
    return count


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Read all rows from JSONL file."""
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def iter_jsonl(path: Path) -> Iterator[Dict[str, Any]]:
    """Stream rows from JSONL file."""
    if not path.exists():
        return iter(())
    def _iter() -> Iterator[Dict[str, Any]]:
        with path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)
    return _iter()


def write_resume_index(path: Path, last_offset: int, extra: Optional[Dict[str, Any]] = None) -> None:
    """Write a minimal resume index (byte offset + optional metadata)."""
    payload: Dict[str, Any] = {"last_offset": int(last_offset)}
    if extra:
        payload["extra"] = extra
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def scan_jsonl_ids(path: Path, id_getter: Callable[[Dict[str, Any]], Optional[str]]) -> Tuple[Set[str], int]:
    """Scan JSONL file and return (ids, last_offset)."""
    ids: Set[str] = set()
    if not path.exists():
        return ids, 0
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            val = id_getter(row)
            if val:
                ids.add(str(val))
    return ids, path.stat().st_size
