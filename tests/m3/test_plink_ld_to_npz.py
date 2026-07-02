"""Tests for src/python/plink_ld_to_npz.py (m3-02e Task 1) + the two native-path
helpers in aou_ld_panel.py (build_plink_ld_command, export_cohort_to_plink).

plink_ld_to_npz.py converts a native plink1.9 per-region LD output (square
``.ld.bin`` float32 OR banded ``.ld.gz``) + the cohort ``.bim`` (variant order) +
an AF sidecar into the SAME egress-clean ``.npz`` contract the downstream loader
(ld_npz_to_rds.R) already consumes — keys: ld, variant_ids, rsids, allele_freq,
lower_triangular. square -> lower_triangular=False (full matrix); banded ->
lower_triangular=True (one materialized triangle). Getting the flag wrong silently
halves/doubles off-diagonals (feedback_npz_triangle_flag_contract: CR-01 doubling,
BR-01 A.3 halving).

Runs in smoke_dev py3.11 (pandas + numpy). No Hail required (the helpers use a
hail-optional import; export_cohort_to_plink is tested with a mock hl module).
"""
from __future__ import annotations

import gzip
import sys
import types
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

import plink_ld_to_npz as pln  # noqa: E402


# --------------------------------------------------------------------------- #
# Fixtures: synthetic plink outputs                                           #
# --------------------------------------------------------------------------- #

def _symmetric_corr(n: int, seed: int = 0) -> np.ndarray:
    """A symmetric float32 correlation-like matrix with unit diagonal."""
    rng = np.random.default_rng(seed)
    a = rng.standard_normal((n, n)).astype("float32")
    m = (a + a.T) / 2.0
    np.fill_diagonal(m, 1.0)
    return m.astype("float32")


def _write_bim(path: Path, rows: list[tuple]) -> None:
    """Write a 6-col plink .bim: chr, snp_id, cm, bp, A1, A2 (tab-separated)."""
    lines = ["\t".join(str(c) for c in r) for r in rows]
    path.write_text("\n".join(lines) + "\n")


def _default_bim_rows(n: int) -> list[tuple]:
    # A1 = ALT = alleles[1]; A2 = REF = alleles[0] (hl.export_plink convention).
    rows = []
    for i in range(n):
        chrom = 12
        snp = f"rs{1000 + i}"
        bp = 53_000_000 + i * 100
        a1, a2 = "A", "T"  # A1=ALT=A, A2=REF=T
        rows.append((chrom, snp, 0, bp, a1, a2))
    return rows


def _write_af(path: Path, n: int, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    af = rng.uniform(0.01, 0.5, size=n).astype("float64")
    path.write_text("\n".join(f"{x:.6f}" for x in af) + "\n")
    return af.astype("float32")


# --------------------------------------------------------------------------- #
# Square mode                                                                 #
# --------------------------------------------------------------------------- #

def test_plink_square_bin_to_npz(tmp_path):
    n = 40
    m = _symmetric_corr(n)
    ld_bin = tmp_path / "region.ld.bin"
    m.astype("<f4").tofile(ld_bin)
    bim = tmp_path / "cohort.bim"
    _write_bim(bim, _default_bim_rows(n))
    af_path = tmp_path / "region.afreq"
    af = _write_af(af_path, n)
    out_npz = tmp_path / "region.npz"

    pln.plink_ld_to_npz(
        mode="square", ld_path=ld_bin, bim_path=bim,
        af_sidecar_path=af_path, out_npz=out_npz, region_id="region", n_var=n,
    )

    z = np.load(out_npz, allow_pickle=True)
    assert z["ld"].shape == (n, n)
    assert z["ld"].dtype == np.float32
    assert np.allclose(np.diag(z["ld"]), 1.0)
    assert np.allclose(z["ld"], z["ld"].T)
    assert bool(z["lower_triangular"][0]) is False
    assert z["variant_ids"].shape[0] == n
    assert z["rsids"].shape[0] == n
    assert z["allele_freq"].shape[0] == n
    assert np.allclose(z["allele_freq"].astype("float32"), af, atol=1e-5)
    # square is full -> round-trips byte-equal (no triangle loss)
    assert np.allclose(z["ld"], m)


# --------------------------------------------------------------------------- #
# Memory-bounded symmetry check (m3-02e-T4 OOM regression, failing-first)      #
# --------------------------------------------------------------------------- #

def test_is_symmetric_blocked_accepts_and_rejects():
    """The blocked check is True for a symmetric matrix and False once a single
    off-diagonal is perturbed beyond atol on ONE side only (m != m.T)."""
    for n in (5, 33, 100):
        m = _symmetric_corr(n)
        assert pln._is_symmetric_blocked(m, atol=1e-4) is True

    n = 100
    m = _symmetric_corr(n)
    m[0, n - 1] += 1.0  # perturb one side only; leave m[n-1, 0] unchanged
    assert pln._is_symmetric_blocked(m, atol=1e-4) is False


def test_blocked_check_matches_allclose():
    """The blocked verdict must equal np.allclose(m, m.T) for both symmetric and
    asymmetric inputs, across block-boundary edge cases (n not a multiple of the
    block, and block > n)."""
    for n in (5, 17, 100):
        sym = _symmetric_corr(n)
        # default block, and a block strictly larger than n (single-block path)
        for block in (1024, 4096):
            assert (
                pln._is_symmetric_blocked(sym, atol=1e-4, block=block)
                == np.allclose(sym, sym.T, atol=1e-4)
            )

        asym = _symmetric_corr(n)
        asym[0, n - 1] += 1.0  # one-sided perturbation -> asymmetric
        for block in (1024, 4096):
            assert (
                pln._is_symmetric_blocked(asym, atol=1e-4, block=block)
                == np.allclose(asym, asym.T, atol=1e-4)
            )


def test_strict_upper_is_zero_blocked_matches_allclose():
    """The memory-bounded 'strict upper triangle is all zero' check (banded-npz
    gate) must equal np.allclose(np.triu(m, k=1), 0.0) for both a lower-triangular
    (strict upper all-zero) input AND a copy with a single nonzero strict-upper
    entry, across block-boundary edge cases (block > n, n % block != 0, block=1)."""
    for n in (5, 17, 100):
        # lower-triangular populated -> strict upper all zero -> True
        lower = np.tril(_symmetric_corr(n))
        for block in (1, 1024, 4096):
            assert (
                pln._strict_upper_is_zero_blocked(lower, block=block)
                == np.allclose(np.triu(lower, k=1), 0.0)
                is True
            )

        # one nonzero strict-upper entry -> False
        dirty = lower.copy()
        dirty[0, n - 1] = np.float32(0.5)
        for block in (1, 1024, 4096):
            assert (
                pln._strict_upper_is_zero_blocked(dirty, block=block)
                == np.allclose(np.triu(dirty, k=1), 0.0)
                is False
            )


def test_read_square_bin_rejects_asymmetric(tmp_path):
    """read_square_bin still raises ValueError on a non-symmetric .ld.bin with a
    unit diagonal (the diagonal check passes, so we reach the symmetry check) —
    proves the invariant is PRESERVED (bounded, not skipped)."""
    n = 50
    m = _symmetric_corr(n)
    m[0, n - 1] += 1.0          # perturb one off-diagonal on one side only
    np.fill_diagonal(m, 1.0)    # keep the diagonal unit so the diag check passes
    ld_bin = tmp_path / "asym.ld.bin"
    m.astype("<f4").tofile(ld_bin)
    with pytest.raises(ValueError):
        pln.read_square_bin(ld_bin, n)


def test_read_square_bin_raises_on_monomorphic_nan(tmp_path):
    """m3-02e-T4 diagnosis lock (quick 260701-qcy): a square ``.ld.bin`` carrying
    NaN LD entries — the fingerprint of a MONOMORPHIC (MAC=0-in-AFR / zero-variance)
    variant, for which plink ``--r`` computes ``0/0 -> NaN`` — must make
    ``read_square_bin`` RAISE ``square LD is not symmetric`` (``NaN != NaN`` breaks
    the symmetry equality even where the NaN placement is itself symmetric). This
    locks WHY the fix drops MAC=0 variants (``--mac 1``) BEFORE ``--r``:
    ``read_square_bin`` is CORRECT and is NOT modified — it CAUGHT the bug (fire #3
    region 1: 12 NaN entries across 11 rows, diagonals still 1.0)."""
    n = 40
    m = _symmetric_corr(n)
    # Model a monomorphic variant at row/col k: its LD with every other variant is
    # NaN (0/0), symmetric in placement, but plink still writes 1.0 self-corr on the
    # diagonal. The diagonal check therefore PASSES and we reach the symmetry check.
    k = 7
    nan32 = np.float32("nan")
    m[k, :] = nan32
    m[:, k] = nan32
    np.fill_diagonal(m, 1.0)  # diagonals stay 1.0 -> diag check passes
    ld_bin = tmp_path / "mono_nan.ld.bin"
    m.astype("<f4").tofile(ld_bin)
    with pytest.raises(ValueError, match="not symmetric"):
        pln.read_square_bin(ld_bin, n)


# --------------------------------------------------------------------------- #
# Banded mode                                                                 #
# --------------------------------------------------------------------------- #

def test_plink_banded_gz_to_npz(tmp_path):
    n = 8
    bim_rows = _default_bim_rows(n)
    bim = tmp_path / "cohort.bim"
    _write_bim(bim, bim_rows)
    af_path = tmp_path / "region.afreq"
    _write_af(af_path, n)

    # in-band pairs only (|i-j| <= 2): build a known full matrix from the pairs
    expected = np.eye(n, dtype="float32")
    pairs = []
    rng = np.random.default_rng(7)
    for i in range(n):
        for j in range(i + 1, min(i + 3, n)):
            r = float(rng.uniform(-0.9, 0.9))
            expected[i, j] = r
            expected[j, i] = r
            # plink --r gz row: CHR_A BP_A SNP_A CHR_B BP_B SNP_B R
            a = bim_rows[i]
            b = bim_rows[j]
            pairs.append((a[0], a[3], a[1], b[0], b[3], b[1], r))

    ld_gz = tmp_path / "region.ld.gz"
    header = "CHR_A BP_A SNP_A CHR_B BP_B SNP_B R"
    body = "\n".join(" ".join(str(c) for c in p) for p in pairs)
    with gzip.open(ld_gz, "wt") as fh:
        fh.write(header + "\n" + body + "\n")

    out_npz = tmp_path / "region.npz"
    pln.plink_ld_to_npz(
        mode="banded", ld_path=ld_gz, bim_path=bim,
        af_sidecar_path=af_path, out_npz=out_npz, region_id="region", n_var=n,
    )

    z = np.load(out_npz, allow_pickle=True)
    tri = z["ld"]
    assert tri.dtype == np.float32
    assert bool(z["lower_triangular"][0]) is True
    # one populated triangle: upper strict triangle must be all zero
    assert np.allclose(np.triu(tri, k=1), 0.0)
    # off-band entries are zero in the lower triangle too
    for i in range(n):
        for j in range(i):
            if i - j > 2:
                assert tri[i, j] == 0.0
    # ld_npz_to_rds.R reconstruction: tri + tri.T - diag(diag) recovers full
    recon = tri + tri.T - np.diag(np.diag(tri))
    assert np.allclose(recon, expected, atol=1e-5)


# --------------------------------------------------------------------------- #
# Flag-per-mode regression guard                                              #
# --------------------------------------------------------------------------- #

def test_lower_triangular_flag_correct_per_mode(tmp_path):
    n = 10
    m = _symmetric_corr(n, seed=3)
    bim = tmp_path / "c.bim"
    _write_bim(bim, _default_bim_rows(n))
    af = tmp_path / "c.afreq"
    _write_af(af, n)

    sq_bin = tmp_path / "sq.ld.bin"
    m.astype("<f4").tofile(sq_bin)
    sq_npz = tmp_path / "sq.npz"
    pln.plink_ld_to_npz(mode="square", ld_path=sq_bin, bim_path=bim,
                        af_sidecar_path=af, out_npz=sq_npz, region_id="sq", n_var=n)
    assert bool(np.load(sq_npz, allow_pickle=True)["lower_triangular"][0]) is False

    # banded (empty band file still valid: only the header + diagonal)
    gz = tmp_path / "bd.ld.gz"
    with gzip.open(gz, "wt") as fh:
        fh.write("CHR_A BP_A SNP_A CHR_B BP_B SNP_B R\n")
    bd_npz = tmp_path / "bd.npz"
    pln.plink_ld_to_npz(mode="banded", ld_path=gz, bim_path=bim,
                        af_sidecar_path=af, out_npz=bd_npz, region_id="bd", n_var=n)
    assert bool(np.load(bd_npz, allow_pickle=True)["lower_triangular"][0]) is True


def test_npz_keys_match_save_npz_contract(tmp_path):
    n = 6
    m = _symmetric_corr(n)
    bim = tmp_path / "c.bim"
    _write_bim(bim, _default_bim_rows(n))
    af = tmp_path / "c.afreq"
    _write_af(af, n)
    sq_bin = tmp_path / "sq.ld.bin"
    m.astype("<f4").tofile(sq_bin)
    out = tmp_path / "r.npz"
    pln.plink_ld_to_npz(mode="square", ld_path=sq_bin, bim_path=bim,
                        af_sidecar_path=af, out_npz=out, region_id="r", n_var=n)
    z = np.load(out, allow_pickle=True)
    assert set(z.files) == {"ld", "variant_ids", "rsids", "allele_freq", "lower_triangular"}


# --------------------------------------------------------------------------- #
# AF sidecar handling (mirror bm_to_npz guards)                               #
# --------------------------------------------------------------------------- #

def test_af_sidecar_row_alignment(tmp_path):
    n = 12
    m = _symmetric_corr(n)
    bim = tmp_path / "c.bim"
    _write_bim(bim, _default_bim_rows(n))
    sq_bin = tmp_path / "sq.ld.bin"
    m.astype("<f4").tofile(sq_bin)

    # length-mismatched AF -> loud ValueError
    bad_af = tmp_path / "bad.afreq"
    bad_af.write_text("\n".join("0.1" for _ in range(n - 3)) + "\n")
    with pytest.raises(ValueError):
        pln.plink_ld_to_npz(mode="square", ld_path=sq_bin, bim_path=bim,
                            af_sidecar_path=bad_af, out_npz=tmp_path / "bad.npz",
                            region_id="bad", n_var=n)

    # omitted AF -> all-NaN + warning (do NOT silently ship a wrong AF)
    out = tmp_path / "noaf.npz"
    pln.plink_ld_to_npz(mode="square", ld_path=sq_bin, bim_path=bim,
                        af_sidecar_path=None, out_npz=out, region_id="noaf", n_var=n)
    z = np.load(out, allow_pickle=True)
    assert z["allele_freq"].shape[0] == n
    assert np.all(np.isnan(z["allele_freq"].astype("float64")))


def test_bim_variant_order_preserved(tmp_path):
    # a shuffled .bim produces correspondingly-ordered ids
    rows = _default_bim_rows(5)
    shuffled = [rows[i] for i in [3, 0, 4, 1, 2]]
    bim = tmp_path / "c.bim"
    _write_bim(bim, shuffled)
    variant_ids, rsids = pln.load_bim(bim)
    assert rsids == [r[1] for r in shuffled]
    # variant_id chr:bp:A2:A1 in the same (shuffled) row order
    expected = [f"{r[0]}:{r[3]}:{r[5]}:{r[4]}" for r in shuffled]
    assert variant_ids == expected


def test_canonical_vid_reconstruction_exact(tmp_path):
    """W-3 silent-misalignment vector: hl.export_plink writes A1=ALT=alleles[1],
    A2=REF=alleles[0]. The canonical vid (aou_ld_panel.py:2504) is
    chr:pos:REF:ALT = chr:pos:alleles[0]:alleles[1] = chr:pos:A2:A1.
    A reconstruction that emits A1:A2 (REF/ALT swapped) is WRONG."""
    bim = tmp_path / "c.bim"
    # .bim line: 12  rs1558902  0  53809247  A  T  (A1=A=ALT, A2=T=REF)
    _write_bim(bim, [(12, "rs1558902", 0, 53809247, "A", "T")])
    variant_ids, rsids = pln.load_bim(bim)
    assert variant_ids == ["12:53809247:T:A"]   # chr:pos:REF(A2):ALT(A1)
    assert variant_ids != ["12:53809247:A:T"]   # REF/ALT swapped == FAIL
    assert rsids == ["rs1558902"]


def test_load_bim_missing_rsid_is_empty(tmp_path):
    bim = tmp_path / "c.bim"
    _write_bim(bim, [(7, ".", 0, 12345, "G", "C")])
    variant_ids, rsids = pln.load_bim(bim)
    assert variant_ids == ["7:12345:C:G"]
    assert rsids == [""]


def test_no_hardcoded_abs_paths():
    """REQ-PATH-PARAMETERIZATION: no /share|/rs1|/gpfs_common literals."""
    src = (PROJECT_ROOT / "src" / "python" / "plink_ld_to_npz.py").read_text()
    for bad in ("/share/clintonlab", "/rs1/researchers", "/gpfs_common"):
        assert bad not in src, f"hardcoded path {bad} in plink_ld_to_npz.py"


def test_plink_ld_to_npz_does_not_import_hail():
    """Runs on the Spot VM / NCSU — must not import hail (AST: no actual import
    statement; the docstring may mention the word)."""
    import ast
    src = (PROJECT_ROOT / "src" / "python" / "plink_ld_to_npz.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(a.name != "hail" for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.module != "hail"


# --------------------------------------------------------------------------- #
# aou_ld_panel.py native-path helpers                                         #
# --------------------------------------------------------------------------- #

def test_build_plink_ld_command_has_keep_allele_order():
    import aou_ld_panel as alp
    cmd = alp.build_plink_ld_command(
        bfile_prefix="cohort", chrom=12, from_bp=37463740, to_bp=45398515,
        out_prefix="m2_region_00040__sub00", mode="square",
    )
    cmd_str = " ".join(cmd) if isinstance(cmd, (list, tuple)) else str(cmd)
    assert "--keep-allele-order" in cmd_str
    assert "--r square bin4" in cmd_str
    assert "--chr 12" in cmd_str
    assert "--from-bp 37463740" in cmd_str
    assert "--to-bp 45398515" in cmd_str
    assert "--bfile cohort" in cmd_str

    banded = alp.build_plink_ld_command(
        bfile_prefix="cohort", chrom=1, from_bp=1, to_bp=100,
        out_prefix="r", mode="banded",
    )
    banded_str = " ".join(banded) if isinstance(banded, (list, tuple)) else str(banded)
    assert "--keep-allele-order" in banded_str
    assert "--r gz" in banded_str
    # banded carries the ld-window + r2 floor flags
    assert "--ld-window-kb" in banded_str


def test_export_cohort_to_plink_invokes_export_plink(monkeypatch):
    import aou_ld_panel as alp

    calls = {"export_plink": 0, "count_cols": 0}

    class _FakeMT:
        def count_cols(self):
            calls["count_cols"] += 1
            return 73122

    fake_mt = _FakeMT()

    def _fake_export_plink(mt, prefix, **kwargs):
        calls["export_plink"] += 1
        assert mt is fake_mt
        assert prefix == "cohort_afr"

    fake_hl = types.SimpleNamespace(export_plink=_fake_export_plink)
    monkeypatch.setitem(sys.modules, "hail", fake_hl)

    alp.export_cohort_to_plink("gs://bucket/ld/mt_afr_qc.mt", "cohort_afr", mt=fake_mt)
    assert calls["export_plink"] == 1
    # the count_cols scan is amortized: at most one scan, never per-region
    assert calls["count_cols"] <= 1


def test_afr_native_path_does_not_route_through_retired_a3():
    """The m3-02d ordering-B Hail A.3 write (_write_a3_banded_correlation_bm) STAYS
    in the tree but the NATIVE AFR helpers must NOT call it (nor hl.row_correlation /
    hl.ld_matrix)."""
    import ast
    import aou_ld_panel as alp

    src = (PROJECT_ROOT / "src" / "python" / "aou_ld_panel.py").read_text()
    assert src.count("def _write_a3_banded_correlation_bm") == 1  # retired path stays

    tree = ast.parse(src)
    retired_markers = ("_write_a3_banded_correlation_bm", "row_correlation", "ld_matrix")
    for fname in ("export_cohort_to_plink", "build_plink_ld_command"):
        fn = next((n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == fname), None)
        assert fn is not None, f"{fname} not found in aou_ld_panel.py"
        fn_src = ast.get_source_segment(src, fn)
        for marker in retired_markers:
            assert marker not in fn_src, (
                f"native helper {fname} must not reference retired Hail A.3 marker {marker}"
            )

    # plink_ld_to_npz must not invoke the retired Hail path either
    pln_src = (PROJECT_ROOT / "src" / "python" / "plink_ld_to_npz.py").read_text()
    for marker in retired_markers:
        assert marker not in pln_src


def test_export_cohort_to_plink_documents_in_perimeter_boundary():
    src = (PROJECT_ROOT / "src" / "python" / "aou_ld_panel.py").read_text()
    import ast
    tree = ast.parse(src)
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == "export_cohort_to_plink"), None)
    assert fn is not None
    fn_src = ast.get_source_segment(src, fn).lower()
    assert any(p in fn_src for p in ("in-perimeter", "never egress", "individual-level"))
