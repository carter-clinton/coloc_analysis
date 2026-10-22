"""D-01 / Pattern 3: matched arms fit the identical retained-variant set (named live gate + fixture proof)."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from .conftest import REPO_ROOT
from .test_frozen_script_armed_e2e import ANC, REGION, RSCRIPT, TRAIT, r4_e2e, retained_ids  # noqa: F401

from ta_r4 import paths
from ta_r4.arms import ARMS

pytestmark = pytest.mark.r4_heavy

MATCHED_PAIRS = (("A2_identity", "A3_1kg"), ("AFR661_A2", "AFR661_A3"), ("A3_ukb_isect", "A3_1kg_isect"))


def _fit_dir(arm):
    return Path(paths.fit_json(arm, "t", "a", "r")).parent


def _retained_by_stem(arm_dir):
    """{trait.anc.region: (status, retained ids)} for every .fit.rds in one arm dir, one R call."""
    code = (f'for (f in list.files("{arm_dir}", "\\\\.fit\\\\.rds$", full.names = TRUE)) {{'
            ' x <- readRDS(f); s <- sub("\\\\.fit\\\\.rds$", "", basename(f));'
            ' ids <- if (!is.null(x$status)) paste0("EARLY:", x$status) else names(x$pip);'
            ' if (is.null(ids)) ids <- "UNNAMED_FIT";'
            ' cat(paste(s, ids, sep = "\\t"), sep = "\\n"); cat("\\n") }')
    p = subprocess.run([RSCRIPT, "-e", code], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr[-2000:]
    out = {}
    for ln in p.stdout.splitlines():
        if ln:
            stem, vid = ln.split("\t")
            out.setdefault(stem, []).append(vid)
    return out


def test_pairs_are_production_arms():
    for a, b in MATCHED_PAIRS:
        assert ARMS[a]["stage"] == ARMS[b]["stage"] == "production"
        assert ARMS[a]["validator_mode"] == ("identity_matched" if a.endswith("A2") or a == "A2_identity"
                                             else "real_ld")


def test_fixture_a2_a3_retained_sets_identical(r4_e2e):
    root = r4_e2e["root"]
    a3, a2 = retained_ids(root, "A3_1kg"), retained_ids(root, "A2_identity")
    print(f"retained variants: A3 {len(a3)}, A2 {len(a2)}")
    assert set(a3) == set(a2) and len(a3) == len(a2)
    assert len(a3) == r4_e2e["A3_1kg"]["json"]["ld_overlap"] == r4_e2e["A2_identity"]["json"]["ld_overlap"]


def matched_set_problems(root):
    """None while no matched-arm dir exists; else every problem found (empty list = pass)."""
    present = {arm: (root / _fit_dir(arm)).is_dir() for pair in MATCHED_PAIRS for arm in pair}
    if not any(present.values()):
        return None
    problems = []
    for a, b in MATCHED_PAIRS:
        if present[a] != present[b]:
            problems.append(f"{a} present={present[a]} but {b} present={present[b]}")
            continue
        if not present[a]:
            continue
        ra, rb = _retained_by_stem(root / _fit_dir(a)), _retained_by_stem(root / _fit_dir(b))
        common = sorted(set(ra) & set(rb))
        if not common:
            problems.append(f"{a} / {b}: no (trait, ancestry, region) fitted in both")
        for stem in common:
            if set(ra[stem]) != set(rb[stem]):
                problems.append(f"{stem}: {a} {len(ra[stem])} ids != {b} {len(rb[stem])} ids")
    return problems


def test_live_matched_arms_have_identical_variant_sets():
    problems = matched_set_problems(REPO_ROOT)
    if problems is None:
        pytest.skip("no matched-arm fits yet (W5a enables)")
    assert problems == []


def test_live_gate_controls(r4_e2e, tmp_path):
    """The gate can fail: one arm of a pair present alone, and two present arms with different sets."""
    src = r4_e2e["root"]
    assert matched_set_problems(tmp_path) is None
    a3 = tmp_path / _fit_dir("A3_1kg")
    a3.mkdir(parents=True)
    shutil.copy2(src / paths.fit_rds("A3_1kg", TRAIT, ANC, REGION), a3)
    assert matched_set_problems(tmp_path) == ["A2_identity present=False but A3_1kg present=True"]
    a2 = tmp_path / _fit_dir("A2_identity")
    a2.mkdir(parents=True)
    _rds = Path(paths.fit_rds("A2_identity", TRAIT, ANC, REGION)).name
    code = (f'f <- readRDS("{src / paths.fit_rds("A2_identity", TRAIT, ANC, REGION)}"); '
            f'f$pip <- f$pip[-1]; saveRDS(f, "{a2 / _rds}")')
    assert subprocess.run([RSCRIPT, "-e", code], capture_output=True).returncode == 0
    assert matched_set_problems(tmp_path) == [f"{TRAIT}.{ANC}.{REGION}: A2_identity 58 ids != A3_1kg 59 ids"]
    shutil.copy2(src / paths.fit_rds("A2_identity", TRAIT, ANC, REGION), a2 / _rds)
    assert matched_set_problems(tmp_path) == []
