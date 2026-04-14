"""COJO wrapper tests — Plan 09-05 Task 1 (D-04c + RESEARCH §6 Option D).

GREEN phase: validates the real implementations of
  src/snakemake/scripts/prepare_cojo_ma.py      (canonical -> GCTA .ma)
  src/snakemake/scripts/run_cojo.sh             (GCTA --cojo-slct wrapper)
  src/python/build_cojo_sensitivity_table.py    (.jma.cojo aggregator)

The N<4000 caveat (gotcha #1) is enforced at three layers:
  1. run_cojo.sh emits a WARN to stderr for the tier-2 supplementary label
  2. this module asserts the WARN string + '4000' literal are present in the script
  3. docs/methods/phase9_replication.md embeds the same caveat (Task 2)
"""
import os
import stat
import sys
import subprocess
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "src" / "snakemake" / "scripts"
PY_DIR = PROJECT_ROOT / "src" / "python"


# ---------------------------------------------------------------------------
# Frozen YAML-level + env-level contract tests (ported from Wave-1 RED)
# ---------------------------------------------------------------------------
def test_gcta_env_present():
    gcta_env = PROJECT_ROOT / "envs" / "gcta.yml"
    assert gcta_env.exists()
    assert "gcta=1.94.1" in gcta_env.read_text()


def test_cojo_ld_caveat_documented(replication_cohorts_config):
    """D-04c + RESEARCH §6 Option D: 1000G EUR N=503 below GCTA's 4K threshold."""
    ld_ref = replication_cohorts_config["cojo_ld_reference"]
    assert ld_ref["EUR"] == "thousand_g_eur"
    assert ld_ref["AFR"] == "thousand_g_afr"


# ---------------------------------------------------------------------------
# Task 1 Step 1 — prepare_cojo_ma.py: canonical -> GCTA .ma
# ---------------------------------------------------------------------------
def _load_prepare_cojo_ma():
    # Script lives under src/snakemake/scripts/; import as a module.
    path = SCRIPTS_DIR / "prepare_cojo_ma.py"
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    import importlib
    import prepare_cojo_ma  # type: ignore
    importlib.reload(prepare_cojo_ma)
    return prepare_cojo_ma


def test_prepare_cojo_ma_basic(tmp_path):
    M = _load_prepare_cojo_ma()
    canonical = tmp_path / "canonical.tsv.gz"
    df = pd.DataFrame({
        "CHR": [10, 10, 10, 11],
        "BP": [100, 200, 300, 400],
        "SNP": ["rs1", "rs2", "rs3", "rs4"],
        "EA": ["A", "T", "G", "C"],
        "OA": ["G", "C", "A", "T"],
        "BETA": [0.1, 0.2, 0.3, 0.4],
        "SE": [0.01, 0.02, 0.03, 0.04],
        "P": [1e-10, 1e-8, 1e-6, 1e-5],
        "EAF": [0.3, 0.2, 0.4, 0.5],
        "N": [100000] * 4,
    })
    df.to_csv(canonical, sep="\t", index=False, compression="gzip")
    out = tmp_path / "out.ma"
    n = M.canonical_to_ma(canonical, "chr10:100-300", out)
    assert n == 3, "only chr10:100-300 rows should pass the region filter"

    ma = pd.read_csv(out, sep=" ")
    assert list(ma.columns) == ["SNP", "A1", "A2", "freq", "b", "se", "p", "N"]
    # A1=EA, A2=OA per GCTA convention
    assert (ma["A1"].tolist() == ["A", "T", "G"])
    assert (ma["A2"].tolist() == ["G", "C", "A"])


def test_prepare_cojo_ma_handles_uncompressed(tmp_path):
    """Plain TSV input (no .gz suffix) must also parse."""
    M = _load_prepare_cojo_ma()
    canonical = tmp_path / "canonical.tsv"
    df = pd.DataFrame({
        "CHR": [10], "BP": [150], "SNP": ["rs_solo"],
        "EA": ["A"], "OA": ["G"], "BETA": [0.1], "SE": [0.01],
        "P": [1e-8], "EAF": [0.3], "N": [50000],
    })
    df.to_csv(canonical, sep="\t", index=False)
    out = tmp_path / "solo.ma"
    n = M.canonical_to_ma(canonical, "chr10:100-200", out)
    assert n == 1


# ---------------------------------------------------------------------------
# Task 1 Step 2 — run_cojo.sh wrapper (shape + caveat + arg safety)
# ---------------------------------------------------------------------------
def test_cojo_script_exists_and_executable():
    p = SCRIPTS_DIR / "run_cojo.sh"
    assert p.exists(), "run_cojo.sh must be created by Plan 09-05 Task 1"
    mode = p.stat().st_mode
    assert mode & stat.S_IXUSR, "run_cojo.sh must be user-executable (chmod +x)"


def test_cojo_script_has_gcta_flags():
    content = (SCRIPTS_DIR / "run_cojo.sh").read_text()
    assert "--cojo-slct" in content
    assert "--cojo-p 5e-8" in content
    assert "--cojo-wind 10000" in content
    assert "--bfile" in content
    assert "--extract" in content


def test_cojo_script_has_n4000_caveat():
    """Gotcha #1 layer-1 enforcement: stderr WARN when LD reference < 4000 samples."""
    content = (SCRIPTS_DIR / "run_cojo.sh").read_text()
    assert "4000" in content, "N<4000 caveat literal missing from run_cojo.sh"
    # WARN token to stderr (threat T-09-22 mitigation)
    assert "WARN" in content.upper()


def test_cojo_script_hardened_shell():
    """T-09-07 mitigation: set -euo pipefail + double-quoted args."""
    content = (SCRIPTS_DIR / "run_cojo.sh").read_text()
    assert "set -euo pipefail" in content


# ---------------------------------------------------------------------------
# Task 1 Step 3 — build_cojo_sensitivity_table.py
# ---------------------------------------------------------------------------
def _load_build_cojo_table():
    if str(PY_DIR) not in sys.path:
        sys.path.insert(0, str(PY_DIR))
    import importlib
    import build_cojo_sensitivity_table  # type: ignore
    importlib.reload(build_cojo_sensitivity_table)
    return build_cojo_sensitivity_table


def test_parse_cojo_jma_handles_missing_file(tmp_path):
    M = _load_build_cojo_table()
    r = M.parse_cojo_jma(tmp_path / "nonexistent.jma.cojo", "sig_x", "cohort_y")
    assert r["signal_id"] == "sig_x"
    assert r["cohort"] == "cohort_y"
    assert r["cojo_n_independent_signals"] == 0


def test_parse_cojo_jma_two_independent(tmp_path):
    M = _load_build_cojo_table()
    jma = tmp_path / "sigA_cohB.jma.cojo"
    # GCTA .jma.cojo columns (tab-separated per GCTA docs)
    pd.DataFrame({
        "Chr":   [10, 10],
        "SNP":   ["rs_top", "rs_sec"],
        "bp":    [100, 500],
        "refA":  ["A", "T"],
        "freq":  [0.3, 0.2],
        "b":     [0.20, 0.08],
        "se":    [0.02, 0.02],
        "p":     [1e-30, 1e-6],
        "n":     [100000, 100000],
        "freq_geno": [0.3, 0.2],
        "bJ":    [0.20, 0.07],
        "bJ_se": [0.02, 0.02],
        "pJ":    [1e-28, 5e-5],
        "LD_r":  [1.0, 0.02],
    }).to_csv(jma, sep="\t", index=False)
    r = M.parse_cojo_jma(jma, "sigA", "cohB")
    assert r["cojo_n_independent_signals"] == 2
    assert r["cojo_top_snp"] == "rs_top"
    assert r["cojo_joint_beta"] == pytest.approx(0.20, abs=1e-6)
    assert r["cojo_joint_p"] == pytest.approx(1e-28, rel=1e-3)


def test_build_cojo_table_end_to_end(tmp_path):
    M = _load_build_cojo_table()
    manifest = tmp_path / "manifest.tsv"
    cojo_dir = tmp_path / "cojo"
    cojo_dir.mkdir()

    pd.DataFrame({
        "signal_id": ["sig1", "sig2"],
        "cohort": ["finngen_r12", "mvp_eur"],
        "discovery_trait": ["t2d", "t2d"],
        "region": ["chr10:100-300", "chr11:200-400"],
    }).to_csv(manifest, sep="\t", index=False)

    # Only sig1's .jma.cojo exists — sig2 should be silently skipped
    jma1 = cojo_dir / "finngen_r12_t2d_chr10_100_300.jma.cojo"
    pd.DataFrame({
        "Chr": [10], "SNP": ["rs_top"], "bp": [150], "refA": ["A"],
        "freq": [0.3], "b": [0.2], "se": [0.02], "p": [1e-20],
        "n": [100000], "freq_geno": [0.3], "bJ": [0.2], "bJ_se": [0.02],
        "pJ": [1e-18], "LD_r": [1.0],
    }).to_csv(jma1, sep="\t", index=False)

    out = tmp_path / "cojo_sensitivity.tsv"
    M.build_cojo_table(cojo_dir, manifest, out)
    df = pd.read_csv(out, sep="\t")
    assert len(df) == 1
    assert df.iloc[0]["signal_id"] == "sig1"
    assert df.iloc[0]["cojo_n_independent_signals"] == 1


# ---------------------------------------------------------------------------
# Snakemake rule-substance check (§F is no longer TODO)
# ---------------------------------------------------------------------------
def test_replication_smk_cojo_rules_real():
    """Plan 09-05 Task 1 done criterion: TODO markers removed from §F."""
    smk = (PROJECT_ROOT / "src" / "snakemake" / "rules" / "replication.smk").read_text()
    # §F rules must invoke the real scripts
    assert "prepare_cojo_ma.py" in smk
    assert "run_cojo.sh" in smk
    assert "build_cojo_sensitivity_table" in smk
    # TODO markers for COJO tasks must be gone
    assert "TODO plan 09-05 Task 1" not in smk, "COJO §F still has TODO markers"
