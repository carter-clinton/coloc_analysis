"""W3f 15.8d (Q-157J R3): E7 fit_yield compares purity-filtered with purity-filtered set counts.

The frozen side is the earlier route-L fit's stored set count (length(fit$sets$cs), manifests/fit_cs_json_vs_rds.tsv
n_cs_rds_sets; NA for an early exit); the earlier JSON count, which includes impure sets, is kept in
frozen_value_json_unfiltered. manifests/fit_cs_repro_routeL_exact_purity.tsv records that the stored counts equal the
exact-purity counts R4 uses.
"""
from __future__ import annotations

import csv
import json
import subprocess

import pandas as pd
import pytest

from .conftest import MAN_DIR, REPO_ROOT

from ta_r4 import estimands, r4_lock_gate, run_aggregation
from ta_r4 import sh2b3_known_answer as ska

RSCRIPT = "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript"
FILTERED = MAN_DIR / "fit_cs_json_vs_rds.tsv"
EXACT_MANIFEST = MAN_DIR / "fit_cs_repro_routeL_exact_purity.tsv"
W3A = MAN_DIR / "known_answer_W3a.tsv"


def _tsv(p):
    return pd.read_csv(p, sep="\t", dtype=str, keep_default_na=False)


def _empty(*cols):
    return pd.DataFrame(columns=list(cols))


def _e7(w3a, filtered, fits=None):
    fits = fits if fits is not None else _empty("arm", "trait", "ancestry", "region_safe", "status", "n_cs",
                                                "ld_allele_exact", "ld_allele_flipped")
    return estimands.e7_frozen_vs_fixed(
        w3a, _empty("config_label", "pair_id", "status", "pp_h4_reproduced"), fits,
        _empty("row_id", "label", "p12_key", "region_stat"), [], a3_arm={"EUR": "A3_1kg", "AFR": "A3_AFR"},
        p12_key="p12_primary", fit_cs_filtered=filtered)


def _w3a(*rows):
    return pd.DataFrame([dict(zip(("pair", "trait", "ancestry", "region_safe", "status_L", "n_cs_L"), r))
                         for r in rows])


def _filtered(*rows):
    return pd.DataFrame([dict(zip(("trait", "ancestry", "region_safe", "status", "n_cs_json", "n_cs_rds_sets",
                                   "eq"), r)) for r in rows])


def test_frozen_value_is_the_purity_filtered_count():
    t = _e7(_tsv(W3A), _tsv(FILTERED)).query("section == 'fit_yield'").set_index("id")
    assert len(t) == 96
    assert t.loc["asthma.AFR.APOE_19q13", "frozen_value"] == "ok;n_cs=0"
    assert t.loc["asthma.AFR.APOL1_22q12", "frozen_value"] == "ok;n_cs=0"
    assert t.loc["asthma.AFR.BMI_5q13_3", "frozen_value"] == "too_many_variants;n_cs=NA"
    fc = _tsv(FILTERED)
    want = {f"{r.trait}.{r.ancestry}.{r.region_safe}": f"{r.status};n_cs={r.n_cs_rds_sets}" for r in fc.itertuples()}
    assert t.frozen_value.to_dict() == want
    assert run_aggregation.FIT_CS_FILTERED == f"{run_aggregation.paths.MAN}/fit_cs_json_vs_rds.tsv"


def test_unfiltered_json_count_is_kept_in_its_labelled_column():
    w3a = _tsv(W3A)
    t = _e7(w3a, _tsv(FILTERED))
    assert list(t.columns)[-3:] == ["fixed_value_qtl_4dp", "changed_qtl_4dp", "frozen_value_json_unfiltered"]
    fy = t[t.section == "fit_yield"].set_index("id")
    assert fy.loc["asthma.AFR.APOE_19q13", "frozen_value_json_unfiltered"] == "ok;n_cs=7"
    want = {f"{r.trait}.{r.ancestry}.{r.region_safe}": f"{r.status_L};n_cs={r.n_cs_L}"
            for r in w3a[w3a.pair == "real_ld"].itertuples()}
    assert fy.frozen_value_json_unfiltered.to_dict() == want
    assert (t[t.section != "fit_yield"].frozen_value_json_unfiltered == "").all()


def test_changed_compares_filtered_with_filtered():
    from ta_r4.estimands import fit_frame

    from .test_estimands import _fitdoc

    w3a = _w3a(("real_ld", "asthma", "EUR", "R1", "ok", "7"), ("real_ld", "bmi", "EUR", "R1", "ok", "2"))
    fc = _filtered(("asthma", "EUR", "R1", "ok", "7", "0", "false"), ("bmi", "EUR", "R1", "ok", "2", "2", "true"))
    fits = fit_frame([("A3_1kg", "asthma", "EUR", "R1", _fitdoc(0, exact=1, flipped=0)),
                      ("A3_1kg", "bmi", "EUR", "R1", _fitdoc(1, exact=1, flipped=0))])
    fy = _e7(w3a, fc, fits).query("section == 'fit_yield'").set_index("id")
    a = fy.loc["asthma.EUR.R1"]
    assert (a.frozen_value, a.fixed_value, a.frozen_value_json_unfiltered) == ("ok;n_cs=0", "ok;n_cs=0", "ok;n_cs=7")
    assert a.changed == False  # noqa: E712  (JSON 7 / filtered 0 vs fixed 0: no change in yield)
    b = fy.loc["bmi.EUR.R1"]
    assert (b.frozen_value, b.fixed_value) == ("ok;n_cs=2", "ok;n_cs=1") and b.changed == True  # noqa: E712


def test_missing_or_mismatched_filtered_row_raises():
    w3a = _w3a(("real_ld", "asthma", "EUR", "R1", "ok", "7"), ("k2d", "bmi", "EUR", "R1", "ok", "2"))
    good = ("asthma", "EUR", "R1", "ok", "7", "0", "false")
    assert len(_e7(w3a, _filtered(good)).query("section == 'fit_yield'")) == 1
    with pytest.raises(KeyError, match="no fit_cs_filtered row"):
        _e7(w3a, _filtered(("bmi", "EUR", "R1", "ok", "2", "2", "true")))
    with pytest.raises(ValueError, match="does not match"):
        _e7(w3a, _filtered(("asthma", "EUR", "R1", "non_converged", "7", "0", "false")))
    with pytest.raises(ValueError, match="does not match"):
        _e7(w3a, _filtered(("asthma", "EUR", "R1", "ok", "6", "0", "false")))
    with pytest.raises(ValueError, match="more than one row"):
        _e7(w3a, _filtered(good, good))


def test_filtered_manifest_is_a_locked_path():
    rel = f"{r4_lock_gate.PHASE_REL}/manifests/fit_cs_json_vs_rds.tsv"
    lp = r4_lock_gate.LOCKED_PATHS
    assert rel in lp
    assert lp.index(rel) == lp.index(f"{r4_lock_gate.PHASE_REL}/manifests/known_answer_W3a.tsv") + 1
    r = subprocess.run(["git", "ls-files", "--error-unmatch", "--", rel], cwd=REPO_ROOT, capture_output=True)
    assert r.returncode == 0
    assert (REPO_ROOT / rel) == FILTERED


_OVER_100_R = r"""
for (p in commandArgs(TRUE)) {
  f <- readRDS(p)
  n <- if (is.list(f) && !is.null(f$sets))
    c(sum(lengths(susieR::susie_get_cs(f, coverage = f$sets$requested_coverage)$cs) > 100),
      sum(lengths(f$sets$cs) > 100)) else c(NA, NA)
  writeLines(paste(p, n[1], n[2], sep = "\t"))
}
"""


@pytest.mark.r4_heavy
def test_exact_purity_manifest_matches_the_stored_counts(monkeypatch):
    monkeypatch.setattr(ska, "RSCRIPT", RSCRIPT)
    monkeypatch.chdir(REPO_ROOT)
    ex = list(csv.DictReader(open(EXACT_MANIFEST, newline=""), delimiter="\t"))
    fc = list(csv.DictReader(open(FILTERED, newline=""), delimiter="\t"))
    assert len(ex) == 96
    cols = ("trait", "ancestry", "region_safe", "status")
    assert [tuple(r[c] for c in cols) + (r["n_cs_rds_sets"],) for r in ex] == \
        [tuple(r[c] for c in cols) + (r["n_cs_rds_sets"],) for r in fc]
    keys = [(r["trait"], r["ancestry"], r["region_safe"]) for r in ex]
    stored = ska.rds_cs_counts("repro_routeL", keys)
    rds = [ska.paths.fit_rds("repro_routeL", *k) for k in keys]
    out = subprocess.run([RSCRIPT, "-e", _OVER_100_R, *rds], check=True, capture_output=True, text=True).stdout
    over = {ln.split("\t")[0]: tuple(ln.split("\t")[1:]) for ln in out.splitlines()}
    for k, p, r in zip(keys, rds, ex):
        s = "NA" if stored[k] is None else str(stored[k])
        assert (r["n_cs_rds_sets"], r["n_components_over_100"], r["n_stored_over_100"]) == (s, *over[p]), k
        if s == "NA":
            assert (r["n_cs_exact"], r["eq"]) == ("NA", "NA"), k
        else:
            # exact purity <= subsampled purity, and only a set over 100 members is subsampled: with no stored set
            # over 100 members the exact count is the stored count
            assert r["n_stored_over_100"] == "0" and r["n_cs_exact"] == s and r["eq"] == "true", k
