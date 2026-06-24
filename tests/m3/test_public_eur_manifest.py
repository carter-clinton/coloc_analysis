"""Tests for m3-02e Task 2: public EUR LD ($0 compute).

build_public_eur_manifest.py maps each M2 EUR region (config/ld_regions.tsv) to
the overlapping public UKBB 337k tile(s) (Weissbrod/PolyFun PRIMARY; Pan-UKBB
420k documented alternate) with an hg19<->hg38 coordinate adapter, and emits the
per-region extract jobs consumed by m3_public_eur_ld.smk. The public panel is
hg19/GRCh37; the AFR panel is hg38; both reconcile through the GRCh37 analytic
plane (DEC-2026-04-24-01).

Runs in smoke_dev py3.11 (pandas + numpy + scipy). No S3 hit in CI (synthetic
tiles); no Hail.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
_SRC_SCRIPTS = PROJECT_ROOT / "src" / "snakemake" / "scripts"
for p in (_SRC_PYTHON, _SRC_SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import build_public_eur_manifest as bpem  # noqa: E402
from download_ukbb_ld_tiles import Tile  # noqa: E402

LD_REGIONS = PROJECT_ROOT / "config" / "ld_regions.tsv"


def _tile(chrom, start, end) -> Tile:
    return Tile(chrom=str(chrom), start=start, end=end,
                npz_key=f"UKBB_LD/chr{chrom}_{start}_{end}.npz")


# --------------------------------------------------------------------------- #

def test_eur_region_to_tile_mapping():
    # three contiguous 3Mb tiles on chr16
    tiles = [_tile(16, 1, 3_000_001),
             _tile(16, 3_000_001, 6_000_001),
             _tile(16, 6_000_001, 9_000_001)]
    # a region fully inside tile 2 -> one tile
    one = bpem.map_region_to_tiles(chrom="16", start=4_000_000, end=5_000_000, tiles=tiles)
    assert len(one) == 1
    # a region spanning tile 2 + tile 3 -> two tiles
    two = bpem.map_region_to_tiles(chrom="16", start=5_500_000, end=6_500_000, tiles=tiles)
    assert len(two) == 2


def test_primary_is_weissbrod_337k():
    assert "Weissbrod" in bpem.EUR_PUBLIC_PRIMARY["panel"]
    assert bpem.EUR_PUBLIC_PRIMARY["source"] == "EUR_ukbb_pub"
    assert bpem.EUR_PUBLIC_PRIMARY["bucket"] == "broad-alkesgroup-ukbb-ld"
    assert bpem.EUR_PUBLIC_PRIMARY["build"] in ("hg19", "GRCh37")
    assert int(bpem.EUR_PUBLIC_PRIMARY["n"]) >= 337000
    # Pan-UKBB 420k is a DOCUMENTED ALTERNATE (not the default)
    alts = bpem.EUR_PUBLIC_ALTERNATES
    assert any("Pan-UKBB" in a["panel"] or "pan-ukb" in a.get("uri", "") for a in alts)
    assert any(int(a["n"]) >= 420000 for a in alts)


def test_hg19_hg38_coordinate_adapter():
    # FTO 16q12-ish anchor: distinct hg19 vs hg38 windows in a synthetic row.
    row = {
        "region_id": "m2_region_fto", "chr": "16", "ancestry": "EUR",
        "start_grch37": 53_700_000, "end_grch37": 54_200_000,
        "start_grch38": 53_666_000, "end_grch38": 54_166_000,
    }
    hg19 = bpem.region_hg19_window(row)
    hg38 = bpem.region_hg38_window(row)
    # the adapter maps the public-panel (hg19) window to the grch37 coords
    assert hg19 == ("16", 53_700_000, 54_200_000)
    # and does NOT silently treat hg19 panel coords as hg38 (the two differ)
    assert hg38 == ("16", 53_666_000, 54_166_000)
    assert hg19 != hg38
    # the explicit liftover helper rejects an unknown direction (no silent build mix)
    with pytest.raises((ValueError, KeyError)):
        bpem.liftover_coordinate("16", 53_700_000, direction="hg19_to_hg99")


def test_emitted_extract_jobs_cover_all_eur_regions():
    regions = bpem.read_eur_regions(LD_REGIONS)
    assert len(regions) > 0
    # one big synthetic tile per EUR chrom -> guaranteed coverage in CI (no S3)
    tiles_by_chrom = {}
    for chrom in regions["chr"].astype(str).unique():
        sub = regions[regions["chr"].astype(str) == chrom]
        hi = int(sub[["end_grch37"]].max().iloc[0]) + 10
        tiles_by_chrom[chrom] = [_tile(chrom, 1, hi)]
    jobs = bpem.build_jobs(regions, tiles_by_chrom=tiles_by_chrom)
    covered = {j["region_id"] for j in jobs}
    assert covered == set(regions["region_id"])
    j0 = jobs[0]
    for key in ("region_id", "region_safe", "chr", "start", "end", "tile_keys", "source"):
        assert key in j0
    assert j0["source"] == "EUR_ukbb_pub"
    assert len(j0["tile_keys"]) >= 1


def test_public_panel_rds_real_round_trip(tmp_path):
    """W-4: build a synthetic public-panel tile (hg19) slice, run the extractor,
    and assert on the REAL produced artifact — never a pure-doc no-op.

    pyreadr is absent in smoke_dev, so ukbb_ld_tile_to_region_rds writes the
    .npz fallback + .meta.json; we assert the LD is a square symmetric matrix,
    dimnames-count == n_variants, and the build provenance (Weissbrod = hg19) is
    recorded. When pyreadr/R IS present the real .rds is produced and read back.
    """
    import gzip
    import scipy.sparse

    sys.path.insert(0, str(_SRC_SCRIPTS))
    import ukbb_ld_tile_to_region_rds as extractor

    n = 12
    rng = np.random.default_rng(0)
    a = rng.standard_normal((n, n)).astype("float32")
    R = ((a + a.T) / 2.0).astype("float32")
    np.fill_diagonal(R, 1.0)
    tile_npz = tmp_path / "chr16_53000001_56000001.npz"
    scipy.sparse.save_npz(str(tile_npz), scipy.sparse.coo_matrix(R))

    # hg19 variant TSV: rsid, chromosome, position, allele1, allele2
    positions = [53_700_000 + i * 1000 for i in range(n)]
    var_df = pd.DataFrame({
        "rsid": [f"rs{i}" for i in range(n)],
        "chromosome": [16] * n,
        "position": positions,
        "allele1": ["A"] * n,
        "allele2": ["G"] * n,
    })
    tile_var = tmp_path / "chr16_53000001_56000001.gz"
    with gzip.open(tile_var, "wt") as fh:
        var_df.to_csv(fh, sep="\t", index=False)

    out_dir = tmp_path / "EUR_ukbb_pub"
    rc = extractor.main([
        "--tile-npz", str(tile_npz), "--tile-var", str(tile_var),
        "--region-id", "m2_region_fto", "--chrom", "16",
        "--start", "53700000", "--end", "53705000",  # first 6 variants
        "--out-dir", str(out_dir),
    ])
    assert rc == 0

    meta = json.loads((out_dir / "m2_region_fto.meta.json").read_text())
    n_var = meta["n_variants"]
    assert n_var == 6  # the 6 in-window variants
    assert "Weissbrod" in meta["source_paper"]  # hg19 public-panel provenance

    # assert on the REAL LD payload (pyreadr -> real .rds; else .npz fallback)
    rds = out_dir / "m2_region_fto.rds"
    if rds.exists() and rds.read_bytes()[:15] != b"PYREADR_MISSING":
        import pyreadr  # noqa: F401  (only when present)
        obj = pyreadr.read_r(str(rds))
        mat = obj["R"].to_numpy().astype("float32")
    else:
        fallback = out_dir / "m2_region_fto.npz"
        z = np.load(fallback, allow_pickle=True)
        mat = np.asarray(z["R"], dtype="float32")
    assert mat.shape == (n_var, n_var)            # dimnames-count == n_var
    assert np.allclose(mat, mat.T, atol=1e-5)     # square symmetric


def test_snakefile_includes_public_eur_rule():
    snakefile = (PROJECT_ROOT / "Snakefile").read_text()
    assert "m3_public_eur_ld.smk" in snakefile


def test_manifest_no_hardcoded_abs_paths():
    src = (PROJECT_ROOT / "src" / "python" / "build_public_eur_manifest.py").read_text()
    for bad in ("/share/clintonlab", "/rs1/researchers", "/gpfs_common"):
        assert bad not in src
