"""Wave 2 test (RED in Wave 1): column-map produces canonical schema.

Placeholder tests xfail until Plan 09-02 creates the harmonize_* scripts.
"""
import pytest

pytest.importorskip("pandas")


def test_finngen_column_map_shape(replication_cohorts_config, canonical_schema):
    cfg = replication_cohorts_config["cohorts"]["finngen_r12"]["column_map"]
    expected_keys = {"chr", "bp", "oa", "ea", "snp", "beta", "se", "p", "eaf"}
    assert expected_keys.issubset(cfg.keys())


def test_finngen_harmonizer_placeholder():
    """RED until Plan 09-02 Task 1 creates src/python/harmonize_finngen.py."""
    try:
        from src.python.harmonize_finngen import harmonize_finngen_sumstats  # noqa: F401
    except ImportError:
        pytest.xfail("harmonize_finngen not yet implemented (Plan 09-02 Task 1)")


def test_bbj_harmonizer_placeholder():
    """RED until Plan 09-02 Task 2 creates src/python/harmonize_bbj.py."""
    try:
        from src.python.harmonize_bbj import harmonize_bbj_sumstats  # noqa: F401
    except ImportError:
        pytest.xfail("harmonize_bbj not yet implemented (Plan 09-02 Task 2)")
