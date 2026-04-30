"""HM3-intersected COJO materializer tests (M2-POST-M3-08).

Per `.planning/m2_post_m3_rerun_queue.tsv` row M2-POST-M3-08
dependency_blockers: "HM3-intersected COJO input materializer (extension of
src/python/build_cojo_inputs.py)".

Witness for the underlying GCTA mtCOJO failure:
  data/processed/mtcojo/EUR/bmi.EUR.GIANT-UKBB.2018.mtcojo.fire.log
  → terminates with "no SNP in common between the summary data and the LD
    score files" after reading 75,783 GW-sig SNPs into PLINK memory.

The remediation specified by the obligation row is to pre-restrict per-trait
COJO inputs to the HapMap3 SNP namespace BEFORE GCTA's internal LDSC step
runs, so its SNP namespace is guaranteed to lie inside the eur_w_ld_chr
ld-score namespace.

These tests pin the contract for the new `--hm3-snplist` CLI flag and the
new `hm3_snps` / `hm3_snplist` kwargs threaded through
`materialize_cojo` / `build_inputs`. Default OFF preserves legacy genome-wide
behavior (Test 1 + Test 4); when supplied, intersection is applied BEFORE the
duplicate-drop write step (Test 2 + Test 3 + Test 5).
"""
from __future__ import annotations

import gzip
import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pandas as pd
import pytest

# conftest.py already inserts src/python on sys.path; import is safe here.
import build_cojo_inputs


REPO = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

_HARMONIZED_COLS = ["CHR", "BP", "SNP", "EA", "OA", "BETA", "SE", "P", "EAF", "N"]


def _write_harmonized_tsvbgz(path: Path, snp_ids: list[str]) -> None:
    """Write a minimal harmonized .tsv.bgz fixture for the listed SNPs.

    Mirrors the M1 harmonized schema consumed by build_cojo_inputs.materialize_cojo:
      CHR BP SNP EA OA BETA SE P EAF N
    Uses gzip.open + text mode so pandas.read_csv(..., compression='gzip') can
    consume it directly (matches the production code path).
    """
    rows = []
    for i, snp in enumerate(snp_ids, start=1):
        rows.append(
            {
                "CHR": (i % 22) + 1,
                "BP": 1_000_000 + i * 1_000,
                "SNP": snp,
                "EA": "A",
                "OA": "G",
                "BETA": 0.01 * i,
                "SE": 0.05,
                "P": 1e-3,
                "EAF": 0.30,
                "N": 100_000,
            }
        )
    df = pd.DataFrame(rows, columns=_HARMONIZED_COLS)
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt") as fh:
        df.to_csv(fh, sep="\t", index=False)


def _write_hm3_snplist(path: Path, snp_ids: list[str]) -> None:
    """Write a minimal HM3 fixture: header `SNP\tA1\tA2` + listed rs IDs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        fh.write("SNP\tA1\tA2\n")
        for snp in snp_ids:
            fh.write(f"{snp}\tA\tG\n")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_materialize_cojo_no_flag_preserves_legacy_behavior(tmp_path: Path):
    """Test 1 — default (hm3_snps=None) keeps all 50 SNPs (legacy genome-wide)."""
    snp_ids = [f"rs{1000 + i}" for i in range(50)]
    harm = tmp_path / "fixture.GRCh37.tsv.bgz"
    _write_harmonized_tsvbgz(harm, snp_ids)

    out_path = tmp_path / "out.cojo"
    n = build_cojo_inputs.materialize_cojo(harm, out_path, hm3_snps=None)
    assert n == 50, f"legacy default must keep all 50 SNPs, got {n}"

    cojo = pd.read_csv(out_path, sep="\t")
    assert len(cojo) == 50
    assert set(cojo["SNP"]) == set(snp_ids)


def test_materialize_cojo_with_hm3_intersects(tmp_path: Path):
    """Test 2 — when hm3_snps provided, COJO file contains exactly the intersection."""
    fixture_snps = [f"rs{1000 + i}" for i in range(50)]
    hm3_snps = set(f"rs{1000 + i}" for i in range(40))  # 40 of 50
    harm = tmp_path / "fixture.GRCh37.tsv.bgz"
    _write_harmonized_tsvbgz(harm, fixture_snps)

    out_path = tmp_path / "out.cojo"
    n = build_cojo_inputs.materialize_cojo(harm, out_path, hm3_snps=hm3_snps)
    assert n == 40, f"HM3 intersection must yield 40 SNPs, got {n}"

    cojo = pd.read_csv(out_path, sep="\t")
    assert len(cojo) == 40
    assert set(cojo["SNP"]) == hm3_snps
    # Confirm out-of-HM3 SNPs are dropped
    out_of_hm3 = set(fixture_snps) - hm3_snps
    assert not out_of_hm3.intersection(set(cojo["SNP"]))


def test_build_inputs_passes_hm3_through(tmp_path: Path):
    """Test 3 — build_inputs(..., hm3_snplist=Path) loads the snplist and
    forwards `hm3_snps=set[str]` to every materialize_cojo call."""
    # Sidecar with 2 traits
    sidecar = tmp_path / "residcov.trait_order.json"
    sidecar.write_text(
        json.dumps({"trait_order": ["target_trait", "covariate_trait"]})
    )

    # Empty harmonized dir — we'll mock materialize_cojo so file IO is unused
    harm_dir = tmp_path / "harmonized"
    harm_dir.mkdir()
    # _harmonized_path checks exists(), so create empty placeholder files
    for trait in ["target_trait", "covariate_trait"]:
        (harm_dir / f"{trait}.GRCh37.tsv.bgz").touch()

    # HM3 fixture
    hm3_path = tmp_path / "hm3_mini.snplist"
    fixture_hm3 = ["rs1", "rs2", "rs3", "rs4", "rs5"]
    _write_hm3_snplist(hm3_path, fixture_hm3)

    out_dir = tmp_path / "out"

    captured_calls = []

    def _fake_materialize(harm_path, cojo_path, hm3_snps=None):
        captured_calls.append((harm_path, cojo_path, hm3_snps))
        # Touch the cojo path so the cache check in build_inputs records it
        cojo_path.parent.mkdir(parents=True, exist_ok=True)
        cojo_path.write_text("SNP\tA1\tA2\tfreq\tb\tse\tp\tN\nrs1\tA\tG\t0.3\t0.01\t0.05\t1e-3\t100000\n")
        return 1

    with mock.patch.object(build_cojo_inputs, "materialize_cojo", side_effect=_fake_materialize):
        build_cojo_inputs.build_inputs(
            target="target_trait",
            stratum="EUR",
            sidecar=sidecar,
            harmonized_dir=harm_dir,
            out_dir=out_dir,
            hm3_snplist=hm3_path,
        )

    # 2 calls (one per trait), each forwarding the SAME set
    assert len(captured_calls) == 2, f"expected 2 materialize_cojo calls, got {len(captured_calls)}"
    expected_set = set(fixture_hm3)
    for harm_path, cojo_path, hm3_snps in captured_calls:
        assert isinstance(hm3_snps, set), f"hm3_snps must be a set[str], got {type(hm3_snps)}"
        assert hm3_snps == expected_set, f"hm3_snps mismatch: {hm3_snps} != {expected_set}"


def test_build_inputs_no_hm3_passes_none(tmp_path: Path):
    """Test 4 — build_inputs(..., hm3_snplist=None) (or default) forwards
    `hm3_snps=None` on every materialize_cojo call (legacy default)."""
    sidecar = tmp_path / "residcov.trait_order.json"
    sidecar.write_text(
        json.dumps({"trait_order": ["target_trait", "covariate_trait"]})
    )

    harm_dir = tmp_path / "harmonized"
    harm_dir.mkdir()
    for trait in ["target_trait", "covariate_trait"]:
        (harm_dir / f"{trait}.GRCh37.tsv.bgz").touch()

    out_dir = tmp_path / "out"

    captured_calls = []

    def _fake_materialize(harm_path, cojo_path, hm3_snps=None):
        captured_calls.append((harm_path, cojo_path, hm3_snps))
        cojo_path.parent.mkdir(parents=True, exist_ok=True)
        cojo_path.write_text("SNP\tA1\tA2\tfreq\tb\tse\tp\tN\nrs1\tA\tG\t0.3\t0.01\t0.05\t1e-3\t100000\n")
        return 1

    with mock.patch.object(build_cojo_inputs, "materialize_cojo", side_effect=_fake_materialize):
        build_cojo_inputs.build_inputs(
            target="target_trait",
            stratum="EUR",
            sidecar=sidecar,
            harmonized_dir=harm_dir,
            out_dir=out_dir,
            # hm3_snplist omitted — defaults to None
        )

    assert len(captured_calls) == 2
    for _, _, hm3_snps in captured_calls:
        assert hm3_snps is None, f"legacy default must forward None, got {hm3_snps!r}"


def test_cli_accepts_hm3_snplist_flag(tmp_path: Path):
    """Test 5 — CLI smoke: `--hm3-snplist <fixture>` exits 0 and produces
    intersected COJO files."""
    # Build a 2-trait stratum fixture
    sidecar = tmp_path / "residcov.trait_order.json"
    sidecar.write_text(json.dumps({"trait_order": ["target_trait", "covariate_trait"]}))

    harm_dir = tmp_path / "harmonized"
    target_snps = [f"rs{1000 + i}" for i in range(20)]
    cov_snps = [f"rs{1000 + i}" for i in range(15, 35)]  # overlap with target
    _write_harmonized_tsvbgz(harm_dir / "target_trait.GRCh37.tsv.bgz", target_snps)
    _write_harmonized_tsvbgz(harm_dir / "covariate_trait.GRCh37.tsv.bgz", cov_snps)

    # 10 SNPs in HM3 (subset of target's 20, subset of cov's 20)
    hm3_path = tmp_path / "hm3_mini.snplist"
    hm3_set = [f"rs{1000 + i}" for i in range(15, 25)]  # rs1015..rs1024 (10 SNPs)
    _write_hm3_snplist(hm3_path, hm3_set)

    out_dir = tmp_path / "out"

    cmd = [
        sys.executable,
        str(REPO / "src" / "python" / "build_cojo_inputs.py"),
        "--target", "target_trait",
        "--stratum", "EUR",
        "--sidecar", str(sidecar),
        "--harmonized-dir", str(harm_dir),
        "--out-dir", str(out_dir),
        "--hm3-snplist", str(hm3_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, (
        f"CLI exited {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )

    # Both per-trait COJO files should exist + be intersected
    target_cojo = pd.read_csv(out_dir / "target_trait.cojo", sep="\t")
    cov_cojo = pd.read_csv(out_dir / "covariate_trait.cojo", sep="\t")
    # target has rs1000..rs1019; HM3 has rs1015..rs1024 → intersection = rs1015..rs1019 (5)
    assert len(target_cojo) == 5
    assert set(target_cojo["SNP"]) == set(f"rs{1000 + i}" for i in range(15, 20))
    # cov has rs1015..rs1034; HM3 has rs1015..rs1024 → intersection = rs1015..rs1024 (10)
    assert len(cov_cojo) == 10
    assert set(cov_cojo["SNP"]) == set(f"rs{1000 + i}" for i in range(15, 25))

    # mtcojo list file must exist and have target FIRST
    list_path = out_dir / "target_trait.mtcojo.list"
    assert list_path.exists()
    lines = list_path.read_text().strip().split("\n")
    assert lines[0].split("\t")[0] == "target_trait"


def test_build_inputs_with_hm3_prunes_empty_covariates(tmp_path: Path):
    """Test 6 — when HM3 intersection yields an empty covariate cojo, that
    covariate is auto-pruned from the mtcojo list. Required for correctness:
    GCTA mtCOJO's LDSC step fails per-pair if a covariate has 0 ld-score-overlapping
    SNPs (witness: sbp.EUR + stroke.EUR harmonize to chr:pos identifiers, not
    rsIDs, so HM3 ∩ sbp = ∅ and HM3 ∩ stroke = ∅; including these covariates
    triggers GCTA error 'no SNP in common between the summary data and the LD
    score files').
    """
    sidecar = tmp_path / "residcov.trait_order.json"
    sidecar.write_text(
        json.dumps({"trait_order": ["target_trait", "chrpos_trait", "rsid_trait"]})
    )

    harm_dir = tmp_path / "harmonized"
    target_snps = [f"rs{1000 + i}" for i in range(20)]
    rsid_cov_snps = [f"rs{1000 + i}" for i in range(15, 25)]
    chrpos_cov_snps = [f"1:{752000 + i}" for i in range(20)]  # not rsIDs
    _write_harmonized_tsvbgz(harm_dir / "target_trait.GRCh37.tsv.bgz", target_snps)
    _write_harmonized_tsvbgz(harm_dir / "rsid_trait.GRCh37.tsv.bgz", rsid_cov_snps)
    _write_harmonized_tsvbgz(harm_dir / "chrpos_trait.GRCh37.tsv.bgz", chrpos_cov_snps)

    # HM3 set covers some target SNPs + the rsid covariate, but NONE of chrpos
    hm3_path = tmp_path / "hm3_mini.snplist"
    hm3_set = [f"rs{1000 + i}" for i in range(15, 25)]
    _write_hm3_snplist(hm3_path, hm3_set)

    out_dir = tmp_path / "out"

    list_path = build_cojo_inputs.build_inputs(
        target="target_trait",
        stratum="EUR",
        sidecar=sidecar,
        harmonized_dir=harm_dir,
        out_dir=out_dir,
        hm3_snplist=hm3_path,
    )

    # chrpos_trait.cojo MUST exist on disk (materializer always writes), but
    # MUST be empty (header only) and MUST NOT appear in the mtcojo list.
    chrpos_cojo = out_dir / "chrpos_trait.cojo"
    assert chrpos_cojo.exists()
    chrpos_df = pd.read_csv(chrpos_cojo, sep="\t")
    assert len(chrpos_df) == 0, "chrpos covariate must materialize empty after HM3 intersection"

    # mtcojo list must contain target + rsid_trait, but NOT chrpos_trait
    list_lines = list_path.read_text().strip().split("\n")
    list_traits = [line.split("\t")[0] for line in list_lines]
    assert list_traits[0] == "target_trait", "target must be FIRST"
    assert "rsid_trait" in list_traits
    assert "chrpos_trait" not in list_traits, (
        f"empty covariate must be pruned, got list: {list_traits}"
    )


def test_build_inputs_with_hm3_raises_when_target_empty(tmp_path: Path):
    """Test 7 — if HM3 intersection leaves the target with 0 SNPs, raise
    (cannot proceed). This guards against silent no-ops on mis-harmonized
    target traits."""
    sidecar = tmp_path / "residcov.trait_order.json"
    sidecar.write_text(
        json.dumps({"trait_order": ["target_trait", "covariate_trait"]})
    )

    harm_dir = tmp_path / "harmonized"
    # Target has chr:pos IDs — not in HM3
    target_snps = [f"1:{752000 + i}" for i in range(20)]
    cov_snps = [f"rs{1000 + i}" for i in range(20)]
    _write_harmonized_tsvbgz(harm_dir / "target_trait.GRCh37.tsv.bgz", target_snps)
    _write_harmonized_tsvbgz(harm_dir / "covariate_trait.GRCh37.tsv.bgz", cov_snps)

    hm3_path = tmp_path / "hm3_mini.snplist"
    _write_hm3_snplist(hm3_path, [f"rs{1000 + i}" for i in range(20)])

    out_dir = tmp_path / "out"

    with pytest.raises(ValueError, match="0 HM3-intersected SNPs"):
        build_cojo_inputs.build_inputs(
            target="target_trait",
            stratum="EUR",
            sidecar=sidecar,
            harmonized_dir=harm_dir,
            out_dir=out_dir,
            hm3_snplist=hm3_path,
        )
