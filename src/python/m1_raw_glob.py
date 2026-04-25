#!/usr/bin/env python3
"""Resolve the single expected raw-file path for a (source_tag, ancestry).

Single source of truth consumed by every M1 harmonize Snakemake rule's
``params: lambda`` so executors do not invent ad-hoc globs.

W8 fix (option A — universal ``.deferred`` guard): when an upstream
``.deferred`` marker is present in the resolved target_dir, this function
returns the module-level constant ``DEFERRED_SENTINEL = "__DEFERRED__"``
BEFORE the ``assert len(matches) == 1`` check. Every harmonize rule's
shell prelude must guard on this sentinel and emit its own ``.deferred``
output marker without invoking the harmonizer body. This single choke
point closes Loh-EUR / Loh-AFR (PENDING_D01_ACCESSION) AND any future
PENDING_* deferral path symmetrically.

Reads:
  - config/download_manifest_m1_portal.tsv (source_tag → {target_dir, filename})
  - .planning/amendments/SUMSTATS-UPGRADE.tsv (fallback for already-
    downloaded rows not on the portal manifest, e.g. GLGC + CKDGen)
  - directory convention data/raw/sumstats_v2/<Consortium><Year>/<trait>/<ancestry>/

Plan reference: m1-02a-harmonizers-continuous-traits-PLAN.md Task 2 step (A0).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

PORTAL_MANIFEST = Path("config/download_manifest_m1_portal.tsv")
UPGRADE_TSV = Path(".planning/amendments/SUMSTATS-UPGRADE.tsv")
RAW_ROOT = Path("data/raw/sumstats_v2")

# W8 fix: returned when an upstream `.deferred` marker is present in the
# resolved target_dir. Every harmonize rule's shell prelude MUST guard on
# `[ "{params.raw}" = "__DEFERRED__" ]` and emit a `.deferred` output marker
# without invoking the harmonizer body.
DEFERRED_SENTINEL = "__DEFERRED__"


def resolve_raw_for(source_tag: str, ancestry: str) -> str:
    """Return the single expected raw-file path for (source_tag, ancestry).

    Resolution order:
      0) ``.deferred`` marker present in target_dir → ``DEFERRED_SENTINEL``
         (W8 fix — option A universal guard).
      1) Portal manifest exact source_tag match.
      2) SUMSTATS-UPGRADE.tsv ``expected_filename`` + directory convention.

    Returns
    -------
    str
        Either the absolute / relative raw-file path, or
        ``DEFERRED_SENTINEL`` if a ``.deferred`` marker was found upstream.

    Raises
    ------
    AssertionError
        If zero or multiple raw files match (and no .deferred marker).
    """
    candidate_dirs: list[Path] = []

    # ---- W8 early-return: check portal manifest target_dir for .deferred ----
    if PORTAL_MANIFEST.exists():
        df = pd.read_csv(PORTAL_MANIFEST, sep="\t")
        row = df[df["source_tag"] == source_tag]
        if len(row) == 1:
            candidate_dirs.append(Path(row["target_dir"].iloc[0]))

    for cand_dir in candidate_dirs:
        if (cand_dir / ".deferred").exists():
            return DEFERRED_SENTINEL

    # ---- pass 1: exact match in portal manifest ----
    matches: list[Path] = []
    if PORTAL_MANIFEST.exists():
        df = pd.read_csv(PORTAL_MANIFEST, sep="\t")
        row = df[df["source_tag"] == source_tag]
        if len(row) == 1:
            target_dir = Path(row["target_dir"].iloc[0])
            filename = row["filename"].iloc[0]
            target = target_dir / filename
            if target.exists():
                matches.append(target)
            else:
                # Glob within target_dir for the canonical filename pattern
                # (handles `x.gz*` style globs).
                for p in target_dir.glob(filename):
                    if p.is_file():
                        matches.append(p)

    # ---- pass 2: SUMSTATS-UPGRADE.tsv fallback (GLGC, CKDGen) ----
    if not matches and UPGRADE_TSV.exists():
        tsv = pd.read_csv(UPGRADE_TSV, sep="\t")
        # Filter by ancestry if column present.
        if "ancestry" in tsv.columns:
            sub = tsv[tsv["ancestry"] == ancestry]
        else:
            sub = tsv
        for _, r in sub.iterrows():
            consortium_full = str(r.get("source_consortium", ""))
            if not consortium_full:
                continue
            consortium = consortium_full.split("-")[0]
            trait = str(r.get("trait", "")).lower()
            citation = str(r.get("citation_first_author_year", ""))
            try:
                year_token = citation.split()[-1].rstrip(")")
            except Exception:
                year_token = ""
            cand_dir = RAW_ROOT / f"{consortium}{year_token}" / trait / ancestry
            if (cand_dir / ".deferred").exists():
                return DEFERRED_SENTINEL
            expected = str(r.get("expected_filename", ""))
            if cand_dir.exists() and expected:
                for p in cand_dir.glob(expected):
                    if p.is_file():
                        matches.append(p)

    assert len(matches) == 1, (
        f"resolve_raw_for: expected exactly 1 raw file for "
        f"{source_tag}/{ancestry}, found {len(matches)}: {matches}"
    )
    return str(matches[0])


def _main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-tag", required=True)
    ap.add_argument("--ancestry", required=True)
    args = ap.parse_args()
    print(resolve_raw_for(args.source_tag, args.ancestry))


if __name__ == "__main__":
    _main()
