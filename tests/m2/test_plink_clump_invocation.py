"""PLINK 1.9 --clump invocation tests (Pitfall 5 — PLINK 2.0 lacks --clump).

Verifies the Snakemake rule shell command contains the canonical PLINK
clump flags: --clump --clump-p1 5e-8 --clump-r2 0.01 --clump-kb 1000.

Wave 4 lands src/snakemake/rules/m2_clumping.smk; this test reads the .smk
file as text and asserts the literal flags appear.
"""
from __future__ import annotations

from pathlib import Path

import pytest

_SMK_PATH = Path(__file__).resolve().parents[2] / "src" / "snakemake" / "rules" / "m2_clumping.smk"


pytestmark = pytest.mark.skipif(
    not _SMK_PATH.exists(),
    reason="src/snakemake/rules/m2_clumping.smk not yet landed (Wave 4)",
)


def test_clump_flags_present():
    """Shell command must contain --clump --clump-p1 5e-8 --clump-r2 0.01 --clump-kb 1000."""
    text = _SMK_PATH.read_text()
    assert "--clump" in text
    assert "--clump-p1 5e-8" in text or "--clump-p1=5e-8" in text
    assert "--clump-r2 0.01" in text or "--clump-r2=0.01" in text
    assert "--clump-kb 1000" in text or "--clump-kb=1000" in text


def test_uses_plink_1_9_env():
    """Snakemake rule must declare m2-clumping.yml conda env (PLINK 1.9)."""
    text = _SMK_PATH.read_text()
    assert "m2-clumping.yml" in text
