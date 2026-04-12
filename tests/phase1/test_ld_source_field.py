"""Wave 5 -- verify new LD panels are in use (not silent identity fallback).

After a real Phase 1 run on toy_3locus, at least one EUR region JSON should
carry ld_source starting with 'ukbb_ld_tiled' and at least one AFR region
JSON should carry ld_source starting with 'hgdp_1kg'. No region should
silently fall back to identity LD (a regression guard).
"""
import json
import os
from pathlib import Path
import pytest

FINEMAP_DIR = Path(os.environ.get("FINEMAP_DIR", "results/finemap"))
SUSIE_DIR = FINEMAP_DIR / "susie"


def _all_jsons():
    return list(SUSIE_DIR.rglob("*.json"))


def test_no_silent_identity_fallback():
    files = _all_jsons()
    if not files:
        pytest.skip("No susie JSON outputs yet (Task 1-06-02 pending)")
    bad = []
    for f in files:
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        src = data.get("ld_source", "")
        if src == "identity":
            bad.append(str(f))
    assert not bad, f"Silent identity-LD fallback detected in {len(bad)} files: {bad[:5]}"


def test_ukbb_ld_eur_in_use():
    files = _all_jsons()
    if not files:
        pytest.skip("No susie JSON outputs yet")
    eur = [f for f in files if ".EUR." in f.name or "/EUR/" in str(f)]
    if not eur:
        pytest.skip("No EUR JSON outputs")
    have_ukbb = any(
        (json.loads(f.read_text()).get("ld_source", "") or "").startswith("ukbb_ld_tiled")
        for f in eur
    )
    assert have_ukbb, "No EUR region uses ld_source starting with 'ukbb_ld_tiled' (UKBB-LD tiled panel not in use)"


def test_hgdp_afr_in_use():
    files = _all_jsons()
    if not files:
        pytest.skip("No susie JSON outputs yet")
    afr = [f for f in files if ".AFR." in f.name or "/AFR/" in str(f)]
    if not afr:
        pytest.skip("No AFR JSON outputs -- toy dataset may not include AFR")
    have_hgdp = any(
        (json.loads(f.read_text()).get("ld_source", "") or "").startswith("hgdp_1kg")
        for f in afr
    )
    assert have_hgdp, "No AFR region uses ld_source starting with 'hgdp_1kg'"
