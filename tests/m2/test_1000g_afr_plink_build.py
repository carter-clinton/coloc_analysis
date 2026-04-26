"""1000G AFR PLINK bfile build smoke tests (Pitfall 3).

22 chr {.bed, .bim, .fam} triples must exist at
data/reference/ldsc/1000G_AFR_Phase3_plink/. .bim line count > 100k SNPs
after MAF/HWE filters.

Wave 0 Task 4 fires src/snakemake/rules/m2_reference.smk to build these.
"""
from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PLINK_DIR = PROJECT_ROOT / "data" / "reference" / "ldsc" / "1000G_AFR_Phase3_plink"


pytestmark = pytest.mark.skipif(
    not PLINK_DIR.exists(),
    reason="data/reference/ldsc/1000G_AFR_Phase3_plink/ not yet built (Wave 0 Task 4 fire)",
)


def test_22_bed_files_exist():
    """22 .bed files (autosomes 1..22) must exist."""
    beds = sorted(PLINK_DIR.glob("1000G.AFR.QC.*.bed"))
    chrs = sorted({p.stem.split(".")[-1] for p in beds})
    assert len(chrs) == 22, f"expected 22 .bed; got {len(chrs)}: {chrs}"
    expected = {str(c) for c in range(1, 23)}
    assert set(chrs) == expected, f"missing: {expected - set(chrs)}"


def test_chr22_bim_has_min_snps():
    """Chr 22 .bim must have ≥ 100k SNPs after QC filters (smallest autosome)."""
    bim = PLINK_DIR / "1000G.AFR.QC.22.bim"
    if not bim.exists():
        pytest.skip("chr22 .bim absent — fire not complete")
    with open(bim) as fh:
        n = sum(1 for _ in fh)
    assert n >= 100_000, f"chr22 has only {n} SNPs (expected ≥100k after QC)"
