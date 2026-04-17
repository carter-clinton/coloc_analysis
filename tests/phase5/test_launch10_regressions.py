"""Regression tests for T1 Launch10 residual failures (debug: t1-launch10-residual-failures).

Three regressions covered (Launch10 fix batch, commit 030130b):
  1. HESS combine rho-HESS dispatch — verify run_combine() routes to
     local_rhog_step2 when --local-hsqg-est is supplied (test via cmd
     introspection; full HESS subprocess requires Python 2.7 env not in CI).
  2. Dummy allele round-trip — verify munge_sumstats_ldsc.convert_sumstats()
     emits A/G (not A/T) for trait sumstats lacking REF/ALT columns so
     LDSC's filter_alleles() does not drop every SNP.
  3. Legacy import smoke — verify summarize_coloc_results imports cleanly
     as a module (PYTHONPATH shim resolves `from scripts.utils_logging import
     get_logger` when invoked outside a `scripts.` package context).

Launch12 fix batch (this session):
  4. Empty-loci filter — run_hsqg_step2() must drop nsnp==0 / rank==0 loci
     from info/eig/prjsq before invoking hess.py so local_hsqg_step2_helper
     doesn't fail with "Rank of A less than the number of loci".
  5. Subprocess diagnostics — _run_hess_subprocess() must surface stderr +
     stdout + hess.py's own {out}.log on CalledProcessError.
  6. AFR ancestry LDSC frqfile dispatch — _ldsc_frqfile_chr() must return
     the AFR frq prefix when ancestry == "AFR" and the EUR prefix otherwise.
"""
import gzip
import importlib.util
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from run_hess import (  # noqa: E402
    _filter_empty_loci,
    _run_hess_subprocess,
    run_combine,
    run_hsqg_step2,
)
from munge_sumstats_ldsc import convert_sumstats  # noqa: E402


# ---------------------------------------------------------------------------
# Regression 1: HESS combine dispatches local_rhog_step2 with all required args
# ---------------------------------------------------------------------------


def test_run_combine_rho_hess_dispatch(tmp_path):
    """run_combine() with --local-hsqg-est must build a command containing
    --pheno-cor, --num-shared, AND --local-hsqg-est (nargs=2). Without all
    three, HESS's dispatcher (tools/hess/hess.py:83-87) silently routes to
    local_hsqg_step2 which fails with "Missing step 1 results" because
    rho-HESS step 1 writes trait-specific info files as
    ``{prefix}_trait{1,2}_chr{N}.info.gz`` (not ``{prefix}_chr{N}.info.gz``).
    """
    # Create stub files so _validate_path doesn't reject them
    python27_bin = tmp_path / "python2.7"
    python27_bin.write_text("#!/bin/sh\nexit 0\n")
    python27_bin.chmod(0o755)

    hess_script = tmp_path / "hess.py"
    hess_script.write_text("# stub\n")

    hsqg1 = tmp_path / "trait1.local.tsv"
    hsqg1.write_text("chr\tstart\tend\tnum_snp\tk\tlocal_h2g\tvar\tse\tz\tp\n")

    hsqg2 = tmp_path / "trait2.local.tsv"
    hsqg2.write_text("chr\tstart\tend\tnum_snp\tk\tlocal_h2g\tvar\tse\tz\tp\n")

    # Intercept subprocess.run so we don't actually invoke HESS
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        result = mock.Mock()
        result.stdout = ""
        result.stderr = ""
        result.returncode = 0
        return result

    with mock.patch("run_hess.subprocess.run", side_effect=fake_run):
        run_combine(
            hess_script=str(hess_script),
            python27=str(python27_bin),
            prefix=str(tmp_path / "test_pair"),
            out=str(tmp_path / "test_pair_combined"),
            local_hsqg_est1=str(hsqg1),
            local_hsqg_est2=str(hsqg2),
            pheno_cor=0.0,
            num_shared=0,
        )

    cmd = captured["cmd"]
    # Must include all three rho-HESS-specific flags
    assert "--pheno-cor" in cmd, (
        f"rho-HESS dispatch requires --pheno-cor; got {cmd}"
    )
    assert "--num-shared" in cmd, (
        f"rho-HESS dispatch requires --num-shared; got {cmd}"
    )
    assert "--local-hsqg-est1" not in cmd, (
        "Internal flag --local-hsqg-est1 must be translated to HESS's --local-hsqg-est; "
        f"got {cmd}"
    )
    assert "--local-hsqg-est" in cmd, (
        f"rho-HESS dispatch requires --local-hsqg-est; got {cmd}"
    )

    # HESS --local-hsqg-est takes nargs=2: the two file paths must appear
    # immediately after the flag, in trait1,trait2 order
    idx = cmd.index("--local-hsqg-est")
    assert cmd[idx + 1] == str(hsqg1), (
        f"First --local-hsqg-est path must be trait1; got {cmd[idx + 1]}"
    )
    assert cmd[idx + 2] == str(hsqg2), (
        f"Second --local-hsqg-est path must be trait2; got {cmd[idx + 2]}"
    )


def test_run_combine_legacy_path_without_hsqg(tmp_path):
    """When called without --local-hsqg-est1/2, run_combine must retain the
    legacy single-trait-hsqg behaviour (back-compat for callers that haven't
    migrated yet). The command MUST NOT include rho-HESS flags.
    """
    python27_bin = tmp_path / "python2.7"
    python27_bin.write_text("#!/bin/sh\nexit 0\n")
    python27_bin.chmod(0o755)
    hess_script = tmp_path / "hess.py"
    hess_script.write_text("# stub\n")

    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        r = mock.Mock()
        r.stdout = ""
        r.stderr = ""
        return r

    with mock.patch("run_hess.subprocess.run", side_effect=fake_run):
        run_combine(
            hess_script=str(hess_script),
            python27=str(python27_bin),
            prefix=str(tmp_path / "test"),
            out=str(tmp_path / "test_out"),
        )

    cmd = captured["cmd"]
    assert "--pheno-cor" not in cmd, (
        f"Legacy path must not pass --pheno-cor; got {cmd}"
    )
    assert "--local-hsqg-est" not in cmd, (
        f"Legacy path must not pass --local-hsqg-est; got {cmd}"
    )


# ---------------------------------------------------------------------------
# Regression 2: Dummy allele round-trip — A/G not A/T
# ---------------------------------------------------------------------------


# LDSC's strand-unambiguous set — mirror of
# tools/ldsc/ldscore/sumstats.py:VALID_SNPS definition (expanded here so
# this test does NOT import the LDSC module, which pulls in optional deps).
# A SNP a1+a2 is strand-ambiguous if a1 is the Watson-Crick complement of a2:
#   A<->T, C<->G. So AT, TA, CG, GC are ambiguous; all other unequal pairs
#   (AG, GA, AC, CA, GT, TG, CT, TC) are valid.
_LDSC_VALID_ALLELES = {"AG", "GA", "AC", "CA", "GT", "TG", "CT", "TC"}


def test_munge_dummy_alleles_survive_ldsc_filter(tmp_path):
    """munge_sumstats_ldsc.convert_sumstats must emit strand-unambiguous
    dummy alleles when REF/ALT are absent from the harmonized input. This
    prevents LDSC's filter_alleles() from silently dropping all SNPs
    (bmi_EUR failure mode in Launch10: 2.3M SNPs in, 0 out after munge
    because every row had A1=A, A2=T, which filter_alleles removes).
    """
    # Input lacks REF/ALT columns — mimics Yengo 2018 bmi_EUR harmonized output
    in_path = tmp_path / "harm.tsv"
    header = "CHR\tPOS\tSNP\tBETA\tSE\tP\tEAF\tN\n"
    rows = [
        f"22\t16{i:07d}\trs{200000 + i}\t0.1\t0.05\t0.01\t0.3\t50000\n"
        for i in range(20)
    ]
    in_path.write_text(header + "".join(rows))

    out_path = tmp_path / "munged.sumstats.gz"
    stats = convert_sumstats(
        input_path=str(in_path),
        output_path=str(out_path),
    )

    assert stats["n_output"] == 20, (
        f"Expected 20 rows out, got {stats['n_output']} (filter={stats['n_filtered']})"
    )

    # Read output and verify every row has an LDSC-valid allele pair
    with gzip.open(out_path, "rt") as f:
        out_header = f.readline().strip().split("\t")
        a1_idx = out_header.index("A1")
        a2_idx = out_header.index("A2")

        checked = 0
        for line in f:
            fields = line.strip().split("\t")
            pair = fields[a1_idx] + fields[a2_idx]
            assert pair in _LDSC_VALID_ALLELES, (
                f"Row {checked}: dummy allele pair {pair!r} is strand-ambiguous. "
                f"LDSC filter_alleles() will drop this SNP. Use A/G, not A/T."
            )
            checked += 1

        assert checked == 20, f"Expected 20 output rows, read {checked}"


def test_munge_real_alleles_preserved(tmp_path):
    """When REF/ALT are present, convert_sumstats must emit them verbatim
    (not overwrite with dummy alleles). Guards against overzealous default
    behaviour that would erase real allele information.
    """
    in_path = tmp_path / "harm.tsv"
    header = "CHR\tPOS\tSNP\tREF\tALT\tBETA\tSE\tP\tEAF\tN\n"
    rows = [
        f"22\t16{i:07d}\trs{200000 + i}\tC\tT\t0.1\t0.05\t0.01\t0.3\t50000\n"
        for i in range(5)
    ]
    in_path.write_text(header + "".join(rows))

    out_path = tmp_path / "munged.sumstats.gz"
    convert_sumstats(input_path=str(in_path), output_path=str(out_path))

    with gzip.open(out_path, "rt") as f:
        out_header = f.readline().strip().split("\t")
        a1_idx = out_header.index("A1")
        a2_idx = out_header.index("A2")
        first = f.readline().strip().split("\t")
        # ALT->A1 (effect allele), REF->A2
        assert first[a1_idx] == "T", f"Expected A1=T (ALT), got {first[a1_idx]}"
        assert first[a2_idx] == "C", f"Expected A2=C (REF), got {first[a2_idx]}"


# ---------------------------------------------------------------------------
# Regression 3: Legacy summarize_coloc_results import smoke test
# ---------------------------------------------------------------------------


def test_summarize_coloc_results_importable():
    """summarize_coloc_results.py must be importable when invoked directly
    (Snakemake shell: `python ... summarize_coloc_results.py ...`).

    The original Launch10 failure was:
      ModuleNotFoundError: No module named 'scripts'
    at line 15: `from scripts.utils_logging import get_logger`.

    The fix adds a sys.path shim that prepends region_analysis/ so the
    `scripts` package resolves. This test loads the script as a module via
    importlib and asserts it imports without ModuleNotFoundError.
    """
    script_path = (
        PROJECT_ROOT
        / "src"
        / "legacy"
        / "region_analysis"
        / "scripts"
        / "summarize_coloc_results.py"
    )
    assert script_path.exists(), f"Script missing: {script_path}"

    # Invoke as subprocess to mimic the Snakemake invocation context
    # (cwd = project root, no prior sys.path injection).
    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )

    # --help exits 0 and writes to stdout. If the import fails,
    # we get exit 1 with ModuleNotFoundError on stderr.
    assert result.returncode == 0, (
        f"summarize_coloc_results --help failed (exit {result.returncode}). "
        f"stdout: {result.stdout!r}, stderr: {result.stderr!r}"
    )
    assert "ModuleNotFoundError" not in result.stderr, (
        f"ModuleNotFoundError leaked through: {result.stderr}"
    )
    # Sanity check: --help output should mention the manifest arg
    assert "--manifest" in result.stdout, (
        f"Expected --manifest in help output; got: {result.stdout!r}"
    )


def test_summarize_coloc_results_loadable_via_importlib():
    """Additional coverage: the script must also be loadable via importlib
    (same semantics as subprocess, but keeps the test in-process so failures
    surface with full traceback).
    """
    script_path = (
        PROJECT_ROOT
        / "src"
        / "legacy"
        / "region_analysis"
        / "scripts"
        / "summarize_coloc_results.py"
    )

    spec = importlib.util.spec_from_file_location(
        "summarize_coloc_results_under_test", script_path
    )
    module = importlib.util.module_from_spec(spec)

    # Should not raise — the PYTHONPATH shim at the top of the script makes
    # the `scripts` package resolvable before the `from scripts...` line runs.
    spec.loader.exec_module(module)

    # Module surface check: main() and parse_args() should exist
    assert hasattr(module, "main"), "summarize_coloc_results must expose main()"
    assert hasattr(module, "parse_args"), "summarize_coloc_results must expose parse_args()"


# ---------------------------------------------------------------------------
# Regression 4 (Launch12): run_hsqg_step2 filters empty loci before HESS
# ---------------------------------------------------------------------------


def _write_step1_files(prefix, chrom, info_rows, eig_rows, prjsq_rows):
    """Write one chromosome's HESS step1 triplet to {prefix}_chr{chrom}.*.gz.

    ``info_rows`` are 5-tuples (start, stop, nsnp, rank, nindv). Empty loci
    use (start, stop, 0, 0, 0.0) and the matching eig/prjsq rows are empty
    strings (which is exactly what ``local_hsqg_step1_helper`` writes --
    see tools/hess/src/estimation.py:81-82).
    """
    info_path = f"{prefix}_chr{chrom}.info.gz"
    eig_path = f"{prefix}_chr{chrom}.eig.gz"
    prjsq_path = f"{prefix}_chr{chrom}.prjsq.gz"

    with gzip.open(info_path, "wt") as fh:
        for start, stop, nsnp, rank, nindv in info_rows:
            fh.write(f"{start}\t{stop}\t{nsnp}\t{rank}\t{nindv:.1f}\n")
    with gzip.open(eig_path, "wt") as fh:
        for row in eig_rows:
            fh.write(row + "\n")
    with gzip.open(prjsq_path, "wt") as fh:
        for row in prjsq_rows:
            fh.write(row + "\n")


def test_filter_empty_loci_drops_nsnp_zero_and_rank_zero(tmp_path):
    """`_filter_empty_loci` must drop rows where nsnp==0 OR rank==0 and
    keep the info/eig/prjsq triplets line-aligned. The bug (Launch11
    §2026-04-17T21:14Z) was that hess.py's local_hsqg_step2 rejects
    "Rank of A less than the number of loci" when any locus has 0 SNPs --
    HESS writes an empty eig/prjsq line for those loci, guaranteeing
    rank deficiency. Filtering before calling HESS is the fix.
    """
    # Build fixture for 3 chromosomes: chr1 has 1 empty locus, chr2 has 0,
    # chr3 has 2 (one nsnp=0, one rank=0 without nsnp=0 -- possible when
    # LD matrix is singular even for a non-empty SNP block).
    prefix = str(tmp_path / "fake_pair_trait1")

    # chr1: 3 loci, middle one empty
    _write_step1_files(
        prefix, 1,
        info_rows=[
            (0, 1000, 5, 3, 1000.0),
            (1000, 2000, 0, 0, 0.0),       # empty
            (2000, 3000, 8, 5, 1000.0),
        ],
        eig_rows=["1.0\t2.0\t3.0", "", "1.5\t2.5\t3.5\t4.5\t5.5"],
        prjsq_rows=["0.1\t0.2\t0.3", "", "0.15\t0.25\t0.35\t0.45\t0.55"],
    )

    # chr2: 2 loci, both valid
    _write_step1_files(
        prefix, 2,
        info_rows=[
            (0, 500, 4, 2, 1000.0),
            (500, 1500, 6, 4, 1000.0),
        ],
        eig_rows=["0.5\t1.5", "0.8\t1.8\t2.8\t3.8"],
        prjsq_rows=["0.05\t0.15", "0.08\t0.18\t0.28\t0.38"],
    )

    # chr3: 3 loci, first has nsnp=0 and last has rank=0 (with nsnp>0)
    _write_step1_files(
        prefix, 3,
        info_rows=[
            (0, 500, 0, 0, 0.0),            # empty
            (500, 1500, 7, 5, 1000.0),
            (1500, 2500, 3, 0, 1000.0),     # rank=0 but nsnp>0 -- still drop
        ],
        eig_rows=["", "1.1\t2.1\t3.1\t4.1\t5.1", ""],
        prjsq_rows=["", "0.11\t0.21\t0.31\t0.41\t0.51", ""],
    )

    filt_prefix = str(tmp_path / "fake_pair_trait1_filt")
    stats = _filter_empty_loci(prefix, filt_prefix, chromosomes=[1, 2, 3])

    # Per-chromosome counts: chr1 3->2, chr2 2->2, chr3 3->1
    assert stats[1] == {"total": 3, "kept": 2, "dropped": 1}
    assert stats[2] == {"total": 2, "kept": 2, "dropped": 0}
    assert stats[3] == {"total": 3, "kept": 1, "dropped": 2}

    # Verify filtered chr1 info has exactly 2 non-empty rows with matching eig
    with gzip.open(f"{filt_prefix}_chr1.info.gz", "rt") as fh:
        lines = [l.strip() for l in fh if l.strip()]
    assert len(lines) == 2
    # Columns: start, stop, nsnp, rank, nindv — first surviving locus is (0, 1000, 5, 3, 1000.0)
    first = lines[0].split("\t")
    assert int(first[2]) == 5 and int(first[3]) == 3

    with gzip.open(f"{filt_prefix}_chr1.eig.gz", "rt") as fh:
        eig_lines = fh.readlines()
    assert len(eig_lines) == 2
    assert eig_lines[0].strip() == "1.0\t2.0\t3.0"
    assert eig_lines[1].strip() == "1.5\t2.5\t3.5\t4.5\t5.5"

    # chr3 survivors: only the middle locus (nsnp=7, rank=5) should remain
    with gzip.open(f"{filt_prefix}_chr3.info.gz", "rt") as fh:
        lines = [l.strip() for l in fh if l.strip()]
    assert len(lines) == 1
    surv = lines[0].split("\t")
    assert int(surv[2]) == 7 and int(surv[3]) == 5


def test_run_hsqg_step2_invokes_hess_with_filtered_prefix(tmp_path):
    """`run_hsqg_step2` must pre-filter step1 outputs and pass the
    ``{prefix}_filt`` prefix to hess.py (not the original ``{prefix}``).
    Confirms the filter pass is wired into the subprocess invocation.
    """
    python27_bin = tmp_path / "python2.7"
    python27_bin.write_text("#!/bin/sh\nexit 0\n")
    python27_bin.chmod(0o755)

    hess_script = tmp_path / "hess.py"
    hess_script.write_text("# stub\n")

    prefix = str(tmp_path / "pair_trait1")
    # Write a minimal 22-chromosome fixture: each chr has 2 loci, none empty
    for chrom in range(1, 23):
        _write_step1_files(
            prefix, chrom,
            info_rows=[(0, 500, 4, 2, 1000.0), (500, 1500, 6, 4, 1000.0)],
            eig_rows=["0.5\t1.5", "0.8\t1.8\t2.8\t3.8"],
            prjsq_rows=["0.05\t0.15", "0.08\t0.18\t0.28\t0.38"],
        )

    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        r = mock.Mock()
        r.stdout = ""
        r.stderr = ""
        r.returncode = 0
        return r

    with mock.patch("run_hess.subprocess.run", side_effect=fake_run):
        run_hsqg_step2(
            hess_script=str(hess_script),
            python27=str(python27_bin),
            prefix=prefix,
            out=str(tmp_path / "out_hsqg"),
        )

    cmd = captured["cmd"]
    # Must use {prefix}_filt as the --prefix passed to hess.py
    assert "--prefix" in cmd
    prefix_idx = cmd.index("--prefix")
    assert cmd[prefix_idx + 1] == f"{prefix}_filt", (
        f"HESS must be invoked with filtered prefix; got {cmd[prefix_idx + 1]}"
    )

    # Filter outputs must exist on disk
    assert Path(f"{prefix}_filt_chr1.info.gz").exists()
    assert Path(f"{prefix}_filt_chr22.info.gz").exists()


# ---------------------------------------------------------------------------
# Regression 5 (Launch12): subprocess diagnostics surfaced on failure
# ---------------------------------------------------------------------------


def test_run_hess_subprocess_surfaces_stderr_stdout_and_log(tmp_path, caplog):
    """`_run_hess_subprocess` must log e.stderr, e.stdout, AND the contents
    of hess.py's own ``{out}.log`` when CalledProcessError raises, before
    re-raising. Launch10 regression: the real HESS error
    ("Rank of A less than the number of loci") was only visible in the
    hess.py-authored log file because ``subprocess.run(..., check=True)``
    swallows stderr and the prior wrapper never read the hess log.
    """
    import logging

    # Seed a hess.py-style log file at {out}.log so the wrapper has
    # something to forward.
    out_prefix = tmp_path / "my_run"
    hess_log = out_prefix.with_suffix(".log")
    hess_log.write_text(
        "[ERROR] Rank of A less than the number of loci. "
        "There might be loci with no SNP.\n"
    )

    # CalledProcessError populated with stderr/stdout so the wrapper
    # logs them at ERROR level.
    def fake_run(cmd, **kwargs):
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=cmd,
            output="some stdout chunk",
            stderr="some stderr chunk from python2.7",
        )

    caplog.set_level(logging.ERROR, logger="run_hess")
    with mock.patch("run_hess.subprocess.run", side_effect=fake_run):
        with pytest.raises(subprocess.CalledProcessError):
            _run_hess_subprocess(
                cmd=["python", "hess.py"],
                description="HESS test",
                out_for_log=str(out_prefix),
            )

    log_text = caplog.text
    # All three must be forwarded before re-raise
    assert "some stderr chunk from python2.7" in log_text, (
        "stderr must be surfaced on CalledProcessError"
    )
    assert "some stdout chunk" in log_text, (
        "stdout must be surfaced on CalledProcessError"
    )
    assert "Rank of A less than the number of loci" in log_text, (
        "hess.py log file contents must be surfaced on CalledProcessError"
    )


# ---------------------------------------------------------------------------
# Regression 6 (Launch12): AFR ancestry LDSC frqfile routing
# ---------------------------------------------------------------------------


def test_ldsc_frqfile_chr_routes_afr_to_afr_prefix():
    """The ancestry dispatch helper in pathway.smk must return the AFR
    frqfile prefix when ancestry == "AFR". Launch11 regression: AFR
    sumstats (asthma_AFR, stroke_AFR, t2d_AFR) failed in ldsc_partitioned_h2
    with "LD Score matrix condition number is 5.6e20" because the EUR
    frqfile was applied to AFR regression weights.

    We import the helper from the Snakemake rule file at runtime (the
    file is not a package, so exec + extract the function).
    """
    smk_path = (
        PROJECT_ROOT / "src" / "snakemake" / "rules" / "pathway.smk"
    )
    # Extract just the two helper functions from the Snakemake rule file
    # by reading the source and executing only the function bodies.
    # Safer than importing the whole file (which references `workflow.basedir`).
    source = smk_path.read_text()

    # Pull out _ldsc_frqfile_chr by locating the def line
    func_lines = []
    in_func = False
    paren_depth = 0
    import_preamble = "import os\n"
    # Also need a PATHWAY_CFG stand-in for the default path fallbacks
    for line in source.splitlines():
        if line.startswith("def _ldsc_frqfile_chr"):
            in_func = True
        elif in_func and line and not line.startswith((" ", "\t")):
            # End of function body
            in_func = False
        if in_func:
            func_lines.append(line)

    assert func_lines, "Could not locate _ldsc_frqfile_chr in pathway.smk"

    # Build an isolated namespace with the config stub the function needs
    ns = {"PATHWAY_CFG": {}, "os": __import__("os")}
    exec("\n".join(func_lines), ns)  # noqa: S102 -- test-only
    helper = ns["_ldsc_frqfile_chr"]

    # AFR -> AFR prefix
    afr_path = helper("AFR")
    assert afr_path.endswith("1000G.AFR.QC."), (
        f"AFR ancestry must route to 1000G.AFR.QC. prefix; got {afr_path}"
    )
    assert "1000G_Phase3_frq_AFR" in afr_path, (
        f"AFR frq path must live under 1000G_Phase3_frq_AFR; got {afr_path}"
    )

    # Case insensitivity
    assert helper("afr") == afr_path

    # EUR stays on the alkesgroup-distributed prefix
    eur_path = helper("EUR")
    assert eur_path.endswith("1000G.EUR.QC."), (
        f"EUR ancestry must stay on 1000G.EUR.QC. prefix; got {eur_path}"
    )
    assert "1000G_Phase3_frq_AFR" not in eur_path, (
        f"EUR path must not reference AFR directory; got {eur_path}"
    )

    # Unknown ancestries fall back to EUR (T1 scope is EUR + AFR only)
    assert helper("EAS") == eur_path
    assert helper("HIS") == eur_path


def test_ldsc_frq_flag_routes_afr_to_afr_sentinel():
    """AFR ancestry must gate ldsc_partitioned_h2 / ldsc_seg_* on
    ``download_ldsc_afr_frq`` (.afr_frq_done) rather than the EUR
    baseline sentinel. Regression: without this dependency, the AFR
    rule could race download_ldsc_afr_frq and point at a missing prefix.
    """
    smk_path = (
        PROJECT_ROOT / "src" / "snakemake" / "rules" / "pathway.smk"
    )
    source = smk_path.read_text()

    func_lines = []
    in_func = False
    for line in source.splitlines():
        if line.startswith("def _ldsc_frq_flag"):
            in_func = True
        elif in_func and line and not line.startswith((" ", "\t")):
            in_func = False
        if in_func:
            func_lines.append(line)

    assert func_lines, "Could not locate _ldsc_frq_flag in pathway.smk"

    ns = {}
    exec("\n".join(func_lines), ns)  # noqa: S102
    helper = ns["_ldsc_frq_flag"]

    assert helper("AFR").endswith(".afr_frq_done"), (
        f"AFR ancestry must gate on .afr_frq_done; got {helper('AFR')}"
    )
    assert helper("EUR").endswith(".baseline_download_done"), (
        f"EUR ancestry must gate on .baseline_download_done; got {helper('EUR')}"
    )
