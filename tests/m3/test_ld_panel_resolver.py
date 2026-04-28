"""Unit tests for src/python/ld_panel.py::resolve_ld_path.

Hermetic: builds an inline config dict matching the production
``config/pipeline.yaml`` ld_panel: block layout. Uses ``tmp_path`` and
``Path.touch()`` to simulate ``.rds`` presence/absence.

Covers the 6 behaviors from the m3-00 plan task 2:
* test_resolver_returns_first_existing_path
* test_resolver_strict_mode_raises
* test_resolver_pin_override
* test_resolver_unknown_ancestry (TRANS fallback chain)
* test_resolver_region_id_vs_region_safe (placeholder substitution)
* test_resolver_no_match_raises
"""
from __future__ import annotations

from pathlib import Path

import pytest

from ld_panel import resolve_ld_path


def _build_config(tmp_path: Path) -> dict:
    """Mirror the production ld_panel: block but rooted at tmp_path."""
    base = tmp_path / "data" / "processed" / "ld_reference"
    return {
        "ld_panel": {
            "EUR": [
                {"source": "EUR_aou",  "path": str(base / "EUR_aou" / "{region_id}.rds")},
                {"source": "EUR_ukbb", "path": str(base / "EUR_ukbb_ld" / "{region_safe}.rds")},
                {"source": "EUR_1kg",  "path": str(base / "EUR" / "{region_safe}.rds")},
            ],
            "AFR": [
                {"source": "AFR_aou",  "path": str(base / "AFR_aou" / "{region_id}.rds")},
                {"source": "AFR_hgdp", "path": str(base / "AFR_hgdp_1kg" / "{region_safe}.rds")},
                {"source": "AFR_1kg",  "path": str(base / "AFR" / "{region_safe}.rds")},
            ],
            "TRANS": [
                {"source": "TRANS_aou_eur", "path": str(base / "EUR_aou" / "{region_id}.rds")},
                {"source": "EUR_1kg",       "path": str(base / "EUR" / "{region_safe}.rds")},
            ],
            "strict_aou_only": False,
            "pin": {"EUR": None, "AFR": None, "TRANS": None},
        }
    }


def _touch(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch()
    return p


def test_resolver_returns_first_existing_path(tmp_path):
    cfg = _build_config(tmp_path)
    base = tmp_path / "data" / "processed" / "ld_reference"
    rid = "m2_region_00067"

    # AFR_aou exists -> returned first
    aou = _touch(base / "AFR_aou" / f"{rid}.rds")
    got = resolve_ld_path(rid, "AFR", cfg)
    assert got == aou

    # Remove AFR_aou; AFR_hgdp_1kg exists -> walk to second entry
    aou.unlink()
    hgdp = _touch(base / "AFR_hgdp_1kg" / f"{rid}.rds")
    got = resolve_ld_path(rid, "AFR", cfg)
    assert got == hgdp

    # Remove AFR_hgdp; AFR_1kg exists -> walk to third entry
    hgdp.unlink()
    onekg = _touch(base / "AFR" / f"{rid}.rds")
    got = resolve_ld_path(rid, "AFR", cfg)
    assert got == onekg


def test_resolver_strict_mode_raises(tmp_path):
    """When strict_aou_only=True and AFR_aou missing, raise FileNotFoundError."""
    cfg = _build_config(tmp_path)
    cfg["ld_panel"]["strict_aou_only"] = True
    rid = "m2_region_00040"
    # No files created -> AFR_aou is the first chain entry and is _aou-suffixed
    with pytest.raises(FileNotFoundError, match="strict_aou_only"):
        resolve_ld_path(rid, "AFR", cfg)


def test_resolver_pin_override(tmp_path):
    """When pin.EUR='EUR_1kg', returns EUR_1kg path even if EUR_aou exists."""
    cfg = _build_config(tmp_path)
    cfg["ld_panel"]["pin"]["EUR"] = "EUR_1kg"
    base = tmp_path / "data" / "processed" / "ld_reference"
    rid = "m2_region_00067"

    aou = _touch(base / "EUR_aou" / f"{rid}.rds")  # would normally win
    onekg = _touch(base / "EUR" / f"{rid}.rds")  # pinned target

    got = resolve_ld_path(rid, "EUR", cfg)
    assert got == onekg, f"pin EUR_1kg should override AoU; got {got}"
    assert got != aou


def test_resolver_unknown_ancestry_trans_chain(tmp_path):
    """TRANS uses TRANS_aou_eur -> EUR_1kg fallback."""
    cfg = _build_config(tmp_path)
    base = tmp_path / "data" / "processed" / "ld_reference"
    rid = "m2_region_00006"

    # Neither exists -> raises
    with pytest.raises(FileNotFoundError, match="No LD panel found"):
        resolve_ld_path(rid, "TRANS", cfg)

    # First chain entry is TRANS_aou_eur which uses EUR_aou path
    aou = _touch(base / "EUR_aou" / f"{rid}.rds")
    got = resolve_ld_path(rid, "TRANS", cfg)
    assert got == aou

    # Remove and use EUR_1kg fallback
    aou.unlink()
    onekg = _touch(base / "EUR" / f"{rid}.rds")
    got = resolve_ld_path(rid, "TRANS", cfg)
    assert got == onekg


def test_resolver_region_id_vs_region_safe_substitution(tmp_path):
    """Both {region_id} and {region_safe} substitute to the resolver's region argument.

    This is the legacy-naming wart from RESEARCH O6: Track A files use
    region_safe slugs (FTO_16q12); M2 uses region_id (m2_region_00067).
    """
    cfg = _build_config(tmp_path)
    base = tmp_path / "data" / "processed" / "ld_reference"

    # Caller passes the M2 region_id; resolver substitutes it into BOTH
    # {region_id} (e.g., AFR_aou path) and {region_safe} (e.g., AFR_1kg path).
    rid = "m2_region_00067"
    onekg = _touch(base / "AFR" / f"{rid}.rds")
    got = resolve_ld_path(rid, "AFR", cfg)
    assert got == onekg

    # Caller can also pass a region_safe slug (the upstream caller is
    # responsible for the translation via config/region_id_mapping.tsv).
    safe = "FTO_16q12"
    onekg_safe = _touch(base / "AFR" / f"{safe}.rds")
    got = resolve_ld_path(safe, "AFR", cfg)
    assert got == onekg_safe


def test_resolver_no_match_raises(tmp_path):
    """When no entry exists in the chain, raise FileNotFoundError."""
    cfg = _build_config(tmp_path)
    rid = "m2_region_99999"
    with pytest.raises(FileNotFoundError, match="No LD panel found"):
        resolve_ld_path(rid, "AFR", cfg)


def test_resolver_pin_with_unknown_source_raises(tmp_path):
    """A pin pointing to a source not in the chain raises ValueError."""
    cfg = _build_config(tmp_path)
    cfg["ld_panel"]["pin"]["AFR"] = "AFR_definitely_not_a_real_source"
    with pytest.raises(ValueError, match="not in"):
        resolve_ld_path("m2_region_00001", "AFR", cfg)


def test_production_pipeline_yaml_loads(tmp_path):
    """Sanity: the production pipeline.yaml ld_panel: block parses + has expected keys."""
    import yaml

    project_root = Path(__file__).resolve().parents[2]
    cfg = yaml.safe_load((project_root / "config" / "pipeline.yaml").read_text())
    assert "ld_panel" in cfg
    panel = cfg["ld_panel"]
    assert {"EUR", "AFR", "TRANS", "strict_aou_only", "pin"}.issubset(set(panel))
    assert panel["strict_aou_only"] is False
    # AFR_aou is the head of the AFR chain per D-M3-05
    assert panel["AFR"][0]["source"] == "AFR_aou"
    # EUR_aou is the head of the EUR chain per D-M3-01
    assert panel["EUR"][0]["source"] == "EUR_aou"
