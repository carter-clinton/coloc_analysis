#!/usr/bin/env python3
"""GBMI TSV -> per-ancestry canonical harmonized sumstats (Plan 09-02 Task 3).

GBMI publishes one file per trait with all-ancestry meta columns plus
per-ancestry columns. This harmonizer extracts a specific ancestry stratum
(eur / afr / eas / amr / sas) and renames to the canonical 10-column
schema.

Note: GBMI v1 flagship releases are GRCh37 — no liftover step. Palindromic
ambiguity filter still applied (RESEARCH pitfall #2).

B-2 guard (plan-check revision): when the caller requests an ancestry
whose per-ancestry columns are absent, fail loudly with a message that
names the missing prefix and lists the observed columns. This prevents
silent empty-output downstream breakage of the D-05b AFR replication
panel when a GBMI file turns out to be EUR-only.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import sumstats_utils as _su  # noqa: E402

CANONICAL_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]

# Per-ancestry column prefix (per GBMI schema, verified against the public
# portal data dictionary). EUR is served via the pan-ancestry `all_meta_*`
# columns because GBMI is EUR-dominated and has no separate `eur_meta_*`
# block in the current flagship releases.
ANCESTRY_PREFIX_MAP = {
    "eur": "all_meta",
    "afr": "afr_meta",
    "eas": "eas_meta",
    "amr": "amr_meta",
    "sas": "sas_meta",
}


def harmonize_gbmi_sumstats(
    input_gz: Path,
    output_prefix: Path,
    trait: str,
    ancestry: str = "eur",
    liftover_chain: "Path | None" = None,
) -> dict:
    """Extract a single-ancestry stratum from a GBMI trait file.

    Parameters
    ----------
    input_gz : Path
        GBMI per-trait tsv.gz.
    output_prefix : Path
        Output path prefix. The harmonized file is written to
        ``{output_prefix}_{ancestry}.tsv.gz``.
    trait : str
        Phase-9 trait label.
    ancestry : str
        One of the five keys of :data:`ANCESTRY_PREFIX_MAP`.
    liftover_chain : Path or None
        If provided, lift coordinates b38 -> b37 using this UCSC chain.
        For the 2022 GBMI asthma release (M1; see DEC-2026-04-24-01).
        The basename must contain "hg38ToHg19" (RESEARCH Pitfall #7
        guard against silent wrong-direction lift). When ``None``,
        Phase 09 behavior is preserved (no liftover; GBMI 2020-2021
        flagship releases are already GRCh37).

    Returns
    -------
    dict
        QC summary: ``cohort``, ``trait``, ``ancestry``, ``n_rows``,
        ``output`` (path string), and (when liftover invoked)
        ``n_liftover_input``, ``n_liftover_lifted``, ``n_liftover_dropped``,
        ``liftover_drop_rate``.

    Raises
    ------
    ValueError
        If ``ancestry`` is not one of the five supported strata, or if the
        input file is missing the expected per-ancestry columns, or if
        ``liftover_chain`` is set but its basename lacks "hg38ToHg19"
        (Pitfall #7 guard).
    """
    if ancestry not in ANCESTRY_PREFIX_MAP:
        raise ValueError(
            f"GBMI ancestry '{ancestry}' not in {sorted(ANCESTRY_PREFIX_MAP)}"
        )
    prefix = ANCESTRY_PREFIX_MAP[ancestry]

    df = pd.read_csv(input_gz, sep="\t", compression="infer", low_memory=False)

    col_map = {
        "CHR": "CHR",
        "POS": "BP",
        "rsid": "SNP",
        "REF": "OA",
        "ALT": "EA",
        f"{prefix}_beta": "BETA",
        f"{prefix}_sebeta": "SE",
        f"{prefix}_pval": "P",
        f"{prefix}_AF": "EAF",
        f"{prefix}_sample_N": "N",
    }

    # B-2 guard: fail loudly if the expected per-ancestry prefix is absent.
    missing = [src for src in col_map if src not in df.columns]
    if missing:
        raise ValueError(
            f"GBMI harmonizer: ancestry='{ancestry}' (prefix='{prefix}') "
            f"expected columns {sorted(col_map.keys())} but file is "
            f"missing {missing}. Found columns: "
            f"{sorted(df.columns.tolist())}. Check GBMI portal schema — "
            f"per-ancestry prefix may have changed, or this file is an "
            f"EUR-only release. Fix either ANCESTRY_PREFIX_MAP or the "
            f"input file."
        )

    df = df[list(col_map.keys())].rename(columns=col_map)
    df = df[CANONICAL_COLS]

    # GBMI flagship releases 2020-2021 are GRCh37; M1 2022 release is
    # GRCh38 and requires --liftover-chain per DEC-2026-04-24-01.
    # See RESEARCH Pitfall #4.
    qc_lift: dict = {}
    if liftover_chain is not None:
        chain_path = Path(liftover_chain)
        if "hg38ToHg19" not in chain_path.name:
            raise ValueError(
                f"--liftover-chain expects hg38ToHg19 chain; got "
                f"'{chain_path.name}'. Use "
                f"data/external/liftover/hg38ToHg19.over.chain.gz. "
                f"Guards against Pitfall #7 silent wrong-direction lift."
            )
        df, qc_lift = _su.liftover_to_grch37(
            df, chain_file=str(chain_path),
            chr_col="CHR", bp_col="BP", max_drop_rate=0.05,
        )
        print(f"[gbmi] liftover b38->b37 qc: {qc_lift}", file=sys.stderr)
        # Re-coerce CHR to str post-liftover.
        df["CHR"] = df["CHR"].astype(str)

    df = _su.filter_palindromic_ambiguous(df)

    output_prefix = Path(output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    out = output_prefix.parent / f"{output_prefix.name}_{ancestry}.tsv.gz"
    df.to_csv(out, sep="\t", index=False, compression="gzip")

    qc = {
        "cohort": f"gbmi_{ancestry}",
        "trait": trait,
        "ancestry": ancestry,
        "n_rows": int(len(df)),
        "output": str(out),
    }
    if qc_lift:
        qc["n_liftover_input"] = qc_lift.get("n_input")
        qc["n_liftover_lifted"] = qc_lift.get("n_lifted")
        qc["n_liftover_dropped"] = qc_lift.get("n_dropped")
        qc["liftover_drop_rate"] = qc_lift.get("drop_rate")
    return qc


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output-prefix", required=True)
    ap.add_argument("--trait", required=True)
    ap.add_argument(
        "--ancestry",
        required=True,
        choices=sorted(ANCESTRY_PREFIX_MAP),
    )
    ap.add_argument(
        "--liftover-chain", type=Path, default=None,
        help=(
            "If set, lift coordinates b38 -> b37 using this chain. "
            "For the 2022 GBMI asthma release. Path basename must "
            "contain 'hg38ToHg19' (Pitfall #7 guard)."
        ),
    )
    args = ap.parse_args()
    harmonize_gbmi_sumstats(
        Path(args.input),
        Path(args.output_prefix),
        args.trait,
        args.ancestry,
        liftover_chain=args.liftover_chain,
    )


if __name__ == "__main__":
    _main()
