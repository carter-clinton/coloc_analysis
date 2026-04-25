#!/usr/bin/env python3
"""Deterministic D-16 trait-keys list builder + canonical TOKEN_MAP export.

Single source of truth for the trait-key list consumed by:
  - src/snakemake/rules/m1_ldsc_rg.smk (rule m1_build_trait_keys_list)
  - src/python/build_trait_inventory.py (imports TOKEN_MAP) — m1-04 future

Reads .planning/amendments/SUMSTATS-UPGRADE.tsv. Filters to in-scope rows
(status IN to_download, already_downloaded), maps SUMSTATS-UPGRADE trait
labels -> D-16 lowercase tokens, parses the 4-digit year robustly, appends
the pre-pivot Evangelou sbp.EUR row (T1-spine reuse via verify_evangelou_sbp),
dedupes + sorts, writes one key per line.

Plan reference: m1-03-munge-and-ldsc-intercept-matrix-PLAN.md Task 1 step (A0).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

# SUMSTATS-UPGRADE.tsv trait-label -> D-16 lowercase token (canonical map; D-16 + D-10).
# CONTEXT D-16 trait tokens: bmi, t2d, sbp, stroke, asthma, cad, ldl, hdl, tg, tc, egfr, hba1c.
TOKEN_MAP = {
    "BMI": "bmi",
    "T2D": "t2d",
    "hypertension": "sbp",  # The TSV uses "hypertension" but the trait token per D-16 is "sbp".
    "stroke": "stroke",
    "asthma": "asthma",
    "CAD": "cad",
    "LDL": "ldl",
    "HDL": "hdl",
    "TG": "tg",
    "TC": "tc",
    "eGFR": "egfr",
    "HbA1c": "hba1c",
}

# Pre-pivot Evangelou SBP-EUR row (T1 spine reuse) is renamed in m1-02b verify_evangelou_sbp.
EVANGELOU_SBP_KEY = "sbp.EUR.Evangelou-ICBP-UKBB.2018"

IN_SCOPE_STATUSES = {"to_download", "already_downloaded"}

# Defensive bound on the produced key count. Current SUMSTATS-UPGRADE.tsv freeze
# has 47 data rows, 35 of which are in-scope per the W2 / m1-01 deferral churn;
# adding Evangelou + dedup yields ~36-46 keys. Allow a generous 40<=N<=50 band
# (W5 fix language). On the FULL TSV this bound enforces inventory hygiene; the
# mini-fixture path in tests catches the AssertionError and accepts it.
_MIN_KEYS = 40
_MAX_KEYS = 50


def _year_from_citation(citation: str) -> str:
    """Robust 4-digit year extraction.

    Handles: ``Yengo 2018``, ``Mahajan 2022``, ``Loh 2022 (Nat Commun)``,
    ``Morris 2019 / Wuttke 2019``, ``Yengo (2018)``. W2 fix replaces the
    brittle ``citation.split()[1].rstrip(')')`` from prior plan drafts.
    """
    m = re.search(r"(\d{4})", citation)
    if not m:
        raise ValueError(f"No 4-digit year found in citation: {citation!r}")
    return m.group(1)


def build_keys(tsv_path: Path) -> list[str]:
    """Read SUMSTATS-UPGRADE.tsv and return the deterministic D-16 trait-key list.

    Steps:
      1. Filter to rows with ``status`` in IN_SCOPE_STATUSES.
      2. Map ``trait`` column through TOKEN_MAP; skip unknown labels silently.
      3. Build ``{token}.{ancestry}.{source_consortium}.{year}`` per row.
      4. Append EVANGELOU_SBP_KEY (T1 spine reuse).
      5. Dedupe + sort.
      6. Defensive bound check: 40 <= N <= 50.
    """
    df = pd.read_csv(tsv_path, sep="\t")
    in_scope = df[df["status"].isin(IN_SCOPE_STATUSES)].copy()

    keys: list[str] = []
    for _, row in in_scope.iterrows():
        trait_label = str(row["trait"])
        if trait_label not in TOKEN_MAP:
            continue
        token = TOKEN_MAP[trait_label]
        ancestry = str(row["ancestry"])
        consortium = str(row["source_consortium"])
        year = _year_from_citation(str(row["citation_first_author_year"]))
        keys.append(f"{token}.{ancestry}.{consortium}.{year}")

    # Pre-pivot Evangelou SBP-EUR (T1 spine reuse via verify_evangelou_sbp).
    keys.append(EVANGELOU_SBP_KEY)

    keys = sorted(set(keys))

    assert _MIN_KEYS <= len(keys) <= _MAX_KEYS, (
        f"m1_trait_keys: expected {_MIN_KEYS}<=N<={_MAX_KEYS} keys, got {len(keys)}. "
        f"Inspect SUMSTATS-UPGRADE.tsv for new rows or DEFERRED churn."
    )
    return keys


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--tsv",
        type=Path,
        default=Path(".planning/amendments/SUMSTATS-UPGRADE.tsv"),
    )
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    keys = build_keys(args.tsv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(keys) + "\n")
    print(f"Wrote {len(keys)} trait keys to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    _main()
