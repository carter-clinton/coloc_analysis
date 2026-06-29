"""plink_ld_to_npz.py -- m3-02e Move 1: convert a NATIVE plink1.9 per-region LD
output into the SAME egress-clean .npz contract that ld_npz_to_rds.R already
ingests (keys: ld, variant_ids, rsids, allele_freq, lower_triangular).

This is the native-plink sibling of bm_to_npz.py (the retired Hail BlockMatrix
A.3 path). The m3-W2 PILOT (2026-06-24, GREEN) measured native plink1.9 at
~25-56 min/region on a single n2-standard-16 vs ~24 cluster-h for the same cell
on the 24-node Hail path -- so the AFR LD panel is built with native plink, not
Hail. This reader runs on the in-perimeter Spot VM (or NCSU after egress); it
deliberately does NOT import hail (it has nothing to do with the cohort MT).

Two plink LD output modes (D-02e-01: square bin4 is the default):

  SQUARE  ``plink1.9 --r square bin4``  ->  ``{prefix}.ld.bin``
    Raw little-endian float32, numpy shape (n_var, n_var), diag = 1.0, symmetric
    (the PILOT verified sym_check = 0.0). The FULL matrix -> lower_triangular=False.

  BANDED  ``plink1.9 --r gz``           ->  ``{prefix}.ld.gz``
    Text columns ``CHR_A BP_A SNP_A CHR_B BP_B SNP_B R``; signed R in [-1, 1] for
    in-band pairs only. Scattered into ONE lower triangle (i >= j) + diag = 1.0
    -> lower_triangular=True. ld_npz_to_rds.R reconstructs symmetry via
    ``tri + t(tri) - diag(diag(tri))``.

THE TRIANGLE-FLAG CONTRACT IS AUTHORITATIVE (feedback_npz_triangle_flag_contract):
square -> lower_triangular=False (already-full; the R loader only symmetrizes);
banded -> lower_triangular=True (one-sided; the R loader mirrors the triangle).
Flipping either silently halves (BR-01) or doubles (CR-01) every off-diagonal.

Variant order comes from the cohort ``.bim`` (plink writes LD rows/cols in .bim
row order). With ``--keep-allele-order`` the .bim A1/A2 keep the GWAS allele
order. CANONICAL VID (W-3): hl.export_plink writes A1 = ALT = ``alleles[1]`` and
A2 = REF = ``alleles[0]``; the .bim columns are ``[chr, rsid, cm, bp, A1, A2]``.
The project canonical variant id is ``chr:pos:REF:ALT`` (aou_ld_panel.py:2504 =
``str(locus)+":"+alleles[0]+":"+alleles[1]``), so the reconstructed vid is
``{chr}:{bp}:{A2}:{A1}`` (REF=A2, ALT=A1) -- NOT ``{chr}:{bp}:{A1}:{A2}``.
Swapping REF/ALT silently misaligns every variant id against the .npz the Hail
AFR path would have produced.

EGRESS (REQ-AOU-LD-EGRESS): this reader operates on the aggregate per-region LD
matrix + AF only; it never touches individual-level genotypes. The plink cohort
``.bed`` stays in-perimeter (it is individual-level) and is consumed only by the
in-perimeter plink LD loop; only the LD .npz + AF crosses egress.

Usage:
    python src/python/plink_ld_to_npz.py \
        --mode        square \
        --ld          region.ld.bin \
        --bim         cohort.bim \
        --allele-freq region.afreq \
        --out-npz     data/interim/aou_ld_exports/AFR_aou/m2_region_00040__sub00.npz \
        --region-id   m2_region_00040__sub00 \
        --n-var       64060
"""
from __future__ import annotations

import argparse
import gzip
import sys
from pathlib import Path

import numpy as np


# --------------------------------------------------------------------------- #
# AF sidecar (mirror bm_to_npz._load_af_sidecar: blank line -> NaN, never 0.0) #
# --------------------------------------------------------------------------- #

def _load_af_sidecar(path: Path) -> np.ndarray:
    """One-float-per-line AF sidecar -> 1-D float array; a BLANK line -> NaN.

    Mirrors bm_to_npz._load_af_sidecar (AF-SIDECAR-01 / WR-03): for a
    MAF>=0.005-prefiltered cohort a true 0.0 is impossible, so a missing AF must
    round-trip to np.nan (NOT a fake 0.0 that would mask a collection fault).
    """
    if not path.is_file():
        raise FileNotFoundError(f"allele_freq sidecar missing: {path}")
    values: list[float] = []
    for line in path.read_text().splitlines():
        token = line.strip()
        values.append(float("nan") if not token else float(token))
    return np.asarray(values, dtype=float)


# --------------------------------------------------------------------------- #
# .bim parsing + canonical vid reconstruction                                 #
# --------------------------------------------------------------------------- #

def _read_bim_rows(bim_path: Path) -> list[list[str]]:
    if not Path(bim_path).is_file():
        raise FileNotFoundError(f".bim missing: {bim_path}")
    rows: list[list[str]] = []
    for line in Path(bim_path).read_text().splitlines():
        if not line.strip():
            continue
        # .bim is whitespace-delimited (tab or space): chr snp cm bp A1 A2
        parts = line.split()
        if len(parts) < 6:
            raise ValueError(
                f"malformed .bim row (need 6 cols chr/snp/cm/bp/A1/A2): {line!r}"
            )
        rows.append(parts[:6])
    return rows


def load_bim(bim_path: "str | Path") -> tuple[list[str], list[str]]:
    """Parse the 6-col plink .bim -> (variant_ids, rsids) in .bim row order.

    .bim columns: [chr, snp_id, cm, bp, A1, A2]. Under hl.export_plink,
    A1 = ALT = alleles[1] and A2 = REF = alleles[0]. The canonical project vid
    is chr:pos:REF:ALT = ``{chr}:{bp}:{A2}:{A1}`` (W-3). rsids = the snp_id col
    ('.' -> '' for a variant without an rsid). Row order == LD row/col order.
    """
    variant_ids: list[str] = []
    rsids: list[str] = []
    for chrom, snp_id, _cm, bp, a1, a2 in _read_bim_rows(Path(bim_path)):
        # REF = A2 = alleles[0]; ALT = A1 = alleles[1]  ->  chr:pos:REF:ALT
        variant_ids.append(f"{chrom}:{bp}:{a2}:{a1}")
        rsids.append("" if snp_id == "." else snp_id)
    return variant_ids, rsids


def _bim_snp_index(bim_path: Path) -> dict[str, int]:
    """Map the plink SNP id (.bim col 2) -> 0-based row index (banded scatter)."""
    return {row[1]: i for i, row in enumerate(_read_bim_rows(Path(bim_path)))}


def _bim_bp_index(bim_path: Path) -> dict[str, int]:
    """Map ``{chr}:{bp}`` -> 0-based row index (banded BP fallback)."""
    return {f"{row[0]}:{row[3]}": i for i, row in enumerate(_read_bim_rows(Path(bim_path)))}


# --------------------------------------------------------------------------- #
# LD readers                                                                   #
# --------------------------------------------------------------------------- #

def _is_symmetric_blocked(m: np.ndarray, atol: float, block: int = 1024) -> bool:
    """Memory-lean symmetry check. ``np.allclose(m, m.T)`` builds several full
    n_var**2 float32 temporaries (~39 GiB each at n_var≈1e5) on top of the matrix
    and OOM-kills a 64 GB VM (m3-02e-T4, region 1). Compare ``block`` rows at a
    time against the matching transposed column block so the transient is bounded
    by ``block * n_var * 4`` bytes (≈420 MB at block=1024, n_var≈1e5)."""
    n = m.shape[0]
    for i in range(0, n, block):
        a = m[i:i + block, :]          # row block (view, b×n)
        b = m[:, i:i + block].T        # transposed col block (b×n)
        if not np.allclose(a, b, atol=atol):
            return False
    return True


def _strict_upper_is_zero_blocked(m, block=1024):
    """Memory-lean 'strict upper triangle is all zero' check (banded-npz gate).
    Equivalent to ``np.allclose(np.triu(m, k=1), 0.0)`` but bounded. The plain
    ``np.triu(m, k=1)`` materializes a FULL n_var**2 float32 copy (~39 GiB at
    n_var≈1e5) — the SAME OOM class as the un-blocked symmetry check
    (_is_symmetric_blocked). Do it block-wise so the transient is bounded by
    ~``block * n_var`` entries: for a row block starting at global row ``i``,
    ``np.triu(block, k=i+1)`` selects exactly the strict-upper entries
    (global column > global row)."""
    n = m.shape[0]
    for i in range(0, n, block):
        if not np.allclose(np.triu(m[i:i + block, :], k=i + 1), 0.0):
            return False
    return True


def read_square_bin(ld_bin_path: "str | Path", n_var: int) -> np.ndarray:
    """Read a plink ``--r square bin4`` ``.ld.bin`` -> dense (n_var, n_var) float32.

    Raw little-endian float32; numpy ``reshape(n_var, n_var)``. Verifies the
    PILOT-observed invariants: square shape, unit diagonal, symmetric (the
    pilot's sym_check = 0.0). Returns the FULL matrix (lower_triangular=False).
    """
    arr = np.fromfile(str(ld_bin_path), dtype="<f4")
    if arr.size != n_var * n_var:
        raise ValueError(
            f"square .ld.bin {ld_bin_path} has {arr.size} float32 values, "
            f"expected n_var**2 = {n_var * n_var} (n_var={n_var}). "
            f"Check --n-var matches the cohort .bim row count for this region."
        )
    m = arr.reshape(n_var, n_var).astype("float32", copy=False)
    if not np.allclose(np.diag(m), 1.0, atol=1e-3):
        raise ValueError(
            f"square LD diagonal is not ~1.0 for {ld_bin_path}; "
            f"plink --r square should write self-correlation 1.0 on the diagonal."
        )
    if not _is_symmetric_blocked(m, atol=1e-4):
        raise ValueError(
            f"square LD is not symmetric for {ld_bin_path} "
            f"(plink --r square is symmetric; the PILOT measured sym_check=0.0)."
        )
    return m


def read_banded_gz(ld_gz_path: "str | Path", bim_path: "str | Path",
                   n_var: int) -> np.ndarray:
    """Read a plink ``--r gz`` ``.ld.gz`` -> one lower-triangle (n_var, n_var) float32.

    Columns: ``CHR_A BP_A SNP_A CHR_B BP_B SNP_B R``. Each in-band pair's signed R
    is scattered into the LOWER triangle (i >= j); the diagonal is set to 1.0.
    SNP ids map to .bim rows (BP fallback when a SNP id is absent). Off-band
    entries stay 0. Returns the one-sided triangle (lower_triangular=True).
    """
    snp_idx = _bim_snp_index(Path(bim_path))
    bp_idx = _bim_bp_index(Path(bim_path))
    tri = np.zeros((n_var, n_var), dtype="float32")
    np.fill_diagonal(tri, 1.0)

    with gzip.open(str(ld_gz_path), "rt") as fh:
        header = fh.readline()  # CHR_A BP_A SNP_A CHR_B BP_B SNP_B R
        if header and "SNP_A" not in header and "BP_A" not in header:
            # No header (rare) -> rewind by re-processing this line as data.
            lines = [header] + fh.readlines()
        else:
            lines = fh.readlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            cols = line.split()
            if len(cols) < 7:
                continue
            chr_a, bp_a, snp_a, chr_b, bp_b, snp_b, r = cols[:7]
            ia = snp_idx.get(snp_a, bp_idx.get(f"{chr_a}:{bp_a}"))
            ib = snp_idx.get(snp_b, bp_idx.get(f"{chr_b}:{bp_b}"))
            if ia is None or ib is None:
                raise ValueError(
                    f"banded pair ({snp_a},{snp_b}) not found in .bim {bim_path}; "
                    f"the .ld.gz and the .bim must come from the same plink run."
                )
            lo, hi = (ia, ib) if ia <= ib else (ib, ia)
            tri[hi, lo] = np.float32(r)  # lower triangle: row >= col
    return tri


# --------------------------------------------------------------------------- #
# Top-level converter                                                          #
# --------------------------------------------------------------------------- #

def plink_ld_to_npz(*, mode: str, ld_path: "str | Path", bim_path: "str | Path",
                    af_sidecar_path: "str | Path | None", out_npz: "str | Path",
                    region_id: str, n_var: int | None = None) -> str:
    """Convert a native plink LD output -> the egress-clean .npz contract.

    Writes EXACTLY the aou_ld_panel._save_npz / bm_to_npz key set
    (ld, variant_ids, rsids, allele_freq, lower_triangular) so ld_npz_to_rds.R
    needs NO change. ``mode='square'`` -> lower_triangular=False (full matrix);
    ``mode='banded'`` -> lower_triangular=True (one materialized triangle).
    """
    if mode not in ("square", "banded"):
        raise ValueError(f"mode must be 'square' or 'banded', got {mode!r}")

    variant_ids, rsids = load_bim(bim_path)
    n = len(variant_ids)
    if n_var is None:
        n_var = n
    if n_var != n:
        raise ValueError(
            f"n_var={n_var} != .bim row count {n} for region {region_id!r}; "
            f"the LD matrix order is the .bim order — they must match."
        )

    if mode == "square":
        ld = read_square_bin(ld_path, n_var)
        lower_triangular = False
    else:
        ld = read_banded_gz(ld_path, bim_path, n_var)
        lower_triangular = True

    ld = ld.astype("float32", copy=False)

    # AF sidecar: provided -> floats (blank -> NaN); omitted -> all-NaN + WARNING
    # (mirror bm_to_npz: never silently ship a wrong/zero AF; absence is auditable).
    if af_sidecar_path is not None:
        allele_freq = _load_af_sidecar(Path(af_sidecar_path))
        if allele_freq.shape[0] != n_var:
            raise ValueError(
                f"allele_freq length {allele_freq.shape[0]} != n_var {n_var} "
                f"(sidecar {af_sidecar_path}); AF must be row-aligned to the .bim "
                f"variant order for region {region_id!r}."
            )
    else:
        allele_freq = np.full(n_var, np.nan, dtype=float)
        print(
            f"WARNING: no --allele-freq sidecar for region {region_id!r}; writing "
            f"all-NaN AF. Supply the per-region .afreq sidecar to carry allele "
            f"frequencies into obj$variants$AF."
        )
    allele_freq = allele_freq.astype("float32")

    out_npz = Path(out_npz)
    out_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        str(out_npz),
        ld=ld,
        variant_ids=np.array(variant_ids),
        rsids=np.array(rsids),
        allele_freq=allele_freq,
        lower_triangular=np.array([lower_triangular]),
    )
    print(
        f"WROTE {out_npz} (mode={mode}, {n_var} x {n_var}, "
        f"lower_triangular={lower_triangular})"
    )
    return str(out_npz)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Native plink1.9 LD (square .ld.bin / banded .ld.gz) -> egress-clean .npz"
    )
    p.add_argument("--mode", choices=["square", "banded"], default="square",
                   help="LD output mode (D-02e-01 default: square bin4)")
    p.add_argument("--ld", dest="ld_path", required=True, type=Path,
                   help="plink LD output (.ld.bin for square, .ld.gz for banded)")
    p.add_argument("--bim", dest="bim_path", required=True, type=Path,
                   help="cohort .bim (variant order; --keep-allele-order kept A1/A2)")
    p.add_argument("--allele-freq", dest="af_sidecar_path", type=Path, default=None,
                   help="Optional per-region AF sidecar (one float/line, .bim row order)")
    p.add_argument("--out-npz", dest="out_npz", required=True, type=Path)
    p.add_argument("--region-id", dest="region_id", required=True)
    p.add_argument("--n-var", dest="n_var", type=int, default=None,
                   help="Variant count (required for square reshape; defaults to .bim rows)")
    args = p.parse_args(argv)

    plink_ld_to_npz(
        mode=args.mode, ld_path=args.ld_path, bim_path=args.bim_path,
        af_sidecar_path=args.af_sidecar_path, out_npz=args.out_npz,
        region_id=args.region_id, n_var=args.n_var,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
