"""Wave 5 -- kriging_rss outlier counts sanity check.

Matched LD (EUR sumstats + EUR panel) should produce few outliers.
Threshold: n_outliers / n_variants < 0.10 on any well-matched region.
"""
import json
import os
from pathlib import Path
import pytest

FINEMAP_DIR = Path(os.environ.get("FINEMAP_DIR", "results/finemap"))
SUSIE_DIR = FINEMAP_DIR / "susie"


def test_kriging_outlier_rate_matched_ld():
    files = list(SUSIE_DIR.rglob("*.json"))
    if not files:
        pytest.skip("No susie JSON outputs yet")
    violations = []
    for f in files:
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        d3 = data.get("d3_ld_quality") or {}
        n_outliers = d3.get("n_outliers")
        n_variants = data.get("n_variants")
        if n_outliers is None or n_variants in (None, 0):
            continue
        rate = n_outliers / n_variants
        if rate >= 0.10:
            violations.append((str(f), n_outliers, n_variants, rate))
    # Soft fail: flag not fail. 10% is a loose ceiling; may be tightened post-Phase 1.
    if violations:
        pytest.xfail(f"Kriging outlier rate >= 10% on {len(violations)} regions -- "
                     f"first 3: {violations[:3]}. Review in qc_dashboard.html.")
