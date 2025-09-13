"""Rule-based tagging utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Set

import yaml

ONTOLOGY_PATH = Path(__file__).resolve().parent.parent / "data" / "ontology.yaml"


def load_ontology(path: Path = ONTOLOGY_PATH) -> dict[str, Set[str]]:
    """Load ontology from YAML file."""
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {facet: set(info.get("any", [])) for facet, info in data.get("facets", {}).items()}


def tag_chunk(text: str, ontology: dict[str, Set[str]]) -> Set[str]:
    """Return set of facets whose keywords appear in text.

    This stub performs simple substring matching, case-insensitive.
    """
    lowered = text.lower()
    result = {facet for facet, keywords in ontology.items() if any(k.lower() in lowered for k in keywords)}
    return result
