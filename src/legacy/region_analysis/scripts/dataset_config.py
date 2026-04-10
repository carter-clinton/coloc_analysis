"""
Helpers for loading dataset configuration metadata used across Snakemake rules.
"""
from __future__ import annotations

import functools
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@functools.lru_cache(maxsize=None)
def _load_config_cached(resolved_path: str, mtime: float) -> Dict[str, Any]:
    config_path = Path(resolved_path)
    with config_path.open("r") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or "datasets" not in data:
        raise ValueError(f"Config at {config_path} missing 'datasets' key")
    data["_resolved_path"] = resolved_path
    return data


def _load_config(path: str) -> Dict[str, Any]:
    config_path = Path(path).expanduser().resolve()
    mtime = config_path.stat().st_mtime
    return _load_config_cached(str(config_path), mtime)


def dataset_descriptor(
    trait: str,
    ancestry: str,
    config_path: str = "config/datasets.yaml",
    dataset_name: Optional[str] = None,
    dataset_priority: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    cfg = _load_config(config_path)
    datasets = cfg["datasets"]
    dataset_name = (
        dataset_name
        or (dataset_priority or {}).get(trait)
        or next(iter(datasets.keys()))
    )
    try:
        dataset = datasets[dataset_name]
    except KeyError as err:
        raise KeyError(f"Dataset '{dataset_name}' not defined in {config_path}") from err

    trait_cfg = dataset.get("traits", {}).get(trait)
    if trait_cfg is None:
        available = ", ".join(dataset.get("traits", {}).keys())
        raise KeyError(
            f"Trait '{trait}' missing for dataset '{dataset_name}'. "
            f"Available: {available}"
        )

    ancestry_cfg = (trait_cfg.get("ancestries") or {}).get(ancestry)
    if ancestry_cfg is None:
        available = ", ".join((trait_cfg.get("ancestries") or {}).keys())
        raise KeyError(
            f"Trait '{trait}' missing ancestry '{ancestry}' for dataset '{dataset_name}'. "
            f"Available: {available}"
        )

    defaults = dataset.get("defaults", {})
    column_map: Dict[str, Any] = {}
    for scope in (defaults, trait_cfg, ancestry_cfg):
        column_map.update(scope.get("column_map", {}))

    compression = ancestry_cfg.get(
        "compression",
        trait_cfg.get("compression", defaults.get("compression", "infer")),
    )
    sep = ancestry_cfg.get(
        "sep",
        trait_cfg.get("sep", defaults.get("sep", "\t")),
    )
    delim_whitespace = ancestry_cfg.get(
        "delim_whitespace",
        trait_cfg.get("delim_whitespace", defaults.get("delim_whitespace", False)),
    )
    local_path = ancestry_cfg.get(
        "local_path",
        trait_cfg.get("local_path", defaults.get("local_path")),
    )

    path = ancestry_cfg.get("path") or trait_cfg.get("path")
    if not path:
        raise ValueError(
            f"No download path specified for trait '{trait}', ancestry '{ancestry}' "
            f"in dataset '{dataset_name}'."
        )

    base_url = dataset.get("base_url", "").rstrip("/")
    if path.startswith("http://") or path.startswith("https://"):
        url = path
    elif base_url:
        url = f"{base_url}/{path.lstrip('/')}"
    else:
        url = path

    descriptor = {
        "dataset": dataset_name,
        "trait": trait,
        "ancestry": ancestry,
        "url": url,
        "path": path,
        "local_path": local_path,
        "md5": ancestry_cfg.get("md5") or trait_cfg.get("md5"),
        "description": dataset.get("description", ""),
        "column_map": column_map,
        "compression": compression,
        "sep": sep,
        "delim_whitespace": bool(delim_whitespace),
        "config_path": cfg["_resolved_path"],
        "zip_member": ancestry_cfg.get("zip_member")
        or trait_cfg.get("zip_member")
        or defaults.get("zip_member"),
        "sample_size": ancestry_cfg.get("sample_size")
        or trait_cfg.get("sample_size")
        or defaults.get("sample_size")
        or dataset.get("sample_size"),
        "rsid_map": ancestry_cfg.get("rsid_map")
        or trait_cfg.get("rsid_map")
        or defaults.get("rsid_map")
        or dataset.get("rsid_map"),
        "snp_id_columns": ancestry_cfg.get("snp_id_columns")
        or trait_cfg.get("snp_id_columns")
        or defaults.get("snp_id_columns"),
    }
    return descriptor


__all__ = ["dataset_descriptor"]
