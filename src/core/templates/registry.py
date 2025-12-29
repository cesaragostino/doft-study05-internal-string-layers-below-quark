"""Template registry + canonical edge normalization (V1)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def canonicalize_edges(edges: List[List[int]]) -> List[List[int]]:
    out: List[List[int]] = []
    for e in edges or []:
        if len(e) < 2:
            continue
        i, j = int(e[0]), int(e[1])
        if i == j:
            continue
        out.append([min(i, j), max(i, j)])
    out.sort()
    return out


def load_templates(path: Path) -> Dict[str, Dict[str, Any]]:
    raw = json.loads(path.read_text())
    templates = raw.get("templates") if isinstance(raw, dict) else raw
    if not isinstance(templates, list):
        raise ValueError(f"templates_json must be a list or include 'templates': {path}")
    out: Dict[str, Dict[str, Any]] = {}
    for tmpl in templates:
        if not isinstance(tmpl, dict):
            continue
        name = tmpl.get("name")
        if not name:
            continue
        edges = tmpl.get("edges", [])
        tmpl = dict(tmpl)
        tmpl["edges"] = canonicalize_edges(edges)
        out[str(name)] = tmpl
    return out
