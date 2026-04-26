#!/usr/bin/env python3
"""M2 deterministic (stratum, trait_key) enumeration helper.

Reads config/trait_inventory.yaml. For each stratum {EUR, AFR, TRANS},
returns the list of trait keys whose harmonized + munged outputs exist
on disk and match the requested ancestry.

Decision references:
  D-M2-06 — strict ancestry match, skip-with-doc when missing
  D-M2-Q6 — _MIN_PER_STRATUM = 3 (Carter-locked; soft floor — NOT 5
            from research defensive default)
  Pattern B (m1_trait_keys.py) — same defensive-bound idiom

"MULTI" ancestry (GBMI naming convention per CONTEXT D-M2-06) maps to
TRANS stratum.

Plan reference: m2-00-preflight-and-environment-PLAN.md Task 7.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yaml

STRATA: tuple[str, ...] = ("EUR", "AFR", "TRANS")
_MIN_PER_STRATUM: int = 3   # D-M2-Q6 Carter-locked (NOT 5 research default)
_MAX_PER_STRATUM: int = 9   # 9-trait inventory locked per Amendment §4

# GBMI ancestry MULTI is logically TRANS for stratum purposes
_ANCESTRY_TO_STRATUM = {
    "EUR": "EUR",
    "AFR": "AFR",
    "TRANS": "TRANS",
    "MULTI": "TRANS",
}


def _is_active(entry: dict) -> bool:
    """Cell is active if qc_status != MISSING AND munged_path exists on disk."""
    if entry.get("qc_status") == "MISSING":
        return False
    munged = entry.get("munged_path", "")
    if not munged:
        return False
    return Path(munged).exists()


def keys_for_stratum(inventory_path: Path, stratum: str) -> list[str]:
    """Return sorted list of trait keys for the given stratum.

    Soft floor: if len < _MIN_PER_STRATUM, returns the partial list anyway;
    the caller is responsible for skip-with-doc handling per D-M2-06 (emit
    a row to skipped_strata.tsv). Use enforce_stratum_floor() to raise
    instead.

    Parameters
    ----------
    inventory_path : Path
        Path to config/trait_inventory.yaml.
    stratum : str
        One of STRATA = ("EUR", "AFR", "TRANS").

    Returns
    -------
    list[str]
        Sorted, deduped list of trait keys whose ancestry maps to the
        requested stratum AND whose munged_path exists on disk.

    Raises
    ------
    ValueError
        If stratum is not in STRATA.
    """
    if stratum not in STRATA:
        raise ValueError(f"stratum must be one of {STRATA}; got {stratum!r}")

    with open(inventory_path) as f:
        inv = yaml.safe_load(f)

    # config/trait_inventory.yaml top-level shape: { traits: { key: {...}, ... } }
    # Tolerate the alternate flat shape { key: {...}, ... } as well.
    cells = inv.get("traits", inv) if isinstance(inv, dict) else {}

    keys: list[str] = []
    for key, entry in cells.items():
        if not isinstance(entry, dict):
            continue
        ancestry = entry.get("ancestry", "")
        cell_stratum = _ANCESTRY_TO_STRATUM.get(ancestry)
        if cell_stratum != stratum:
            continue
        if not _is_active(entry):
            continue
        keys.append(key)

    return sorted(set(keys))


def enforce_stratum_floor(keys: Iterable[str], stratum: str) -> None:
    """Raise AssertionError if len(keys) is outside [_MIN_PER_STRATUM, _MAX_PER_STRATUM].

    Production-fire validator. NOT used by Snakemake rules directly
    (they emit skipped_strata.tsv per D-M2-06 instead).
    """
    keys = list(keys)
    assert len(keys) >= _MIN_PER_STRATUM, (
        f"m2_stratum_keys: stratum {stratum} has {len(keys)} keys, "
        f"below floor _MIN_PER_STRATUM={_MIN_PER_STRATUM}. "
        f"Carter-locked at 3 per D-M2-Q6."
    )
    assert len(keys) <= _MAX_PER_STRATUM, (
        f"m2_stratum_keys: stratum {stratum} has {len(keys)} keys, "
        f"above ceiling _MAX_PER_STRATUM={_MAX_PER_STRATUM}. "
        f"9-trait inventory locked per Amendment §4."
    )


def _main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--inventory", type=Path, default=Path("config/trait_inventory.yaml")
    )
    ap.add_argument("--stratum", required=True, choices=STRATA)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    keys = keys_for_stratum(args.inventory, args.stratum)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(keys) + ("\n" if keys else ""))
    print(f"Wrote {len(keys)} {args.stratum} keys to {args.out}")


if __name__ == "__main__":
    _main()
