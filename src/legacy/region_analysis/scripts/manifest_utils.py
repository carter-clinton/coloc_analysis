from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Tuple


def parse_trait_ancestry(path: str) -> Tuple[str, str]:
    name = Path(path).name
    tokens = name.split(".")
    if len(tokens) < 2:
        raise ValueError(
            f"Cannot infer trait/ancestry from filename '{name}'. "
            "Expected <trait>.<ancestry>.<ext>"
        )
    trait, ancestry = tokens[0], tokens[1]
    return trait, ancestry


def harmonized_records(paths: Iterable[str]) -> List[Dict[str, str]]:
    records: List[Dict[str, str]] = []
    for path in paths:
        trait, ancestry = parse_trait_ancestry(path)
        records.append(
            {
                "trait": trait,
                "ancestry": ancestry,
                "path": str(path),
            }
        )
    return records


__all__ = ["parse_trait_ancestry", "harmonized_records"]
