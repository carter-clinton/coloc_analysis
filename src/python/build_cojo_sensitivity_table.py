"""Plan 09-05 Task 1 — aggregate GCTA .jma.cojo outputs into cojo_sensitivity.tsv.

Emits one supplementary row per (signal_id, cohort) tuple in the replication
manifest; rows with a missing or unparseable .jma.cojo file carry
cojo_n_independent_signals=0 so downstream joins are total (D-04c).

Output schema (7 cols):
    signal_id, cohort, cojo_n_independent_signals,
    cojo_top_snp, cojo_joint_beta, cojo_joint_p, secondary_signal_notes

CLI:
    python build_cojo_sensitivity_table.py \
        --cojo-dir results/replication/cojo \
        --manifest data/processed/replication/manifest.tsv \
        --out results/replication/cojo_sensitivity.tsv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Union

import pandas as pd

OUTPUT_COLUMNS = [
    "signal_id",
    "cohort",
    "cojo_n_independent_signals",
    "cojo_top_snp",
    "cojo_joint_beta",
    "cojo_joint_p",
    "secondary_signal_notes",
]


def _empty_row(signal_id: str, cohort: str, note: str | None = None) -> dict:
    return {
        "signal_id": signal_id,
        "cohort": cohort,
        "cojo_n_independent_signals": 0,
        "cojo_top_snp": None,
        "cojo_joint_beta": None,
        "cojo_joint_p": None,
        "secondary_signal_notes": note,
    }


def parse_cojo_jma(
    jma_path: Union[str, Path], signal_id: str, cohort: str
) -> dict:
    """Parse a single GCTA .jma.cojo tab-separated file.

    GCTA .jma.cojo columns:
        Chr SNP bp refA freq b se p n freq_geno bJ bJ_se pJ LD_r

    Missing file or unreadable table -> row with 0 independent signals (not
    an exception; downstream expects a total join over the manifest).
    """
    jma_path = Path(jma_path)
    if not jma_path.exists():
        return _empty_row(signal_id, cohort)

    try:
        df = pd.read_csv(jma_path, sep="\t")
    except Exception as e:  # noqa: BLE001 — defensive over any parse failure
        return _empty_row(signal_id, cohort, note=f"parse_failed: {e}")

    n_indep = len(df)
    if n_indep == 0:
        return _empty_row(signal_id, cohort)

    # Row with smallest joint p (pJ) is the top signal; fall back to first
    # row if pJ is absent (unexpected for GCTA output but defensive).
    if "pJ" in df.columns and df["pJ"].notna().any():
        idx = df["pJ"].astype(float).idxmin()
        top = df.loc[idx]
    else:
        top = df.iloc[0]

    ld_r = top.get("LD_r", "NA")
    return {
        "signal_id": signal_id,
        "cohort": cohort,
        "cojo_n_independent_signals": n_indep,
        "cojo_top_snp": top.get("SNP"),
        "cojo_joint_beta": top.get("bJ"),
        "cojo_joint_p": top.get("pJ"),
        "secondary_signal_notes": f"top-SNP LD_r to lead = {ld_r}",
    }


def _region_to_filename_stub(region: str) -> str:
    """'chr10:100-300' -> 'chr10_100_300' (matches run_cojo.sh output naming)."""
    return str(region).replace(":", "_").replace("-", "_")


def build_cojo_table(
    cojo_dir: Union[str, Path],
    manifest_tsv: Union[str, Path],
    output_tsv: Union[str, Path],
) -> pd.DataFrame:
    """Walk the manifest × cojo_dir, emit cojo_sensitivity.tsv."""
    cojo_dir = Path(cojo_dir)
    manifest_tsv = Path(manifest_tsv)
    output_tsv = Path(output_tsv)

    manifest = pd.read_csv(manifest_tsv, sep="\t", dtype=str)

    rows = []
    for _, m in manifest.iterrows():
        sig = m.get("signal_id")
        coh = m.get("cohort")
        if sig is None or coh is None:
            continue
        trait = m.get("discovery_trait", m.get("trait", "trait"))
        region = m.get("region")
        if region is None:
            continue
        stub = _region_to_filename_stub(region)
        jma = cojo_dir / f"{coh}_{trait}_{stub}.jma.cojo"
        if not jma.exists():
            # Silently skip so unavailable loci (no .ma or non-complex loci)
            # do not bloat the table with empty rows. COJO is supplementary.
            continue
        rows.append(parse_cojo_jma(jma, sig, coh))

    df = pd.DataFrame(rows, columns=OUTPUT_COLUMNS) if rows else pd.DataFrame(
        columns=OUTPUT_COLUMNS
    )
    output_tsv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_tsv, sep="\t", index=False)
    return df


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--cojo-dir", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    a = _parse_args(argv)
    build_cojo_table(a.cojo_dir, a.manifest, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
