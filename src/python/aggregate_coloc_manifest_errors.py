#!/usr/bin/env python
"""aggregate_coloc_manifest_errors.py -- Track A pre-bioRxiv placeholder-fill
aggregator for placeholder PH-10c (Table 4 COLOC_ERROR breakdown) of
quick-260427-e8n.

Purpose: Join results/multitrait/coloc_manifest.tsv (44 attempted entries
  + header) with results/multitrait/coloc_summary.tsv (28 produced rows
  + header) to produce a per-trait-pair attempted-vs-empty-PP-vs-missing
  breakdown that fills Table 4 of the manuscript at L293.

Manifest entries that do not appear in coloc_summary represent attempts
that did not even reach the empty-PP outcome (failed earlier in the
pipeline -- e.g., one or both fine-mapping fits returned no credible set,
or the join failed before coloc.susie ran).

COLOC_ERROR codes are NOT recorded in the coloc_summary.tsv schema, so
columns n_insufficient_overlap, n_illconditioned_LD, n_SuSiE_nonconvergence
cannot be parsed from on-disk artifacts at this freeze. They are populated
as 0 (NA-equivalent) and the catchall n_other carries the failed count.
This is disclosed in a leading comment line on the output TSV.

Authoritative ledger: .planning/amendments/TRACK-A-FROZEN-NUMBERS.md
  Pre-bioRxiv placeholder-fill (2026-04-27) -- LIVE block (extended in W5
  with PH-10c scalars).

Outputs (relative to PROJECT_ROOT):
  results/track_a_aggregations/table4_coloc_error_breakdown.tsv

Stdout: FROZEN_BEGIN ... FROZEN_END markers for LIVE-block append.

Render env: /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python
  (Python 3.x; pandas).

Invocation (from project root):
  /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/python \\
    src/python/aggregate_coloc_manifest_errors.py

Disk-truth assertions:
  - df_summary.shape[0] == 28
  - df_manifest.shape[0] >= 28 (manifest is superset)

Author: Carter K. Clinton -- 2026-04-27 (built quick-260427-e8n W5; closes
        PH-10c of Decision-pending item 4).
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import pandas as pd

# --- Paths -------------------------------------------------------------------

PROJECT_ROOT = Path(os.getcwd()).resolve()
if not (PROJECT_ROOT / "results" / "multitrait").is_dir():
    sys.stderr.write(
        f"[agg-coloc-err] expected to be run from project root; cwd={PROJECT_ROOT}\n"
    )
    sys.exit(2)

COLOC_MANIFEST_PATH = PROJECT_ROOT / "results" / "multitrait" / "coloc_manifest.tsv"
COLOC_SUMMARY_PATH = PROJECT_ROOT / "results" / "multitrait" / "coloc_summary.tsv"
OUT_DIR = PROJECT_ROOT / "results" / "track_a_aggregations"
OUT_TABLE4 = OUT_DIR / "table4_coloc_error_breakdown.tsv"

OUT_DIR.mkdir(parents=True, exist_ok=True)

# Source-of-truth invariant md5s (W0 inventory).
COLOC_SUMMARY_MD5_EXPECTED = "5fa3c4004970c5da711d05947cb1f7d2"


def _md5(path: Path) -> str:
    h = hashlib.md5()  # noqa: S324 -- not security-sensitive; provenance only.
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# --- Load + assertions -------------------------------------------------------

df_manifest = pd.read_csv(COLOC_MANIFEST_PATH, sep="\t", dtype=str, na_filter=False)
df_summary = pd.read_csv(COLOC_SUMMARY_PATH, sep="\t", dtype=str, na_filter=False)

assert df_summary.shape[0] == 28, (
    f"Disk-truth violation: coloc_summary.tsv has {df_summary.shape[0]} rows, expected 28"
)
assert df_manifest.shape[0] >= 28, (
    f"Disk-truth violation: coloc_manifest.tsv has {df_manifest.shape[0]} rows, "
    "expected superset of coloc_summary (>=28)"
)

manifest_md5 = _md5(COLOC_MANIFEST_PATH)
summary_md5 = _md5(COLOC_SUMMARY_PATH)
assert summary_md5 == COLOC_SUMMARY_MD5_EXPECTED, (
    f"coloc_summary.tsv md5 mismatch: actual={summary_md5} expected={COLOC_SUMMARY_MD5_EXPECTED}"
)

# --- Build per-trait-pair breakdown ------------------------------------------

# Use (base_region, ancestry, trait_a, trait_b) as the join key.
key_cols = ["base_region", "ancestry", "trait_a", "trait_b"]

# Per-attempt classification.
manifest_keys = set(df_manifest.apply(lambda r: tuple(r[c] for c in key_cols), axis=1))
summary_keys = set(df_summary.apply(lambda r: tuple(r[c] for c in key_cols), axis=1))

# How many manifest attempts produced rows in summary (= 28 expected).
n_in_summary = sum(1 for k in manifest_keys if k in summary_keys)
n_no_summary_row = sum(1 for k in manifest_keys if k not in summary_keys)

# Per-trait-pair grouping (across regions/ancestries).
def _classify(row: pd.Series) -> str:
    key = tuple(row[c] for c in key_cols)
    if key in summary_keys:
        # In summary: PP.H4 always empty under disk-truth.
        return "empty_pp_h4_row"
    return "no_summary_row"


df_manifest["error_category"] = df_manifest.apply(_classify, axis=1)

# Group to (trait_a, trait_b) level.
agg = (
    df_manifest.groupby(["trait_a", "trait_b"])
    .agg(
        n_attempted=("error_category", "count"),
        n_no_summary_row=(
            "error_category",
            lambda s: int((s == "no_summary_row").sum()),
        ),
        n_empty_pp_h4=(
            "error_category",
            lambda s: int((s == "empty_pp_h4_row").sum()),
        ),
    )
    .reset_index()
)
agg["n_valid_pp_h4"] = 0  # disk-truth: all PP.H4 empty.
agg["n_failed"] = agg["n_no_summary_row"] + agg["n_empty_pp_h4"]

# Manuscript Table 4 schema:
# Trait Pair | n_attempted | n_failed | n_insufficient_overlap | n_illconditioned_LD
#   | n_SuSiE_nonconvergence | n_other
# COLOC_ERROR codes are NOT in coloc_summary schema -> n_insufficient_overlap,
# n_illconditioned_LD, n_SuSiE_nonconvergence = 0 (unattributed); n_other =
# n_failed (catchall).
table4 = pd.DataFrame(
    {
        "Trait Pair": agg.apply(lambda r: f"{r['trait_a']}–{r['trait_b']}", axis=1),
        "n_attempted": agg["n_attempted"],
        "n_failed": agg["n_failed"],
        "n_insufficient_overlap": 0,
        "n_illconditioned_LD": 0,
        "n_SuSiE_nonconvergence": 0,
        "n_other": agg["n_failed"],
    }
)

# Sort by n_attempted desc for readability.
table4 = table4.sort_values(by="n_attempted", ascending=False).reset_index(drop=True)

# Footer TOTAL row.
total_row = pd.DataFrame(
    [
        {
            "Trait Pair": "TOTAL",
            "n_attempted": int(table4["n_attempted"].sum()),
            "n_failed": int(table4["n_failed"].sum()),
            "n_insufficient_overlap": int(table4["n_insufficient_overlap"].sum()),
            "n_illconditioned_LD": int(table4["n_illconditioned_LD"].sum()),
            "n_SuSiE_nonconvergence": int(table4["n_SuSiE_nonconvergence"].sum()),
            "n_other": int(table4["n_other"].sum()),
        }
    ]
)
table4_with_total = pd.concat([table4, total_row], ignore_index=True)

# --- Write output -------------------------------------------------------------

header_comment = (
    "# COLOC_ERROR codes are not present in coloc_summary.tsv schema; columns "
    "n_insufficient_overlap / n_illconditioned_LD / n_SuSiE_nonconvergence are "
    "populated as 0 (unattributed; counted under n_other) where the underlying "
    "error code cannot be parsed from on-disk artifacts. n_failed = total "
    "failures (attempts not reaching valid PP.H4) = n_no_summary_row + "
    "n_empty_pp_h4. Source: results/multitrait/coloc_manifest.tsv md5 "
    f"{manifest_md5}; results/multitrait/coloc_summary.tsv md5 {summary_md5}."
)

with open(OUT_TABLE4, "w", encoding="utf-8") as fh:
    fh.write(header_comment + "\n")
    table4_with_total.to_csv(fh, sep="\t", index=False)

sys.stderr.write(
    f"[agg-coloc-err] wrote {OUT_TABLE4} ({len(table4)} trait-pair rows + 1 TOTAL)\n"
)

# --- Locked scalars (emit to stdout for FROZEN-NUMBERS) ----------------------

print("FROZEN_BEGIN")
print(f"table4_total_attempted\t{int(table4['n_attempted'].sum())}")
print(f"table4_total_with_summary_row\t{n_in_summary}")
print(f"table4_total_with_valid_pp_h4\t0")
print(f"table4_total_no_summary_row\t{n_no_summary_row}")
print(f"table4_unique_trait_pairs\t{len(table4)}")
print("FROZEN_END")

sys.stderr.write("[agg-coloc-err] done.\n")
