"""Plan 09-05 Task 2 — cross-ancestry generalization panel (D-05c).

BBJ-EAS is reported as a **generalization** cohort, NOT a replication cohort:
EAS is ancestry-distinct from the EUR + AFR discovery panels, so coloc /
effect-size agreement with BBJ speaks to cross-ancestry transferability
rather than within-ancestry replication.

Per D-05c, only Tier A+B gene-tissue-trait triples enter this panel —
credible-set SNP rows are excluded because within-ancestry LD structure is
the primary determinant of credible-set membership, making the SNP-level
generalization question ill-posed.

Output columns:
    <all manifest columns>, <all BBJ per-cohort columns>,
    is_generalization (always True), framing_note
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Union

import pandas as pd

GENERALIZATION_NOTE = (
    "Cross-ancestry generalization evidence, NOT independent replication "
    "(D-05c). BBJ-EAS is ancestry-distinct from EUR/AFR discovery panels."
)


def build_bbj_generalization(
    manifest_tsv: Union[str, Path],
    bbj_cohort_tsv: Union[str, Path],
    output_tsv: Union[str, Path],
) -> pd.DataFrame:
    """Assemble the Tier A+B × BBJ-EAS cross-ancestry panel."""
    manifest_tsv = Path(manifest_tsv)
    bbj_cohort_tsv = Path(bbj_cohort_tsv)
    output_tsv = Path(output_tsv)

    manifest = pd.read_csv(manifest_tsv, sep="\t")

    # D-05c enforcement: Tier A+B only, BBJ cohort only.
    if "signal_class" in manifest.columns:
        tier_ab = manifest[manifest["signal_class"].isin(
            ["tier_A_triple", "tier_B_triple"]
        )].copy()
    else:
        tier_ab = manifest.copy()

    if "cohort" in tier_ab.columns:
        tier_ab_bbj = tier_ab[tier_ab["cohort"] == "bbj"].copy()
    else:
        tier_ab_bbj = tier_ab.copy()

    # Belt-and-braces: assert no credible_set_SNP leak.
    if "signal_class" in tier_ab_bbj.columns:
        assert (tier_ab_bbj["signal_class"] != "credible_set_SNP").all(), (
            "D-05c violation: BBJ generalization panel must exclude credible_set_SNP"
        )

    # Merge BBJ effect-size if available.
    if bbj_cohort_tsv.exists() and bbj_cohort_tsv.stat().st_size > 0:
        bbj = pd.read_csv(bbj_cohort_tsv, sep="\t")
        out = tier_ab_bbj.merge(
            bbj, on="signal_id", how="left", suffixes=("", "_bbj")
        )
    else:
        out = tier_ab_bbj

    out["is_generalization"] = True
    out["framing_note"] = GENERALIZATION_NOTE

    output_tsv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_tsv, sep="\t", index=False)
    return out


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--manifest", required=True)
    p.add_argument("--bbj-cohort", required=True)
    p.add_argument("--out", required=True)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    a = _parse_args(argv)
    build_bbj_generalization(a.manifest, a.bbj_cohort, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
