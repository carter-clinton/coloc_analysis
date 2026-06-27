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
    cohort .bim) and records every argv it received."""

    def __init__(self, bim_path: Path, *, corrupt_regions=None, seed: int = 0):
        self.bim_path = Path(bim_path)
        self.calls: list[list[str]] = []
        self.corrupt_regions = set(corrupt_regions or [])
        self.seed = seed
        self._bim_rows = [ln.split() for ln in self.bim_path.read_text().splitlines() if ln.strip()]

    def _n_var_in_window(self, chrom: str, from_bp: int, to_bp: int) -> int:
        return sum(
            1 for r in self._bim_rows
            if str(r[0]) == str(chrom) and from_bp <= int(r[3]) <= to_bp
        )

    def __call__(self, cmd: list[str]):
        self.calls.append(list(cmd))
        # parse the window + out prefix back out of the argv
        def _arg(flag):
            return cmd[cmd.index(flag) + 1]
        chrom = _arg("--chr")
        from_bp = int(_arg("--from-bp"))
        to_bp = int(_arg("--to-bp"))
        out_prefix = _arg("--out")
        n = self._n_var_in_window(chrom, from_bp, to_bp)
        region_id = Path(out_prefix).name
        m = _symmetric_corr(n, seed=self.seed)
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
