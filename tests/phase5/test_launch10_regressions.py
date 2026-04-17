"""Regression tests for T1 Launch10 residual failures (debug: t1-launch10-residual-failures).

Three regressions covered:
  1. HESS combine rho-HESS dispatch — verify run_combine() routes to
     local_rhog_step2 when --local-hsqg-est is supplied (test via cmd
     introspection; full HESS subprocess requires Python 2.7 env not in CI).
  2. Dummy allele round-trip — verify munge_sumstats_ldsc.convert_sumstats()
     emits A/G (not A/T) for trait sumstats lacking REF/ALT columns so
     LDSC's filter_alleles() does not drop every SNP.
  3. Legacy import smoke — verify summarize_coloc_results imports cleanly
     as a module (PYTHONPATH shim resolves `from scripts.utils_logging import
     get_logger` when invoked outside a `scripts.` package context).
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

from run_hess import run_combine, run_hsqg_step2  # noqa: E402
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
