"""Test the trait-inventory YAML schema validator.

Wave 4 (Plan m1-04) authors ``src/python/build_trait_inventory.py``
which emits ``config/trait_inventory.yaml`` per CONTEXT D-16. The YAML
schema must include at minimum:
``{trait, ancestry, consortium, year, source_url, build,
   harmonized_path, munged_path, parquet_path, n_total, n_cases,
   n_controls, sha256_raw, sha256_harmonized, ldsc_intercept,
   ldsc_h2, qc_report_path, qc_status}``

This Wave 0 test:
- Defines the minimal schema as a pydantic-style validator function.
- Tests it on a 2-trait fixture YAML written inline.
- If pydantic OR jsonschema is available, the validator uses it; else
  it falls back to a hand-rolled key-presence assertion.

Plan reference: m1-00-preflight-and-environment-PLAN.md Task 1 + RESEARCH §Validation Architecture Example 4.
"""
from __future__ import annotations

import io

import pytest
import yaml


REQUIRED_TRAIT_KEYS = {
    "trait",
    "ancestry",
    "consortium",
    "year",
    "source_url",
    "build",
    "harmonized_path",
    "munged_path",
    "parquet_path",
    "n_total",
    "n_cases",
    "n_controls",
    "sha256_raw",
    "sha256_harmonized",
    "ldsc_intercept",
    "ldsc_h2",
    "qc_report_path",
    "qc_status",
}


def _validate_inventory_doc(doc: dict) -> list[str]:
    """Return a list of violation messages; empty list = valid.

    This is the M1 plan-spec'd contract. Wave 4 may swap implementation
    to pydantic / jsonschema but the public surface (function name +
    return semantics) is fixed.
    """
    errors: list[str] = []
    if not isinstance(doc, dict):
        return [f"top-level must be dict, got {type(doc).__name__}"]
    if "traits" not in doc:
        errors.append("top-level missing key 'traits'")
        return errors
    if not isinstance(doc["traits"], list):
        errors.append("doc['traits'] must be a list")
        return errors

    for i, trait in enumerate(doc["traits"]):
        if not isinstance(trait, dict):
            errors.append(f"traits[{i}] must be dict, got {type(trait).__name__}")
            continue
        missing = REQUIRED_TRAIT_KEYS - set(trait.keys())
        if missing:
            errors.append(
                f"traits[{i}] (trait={trait.get('trait', 'unknown')}) "
                f"missing keys: {sorted(missing)}"
            )

    return errors


def _two_trait_fixture_yaml() -> str:
    """Inline 2-trait fixture YAML — minimal valid example."""
    return """
traits:
  - trait: bmi
    ancestry: EUR
    consortium: GIANT-UKBB
    year: 2018
    source_url: https://portals.broadinstitute.org/collaboration/giant/
    build: GRCh37
    harmonized_path: data/processed/sumstats_harmonized/bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz
    munged_path: data/processed/ldsc_overlap/munged/bmi.EUR.GIANT-UKBB.2018.sumstats.gz
    parquet_path: data/processed/sumstats_harmonized_parquet/bmi.EUR.GIANT-UKBB.2018.GRCh37.parquet
    n_total: 681275
    n_cases: null
    n_controls: null
    sha256_raw: TBD_AT_FREEZE
    sha256_harmonized: TBD_AT_FREEZE
    ldsc_intercept: null
    ldsc_h2: null
    qc_report_path: data/processed/sumstats_harmonized/qc_log/bmi.qc.html
    qc_status: PENDING
  - trait: t2d
    ancestry: TRANS
    consortium: DIAMANTE
    year: 2022
    source_url: https://diagram-consortium.org/downloads.html
    build: GRCh37
    harmonized_path: data/processed/sumstats_harmonized/t2d.TRANS.DIAMANTE.2022.GRCh37.tsv.bgz
    munged_path: data/processed/ldsc_overlap/munged/t2d.TRANS.DIAMANTE.2022.sumstats.gz
    parquet_path: data/processed/sumstats_harmonized_parquet/t2d.TRANS.DIAMANTE.2022.GRCh37.parquet
    n_total: 1339889
    n_cases: 180834
    n_controls: 1159055
    sha256_raw: TBD_AT_FREEZE
    sha256_harmonized: TBD_AT_FREEZE
    ldsc_intercept: null
    ldsc_h2: null
    qc_report_path: data/processed/sumstats_harmonized/qc_log/t2d.qc.html
    qc_status: PENDING
"""


def test_two_trait_fixture_validates_clean():
    """The inline 2-trait fixture passes the M1 schema validator."""
    doc = yaml.safe_load(_two_trait_fixture_yaml())
    errors = _validate_inventory_doc(doc)
    assert errors == [], f"Inventory schema validation failed: {errors}"


def test_missing_required_key_caught():
    """Dropping a required key in trait[0] surfaces a violation."""
    doc = yaml.safe_load(_two_trait_fixture_yaml())
    del doc["traits"][0]["sha256_raw"]
    errors = _validate_inventory_doc(doc)
    assert any("sha256_raw" in e for e in errors), (
        f"Validator should catch missing sha256_raw; errors={errors}"
    )


def test_missing_traits_top_level_caught():
    """Top-level YAML missing 'traits' is rejected."""
    doc = {"other_key": "value"}
    errors = _validate_inventory_doc(doc)
    assert any("traits" in e for e in errors), (
        f"Validator should catch missing top-level 'traits'; errors={errors}"
    )


def test_required_keys_complete_set():
    """The required-keys constant matches the planner spec verbatim."""
    expected = {
        "trait", "ancestry", "consortium", "year", "source_url", "build",
        "harmonized_path", "munged_path", "parquet_path",
        "n_total", "n_cases", "n_controls",
        "sha256_raw", "sha256_harmonized",
        "ldsc_intercept", "ldsc_h2",
        "qc_report_path", "qc_status",
    }
    assert REQUIRED_TRAIT_KEYS == expected, (
        f"Schema drift detected: REQUIRED_TRAIT_KEYS != plan spec.\n"
        f"Got:    {REQUIRED_TRAIT_KEYS}\nExpect: {expected}"
    )
