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

import re
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


# ---------------------------------------------------------------------
# CR-001 regression tests (added 260501-v9q).
#
# Background: pre-fix `resolve_ld_path` substituted both `{region_id}`
# and `{region_safe}` placeholders with the SAME value (the single
# `region_id` arg). This made AoU paths resolve correctly by accident
# when callers happened to pass an `m2_region_NNNNN` id, but the 1kg
# fallback NEVER resolved when the legacy bucket only had
# `{region_safe}`-named files. CR-001 fix (commit 6d2e753) made
# `region_safe` an independent kwarg.
#
# The pre-existing `test_resolver_region_id_vs_region_safe_substitution`
# test only covers the back-compat single-arg call (where both
# placeholders SHOULD resolve to the same value). The tests below cover
# the bug CR-001 actually fixed: DISTINCT region_id and region_safe
# values, and the static call-site contract in finemap.smk.
# ---------------------------------------------------------------------


def test_resolver_distinct_region_id_and_region_safe_aou_head(tmp_path):
    """AoU head: DISTINCT region_id vs region_safe; only AoU file exists.

    Pre-CR-001: resolver would have looked for `FTO_16q12.rds` in the
    AoU bucket (since both placeholders got the same value) and missed
    it, walking to hgdp/1kg fallback. Post-CR-001: returns the AoU path.
    """
    cfg = _build_config(tmp_path)
    base = tmp_path / "data" / "processed" / "ld_reference"

    rid = "m2_region_00067"   # AoU naming
    safe = "FTO_16q12"        # Track A naming — DISTINCT from rid

    # Only the AoU bucket has the file (named by region_id).
    aou_path = _touch(base / "AFR_aou" / f"{rid}.rds")

    # No FTO_16q12.rds anywhere — guard against accidental cross-bucket hits.
    assert not (base / "AFR_aou" / f"{safe}.rds").exists()
    assert not (base / "AFR_hgdp_1kg" / f"{safe}.rds").exists()
    assert not (base / "AFR" / f"{safe}.rds").exists()

    got = resolve_ld_path(
        region_id=rid,
        ancestry="AFR",
        config=cfg,
        region_safe=safe,
    )
    assert got == aou_path
    assert got.name == f"{rid}.rds", (
        f"AoU resolution must use region_id naming; got {got.name!r}"
    )
    # Belt-and-suspenders: ensure the resolver did NOT substitute the
    # safe slug into the AoU path template.
    assert safe not in str(got), (
        f"region_safe leaked into AoU path: {got}"
    )


def test_resolver_distinct_region_id_and_region_safe_1kg_fallback(tmp_path):
    """1kg fallback: DISTINCT region_id vs region_safe; only 1kg file exists.

    AoU bucket empty + only `{region_safe}.rds` in the legacy 1kg
    bucket. Pre-CR-001: resolver would have looked for
    `m2_region_00067.rds` in the 1kg bucket and missed (cascading
    FileNotFoundError). Post-CR-001: substitutes `{region_safe}` with
    `FTO_16q12` and finds the legacy file.
    """
    cfg = _build_config(tmp_path)
    base = tmp_path / "data" / "processed" / "ld_reference"

    rid = "m2_region_00067"
    safe = "FTO_16q12"

    # AoU bucket: empty.
    # hgdp bucket: empty.
    # 1kg bucket: ONLY the region_safe-named file (legacy convention).
    onekg_path = _touch(base / "AFR" / f"{safe}.rds")

    # Confirm no region_id-named files anywhere — pre-fix code would
    # have looked for these and missed.
    assert not (base / "AFR_aou" / f"{rid}.rds").exists()
    assert not (base / "AFR_hgdp_1kg" / f"{rid}.rds").exists()
    assert not (base / "AFR" / f"{rid}.rds").exists()

    got = resolve_ld_path(
        region_id=rid,
        ancestry="AFR",
        config=cfg,
        region_safe=safe,
    )
    assert got == onekg_path
    assert got.name == f"{safe}.rds", (
        f"1kg fallback must use region_safe naming; got {got.name!r}"
    )
    # Belt-and-suspenders: ensure the resolver did NOT substitute the
    # region_id into the 1kg path template.
    assert rid not in str(got), (
        f"region_id leaked into 1kg path: {got}"
    )


def test_finemap_smk_calls_resolver_with_both_kwargs():
    """Static contract: finemap.smk must pass region_id= AND region_safe=.

    Locks the production call-site contract from m3-W3-T2 (commit caf57ef
    + CR-001 fix in commit 6d2e753). A future refactor that drops one
    kwarg and falls back to single-positional region passing (which would
    silently re-introduce the same-value substitution bug per the
    back-compat default in resolve_ld_path) is caught here, before any
    pipeline run.
    """
    project_root = Path(__file__).resolve().parents[2]
    smk_path = project_root / "src" / "snakemake" / "rules" / "finemap.smk"
    assert smk_path.exists(), f"finemap.smk not at {smk_path}"
    text = smk_path.read_text()

    # Sanity: the resolver is referenced.
    assert re.search(r"resolve_ld_path\s*\(", text), (
        "finemap.smk no longer calls resolve_ld_path()"
    )

    # Both kwargs must appear in the resolve_ld_path(...) call. We use
    # `[^)]*` because the call's argument list contains no nested parens
    # in the current production code; if that ever changes, broaden to
    # a non-greedy `[\s\S]*?` with explicit closing-paren anchoring.
    assert re.search(
        r"resolve_ld_path\s*\([^)]*region_id\s*=", text, re.DOTALL
    ), "finemap.smk's resolve_ld_path call is missing region_id= kwarg"

    assert re.search(
        r"resolve_ld_path\s*\([^)]*region_safe\s*=", text, re.DOTALL
    ), (
        "finemap.smk's resolve_ld_path call is missing region_safe= "
        "kwarg — CR-001 regression risk: without region_safe=, the "
        "resolver's back-compat default re-introduces the same-value "
        "substitution bug for the 1kg/HGDP/UKBB tails of the chain."
    )
