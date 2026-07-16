"""Tests for src/python/run_native_ld_panel.py (quick 260625-r6m / m3-02e STEP 4):
the resumable native-plink LD loop driver for the 276-region AFR panel.

The driver wraps the existing native-plink helpers — it reuses
``aou_ld_panel._existing_region_npz`` (the MED-6 byte-floor resume guard, NOT a
bare ``[ -f ]`` check) for idempotent skip across Spot-VM preemption, issues plink
ONLY through ``aou_ld_panel.build_plink_ld_command`` (so ``--keep-allele-order`` is
always present), and converts each region via ``plink_ld_to_npz.plink_ld_to_npz``.
It must NOT import hail at module scope and must NOT touch the retired Hail A.3
path (``compute_region_ld`` / ``_write_a3_banded_correlation_bm`` /
``row_correlation`` / ``ld_matrix``).

Runs in smoke_dev py3.11 (pandas + numpy). plink is mocked: the module's SOLE
subprocess seam (``_run_plink``) is monkeypatched to WRITE a synthetic
``{out_prefix}.ld.bin`` and record the argv, instead of invoking real plink1.9.
"""
from __future__ import annotations

import ast
import gzip
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

import run_native_ld_panel as drv  # noqa: E402


# --------------------------------------------------------------------------- #
# Fixtures (mirror tests/m3/test_plink_ld_to_npz.py)                          #
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


def _default_bim_rows(n: int, chrom: int = 12, bp0: int = 53_000_000) -> list[tuple]:
    rows = []
    for i in range(n):
        snp = f"rs{1000 + i}"
        bp = bp0 + i * 100
        a1, a2 = "A", "T"  # A1=ALT=A, A2=REF=T
        rows.append((chrom, snp, 0, bp, a1, a2))
    return rows


def _write_af(path: Path, n: int, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    af = rng.uniform(0.01, 0.5, size=n).astype("float64")
    path.write_text("\n".join(f"{x:.6f}" for x in af) + "\n")
    return af.astype("float32")


def _write_manifest(path: Path, rows: list[dict]) -> None:
    """Write a tiny region manifest TSV with the REAL column names."""
    import pandas as pd
    cols = ["region_id", "chr", "ancestry", "window_start_grch38", "window_end_grch38"]
    pd.DataFrame(rows, columns=cols).to_csv(path, sep="\t", index=False)


class _MockPlink:
    """Monkeypatch target for drv._run_plink. WRITES a synthetic square
    {out_prefix}.ld.bin (n_var derived from the --from-bp/--to-bp window over the
    cohort .bim) and records every argv it received.

    ``mono_snps`` (quick 260701-qcy) models plink ``--mac 1``: when the issued argv
    contains ``--write-snplist``, the in-window rows whose SNP id is in ``mono_snps``
    are DROPPED (monomorphic / MAC=0 -> plink would emit NaN LD), a
    ``{out_prefix}.snplist`` is written with the RETAINED SNP ids one-per-line in
    ``.bim`` order (== ``.ld.bin`` row order), and the ``.ld.bin`` is sized to
    ``(n_retained)^2``. Without ``--write-snplist`` (banded, or the PRE-fix square
    argv) NO snplist is written and the ``.ld.bin`` is the full raw-window ``N^2``.

    ``--exclude <file>`` (m3-07) models plink's exclude-list: the listed col-2 ids
    are dropped from the window BEFORE sizing the ``.ld.bin``/snplist, composing
    with (and applied ahead of) the ``--mac``/``--write-snplist`` monomorphic drop —
    so ``n_dropped_occluded`` and ``n_dropped_monomorphic`` are separable. Every
    exclude file is recorded in ``self.exclude_calls``.

    ``nan_snps`` (m3-07) models THE MECHANISM THIS PHASE EXISTS FOR: a variant whose
    LD is structurally undefined because an overlapping deletion's REF span occludes
    it makes plink ``--r`` emit a NaN row/col. It reproduces the REAL m3-02e-T4
    fire-#3 fingerprint — whole-row/col NaN with the DIAGONAL STILL 1.0. Any retained
    row whose id is in ``nan_snps`` gets that treatment, so a driver that does NOT
    exclude the occluded variants produces a NaN matrix (and fails conversion), while
    a driver that DOES excludes them cleanly. Without this, an "npz has no NaN" test
    would pass GREEN for the wrong reason."""

    def __init__(self, bim_path: Path, *, corrupt_regions=None, seed: int = 0,
                 mono_snps=None, nan_snps=None):
        self.bim_path = Path(bim_path)
        self.calls: list[list[str]] = []
        self.corrupt_regions = set(corrupt_regions or [])
        self.seed = seed
        self.mono_snps = set(mono_snps or [])
        self.nan_snps = set(nan_snps or [])
        self.exclude_calls: list[set[str]] = []
        self._bim_rows = [ln.split() for ln in self.bim_path.read_text().splitlines() if ln.strip()]

    def _window_rows(self, chrom: str, from_bp: int, to_bp: int) -> list[list[str]]:
        return [
            r for r in self._bim_rows
            if str(r[0]) == str(chrom) and from_bp <= int(r[3]) <= to_bp
        ]

    def _n_var_in_window(self, chrom: str, from_bp: int, to_bp: int) -> int:
        return len(self._window_rows(chrom, from_bp, to_bp))

    def __call__(self, cmd: list[str]):
        self.calls.append(list(cmd))
        # parse the window + out prefix back out of the argv
        def _arg(flag):
            return cmd[cmd.index(flag) + 1]
        chrom = _arg("--chr")
        from_bp = int(_arg("--from-bp"))
        to_bp = int(_arg("--to-bp"))
        out_prefix = _arg("--out")
        region_id = Path(out_prefix).name
        window_rows = self._window_rows(chrom, from_bp, to_bp)

        # ``--exclude <file>``: plink drops the listed col-2 ids from the window
        # BEFORE any sizing/LD work (m3-07 occlusion span-filter seam).
        if "--exclude" in cmd:
            excluded = {
                ln.strip()
                for ln in Path(_arg("--exclude")).read_text().splitlines()
                if ln.strip()
            }
            self.exclude_calls.append(excluded)
            window_rows = [r for r in window_rows if r[1] not in excluded]

        # BANDED (``--r gz``): plink writes ``{out_prefix}.ld.gz`` (text), and banded
        # does NOT drop MAC=0 (no ``--mac`` / ``--write-snplist``), so no snplist is
        # emitted. A minimal HEADER-ONLY .ld.gz -> read_banded_gz builds a valid
        # identity lower-triangle that content_verify_npz(mode='banded') accepts.
        if "--r" in cmd and cmd[cmd.index("--r") + 1] == "gz":
            Path(out_prefix + ".ld.gz").parent.mkdir(parents=True, exist_ok=True)
            with gzip.open(out_prefix + ".ld.gz", "wt") as fh:
                fh.write("CHR_A BP_A SNP_A CHR_B BP_B SNP_B R\n")
            return (1.5, 2.0)  # (wall_min, peak_ram_gib)

        if "--write-snplist" in cmd:
            # --mac 1 drops MAC=0 monomorphic rows BEFORE --r; --write-snplist emits
            # the RETAINED ids in .bim order (== .ld.bin row order).
            retained = [r for r in window_rows if r[1] not in self.mono_snps]
            Path(out_prefix + ".snplist").parent.mkdir(parents=True, exist_ok=True)
            Path(out_prefix + ".snplist").write_text(
                "".join(f"{r[1]}\n" for r in retained)
            )
            emitted_rows = retained
            n = len(retained)
        else:
            emitted_rows = window_rows
            n = len(window_rows)

        m = _symmetric_corr(n, seed=self.seed)

        # Occluded (structurally-undefined-LD) variants that SURVIVED into the LD
        # step make plink --r emit NaN: whole row/col NaN, diagonal still 1.0 (the
        # real fire-#3 fingerprint). Excluded variants never reach here.
        if self.nan_snps:
            for i, row in enumerate(emitted_rows):
                if row[1] in self.nan_snps:
                    m[i, :] = np.float32("nan")
                    m[:, i] = np.float32("nan")
                    m[i, i] = np.float32(1.0)

        if region_id in self.corrupt_regions:
            # break symmetry AND the diagonal -> content_verify_npz must reject
            m[0, 1] = np.float32(0.5)
            m[1, 0] = np.float32(-0.5)
            m[0, 0] = np.float32(0.2)
        Path(out_prefix + ".ld.bin").parent.mkdir(parents=True, exist_ok=True)
        m.astype("<f4").tofile(out_prefix + ".ld.bin")
        return (1.5, 2.0)  # (wall_min, peak_ram_gib)


def _setup_cohort(tmp_path: Path, n: int = 20, chrom: int = 12, bp0: int = 53_000_000):
    """Write a cohort .bim + .afreq; return (bfile_prefix, bim_path, window)."""
    bim = tmp_path / "cohort.bim"
    rows = _default_bim_rows(n, chrom=chrom, bp0=bp0)
    _write_bim(bim, rows)
    af = tmp_path / "cohort.afreq"
    _write_af(af, n)
    from_bp = bp0
    to_bp = bp0 + (n - 1) * 100
    return str(tmp_path / "cohort"), bim, (chrom, from_bp, to_bp)


# --------------------------------------------------------------------------- #
# 1. hail-free at module scope                                                #
# --------------------------------------------------------------------------- #

def test_module_imports_without_hail():
    """AST: no module-scope ``import hail`` / ``from hail import``. A lazy import
    inside a function body (mirroring _existing_region_npz) is acceptable."""
    src = (_SRC_PYTHON / "run_native_ld_panel.py").read_text()
    tree = ast.parse(src)
    for node in tree.body:  # module-scope statements ONLY
        if isinstance(node, ast.Import):
            assert all(a.name.split(".")[0] != "hail" for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] != "hail"


# --------------------------------------------------------------------------- #
# 2. resume idempotency (second run = ZERO plink work)                        #
# --------------------------------------------------------------------------- #

def test_resume_skip_zero_plink_work(tmp_path, monkeypatch):
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "regA", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
        {"region_id": "regB", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"

    mock = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock)

    res1 = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")
    assert len(res1) == 2
    assert len(mock.calls) == 2  # both regions computed on the first pass
    assert (out_dir / "regA.npz").is_file()
    assert (out_dir / "regB.npz").is_file()

    # Second run over the SAME out_dir -> ZERO plink calls (preemption idempotency)
    mock2 = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock2)
    res2 = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")
    assert len(mock2.calls) == 0
    assert all(r["status"] == "skipped_idempotent" for r in res2)


def test_skip_uses_existing_region_npz_not_bare_exists(tmp_path, monkeypatch):
    """A TRUNCATED (<256 B) region .npz must NOT short-circuit — the MED-6
    byte-floor guard recomputes it (proves it is not a bare [ -f ] check)."""
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "regT", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "regT.npz").write_bytes(b"x" * 100)  # < _MIN_REGION_NPZ_BYTES (256)
    assert (out_dir / "regT.npz").stat().st_size < drv.alp._MIN_REGION_NPZ_BYTES

    mock = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock)
    res = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")
    assert len(mock.calls) == 1  # truncated file rejected -> recompute
    assert res[0]["status"] == "ok"


# --------------------------------------------------------------------------- #
# 3. content verification                                                     #
# --------------------------------------------------------------------------- #

def test_content_verify_rejects_bad_npz(tmp_path):
    n = 8
    good = tmp_path / "good.npz"
    m = _symmetric_corr(n)
    np.savez_compressed(good, ld=m, variant_ids=np.array(["x"] * n),
                        rsids=np.array([""] * n), allele_freq=np.zeros(n, "float32"),
                        lower_triangular=np.array([False]))
    ok, _ = drv.content_verify_npz(good, mode="square")
    assert ok is True

    # non-symmetric
    asym = m.copy()
    asym[0, 1] = np.float32(0.9)
    asym[1, 0] = np.float32(-0.9)
    bad1 = tmp_path / "asym.npz"
    np.savez_compressed(bad1, ld=asym, variant_ids=np.array(["x"] * n),
                        rsids=np.array([""] * n), allele_freq=np.zeros(n, "float32"),
                        lower_triangular=np.array([False]))
    ok1, reason1 = drv.content_verify_npz(bad1, mode="square")
    assert ok1 is False and reason1

    # wrong diagonal
    baddiag = _symmetric_corr(n)
    baddiag[3, 3] = np.float32(0.4)
    bad2 = tmp_path / "diag.npz"
    np.savez_compressed(bad2, ld=baddiag, variant_ids=np.array(["x"] * n),
                        rsids=np.array([""] * n), allele_freq=np.zeros(n, "float32"),
                        lower_triangular=np.array([False]))
    ok2, reason2 = drv.content_verify_npz(bad2, mode="square")
    assert ok2 is False and reason2


def test_content_verify_banded_accepts_lower_triangular(tmp_path):
    """A banded npz (lower_triangular flag True, strict upper all zero, unit
    diagonal) ACCEPTS — proves the bounded strict-upper check is behavior-
    preserving on the accept path."""
    n = 8
    m = np.tril(_symmetric_corr(n))  # lower-triangular, unit diagonal preserved
    banded = tmp_path / "banded_good.npz"
    np.savez_compressed(banded, ld=m, variant_ids=np.array(["x"] * n),
                        rsids=np.array([""] * n), allele_freq=np.zeros(n, "float32"),
                        lower_triangular=np.array([True]))
    ok, _ = drv.content_verify_npz(banded, mode="banded")
    assert ok is True


def test_content_verify_banded_rejects_nonzero_strict_upper(tmp_path):
    """A banded npz with a nonzero strict-upper entry REJECTS with the
    BYTE-IDENTICAL reason string (guards the bounded-helper swap against drift)."""
    n = 8
    m = np.tril(_symmetric_corr(n))
    m[0, n - 1] = np.float32(0.3)  # nonzero strict-upper entry
    banded = tmp_path / "banded_bad.npz"
    np.savez_compressed(banded, ld=m, variant_ids=np.array(["x"] * n),
                        rsids=np.array([""] * n), allele_freq=np.zeros(n, "float32"),
                        lower_triangular=np.array([True]))
    ok, reason = drv.content_verify_npz(banded, mode="banded")
    assert ok is False
    assert reason == "banded npz has non-zero strict upper triangle"


def test_one_bad_region_does_not_abort_loop(tmp_path, monkeypatch):
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "regBAD", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
        {"region_id": "regOK", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"

    mock = _MockPlink(bim, corrupt_regions={"regBAD"})
    monkeypatch.setattr(drv, "_run_plink", mock)
    res = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")

    by_id = {r["region_id"]: r for r in res}
    # The corrupt region is rejected (either at conversion -> 'error: ...' or at the
    # content-verify gate -> 'verify_failed'); EITHER way it is a non-ok failure and
    # the loop did NOT abort. The clean region still completed + banked.
    bad_status = by_id["regBAD"]["status"]
    assert bad_status == "verify_failed" or bad_status.startswith("error")
    assert bad_status != "ok"
    assert by_id["regOK"]["status"] == "ok"
    assert (out_dir / "regOK.npz").is_file()  # clean region still banked
    assert not (out_dir / "regBAD.npz").is_file()  # corrupt region not banked


# --------------------------------------------------------------------------- #
# 4. panel TSV append is resume-safe                                          #
# --------------------------------------------------------------------------- #

def test_panel_tsv_append_resume_safe(tmp_path, monkeypatch):
    import pandas as pd
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "regA", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
        {"region_id": "regB", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"
    panel = out_dir / "m3-W2-native-plink-panel.tsv"

    mock = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock)
    drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square", panel_tsv=panel)
    monkeypatch.setattr(drv, "_run_plink", _MockPlink(bim))
    drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square", panel_tsv=panel)

    df = pd.read_csv(panel, sep="\t")
    assert list(df.columns) == [
        "region_id", "chr", "n_var", "wall_min", "peak_ram_gib", "output_gib", "status",
        "n_dropped_occluded",  # m3-07b: occlusion span-filter drop-count provenance
        "n_dropped_monomorphic",  # 260701-qcy hardening H2: drop-count provenance
    ]
    # exactly one row per region (no duplicates after the re-skip pass)
    assert sorted(df["region_id"].tolist()) == ["regA", "regB"]
    # header appears exactly once in the raw file
    raw = panel.read_text().splitlines()
    assert sum(1 for ln in raw if ln.startswith("region_id\t")) == 1


# --------------------------------------------------------------------------- #
# 5. --keep-allele-order on every issued command (T-M3-02e-SIGN)              #
# --------------------------------------------------------------------------- #

def test_keep_allele_order_on_every_issued_command(tmp_path, monkeypatch):
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "regA", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
        {"region_id": "regB", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"
    mock = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock)
    drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")

    assert len(mock.calls) == 2
    for argv in mock.calls:
        assert "--keep-allele-order" in argv
        # matches build_plink_ld_command output -> not a hand-rolled argv
        assert argv[0] == "plink1.9"
        assert "--r" in argv
        assert "--bfile" in argv


def test_keep_allele_order_came_from_helper():
    """The driver must obtain its argv via build_plink_ld_command and must NOT
    hardcode the plink argv. AST guard: ``--keep-allele-order`` may appear only in
    the module docstring (prose), NEVER as a code-level string constant (which is
    what a hand-rolled argv would use)."""
    src = (_SRC_PYTHON / "run_native_ld_panel.py").read_text()
    assert "build_plink_ld_command" in src

    tree = ast.parse(src)
    # Collect every docstring node (module/function/class) — docstring PROSE may
    # mention the flag; a hand-rolled argv would put it in a NON-docstring string.
    docstring_nodes = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and \
                    isinstance(body[0].value, ast.Constant) and \
                    isinstance(body[0].value.value, str):
                docstring_nodes.add(id(body[0].value))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in docstring_nodes:
                continue  # docstring prose is allowed
            assert "--keep-allele-order" not in node.value, (
                "driver hand-rolled --keep-allele-order in a code string; it must "
                "come ONLY from build_plink_ld_command"
            )


# --------------------------------------------------------------------------- #
# 6. AFR-only filtering                                                       #
# --------------------------------------------------------------------------- #

def test_filters_to_afr_only(tmp_path, monkeypatch):
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "afr1", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
        {"region_id": "eur1", "chr": chrom, "ancestry": "EUR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
        {"region_id": "afr2", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"
    mock = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock)
    res = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square", ancestry="AFR")

    processed = {r["region_id"] for r in res}
    assert processed == {"afr1", "afr2"}
    assert not (out_dir / "eur1.npz").exists()


# --------------------------------------------------------------------------- #
# 7. retired-Hail-path boundary + no hardcoded abs paths (Task 2 guards)      #
# --------------------------------------------------------------------------- #

def test_driver_does_not_touch_retired_hail_path():
    """The driver imports aou_ld_panel ONLY for _existing_region_npz +
    build_plink_ld_command; it must NOT reference the retired Hail A.3 markers
    (mirrors test_afr_native_path_does_not_route_through_retired_a3)."""
    src = (_SRC_PYTHON / "run_native_ld_panel.py").read_text()
    for marker in ("compute_region_ld", "_write_a3_banded_correlation_bm",
                   "row_correlation", "ld_matrix"):
        assert marker not in src, (
            f"driver must not reference retired Hail A.3 marker {marker!r}"
        )


def test_no_hardcoded_abs_paths():
    """REQ-PATH-PARAMETERIZATION: no /share|/rs1|/gpfs_common literals."""
    src = (_SRC_PYTHON / "run_native_ld_panel.py").read_text()
    for bad in ("/share/clintonlab", "/rs1/researchers", "/gpfs_common"):
        assert bad not in src, f"hardcoded path {bad} in run_native_ld_panel.py"


# --------------------------------------------------------------------------- #
# 8. static index-sharding for the 8-VM Spot fan-out (follow-up)              #
# --------------------------------------------------------------------------- #

def _write_276_afr_manifest(path: Path, chrom: int = 12, bp0: int = 53_000_000):
    """276 AFR rows (mirrors config/ld_regions.tsv AFR count), with a few EUR rows
    interleaved so the AFR-filter-then-shard ordering is exercised. Each AFR row
    gets its own non-overlapping window so the regions are distinguishable."""
    import pandas as pd
    cols = ["region_id", "chr", "ancestry", "window_start_grch38", "window_end_grch38"]
    rows = []
    for i in range(276):
        start = bp0 + i * 10_000
        rows.append({
            "region_id": f"afr_{i:03d}", "chr": chrom, "ancestry": "AFR",
            "window_start_grch38": start, "window_end_grch38": start + 5_000,
        })
        if i % 40 == 0:  # sprinkle EUR rows that must be filtered out before sharding
            estart = bp0 + 5_000_000 + i * 10_000
            rows.append({
                "region_id": f"eur_{i:03d}", "chr": chrom, "ancestry": "EUR",
                "window_start_grch38": estart, "window_end_grch38": estart + 5_000,
            })
    pd.DataFrame(rows, columns=cols).to_csv(path, sep="\t", index=False)


def _shard_region_ids(manifest, num_shards, shard_index, ancestry="AFR"):
    """Return the region_ids a given shard would PROCESS, without running plink
    (uses the driver's pure partition helper)."""
    return drv.select_shard_region_ids(
        manifest, num_shards=num_shards, shard_index=shard_index, ancestry=ancestry,
    )


def test_sharding_partitions_disjoint_and_exhaustive(tmp_path):
    """num_shards=8 over the 276 AFR regions: the 8 shards' region sets are
    pairwise-disjoint AND their union == all 276 (no region dropped, none doubled)."""
    manifest = tmp_path / "regions.tsv"
    _write_276_afr_manifest(manifest)

    full = set(_shard_region_ids(manifest, 1, 0))
    assert len(full) == 276

    shards = [set(_shard_region_ids(manifest, 8, i)) for i in range(8)]
    union = set().union(*shards)
    assert union == full                      # exhaustive
    assert sum(len(s) for s in shards) == 276  # pairwise-disjoint (no overlap)
    for a in range(8):
        for b in range(a + 1, 8):
            assert shards[a].isdisjoint(shards[b])
    # static idx % num_shards == shard_index assignment (round-robin balance)
    assert all(33 <= len(s) <= 36 for s in shards)


def test_sharding_index_out_of_range_raises(tmp_path):
    manifest = tmp_path / "regions.tsv"
    _write_276_afr_manifest(manifest)
    bfile, bim, _ = _setup_cohort(tmp_path)
    for bad_idx, n in [(8, 8), (-1, 8), (3, 3), (0, 0)]:
        with pytest.raises(ValueError):
            drv.run_native_ld_panel(
                manifest, bfile, tmp_path / "out", mode="square",
                num_shards=n, shard_index=bad_idx,
            )


def test_num_shards_one_processes_all_regions(tmp_path, monkeypatch):
    """Regression: default num_shards=1 / shard_index=0 processes every AFR region
    (existing single-VM behavior unchanged)."""
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "afr1", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
        {"region_id": "afr2", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
        {"region_id": "afr3", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"
    mock = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock)
    # explicit defaults
    res = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square",
                                  num_shards=1, shard_index=0)
    assert {r["region_id"] for r in res} == {"afr1", "afr2", "afr3"}
    assert len(mock.calls) == 3


def test_shards_share_resume_guard_across_distinct_panel_tsvs(tmp_path, monkeypatch):
    """Two shards pointed at the SAME out_dir but DIFFERENT --panel-tsv: a region
    banked by shard 0 is skipped by ANY shard that later looks at it, because the
    _existing_region_npz guard consults the SHARED out_dir (resume is global, NOT
    per-shard) while each shard writes its own panel TSV (no concurrent-append
    corruption)."""
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    # 2 AFR regions; with num_shards=2: afr_a -> shard 0, afr_b -> shard 1
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "afr_a", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
        {"region_id": "afr_b", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "shared_out"           # SHARED across shards
    panel0 = tmp_path / "panel.shard0.tsv"
    panel1 = tmp_path / "panel.shard1.tsv"

    # shard 0 computes its partition (afr_a) into the shared out_dir
    mock0 = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock0)
    res0 = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square",
                                   num_shards=2, shard_index=0, panel_tsv=panel0)
    assert {r["region_id"] for r in res0} == {"afr_a"}  # only its partition
    assert (out_dir / "afr_a.npz").is_file()
    assert not (out_dir / "afr_b.npz").exists()

    # shard 1 computes its partition (afr_b) into the SAME shared out_dir
    mock1 = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock1)
    res1 = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square",
                                   num_shards=2, shard_index=1, panel_tsv=panel1)
    assert {r["region_id"] for r in res1} == {"afr_b"}
    assert (out_dir / "afr_b.npz").is_file()

    # Distinct panel TSVs (no shared-append corruption); the resume guard is GLOBAL:
    # re-running shard 0 now skips afr_a (banked) with zero plink work because it
    # consults the shared out_dir, not panel0.
    mock0b = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock0b)
    res0b = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square",
                                    num_shards=2, shard_index=0, panel_tsv=panel0)
    assert len(mock0b.calls) == 0
    assert all(r["status"] == "skipped_idempotent" for r in res0b)
    assert panel0.exists() and panel1.exists()  # each shard wrote its OWN TSV


def test_sharding_args_in_main_signature():
    """main() exposes --num-shards / --shard-index / --panel-tsv for the 8-VM fan-out."""
    src = (_SRC_PYTHON / "run_native_ld_panel.py").read_text()
    for flag in ("--num-shards", "--shard-index", "--panel-tsv"):
        assert flag in src, f"main() must expose {flag}"


# --------------------------------------------------------------------------- #
# 9. durable gs:// out-dir (Dataproc bucket-first; local disk dies w/ cluster) #
# --------------------------------------------------------------------------- #

class _MockGsutil:
    """Monkeypatch target for drv._run_gsutil. Emulates a bucket as an in-memory
    dict {gs_uri: size_bytes}. Records every gsutil argv. Supports the two verbs
    the driver uses: `stat <uri>` (-> Content-Length) and `cp <src> <dst>`."""

    def __init__(self, *, prestaged: dict | None = None, stat_error_uris=None):
        self.objects: dict[str, int] = dict(prestaged or {})
        self.stat_error_uris = set(stat_error_uris or [])
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str]):
        import subprocess as _sp
        self.calls.append(list(args))
        verb = args[0]
        if verb == "stat":
            uri = args[1]
            if uri in self.stat_error_uris or uri not in self.objects:
                # gsutil stat exits non-zero on a missing object
                raise _sp.CalledProcessError(1, ["gsutil", *args], output="", stderr="No URL matched")
            size = self.objects[uri]
            out = (
                f"{uri}:\n"
                f"    Creation time:          Tue, 24 Jun 2026 00:00:00 GMT\n"
                f"    Content-Length:         {size}\n"
                f"    Content-Type:           application/octet-stream\n"
            )
            return _sp.CompletedProcess(["gsutil", *args], 0, stdout=out, stderr="")
        if verb == "cp":
            src, dst = args[1], args[2]
            self.objects[dst] = Path(src).stat().st_size  # "upload" -> record size
            return _sp.CompletedProcess(["gsutil", *args], 0, stdout="", stderr="")
        raise AssertionError(f"unexpected gsutil verb {verb!r}")


def test_gs_out_dir_uploads_verified_npz(tmp_path, monkeypatch):
    """gs:// out-dir: after a region verifies, the driver uploads the .npz (and the
    .afreq sidecar if present) to the bucket via gsutil cp; the .bed/.bim/.fam are
    NEVER uploaded."""
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "afr1", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    gs_out = "gs://test-bucket/ld/AFR_aou"
    scratch = tmp_path / "scratch"

    mock_plink = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock_plink)
    mock_gs = _MockGsutil()
    monkeypatch.setattr(drv, "_run_gsutil", mock_gs)

    res = drv.run_native_ld_panel(manifest, bfile, gs_out, mode="square",
                                  scratch_dir=scratch)
    assert res[0]["status"] == "ok"

    cp_dsts = [c[2] for c in mock_gs.calls if c[0] == "cp"]
    assert f"{gs_out}/afr1.npz" in cp_dsts          # the verified .npz was uploaded
    # NO individual-level genotype upload
    for dst in cp_dsts:
        assert not dst.endswith((".bed", ".bim", ".fam"))
    # the recorded out URI points at the bucket, not local scratch
    assert res[0]["out"] == f"{gs_out}/afr1.npz"


def test_gs_mode_reclaims_region_scratch(tmp_path, monkeypatch):
    """gs:// out-dir: after a region's verified .npz is uploaded to the bucket, its
    bulky LOCAL scratch ({region_id}.ld.bin ~ n_var^2 f32 + the local .npz) is
    DELETED so a long serial panel can't fill the disk. The bucket copy is the
    durable deliverable; the cohort bfile (outside scratch) is untouched."""
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "afr1", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    gs_out = "gs://test-bucket/ld/AFR_aou"
    scratch = tmp_path / "scratch"
    monkeypatch.setattr(drv, "_run_plink", _MockPlink(bim))
    monkeypatch.setattr(drv, "_run_gsutil", _MockGsutil())

    res = drv.run_native_ld_panel(manifest, bfile, gs_out, mode="square",
                                  scratch_dir=scratch)
    assert res[0]["status"] == "ok"
    leftovers = sorted(p.name for p in scratch.glob("afr1.*"))
    assert leftovers == [], f"per-region scratch not reclaimed: {leftovers}"


def test_local_mode_keeps_npz_but_drops_ld_bin(tmp_path, monkeypatch):
    """LOCAL out-dir: the .npz IS the deliverable (kept for the local resume guard),
    but the bulky intermediate .ld.bin is still reclaimed so a long serial panel
    can't fill the disk."""
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "afr1", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"
    monkeypatch.setattr(drv, "_run_plink", _MockPlink(bim))

    res = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")
    assert res[0]["status"] == "ok"
    assert (out_dir / "afr1.npz").is_file()            # deliverable kept
    assert not (out_dir / "afr1.ld.bin").exists()      # intermediate reclaimed


def test_gs_resume_skips_when_object_meets_floor(tmp_path, monkeypatch):
    """gs:// resume-check consults the BUCKET via gsutil stat: an object whose
    Content-Length >= MED-6 floor short-circuits (zero plink work)."""
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "afr1", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    gs_out = "gs://test-bucket/ld/AFR_aou"

    floor = drv.alp._MIN_REGION_NPZ_BYTES
    mock_gs = _MockGsutil(prestaged={f"{gs_out}/afr1.npz": floor + 1000})
    monkeypatch.setattr(drv, "_run_gsutil", mock_gs)
    mock_plink = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock_plink)

    res = drv.run_native_ld_panel(manifest, bfile, gs_out, mode="square",
                                  scratch_dir=tmp_path / "scratch")
    assert len(mock_plink.calls) == 0                 # banked in bucket -> skipped
    assert res[0]["status"] == "skipped_idempotent"


def test_gs_resume_recomputes_when_object_short_or_stat_errors(tmp_path, monkeypatch):
    """A short (< floor) bucket object OR a gsutil stat error -> recompute (the
    MED-6 truncation floor + 'any error = not present' safety)."""
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    gs_out = "gs://test-bucket/ld/AFR_aou"

    # (a) short object < floor -> recompute
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "afr_short", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    floor = drv.alp._MIN_REGION_NPZ_BYTES
    mock_gs = _MockGsutil(prestaged={f"{gs_out}/afr_short.npz": floor - 1})
    monkeypatch.setattr(drv, "_run_gsutil", mock_gs)
    mock_plink = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock_plink)
    res = drv.run_native_ld_panel(manifest, bfile, gs_out, mode="square",
                                  scratch_dir=tmp_path / "s1")
    assert len(mock_plink.calls) == 1                 # short -> recompute
    assert res[0]["status"] == "ok"

    # (b) stat errors (e.g. transient) -> treat as not present -> recompute
    manifest2 = tmp_path / "regions2.tsv"
    _write_manifest(manifest2, [
        {"region_id": "afr_err", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    mock_gs2 = _MockGsutil(stat_error_uris={f"{gs_out}/afr_err.npz"})
    monkeypatch.setattr(drv, "_run_gsutil", mock_gs2)
    mock_plink2 = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock_plink2)
    res2 = drv.run_native_ld_panel(manifest2, bfile, gs_out, mode="square",
                                   scratch_dir=tmp_path / "s2")
    assert len(mock_plink2.calls) == 1                # stat error -> recompute
    assert res2[0]["status"] == "ok"


def test_gs_panel_tsv_uploaded(tmp_path, monkeypatch):
    """A gs:// --panel-tsv is written locally in scratch then uploaded via gsutil cp
    (resume-safe dedup-by-region_id preserved within the local file)."""
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "afr1", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    gs_out = "gs://test-bucket/ld/AFR_aou"
    gs_panel = "gs://test-bucket/ld/AFR_aou/m3-W2-native-plink-panel.tsv"

    mock_plink = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock_plink)
    mock_gs = _MockGsutil()
    monkeypatch.setattr(drv, "_run_gsutil", mock_gs)
    drv.run_native_ld_panel(manifest, bfile, gs_out, mode="square",
                            panel_tsv=gs_panel, scratch_dir=tmp_path / "scratch")

    cp_dsts = [c[2] for c in mock_gs.calls if c[0] == "cp"]
    assert gs_panel in cp_dsts                         # panel TSV uploaded to bucket


def test_local_out_dir_unchanged_no_gsutil(tmp_path, monkeypatch):
    """Regression: a LOCAL --out-dir path never touches gsutil and behaves exactly
    as before (zero _run_gsutil calls)."""
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "afr1", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
        {"region_id": "afr2", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"

    mock_plink = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock_plink)
    # If the local path tries to call gsutil, blow up loudly.
    def _boom(args):
        raise AssertionError(f"local out-dir must not call gsutil; got {args!r}")
    monkeypatch.setattr(drv, "_run_gsutil", _boom)

    res = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")
    assert {r["region_id"] for r in res} == {"afr1", "afr2"}
    assert (out_dir / "afr1.npz").is_file()
    assert (out_dir / "afr2.npz").is_file()


def test_is_gs_uri_helper():
    assert drv._is_gs_uri("gs://bucket/ld") is True
    assert drv._is_gs_uri("/local/path") is False
    assert drv._is_gs_uri(Path("/local/path")) is False


# --------------------------------------------------------------------------- #
# 12. chr-prefix normalization in the window-.bim verify (260628-244)         #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "bim_chrom, manifest_chrom",
    [
        ("chr12", "12"),    # prefixed .bim (AoU GRCh38 export) + bare manifest -> the LIVE bug
        ("12", "chr12"),    # symmetric reverse
        ("chr12", "chr12"),  # both prefixed
        ("12", "12"),       # both bare (pre-existing happy path)
    ],
)
def test_window_bim_n_var_chr_prefix_agnostic(tmp_path, bim_chrom, manifest_chrom):
    """``_window_bim_n_var`` must mirror plink1.9's chr-prefix normalization.

    The AoU GRCh38 cohort ``.bim`` uses ``chr``-prefixed contigs (``chr12``); the
    ``config/ld_regions.tsv`` ``chr`` column is bare numeric (``12``). plink1.9
    normalizes the prefix, so ``--chr 12`` correctly emits the in-window
    ``.ld.bin`` — but a literal ``str(parts[0]) == chrom`` compare yields 0 rows on
    the mismatched-prefix case, so EVERY region fails the ``n_var`` cross-check,
    never banks, and never reclaims its ``.ld.bin`` (the 0/276-banked-after-17h
    scratch-fill live failure). The kept window-``.bim`` content stays VERBATIM
    (downstream ``ld_npz_to_rds.R`` strips a leading ``chr`` before the GWAS join).
    """
    n, bp0 = 20, 53_000_000
    bim = tmp_path / "cohort.bim"
    _write_bim(bim, _default_bim_rows(n, chrom=bim_chrom, bp0=bp0))
    from_bp, to_bp = bp0, bp0 + (n - 1) * 100

    n_var, window_bim = drv._window_bim_n_var(bim, manifest_chrom, from_bp, to_bp)

    assert n_var == n, f"{bim_chrom!r} .bim vs {manifest_chrom!r} manifest -> {n_var} (want {n})"
    kept = [ln for ln in window_bim.read_text().splitlines() if ln.strip()]
    assert len(kept) == n
    # verbatim contig preserved in the written window .bim (not rewritten):
    assert all(ln.split()[0] == str(bim_chrom) for ln in kept)


# --------------------------------------------------------------------------- #
# 13. transient-short-read retry guard (260630-rn4)                           #
# --------------------------------------------------------------------------- #
#
# m3-02e-T4 fire #3 errored region 1 with `n_var mismatch ... window .bim has 0
# rows` while plink had already emitted a correct 102,421-var .ld.bin. Forensics
# proved NO static defect (code md5 authentic, cohort .bim full+stable, driver
# path REPLAYS to window_n_var == bin_n_var == 102421) -> a one-off TRANSIENT
# short read of the cohort .bim by ``_window_bim_n_var``'s ``read_text()`` at the
# instant plink finished writing the 42 GB .ld.bin. A transient must SELF-HEAL
# in-run rather than silently drop a region across an ~11-day serial fire, while
# a GENUINE persistent mismatch must still raise the byte-identical ValueError.


def _throwaway_window_bim(tmp_path: Path) -> Path:
    """A real (empty) .bim path so a stubbed _window_bim_n_var can return a valid Path."""
    p = tmp_path / "throwaway.window.bim"
    p.write_text("")
    return p


def test_retry_wrapper_self_heals_on_transient_zero_and_warns(tmp_path, monkeypatch, capsys):
    """T1: first call returns 0 (transient), retry returns the real count; the
    wrapper recovers, calls the wrapped fn EXACTLY twice, and emits a LOUD
    auditable stderr WARN naming the recovered count / window."""
    monkeypatch.setattr(drv.time, "sleep", lambda *_a, **_k: None)
    tmp_win = _throwaway_window_bim(tmp_path)
    calls = {"n": 0}

    def stub(bim_path, chrom, from_bp, to_bp):
        calls["n"] += 1
        return (0, tmp_win) if calls["n"] == 1 else (102421, tmp_win)

    monkeypatch.setattr(drv, "_window_bim_n_var", stub)

    from_bp, to_bp = 53_000_000, 53_100_000
    n_var, window_bim = drv._window_bim_n_var_retry_on_zero(
        tmp_path / "cohort.bim", "12", from_bp, to_bp, expect_nonzero=True,
    )

    assert n_var == 102421           # recovered on retry
    assert window_bim == tmp_win     # returns the wrapped fn's Path
    assert calls["n"] == 2           # exactly one retry

    captured = capsys.readouterr()
    assert "WARN" in captured.err
    # auditable tokens: the recovered count AND the window from_bp appear
    assert "102421" in captured.err
    assert str(from_bp) in captured.err


def test_retry_wrapper_persistent_zero_preserves_byte_identical_mismatch(tmp_path, monkeypatch):
    """T2: a persistent n_var==0 against a NON-EMPTY square .ld.bin still raises
    the byte-identical ValueError mismatch -> the region records
    ``status='error: ...'`` and the loop continues; the region does NOT bank."""
    monkeypatch.setattr(drv.time, "sleep", lambda *_a, **_k: None)
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "regZERO", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"

    # non-empty square .ld.bin IS written for the region (bin_n_var > 0) ...
    mock = _MockPlink(bim)
    monkeypatch.setattr(drv, "_run_plink", mock)
    # ... but the window count NEVER heals (always 0) -> persistent mismatch.
    tmp_win = _throwaway_window_bim(tmp_path)
    monkeypatch.setattr(drv, "_window_bim_n_var", lambda *_a, **_k: (0, tmp_win))

    res = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")

    by_id = {r["region_id"]: r for r in res}
    status = by_id["regZERO"]["status"]

    # bin_n_var recomputed the SAME way the driver does, from the written .ld.bin
    region_id = "regZERO"
    ld_bin = out_dir / f"{region_id}.ld.bin"
    if not ld_bin.is_file():
        # gs-mode/scratch layouts aside, local square writes {region_id}.ld.bin
        # next to the compute prefix; fall back to the mock's known write path.
        ld_bin = next(out_dir.rglob(f"{region_id}.ld.bin"))
    bin_n_var = drv._n_var_from_ld_bin(ld_bin)

    expected = (
        f"n_var mismatch for {region_id}: .ld.bin implies {bin_n_var} but the "
        f"window .bim has 0 rows — the .ld.bin and the [{from_bp},{to_bp}] window "
        f"must agree."
    )
    assert status.startswith("error:")
    assert expected in status
    # region did NOT bank a .npz
    assert not (out_dir / f"{region_id}.npz").is_file()


def test_retry_wrapper_nonzero_first_call_no_retry_no_warn(tmp_path, monkeypatch, capsys):
    """T3: a legit nonzero on the first (and only) call does NOT retry and emits
    NO WARN."""
    monkeypatch.setattr(drv.time, "sleep", lambda *_a, **_k: None)
    tmp_win = _throwaway_window_bim(tmp_path)
    calls = {"n": 0}

    def stub(bim_path, chrom, from_bp, to_bp):
        calls["n"] += 1
        return (20, tmp_win)

    monkeypatch.setattr(drv, "_window_bim_n_var", stub)

    n_var, window_bim = drv._window_bim_n_var_retry_on_zero(
        tmp_path / "cohort.bim", "12", 53_000_000, 53_100_000, expect_nonzero=True,
    )

    assert n_var == 20
    assert calls["n"] == 1  # no retry
    captured = capsys.readouterr()
    assert "WARN" not in captured.err


def test_retry_wrapper_expect_nonzero_false_does_not_spin(tmp_path, monkeypatch):
    """T4: expect_nonzero=False on a legitimately empty window returns 0 with NO
    retry spin (a genuinely empty region must not loop)."""
    monkeypatch.setattr(drv.time, "sleep", lambda *_a, **_k: None)
    tmp_win = _throwaway_window_bim(tmp_path)
    calls = {"n": 0}

    def stub(bim_path, chrom, from_bp, to_bp):
        calls["n"] += 1
        return (0, tmp_win)

    monkeypatch.setattr(drv, "_window_bim_n_var", stub)

    n_var, window_bim = drv._window_bim_n_var_retry_on_zero(
        tmp_path / "cohort.bim", "12", 53_000_000, 53_100_000, expect_nonzero=False,
    )

    assert n_var == 0
    assert calls["n"] == 1  # never spins the retry loop


# --------------------------------------------------------------------------- #
# 14. drop monomorphic (MAC=0-in-AFR) variants via --mac 1 + --write-snplist   #
#     (quick 260701-qcy)                                                        #
# --------------------------------------------------------------------------- #
#
# m3-02e-T4 fire #3 region 1 hit a REAL, reproducible symmetry-check failure:
# ~11 monomorphic (MAC=0-in-AFR) variants make plink --r emit NaN LD (0/0), and
# NaN != NaN breaks read_square_bin's symmetry check. Decision (Carter 2026-07-01):
# DROP MAC=0 variants at the plink step (--mac 1 --nonfounders --write-snplist),
# threading the RETAINED snplist so the .ld.bin, the window .bim, n_var, and the
# .npz variant list all align to the same retained (polymorphic) set.


def _retained_vid(row: tuple) -> str:
    """Canonical vid for a _default_bim_rows tuple: chr:bp:REF:ALT = chr:bp:A2:A1."""
    chrom, _snp, _cm, bp, a1, a2 = row
    return f"{chrom}:{bp}:{a2}:{a1}"


def test_square_command_emits_mac_and_snplist_banded_does_not():
    """(a) build_plink_ld_command SQUARE argv drops MAC=0 (``--mac 1``), counts all
    samples (``--nonfounders``), and emits the retained ids (``--write-snplist``),
    while KEEPING ``--keep-allele-order`` and ``--r square bin4``. The BANDED argv
    does NOT gain ``--mac`` / ``--write-snplist`` / ``--nonfounders`` (the fire runs
    square only; banded is out of scope)."""
    import aou_ld_panel as alp

    sq = alp.build_plink_ld_command(
        bfile_prefix="cohort", chrom=1, from_bp=1, to_bp=100,
        out_prefix="m2_region_00001", mode="square",
    )
    assert "--mac" in sq and sq[sq.index("--mac") + 1] == "1"
    assert "--nonfounders" in sq
    assert "--write-snplist" in sq
    assert "--keep-allele-order" in sq
    ri = sq.index("--r")
    assert sq[ri:ri + 3] == ["--r", "square", "bin4"]

    bd = alp.build_plink_ld_command(
        bfile_prefix="cohort", chrom=1, from_bp=1, to_bp=100,
        out_prefix="r", mode="banded",
    )
    assert "--mac" not in bd
    assert "--write-snplist" not in bd
    assert "--nonfounders" not in bd
    assert "--keep-allele-order" in bd  # sign-correctness flag unchanged on banded


def test_process_region_drops_monomorphic_and_aligns_npz(tmp_path, monkeypatch):
    """(b) process_region on a window with k=2 designated monomorphic variants ->
    status==ok, n_var == retained (N-k), the produced .npz variant/rsid lists ==
    the RETAINED set in snplist order, and the LD matrix is (N-k)^2 with NO NaN."""
    n, chrom, bp0 = 20, 12, 53_000_000
    bim = tmp_path / "cohort.bim"
    rows = _default_bim_rows(n, chrom=chrom, bp0=bp0)
    _write_bim(bim, rows)
    bfile = str(tmp_path / "cohort")
    from_bp, to_bp = bp0, bp0 + (n - 1) * 100

    mono = {"rs1005", "rs1012"}  # drop rows at in-window indices 5 and 12
    retained_rows = [r for r in rows if r[1] not in mono]
    retained_snps = [r[1] for r in retained_rows]
    retained_vids = [_retained_vid(r) for r in retained_rows]

    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "afr1", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"

    monkeypatch.setattr(drv, "_run_plink", _MockPlink(bim, mono_snps=mono))
    res = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")

    r0 = res[0]
    assert r0["status"] == "ok"
    assert r0["n_var"] == n - len(mono) == 18

    z = np.load(out_dir / "afr1.npz", allow_pickle=True)
    assert z["ld"].shape == (18, 18)
    assert not np.isnan(z["ld"]).any()          # monomorphic NaN rows are GONE
    assert list(z["rsids"]) == retained_snps     # retained ids, in snplist order
    assert list(z["variant_ids"]) == retained_vids
    assert "rs1005" not in set(z["rsids"])       # the dropped monomorphic vars
    assert "rs1012" not in set(z["rsids"])


def test_retained_window_bim_reorders_to_snplist(tmp_path):
    """(c) _retained_window_bim intersects the RAW in-window .bim with the plink
    .snplist, RE-ORDERED to snplist (== .ld.bin) order, returning (n_retained,
    path). A snplist that both subsets AND reorders the raw window proves the
    row order follows the snplist, not the raw .bim."""
    n, chrom, bp0 = 8, 12, 53_000_000
    rows = _default_bim_rows(n, chrom=chrom, bp0=bp0)
    raw_bim = tmp_path / "cohort.12_win.window.bim"
    _write_bim(raw_bim, rows)

    # snplist: drop rs1003, and deliberately REORDER (not raw .bim order)
    snplist_order = ["rs1005", "rs1000", "rs1007", "rs1002", "rs1001", "rs1006", "rs1004"]
    snplist = tmp_path / "afr1.snplist"
    snplist.write_text("".join(f"{s}\n" for s in snplist_order))

    n_ret, ret_bim = drv._retained_window_bim(raw_bim, snplist)

    assert n_ret == len(snplist_order) == 7
    kept = [ln.split() for ln in ret_bim.read_text().splitlines() if ln.strip()]
    assert [r[1] for r in kept] == snplist_order   # row order == snplist order
    assert "rs1003" not in {r[1] for r in kept}    # dropped variant absent


def test_square_path_still_routes_through_transient_guard(tmp_path, monkeypatch):
    """(e) GUARD-PRESERVATION integration test (checker warning 1): with k=2
    monomorphic dropped, a process_region SQUARE call whose RAW window .bim read
    returns 0 on the FIRST attempt then the real count on retry (a transient short
    read) STILL self-heals THROUGH the 27af416 retry guard AND threads the retained
    snplist -> status==ok with n_var == retained (N-k). If the fix had bypassed the
    guard, the first-attempt 0 would intersect to 0 retained and raise the n_var
    mismatch (status error) instead of healing."""
    monkeypatch.setattr(drv.time, "sleep", lambda *_a, **_k: None)
    n, chrom, bp0 = 20, 12, 53_000_000
    bim = tmp_path / "cohort.bim"
    _write_bim(bim, _default_bim_rows(n, chrom=chrom, bp0=bp0))
    bfile = str(tmp_path / "cohort")
    from_bp, to_bp = bp0, bp0 + (n - 1) * 100
    mono = {"rs1005", "rs1012"}

    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "afr1", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"
    monkeypatch.setattr(drv, "_run_plink", _MockPlink(bim, mono_snps=mono))

    # Wrap the REAL _window_bim_n_var so the FIRST call short-reads to 0 (transient)
    # and the retry returns the true raw window .bim -> the guard must heal it, then
    # _retained_window_bim subsets to the retained set.
    real_wbnv = drv._window_bim_n_var
    state = {"n": 0}

    def flaky(bim_path, chrom_, from_bp_, to_bp_):
        state["n"] += 1
        real_n, real_bim = real_wbnv(bim_path, chrom_, from_bp_, to_bp_)
        if state["n"] == 1:
            empty = tmp_path / "transient_empty.window.bim"
            empty.write_text("")
            return (0, empty)          # transient short read
        return (real_n, real_bim)

    monkeypatch.setattr(drv, "_window_bim_n_var", flaky)

    res = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")

    assert state["n"] >= 2                       # the guard DID retry (self-heal)
    assert res[0]["status"] == "ok"              # healed + threaded, not an error
    assert res[0]["n_var"] == n - len(mono) == 18


# --------------------------------------------------------------------------- #
# 15. drop-monomorphic HARDENING (260701-qcy blast-radius D1+D2, D4)          #
# --------------------------------------------------------------------------- #
#
# H1 (blast-radius D1+D2): a DUPLICATE col-2 (SNP id) in the RAW window .bim that
#   the snplist references would SILENTLY misalign LD rows against variant ids —
#   n_var still matches and the matrix is still symmetric, so NO existing guard
#   catches it. _retained_window_bim must FAIL LOUD (ValueError naming region+id)
#   instead of first-occurrence-wins misalignment. Production hl.export_plink
#   varids chr:pos:ref:alt ARE unique, so this never trips on the real cohort.
# H2 (blast-radius D4): the per-region monomorphic-drop count was computed then
#   DISCARDED. Make it durable: a new appended panel column n_dropped_monomorphic
#   + a LOUD per-region stderr line (plink's own .log is reclaimed).


def test_retained_window_bim_raises_on_duplicate_snp_id(tmp_path):
    """(H1-i) A DUPLICATE col-2 id in the RAW window .bim that the snplist references
    would SILENTLY misalign LD rows against variant ids (n_var still matches, the
    matrix is still symmetric -> no existing guard catches it). _retained_window_bim
    must RAISE a clear ValueError naming the region + the offending id instead."""
    chrom, bp0 = 12, 53_000_000
    # two DISTINCT bp share the SAME col-2 id "rsDUP" -> ambiguous LD-row alignment
    rows = [
        (chrom, "rs1000", 0, bp0 + 0, "A", "T"),
        (chrom, "rsDUP", 0, bp0 + 100, "A", "T"),
        (chrom, "rsDUP", 0, bp0 + 200, "A", "T"),   # duplicate col-2 id, distinct bp
        (chrom, "rs1003", 0, bp0 + 300, "A", "T"),
    ]
    raw_bim = tmp_path / "cohort.12_win.window.bim"
    _write_bim(raw_bim, rows)
    snplist = tmp_path / "afr_dup.snplist"
    snplist.write_text("rs1000\nrsDUP\nrs1003\n")   # references the ambiguous id

    with pytest.raises(ValueError) as ei:
        drv._retained_window_bim(raw_bim, snplist, region_id="afr_dup")
    msg = str(ei.value)
    assert "afr_dup" in msg          # names the region
    assert "rsDUP" in msg            # names the offending id


def test_retained_window_bim_unique_ids_do_not_false_trip(tmp_path):
    """(H1-ii) Regression: the duplicate-id assertion must NOT false-trip on the
    normal UNIQUE-id case — it returns the correct (n_retained, .bim) in snplist
    order with NO raise even when region_id is threaded (production
    chr:pos:ref:alt varids are unique)."""
    n, chrom, bp0 = 8, 12, 53_000_000
    rows = _default_bim_rows(n, chrom=chrom, bp0=bp0)
    raw_bim = tmp_path / "cohort.12_win.window.bim"
    _write_bim(raw_bim, rows)
    snplist_order = ["rs1005", "rs1000", "rs1007", "rs1002", "rs1004"]  # subset+reorder
    snplist = tmp_path / "afr_uniq.snplist"
    snplist.write_text("".join(f"{s}\n" for s in snplist_order))

    n_ret, ret_bim = drv._retained_window_bim(raw_bim, snplist, region_id="afr_uniq")
    assert n_ret == len(snplist_order) == 5
    kept = [ln.split() for ln in ret_bim.read_text().splitlines() if ln.strip()]
    assert [r[1] for r in kept] == snplist_order    # order == snplist, no false raise


def test_panel_columns_include_n_dropped_monomorphic():
    """(H2-iv) The new provenance column is APPENDED to _PANEL_COLUMNS (existing
    columns keep their exact leading order/positions; append-only)."""
    assert "n_dropped_monomorphic" in drv._PANEL_COLUMNS
    assert drv._PANEL_COLUMNS[:7] == [
        "region_id", "chr", "n_var", "wall_min", "peak_ram_gib", "output_gib", "status",
    ]
    assert drv._PANEL_COLUMNS[-1] == "n_dropped_monomorphic"


def test_process_region_records_n_dropped_monomorphic(tmp_path, monkeypatch):
    """(H2-iii) process_region on a window with k=2 monomorphic -> the result dict
    records n_dropped_monomorphic == raw_window - retained == 2 (the drop count is
    now durable provenance, blast-radius D4)."""
    n, chrom, bp0 = 20, 12, 53_000_000
    bim = tmp_path / "cohort.bim"
    _write_bim(bim, _default_bim_rows(n, chrom=chrom, bp0=bp0))
    bfile = str(tmp_path / "cohort")
    from_bp, to_bp = bp0, bp0 + (n - 1) * 100
    mono = {"rs1005", "rs1012"}

    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "afr1", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"
    monkeypatch.setattr(drv, "_run_plink", _MockPlink(bim, mono_snps=mono))
    res = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")

    assert res[0]["status"] == "ok"
    assert res[0]["n_dropped_monomorphic"] == 2
    assert res[0]["n_var"] == n - 2 == 18


def test_process_region_logs_drop_to_stderr(tmp_path, monkeypatch, capsys):
    """(H2-v) When n_dropped > 0 the square path emits a LOUD per-region stderr line
    (plink's own .log is reclaimed, so the drop must be visible in the run log)."""
    n, chrom, bp0 = 20, 12, 53_000_000
    bim = tmp_path / "cohort.bim"
    _write_bim(bim, _default_bim_rows(n, chrom=chrom, bp0=bp0))
    bfile = str(tmp_path / "cohort")
    from_bp, to_bp = bp0, bp0 + (n - 1) * 100
    mono = {"rs1005", "rs1012"}

    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "afr1", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"
    monkeypatch.setattr(drv, "_run_plink", _MockPlink(bim, mono_snps=mono))
    drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")

    err = capsys.readouterr().err
    assert "afr1" in err
    assert "dropped 2 monomorphic" in err


def test_skip_and_error_result_dicts_carry_none_drop_count(tmp_path, monkeypatch):
    """(H2-vi) Schema consistency: the skip-idempotent AND error result dicts BOTH
    carry n_dropped_monomorphic=None (no drop happened / not computed), so
    append_panel_row writes a consistent schema with NO KeyError."""
    monkeypatch.setattr(drv.time, "sleep", lambda *_a, **_k: None)
    bfile, bim, (chrom, from_bp, to_bp) = _setup_cohort(tmp_path)

    # (a) skip-idempotent: run once, then re-run -> the second result is a skip, None.
    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "afr1", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"
    monkeypatch.setattr(drv, "_run_plink", _MockPlink(bim))
    drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")
    monkeypatch.setattr(drv, "_run_plink", _MockPlink(bim))
    res_skip = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")
    assert res_skip[0]["status"] == "skipped_idempotent"
    assert res_skip[0]["n_dropped_monomorphic"] is None

    # (b) error: a persistent zero-row window .bim vs a NON-empty .ld.bin raises the
    # n_var mismatch BEFORE the drop count is computed -> the init/error dict is None.
    manifest2 = tmp_path / "regions2.tsv"
    _write_manifest(manifest2, [
        {"region_id": "regERR", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir2 = tmp_path / "out2"
    monkeypatch.setattr(drv, "_run_plink", _MockPlink(bim))
    tmp_win = _throwaway_window_bim(tmp_path)
    monkeypatch.setattr(drv, "_window_bim_n_var", lambda *_a, **_k: (0, tmp_win))
    res_err = drv.run_native_ld_panel(manifest2, bfile, out_dir2, mode="square")
    assert res_err[0]["status"].startswith("error:")
    assert res_err[0]["n_dropped_monomorphic"] is None


def test_banded_result_dict_carries_none_drop_count(tmp_path, monkeypatch):
    """(H2-vi, banded) The BANDED path does not drop MAC=0 variants (``--mac`` /
    ``--write-snplist`` are square-only), so its result dict carries
    n_dropped_monomorphic=None (banded doesn't drop)."""
    n, chrom, bp0 = 12, 12, 53_000_000
    bim = tmp_path / "cohort.bim"
    _write_bim(bim, _default_bim_rows(n, chrom=chrom, bp0=bp0))
    bfile = str(tmp_path / "cohort")
    from_bp, to_bp = bp0, bp0 + (n - 1) * 100

    manifest = tmp_path / "regions.tsv"
    _write_manifest(manifest, [
        {"region_id": "bnd1", "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    out_dir = tmp_path / "out"
    monkeypatch.setattr(drv, "_run_plink", _MockPlink(bim))
    res = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="banded")

    assert res[0]["status"] == "ok"
    assert res[0]["n_dropped_monomorphic"] is None


# --------------------------------------------------------------------------- #
# 16. occlusion span-filter integration (m3-07a Wave 0 — RED)                 #
# --------------------------------------------------------------------------- #
#
# The panel policy pre-registered on OSF (osf.io/az52u, POSTED 2026-07-10T13:32:22Z,
# recorded ac4c990) is: a variant whose LD is structurally undefined because an
# overlapping deletion's REF span occludes it is EXCLUDED — in lockstep, with
# provenance — NEVER zeroed. NaN->0 is DEAD.
#
# These tests are RED until 07b wires the span-filter into the driver. They fail on
# ASSERTIONS (the driver module imports fine), not on collection.
#
# Occlusion rule (SETTLED, geometry verdict `4543dcf4…`):
#   V is OCCLUDED iff ∃ window D with len(REF_D) > 1 and
#   POS_D < POS_V <= POS_D + len(REF_D) − 1.
# Region-1 synthetic fixture -> EXACTLY 5 occluded: {1980475, 5733487, 5922718,
# 7492693, 8375822}. Pair-4 is second-order: 5922718 is occluded by the UPSTREAM
# DEL 5922716, not the downstream DEL 5922724.


def _region1_fixture_module():
    """Load the CANONICAL region-1 `.bim` fixture from test_occlusion_span_filter.py.

    Loaded by file path so it resolves regardless of pytest's package/rootdir import
    mode. Sourcing the single source of truth (rather than re-typing the coordinate
    table here) is the T-m3-07a-02 mitigation: a drifted copy would let a WRONG 07b
    impl pass. Safe to exec — that module's impl imports are all function-local.
    """
    import importlib.util

    path = Path(__file__).with_name("test_occlusion_span_filter.py")
    spec = importlib.util.spec_from_file_location("_m3_occlusion_span_fixture", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _setup_region1_cohort(tmp_path: Path):
    """Cohort .bim/.afreq seeded with the region-1 occlusion topology (chr1, 11 rows:
    7 deletions + 4 SNPs, 5 of which are occluded).

    Returns (bfile_prefix, bim_path, (chrom, from_bp, to_bp), occluded_ids, vid_at).
    """
    fx = _region1_fixture_module()
    rows = list(fx._REGION1_BIM_ROWS)

    bim = tmp_path / "cohort.bim"
    _write_bim(bim, rows)
    _write_af(tmp_path / "cohort.afreq", len(rows))

    def vid_at(bp: int) -> str:
        hits = [r[1] for r in rows if int(r[3]) == bp]
        assert len(hits) == 1
        return hits[0]

    occluded_ids = {vid_at(bp) for bp in fx._REGION1_EXPECTED_OCCLUDED_POS}
    assert len(occluded_ids) == 5
    chrom = int(rows[0][0])
    from_bp, to_bp = 1_980_000, 8_400_000
    return str(tmp_path / "cohort"), bim, (chrom, from_bp, to_bp), occluded_ids, vid_at


def _region1_manifest(path: Path, chrom, from_bp, to_bp, region_id="m2_region_00001"):
    _write_manifest(path, [
        {"region_id": region_id, "chr": chrom, "ancestry": "AFR",
         "window_start_grch38": from_bp, "window_end_grch38": to_bp},
    ])
    return path


def test_driver_writes_occluded_excludelist_with_exactly_the_occluded_ids(tmp_path, monkeypatch):
    """(a) For a cohort seeded with the region-1 topology, the driver writes
    ``{out_prefix}.occluded.excludelist`` containing EXACTLY the 5 occluded ids —
    and NOT the occluding deletions (only the downstream V is excluded). The
    excludelist is durable provenance, not a scratch temp."""
    bfile, bim, (chrom, from_bp, to_bp), occluded_ids, vid_at = _setup_region1_cohort(tmp_path)
    manifest = _region1_manifest(tmp_path / "regions.tsv", chrom, from_bp, to_bp)
    out_dir = tmp_path / "out"

    monkeypatch.setattr(drv, "_run_plink", _MockPlink(bim, nan_snps=occluded_ids))
    drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")

    excl = out_dir / "m2_region_00001.occluded.excludelist"
    assert excl.is_file(), "driver did not write {out_prefix}.occluded.excludelist"
    listed = {ln.strip() for ln in excl.read_text().splitlines() if ln.strip()}
    assert listed == occluded_ids
    # the occluding deletions are KEPT
    for keeper_bp in (1_980_423, 5_733_474, 5_922_716, 5_922_724, 7_492_679, 8_375_794):
        assert vid_at(keeper_bp) not in listed


def test_exclude_reaches_the_plink_argv(tmp_path, monkeypatch):
    """(b) ``--exclude <file>`` reaches the issued plink argv, and the file it names
    is the occluded excludelist carrying exactly the 5 occluded ids."""
    bfile, bim, (chrom, from_bp, to_bp), occluded_ids, _vid_at = _setup_region1_cohort(tmp_path)
    manifest = _region1_manifest(tmp_path / "regions.tsv", chrom, from_bp, to_bp)
    out_dir = tmp_path / "out"

    mock = _MockPlink(bim, nan_snps=occluded_ids)
    monkeypatch.setattr(drv, "_run_plink", mock)
    drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")

    assert len(mock.calls) == 1
    argv = mock.calls[0]
    assert "--exclude" in argv, f"--exclude absent from plink argv: {argv}"
    assert argv[argv.index("--exclude") + 1].endswith(".occluded.excludelist")
    assert mock.exclude_calls == [occluded_ids]


def test_keep_allele_order_still_present_alongside_exclude(tmp_path, monkeypatch):
    """(c) Adding ``--exclude`` must NOT disturb the sign-correctness contract:
    ``--keep-allele-order`` is still on every issued command, the argv still comes
    from build_plink_ld_command, and ``--mac``/``--write-snplist`` survive."""
    bfile, bim, (chrom, from_bp, to_bp), occluded_ids, _vid_at = _setup_region1_cohort(tmp_path)
    manifest = _region1_manifest(tmp_path / "regions.tsv", chrom, from_bp, to_bp)
    out_dir = tmp_path / "out"

    mock = _MockPlink(bim, nan_snps=occluded_ids)
    monkeypatch.setattr(drv, "_run_plink", mock)
    drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")

    for argv in mock.calls:
        assert "--keep-allele-order" in argv
        assert argv[0] == "plink1.9"
        assert "--mac" in argv and "--write-snplist" in argv
        assert "--exclude" in argv


def test_occlusion_filtered_npz_has_no_nan_and_verifies(tmp_path, monkeypatch):
    """(d) THE HEADLINE: with the occluded variants excluded, the region's .npz has
    NO NaN and passes content_verify_npz — and the excluded variants are absent from
    its variant list.

    The mock models the real mechanism: an occluded variant that SURVIVES into the
    LD step makes plink emit a NaN row/col (diagonal 1.0 — the fire-#3 fingerprint).
    So this test is RED today for the RIGHT reason (the unfiltered driver banks NaN
    or errors out), and goes GREEN only once 07b actually excludes them — never by
    zeroing anything. NaN->0 is DEAD.
    """
    bfile, bim, (chrom, from_bp, to_bp), occluded_ids, _vid_at = _setup_region1_cohort(tmp_path)
    manifest = _region1_manifest(tmp_path / "regions.tsv", chrom, from_bp, to_bp)
    out_dir = tmp_path / "out"

    monkeypatch.setattr(drv, "_run_plink", _MockPlink(bim, nan_snps=occluded_ids))
    res = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")

    assert res[0]["status"] == "ok"
    npz = out_dir / "m2_region_00001.npz"
    assert npz.is_file()

    z = np.load(npz, allow_pickle=True)
    assert not np.isnan(z["ld"]).any(), "occluded variants must be EXCLUDED, never zeroed"
    assert z["ld"].shape == (6, 6)                       # 11 raw − 5 occluded
    assert set(z["variant_ids"]) & occluded_ids == set()  # excluded, not present
    ok, reason = drv.content_verify_npz(npz, mode="square")
    assert ok is True, reason


def test_n_dropped_occluded_is_separated_from_n_dropped_monomorphic(tmp_path, monkeypatch):
    """(e) The two drop reasons are DISTINCT provenance columns and must not be
    conflated: a window carrying BOTH an occluded set (5) AND an in-window
    monomorphic variant (1) records n_dropped_occluded==5 and
    n_dropped_monomorphic==1 — each counted in its own column.

    This is the assertion that catches the naive implementation: computing
    n_dropped_monomorphic as (RAW window − retained) would score 6 here. It must be
    computed against the POST-exclude window (6 − 5 == 1).

    del4 (5922724) is chosen as the monomorphic variant precisely because it is
    neither occluded nor an occluder of anything in this window — so the two
    counts cannot overlap.
    """
    bfile, bim, (chrom, from_bp, to_bp), occluded_ids, vid_at = _setup_region1_cohort(tmp_path)
    manifest = _region1_manifest(tmp_path / "regions.tsv", chrom, from_bp, to_bp)
    out_dir = tmp_path / "out"

    mono_id = vid_at(5_922_724)          # a deletion; occludes nothing, not occluded
    assert mono_id not in occluded_ids   # the two drop reasons are disjoint here

    monkeypatch.setattr(
        drv, "_run_plink",
        _MockPlink(bim, mono_snps={mono_id}, nan_snps=occluded_ids),
    )
    res = drv.run_native_ld_panel(manifest, bfile, out_dir, mode="square")

    r0 = res[0]
    assert r0["status"] == "ok"
    assert r0["n_dropped_occluded"] == 5
    assert r0["n_dropped_monomorphic"] == 1     # NOT 6 (raw − retained)
    assert r0["n_var"] == 11 - 5 - 1 == 5


def test_panel_columns_include_n_dropped_occluded():
    """(e-ii) ``n_dropped_occluded`` is APPENDED to _PANEL_COLUMNS as durable panel
    provenance (append-only: the existing leading columns keep their positions, and
    n_dropped_monomorphic is retained)."""
    assert "n_dropped_occluded" in drv._PANEL_COLUMNS
    assert drv._PANEL_COLUMNS[:7] == [
        "region_id", "chr", "n_var", "wall_min", "peak_ram_gib", "output_gib", "status",
    ]
    assert "n_dropped_monomorphic" in drv._PANEL_COLUMNS


def test_no_nan_to_zero_conditioning_in_the_driver():
    """The pre-registered policy is EXCLUSION, never zeroing. The driver must not
    grow a NaN->0 conditioning path: the retired m3-06 conditioning module
    (condition_ld_matrix, FROZEN/HELD) must never be imported or referenced here.
    Mirrors the retired-Hail-A.3 boundary guard."""
    src = (_SRC_PYTHON / "run_native_ld_panel.py").read_text()
    for marker in ("condition_ld_matrix", "write_conditioned_ld_npz", "nan_to_num"):
        assert marker not in src, (
            f"driver must not reference the retired NaN->0 conditioning path: {marker!r}"
        )


# --------------------------------------------------------------------------- #
# 17. panel-TSV header reconciliation (260715-u22 blast-radius P1/P2/P4)      #
# --------------------------------------------------------------------------- #
#
# _append_panel_row_local gated the header on file EXISTENCE only (:481) and read the
# existing TSV ONLY to dedup region_id (:487) — it never compared list(existing.columns)
# to _PANEL_COLUMNS. m3-07b's 8->9 widening ARMED that (the SECOND arming — ed9cfd4
# already did 7->8, so EVERY future panel column re-arms it).
#
# A stale panel TSV at the gs:// path is very likely: append_panel_row at :808 is called
# UNCONDITIONALLY after the per-region try/except, and every June/July fire reached
# region 1 and errored, so those fires DID write panel rows under a 7- or 8-column
# schema. "0/276 banked" does NOT evidence its absence — 0/276 is measured in .npz
# objects, and the .npz (not the panel TSV) gates the resume skip (:605-608).
#
# These tests call the seam DIRECTLY (no plink mock, no _setup_cohort) — it is pure
# pandas. The guard REFUSES; it must never auto-repair a stale file
# ([[feedback_skip_guard_masks_not_fixes]] — a guard that silently repairs HIDES the bug).


def test_append_panel_row_local_raises_on_a_stale_header(tmp_path):
    """A stale (pre-m3-07b, 8-column) panel TSV RAISES instead of appending ragged.

    EMPIRICAL REPRO (pre-fix): the append silently succeeded and produced a file with
    `field counts: [8, 8, 9]` — 9 fields written under an 8-name header. The damage
    lands on the NEXT region: its dedup read (`pd.read_csv` at :487) raises
    `ParserError: Expected 8 fields, saw 9`, UNCAUGHT — `append_panel_row` is called at
    :808, OUTSIDE the per-region try/except, and the main loop wraps `process_region` in
    no try (:930-935). The billed ~11-day fire would ABORT after ~2 regions of compute.

    Fail at region 1 at zero cost instead. The message must be ACTIONABLE: name the
    offending column and tell the operator to rotate the stale file (it is rebuilt from
    the banked per-region .npz, so deleting it costs no compute).
    """
    import pandas as pd

    stale_cols = [c for c in drv._PANEL_COLUMNS if c != "n_dropped_occluded"]
    assert len(stale_cols) == 8, "the real pre-m3-07b panel schema is 8 columns"
    panel = tmp_path / "m3-W2-native-plink-panel.tsv"
    pd.DataFrame(
        [{c: "regA" if c == "region_id" else 1 for c in stale_cols}], columns=stale_cols
    ).to_csv(panel, sep="\t", index=False)

    row = {c: "regB" if c == "region_id" else 1 for c in drv._PANEL_COLUMNS}
    with pytest.raises(ValueError) as exc:
        drv._append_panel_row_local(panel, row)

    msg = str(exc.value)
    assert "n_dropped_occluded" in msg          # names the actual skew
    assert "stale" in msg.lower()               # names the diagnosis
    assert "rotate" in msg.lower() or "delete" in msg.lower()   # actionable


def test_append_panel_row_local_appends_under_a_matching_header(tmp_path):
    """A header MATCHING _PANEL_COLUMNS still appends — the guard must not false-trip.

    The guard's whole value is that it fires ONLY on real skew; a false trip would
    abort a healthy fire. Re-appending the same region must still be a dedup no-op:
    the guard sits upstream of the dedup and must not break resume-safety.
    """
    import pandas as pd

    panel = tmp_path / "m3-W2-native-plink-panel.tsv"
    first = {c: "regA" if c == "region_id" else 1 for c in drv._PANEL_COLUMNS}
    pd.DataFrame([first], columns=drv._PANEL_COLUMNS).to_csv(
        panel, sep="\t", index=False
    )

    second = {c: "regB" if c == "region_id" else 2 for c in drv._PANEL_COLUMNS}
    drv._append_panel_row_local(panel, second)          # must NOT raise

    df = pd.read_csv(panel, sep="\t")
    assert list(df.columns) == drv._PANEL_COLUMNS
    assert sorted(df["region_id"].tolist()) == ["regA", "regB"]
    # header appears exactly once in the raw text
    raw = panel.read_text().splitlines()
    assert sum(1 for ln in raw if ln.startswith("region_id\t")) == 1

    # resume-safety survives the guard: re-appending regB is still a no-op
    drv._append_panel_row_local(panel, second)
    df2 = pd.read_csv(panel, sep="\t")
    assert sorted(df2["region_id"].tolist()) == ["regA", "regB"]
